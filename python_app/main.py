import argparse
from NL_to_SPARQL import translate_nl_to_sparql
from SPARQL_to_NL import translate_sparql_to_nl
import execute_queries

def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["nl2sparql", "sparql2nl", "testrun"], help="Choose operation: nl2sparql, sparql2nl or testrun")
    args = p.parse_args()

    if args.mode == "nl2sparql":
        translate_nl_to_sparql()
    elif args.mode == "sparql2nl":
        translate_sparql_to_nl()
    else: 
        execute_queries.run_generated_queries()

if __name__ == "__main__":
    main()
