import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

BASE_POD_DIR = pathlib.Path(os.getenv("BASE_POD_DIR", "."))
NUM_PODS = int(os.getenv("NUM_PODS", "6"))
FUSEKI_ENDPOINT = os.getenv("FUSEKI_ENDPOINT", "http://localhost:3030/solid-pod-1/sparql")

NATURAL_LANGUAGE_QUESTION = "Which NORTEC components are available for reuse?"

GENERATED_RESULTS_FILE = pathlib.Path(__file__).parent / "query_results.txt"
GENERATED_QUERIES_FILE = pathlib.Path(__file__).parent / "generated_queries.txt"
GENERATED_NL_FILE = pathlib.Path(__file__).parent / "generated_nl.txt"
EXAMPLE_NL_TO_SPARQL = pathlib.Path(__file__).parent / "example_nl_to_SPARQL.txt"
EXAMPLE_SPARQL_TO_NL = pathlib.Path(__file__).parent / "example_SPARQL_to_nl.txt"
