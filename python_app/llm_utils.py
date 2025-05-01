import os
import pathlib
from typing import Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

def load_azure_client():
    load_dotenv()
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_API_KEY")
    api_version = os.getenv("AZURE_API_VERSION")
    deployment  = os.getenv("AZURE_DEPLOYMENT_NAME")

    if not all([endpoint, key, deployment]):
        raise EnvironmentError(
            "Missing Azure OpenAI config; set AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME in .env"
        )
    
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=api_version
    )
    return client, deployment

def read_ttl_files(directory_path: pathlib.Path) -> Dict[str,str]:
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

def call_llm(client: AzureOpenAI, model: str, prompt: str) -> str:
    """Sends the prompt to Azure OpenAI."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":"You are an RDF/SPARQL expert."},
                {"role":"user",  "content":prompt}
            ],
            max_completion_tokens=100000,
        )

        query = response.choices[0].message.content.strip()
        return query
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        return None
