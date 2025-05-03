import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

BASE_POD_DIR = pathlib.Path(os.getenv("BASE_POD_DIR", "."))
NUM_PODS = int(os.getenv("NUM_PODS", "5"))

NATURAL_LANGUAGE_QUESTION = "Which NORTEC components are available for reuse?"

GENERATED_QUERIES_FILE = pathlib.Path(__file__).parent / "generated_queries.txt"
GENERATED_NL_FILE = pathlib.Path(__file__).parent / "generated_nl.txt"
