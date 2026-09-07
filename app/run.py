"""Ponto de entrada da aplicacao."""

import os

from snh_paths import repo_path
from presentation.cli.bootstrap import main


if __name__ == "__main__":
    root = repo_path()
    os.chdir(root)
    main(root)
