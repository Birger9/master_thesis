# master_thesis

Application Flow:

1. User Input: The process begins when a user launches the app.py script and enters a question into the Gradio chatbot interface.
2. NL to SPARQL Translation: The user's message is passed to the translate_nl_to_sparql function.
    - This function gathers context from meta_data.py and the .ttl ontology files.
    - It constructs a detailed prompt and sends it to the Azure LLM via llm_utils.py
    - The LLM returns a federated SPARQL query, which is displayed in the chat UI and appended to generated_queries.txt.
3. SPARQL to NL Translation: The newly generated SPARQL query is immediately passed to the translate_sparql_to_nl function.
    - This function builds a new prompt, asking the LLM to explain the query in simple terms using the ontologies for context.
    - The LLM returns a natural language explanation.
4. Final Output: This explanation is displayed as a response in the chatbot UI and appended to generated_nl.txt.

.env files needs to contain the following data:
1. BASE_POD_DIR (The path to the solid_pods folder)
2. NUM_PODS (Number of Solid Pods, currently 6)
3. FUSEKI_ENDPOINT (The endpoint you want to query with your Federated SPARQL query, right now: http://localhost:3030/solid-pod-1/sparql)

How to start fuseki-sever:
Command: docker run -d --name fuseki -p 3030:3030 -e ADMIN_PASSWORD=pw123 stain/jena-fuseki

In the fuseki-server UI (http://localhost:3030/#/):
Steps:
1. Username: Admin and password: pw123
2. Create 5 datasets called solid-pod-1 to solid-pod-5
3. Then upload for each solid pod their Ontology data and RDF data (Do not set a dataset graph name)
 
Query Execution (Testing):
This part of the pipeline is run manually for testing purposes and is separate from the user-facing application.

1. Run Command: A developer executes python run.py testrun from the command line (PS. the fuseki server needs to on and have data, see How to start fuseki-sever and In the fuseki-server UI).
2. Execute Queries: The run_generated_queries function in execute_queries.py reads the queries in the file: generated_queries.txt.
3. Fetch Results: It sends each query to the Fuseki SPARQL endpoint defined in config.py (It does not matter which endpoint/dataset you query as it will call other endpoints/datasets, so Federated SPARQL queries are supported).
4. Save Results: The server's response for each query is appended to the query_results.txt file for analysis.

File information:

1. generated_nl.txt contains all the LLM-generated NL explanations of SPARQL queries by the pipeline.
2. generated_queries.txt contains all the LLM-generated SPARQL queries by the pipeline.
3. query_results.txt contains all the results set returned by the fuseki server when executing the LLM-generated SPARQL queris in the generated_queries.txt file.

File Overview

This section provides a brief overview of the key files in this repo

- app.py:
Launches the Gradio web application. It provides a chatbot interface where users can input natural language questions. The application handles the full translation pipeline: NL → SPARQL → NL Explanation, displaying the intermediate and final results in the chat UI.

- NL_to_SPARQL.py
Contains the core logic for translating a natural language question into a federated SPARQL query. It dynamically builds a detailed prompt for the LLM, incorporating pod metadata, ontology definitions, and an optional one-shot example.

- SPARQL_to_NL.py
Handles the reverse translation from a SPARQL query back to a natural language explanation. It constructs a prompt with the query and relevant ontologies to ask the LLM for a human-readable description.

- llm_utils.py
A utility module for interacting with the Azure OpenAI LLM. It includes helper functions for loading API credentials from a .env file, making API calls, and reading .ttl ontology files from the pod directories.

- execute_queries.py
A script to execute the generated SPARQL queries, used by main.py, against the specified Fuseki SPARQL endpoint. It reads queries from the output file (generated_queries.txt), sends them to the server, and saves the JSON results.

- main.py
It provides a testrun command to conveniently execute all generated SPARQL queries via the execute_queries.py script. Command: python main.py testrun

- config.py
Centralizes all configuration variables for the project. This includes file paths for generated outputs, the Fuseki endpoint URL, and Solid Pod directory settings.

- meta_data.py
Contains a Python dictionary (POD_METADATA) that stores descriptive metadata for each Solid Pod, such as its name, description, and URLs. This information is used to provide essential context to the LLM during prompt generation.


