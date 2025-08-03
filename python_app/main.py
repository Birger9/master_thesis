"""
CLI tool for test running (executing) LLM-generated SPARQL queries.
"""

import argparse
from execute_queries import run_generated_queries

def main():
    """Parse args and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(
        description="Execute generated SPARQL queries for testing."
    )
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
        description="Available commands"
    )

    subparsers.add_parser(
        "testrun",
        help="Execute all generated SPARQL queries."
    )

    args = parser.parse_args()

    if args.command == "testrun":
        run_generated_queries()

if __name__ == "__main__":
    main()
