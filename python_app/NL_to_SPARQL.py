"""
Translates a natural language question into a federated SPARQL query.

This module is responsible for taking a user's NL question, gathering contextual
information from multiple Solid Pods (metadata and ontologies), constructing
a detailed prompt, and using an LLM to generate the corresponding SPARQL query.
"""

from typing import List, Dict, Optional
from llm_utils import load_azure_client, read_ttl_files, call_llm
from meta_data import POD_METADATA
from config import BASE_POD_DIR, NUM_PODS, GENERATED_QUERIES_FILE, EXAMPLE_NL_TO_SPARQL

def load_one_shot_nl_to_sparql_example() -> Optional[str]:
    """
    Loads a pre-written example of an NL-to-SPARQL translation.

    This is used to provide a one-shot demonstration to the LLM to guide it
    towards generating a query in the correct format and style.
    """
    try:
        example_str = EXAMPLE_NL_TO_SPARQL.read_text(encoding="utf-8")
        return example_str
    except FileNotFoundError:
        raise FileNotFoundError("One Shot NL to SPARQL example file not found")

def build_nl_to_sparql_prompt(nl_question: str, pod_details: List[Dict], example: Optional[str]) -> str:
    """
    Constructs the full prompt for the LLM to translate a question to SPARQL.

    The prompt includes instructions, pod descriptions, pod URLs, full ontology
    contents for context, the user's NL question, and an optional one-shot example.
    """
    prompt_head = (
        f"You will translate a natural language question into a Federated SPARQL query for Solid Pods. "
        f"You will be provided with background information about several Solid Pods that store both RDF data and ontologies. "
        f"Use that context to generate a correct SPARQL query that reflects the intent of the following natural language question: {{{nl_question}}}\n"
    )
    background_intro = "\nBackground Information:\n"
    pod_summaries = ""
    pod_urls = "\nSolid Pods URLs:\n"
    pod_ontology_details = "\nPod Ontologies:\n"

    for i, pod in enumerate(pod_details):
        pod_summaries += (
            f"Pod {i} - {pod['name']}: {pod['description']}\n"
            f"Ontology URL: {pod['ontology_url']}\n"
        )
        pod_urls += f"Pod {i - 1} - {pod['pod_url']}\n"
        pod_ontology_details += (
            f"Pod {i} - Ontology ({pod['ontology_filename']}):\n"
            f"\n{pod['ontology_content']}\n\n"
        )

    example_section = ""
    if example:
        example_section = (
            "\nExample: \n"
            f"{example.strip()}\n"
        )

    prompt_tail = (
        "\nBased on the given background information and the given natural language question, "
        "generate a Federated SPARQL query. Output just the Federated SPARQL query"
    )
    return prompt_head + background_intro + pod_summaries + pod_urls + pod_ontology_details + example_section + prompt_tail

def translate_nl_to_sparql(nl_question: str, one_shot: bool = False):
    """
    Handles the translation of a natural language question to SPARQL.

    This main function gathers pod metadata and ontologies, builds the prompt,
    calls the LLM, and then saves and returns the generated SPARQL query.
    """
    print("Reading Pod metadata and ontologies")

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
        print("No pod metadata loaded. Exiting.")
        exit(1)
    
    example_str = None
    if one_shot:
        example_str = load_one_shot_nl_to_sparql_example()

    print(f"Loaded metadata and ontologies for {len(pod_details)} pods.")
    client, model = load_azure_client()

    print("Building LLM prompt...")
    prompt = build_nl_to_sparql_prompt(nl_question, pod_details, example=example_str) 

    print("Sending prompt to Azure OpenAI...")
    sparql_query = call_llm(client, model, prompt)

    try:
        with open(GENERATED_QUERIES_FILE, "a", encoding="utf-8") as f:
            f.write(sparql_query)
            f.write("\n---\n")
        print(f"Generated query appended to {GENERATED_QUERIES_FILE}")
    except Exception as e:
        print(f"Error writing to {GENERATED_QUERIES_FILE}: {e}")

    print("--- Generated Federated SPARQL Query ---")
    print(sparql_query)
    print("--- End Query ---")
    return sparql_query
