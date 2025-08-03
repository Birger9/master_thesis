"""
Translates a SPARQL query into a human-readable, natural language description.

This module handles the process of taking a SPARQL query, gathering
context from local ontology files, and using an LLM to generate a clear
explanation of what the query does.
"""

from typing import List, Dict, Optional
from llm_utils import load_azure_client, read_ttl_files, call_llm
from config import BASE_POD_DIR, NUM_PODS, GENERATED_NL_FILE, EXAMPLE_SPARQL_TO_NL
from meta_data import POD_METADATA

def load_one_shot_sparql_to_nl_example() -> Optional[str]:
    """
    Loads a pre-written example of a SPARQL-to-NL translation.
    
    This example is used to provide a one-shot demonstration to the LLM,
    guiding it towards the desired output format and style.
    """
    try:
        example_str = EXAMPLE_SPARQL_TO_NL.read_text(encoding="utf-8")
        return example_str
    except FileNotFoundError:
        raise FileNotFoundError("One Shot SPARQL to NL example file not found")

def build_sparql_to_nl_prompt(sparql_query: str, pod_details: List[Dict], example: Optional[str]) -> str:
    """
    Builds the full prompt for the LLM to translate a SPARQL query to NL.
    """
     
    prompt_head = (
        "You will translate a Federated SPARQL query into a natural language description in English.\n" \
        "Describe the federated SPARQL query in a comprehensible, concise and easy way to understand for a non-technical reader.\n"
        "The description should be written as a flowing text.\n"
        "Use the following ontologies as context.\n"
    )
    background_intro = "\nOntologies:\n"
    summary = ""
    for i, p in enumerate(pod_details, 1):
        summary += (
            f"Pod {i - 1} - {p['name']} ontology ({p['ontology_filename']}):\n\n"
            f"{p['ontology_content']}\n\n"
        )
    prompt_tail = "\nSPARQL Query that you will translate:\n\n" + sparql_query + "\n\n"
    prompt_tail += "Output only the natural language description."

    example_section = ""
    if example:
        example_section = (
            "\nExample:\n"
            f"{example.strip()}\n"
        )
    return prompt_head + background_intro + summary + example_section + prompt_tail

def translate_sparql_to_nl(sparql: str, one_shot: bool = False):
    """
    Handles the translation of a SPARQL query to natural language.
    """
    print("Reading ontologies from Solid Pods")
    pod_details = []
    for i in range(0, NUM_PODS):
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
    
    example_str = None
    if one_shot:
        example_str = load_one_shot_sparql_to_nl_example()
    
    print(f"Loaded data for {len(pod_details)} pods.")
    client, model = load_azure_client()

    print("Building LLM prompt...")
    prompt = build_sparql_to_nl_prompt(sparql, pod_details, example=example_str)

    print("Sending prompt to Azure OpenAI...")
    nl = call_llm(client, model, prompt)

    try:
        with open(GENERATED_NL_FILE, "a", encoding="utf-8") as f:
            f.write(nl)
            f.write("\n---\n")
        print(f"Generated NL appended to {GENERATED_NL_FILE}")
    except Exception as e:
        print(f"Error writing to {GENERATED_NL_FILE}: {e}")

    print("--- Generated Natural Language ---") 
    print(nl)
    print("--- End ---")
    return nl
