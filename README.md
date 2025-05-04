# master_thesis
How to start fuseki-sever:

Command: docker run -d --name fuseki -p 3030:3030 -e ADMIN_PASSWORD=pw123 stain/jena-fuseki

In the fuseki-server UI:

Steps:
1. Create 5 datasets called solid-pod-1 to solid-pod-5
2. Then upload for each solid pod their Ontology data and RDF data (Do not set a dataset graph name)
3. Then you can run command: python main.py testrun (It does not matter which dataset you query as it will call other datasets (so Federated SPARQL queries works))
