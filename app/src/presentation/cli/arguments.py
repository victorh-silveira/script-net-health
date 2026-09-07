"""Parser de argumentos da CLI."""

import argparse


def parse_args() -> argparse.Namespace:
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Script Net Health")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Reporta apenas o status da aplicacao",
    )
    return parser.parse_args()
