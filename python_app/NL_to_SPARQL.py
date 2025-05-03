import pathlib
from typing import List, Dict
import os

from llm_utils import load_azure_client, read_ttl_files, call_llm
from meta_data import POD_METADATA
from main import BASE_POD_DIR

NATURAL_LANGUAGE_QUESTION = "Which NORTEC components are available for reuse?"

def build_nl_to_sparql_prompt(nl_question: str, pod_details: List[Dict]) -> str:
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

def translate_nl_to_sparql():
    print("Reading TTL data from Solid Pods")

    pod_details = []
    for i in range(1, int(os.getenv("NUM_PODS","5"))+1):
        pod_key = f"solid_pod_{i}"
        pod_dir = BASE_POD_DIR / pod_key
        ont = read_ttl_files(pod_dir / "ontology")
        data = read_ttl_files(pod_dir / "data")
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
    client, model = load_azure_client()

    print("Building LLM prompt...")
    prompt = build_nl_to_sparql_prompt(NATURAL_LANGUAGE_QUESTION, pod_details)

    print("Sending prompt to Azure OpenAI...")
    sparql_query = call_llm(client, model, prompt)

    output_file = pathlib.Path(__file__).parent / "generated_queries.txt"
    try:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(sparql_query)
            f.write("\n---\n")
        print(f"Generated query appended to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

    print("--- Generated Federated SPARQL Query ---") 
    print(sparql_query)
    print("--- End Query ---")
