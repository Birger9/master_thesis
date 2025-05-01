import pathlib
from typing import List, Dict
import os

from llm_utils import load_azure_client, read_ttl_files, call_llm
from python_app.main import BASE_POD_DIR
from python_app.meta_data import POD_METADATA

def build_sparql_to_nl_prompt(sparql_query: str, pod_details: List[Dict]) -> str:
    prompt_head = (
        "You will translate a Federated SPARQL query into a natural language description.\n"
        "Use the following ontologies as context.\n"
    )
    background_intro = "\nOntologies:\n"
    summary = ""
    for i,p in enumerate(pod_details,1):
        summary += (
            f"Pod {i} - {p['name']} ontology ({p['ontology_filename']}):\n\n"
            f"{p['ontology_content']}\n\n"
        )
    prompt_tail = "\nSPARQL Query:\n\n" + sparql_query + "\n\n"
    prompt_tail += "Output just the plain English description of what this query does."
    return prompt_head + background_intro + summary + prompt_tail

def translate_sparql_to_nl(sparql_query: str):
    print("Reading ontologies from Solid Pods")

    pod_details = []
    for i in range(1, int(os.getenv("NUM_PODS","5"))+1):
        pod_key = f"solid_pod_{i}"
        pod_dir = BASE_POD_DIR / pod_key
        ont = read_ttl_files(pod_dir / "ontology")
        ont_fn = next(iter(ont.keys()), "ontology.ttl")
        pod_details.append({
            "id": pod_key,
            **POD_METADATA[pod_key],
            "ontology_filename": ont_fn,
            "ontology_content": ont.get(ont_fn, ""),
        })

    if not pod_details:
        print("No pod data loaded. Exiting.")
        exit(1)
    
    print(f"Loaded data for {len(pod_details)} pods.")
    client, model = load_azure_client()

    print("Building LLM prompt...")
    prompt = build_sparql_to_nl_prompt(sparql_query, pod_details)

    print("Sending prompt to Azure OpenAI...")
    nl = call_llm(client, model, prompt)

    output_file = pathlib.Path(__file__).parent / "generated_nl.txt"
    try:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(nl)
            f.write("\n---\n")
        print(f"Generated NL appended to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

    print("--- Generated Natural Language ---") 
    print(nl)
    print("--- End ---")
