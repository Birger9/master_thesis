import argparse
from NL_to_SPARQL import translate_nl_to_sparql
from SPARQL_to_NL import translate_sparql_to_nl

def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["nl2sparql","sparql2nl"], help="Choose operation: nl2sparql or sparql2nl")
    args = p.parse_args()

    if args.mode == "nl2sparql":
        translate_nl_to_sparql()
    else:
        translate_sparql_to_nl()

if __name__ == "__main__":
    main()
