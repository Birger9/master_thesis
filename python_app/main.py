import os
import pathlib
from dotenv import load_dotenv
from typing import Dict, List, Optional
from openai import AzureOpenAI

load_dotenv()  # Load environment variables from .env file

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-12-01-preview")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")  

if not all([AZURE_ENDPOINT, AZURE_API_KEY, DEPLOYMENT_NAME]):
    raise EnvironmentError(
        "Missing Azure OpenAI config. Please set AZURE_ENDPOINT, AZURE_API_KEY, and AZURE_DEPLOYMENT_NAME in .env"
    )

OPENAI_MODEL = DEPLOYMENT_NAME
SCRIPT_ROOT    = pathlib.Path(__file__).parent.resolve()
base_subdir    = os.getenv("BASE_POD_DIR", "solid_pods")
BASE_POD_DIR   = SCRIPT_ROOT / base_subdir
NUM_PODS = int(os.getenv("NUM_PODS", "5"))
NATURAL_LANGUAGE_QUESTION = "Which NORTEC components are available for reuse?"

POD_METADATA = {
    "solid_pod_1": {
        "name": "Lindner",
        "description": "Contains product/component data and related Ontology associated with products and components.",
        "ontology_url": "http://localhost:3001/ontology#",
        "data_url": "http://localhost:3001/data/",
        "pod_url": "http://localhost:3001"
    },
    "solid_pod_2": {
        "name": "Concular",
        "description": "Contains inventory and assessment of an inventory item with the associated Ontology.",
        "ontology_url": "http://localhost:3002/ontology#",
        "data_url": "http://localhost:3002/data/",
        "pod_url": "http://localhost:3002"
    },
    "solid_pod_3": {
        "name": "Ragnsells",
        "description": "Contains facility data and the associated Ontology.",
        "ontology_url": "http://localhost:3003/ontology#",
        "data_url": "http://localhost:3003/data/",
        "pod_url": "http://localhost:3003"
    },
    "solid_pod_4": {
        "name": "Riksbyggen",
        "description": "Contains building data with the associated Ontology.",
        "ontology_url": "http://localhost:3004/ontology#",
        "data_url": "http://localhost:3004/data/",
        "pod_url": "http://localhost:3004"
    },
    "solid_pod_5": {
        "name": "Bring",
        "description": "Contains logistics data with the associated Ontology.",
        "ontology_url": "http://localhost:3005/ontology#",
        "data_url": "http://localhost:3005/data/",
        "pod_url": "http://localhost:3005"
    }
}

# --- Helper Functions ---

def read_ttl_files_content(directory_path: pathlib.Path) -> Dict[str, str]:
    """Reads all .ttl files in a directory and returns their content."""
    content_dict: Dict[str, str] = {}
    if not directory_path.is_dir():
        print(f"Warning: Directory not found: {directory_path}")
        return content_dict
    for file_path in directory_path.glob("*.ttl"):
        try:
            content_dict[file_path.name] = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    return content_dict


def build_llm_prompt(nl_question: str, pod_details: List[Dict]) -> str:
    """Constructs the prompt for the LLM based on the template."""
    prompt_head = (
        f"You will translate a natural language question into a Federated SPARQL query for Solid Pods. "
        f"You will be provided with background information about several Solid Pods that store RDF data and ontologies. "
        f"Use that context to generate a correct SPARQL query that reflects the intent of the following natural language question: {{{nl_question}}}\n"
    )
    background_intro = "\nBackground Information:\n"
    pod_summaries = ""
    pod_urls = "\nSolid Pods URLS:\n"
    pod_data_details = "\nSolid Pods Data:\n"

    for i, pod in enumerate(pod_details):
        idx = i + 1
        pod_summaries += (f"Pod {idx} - {pod['name']}: {pod['description']}\n"
                          f"  Ontology URL: {pod['ontology_url']}\n"
                          f"  Data URL: {pod['data_url']}\n")
        pod_urls += f"Pod {idx} - {pod['pod_url']}\n"
        pod_data_details += (
            f"Pod {idx} - Ontology ({pod['ontology_filename']}):\n\n{pod['ontology_content']}\n\n"
            f"Pod {idx} - RDF Data ({pod['data_filename']}):\n\n{pod['data_content']}\n\n"
        )

    prompt_tail = (
        "\nBased on the given background information and the given natural language question, "
        "generate a Federated SPARQL query. Output just the Federated SPARQL query"
    )

    return prompt_head + background_intro + pod_summaries + pod_urls + pod_data_details + prompt_tail


def get_sparql_from_llm(prompt: str, client: AzureOpenAI, model: str) -> Optional[str]:
    """Sends the prompt to Azure OpenAI and retrieves the SPARQL query."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": 
                 "You are an expert in RDF, SPARQL, Solid Pods, and translating natural language to Federated SPARQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        query = response.choices[0].message.content.strip()

        for fence in ("```sparql", "```json", "```"):
            if query.startswith(fence):
                query = query[len(fence):].strip()
            if query.endswith("```"):
                query = query[:-3].strip()
        return query
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        return None

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting NL to Federated SPARQL Pipeline")
    print(f"Using BASE_POD_DIR: {BASE_POD_DIR.resolve()}")


    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )

    print("Reading TTL data from Solid Pods")
    pod_details = []
    for i in range(1, NUM_PODS + 1):
        pod_key = f"solid_pod_{i}"
        pod_dir = BASE_POD_DIR / pod_key
        ont = read_ttl_files_content(pod_dir / "ontology")
        data = read_ttl_files_content(pod_dir / "data")
        ont_fn = next(iter(ont.keys()), "ontology.ttl")
        data_fn = next(iter(data.keys()), "data.ttl")
        pod_details.append({
            "id": pod_key,
            **POD_METADATA[pod_key],
            "ontology_filename": ont_fn,
            "ontology_content": ont.get(ont_fn, ""),
            "data_filename": data_fn,
            "data_content": data.get(data_fn, ""),
        })

    if not pod_details:
        print("No pod data loaded. Exiting.")
        exit(1)

    print(f"Loaded data for {len(pod_details)} pods.")
    #print("Building LLM prompt...")
    #prompt = build_llm_prompt(NATURAL_LANGUAGE_QUESTION, pod_details)

    #print("Sending prompt to Azure OpenAI...")
    #sparql_query = get_sparql_from_llm(prompt, client, OPENAI_MODEL)

    #if not sparql_query:
    #    print("Failed to generate SPARQL query. Exiting.")
    #   exit(1)

    #print("--- Generated Federated SPARQL Query ---")
    #print(sparql_query)
    #print("--- End Query ---")
