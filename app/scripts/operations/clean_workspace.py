from __future__ import annotations

import argparse
import sys
from pathlib import Path


OPERATIONS = Path(__file__).resolve().parent
if str(OPERATIONS) not in sys.path:
    sys.path.insert(0, str(OPERATIONS))

from config_gates import run_config_text
from gate_runtime import AREA_STAGES, AREAS, STAGES, fail, use_app_cwd
from python_gates import (
    stage_build,
    stage_clean,
    stage_lint,
    stage_security,
    stage_test,
    stage_validate,
)


def _dispatch(area: str, stage: str, coverage_fail_under: int) -> None:
    if area not in AREA_STAGES:
        fail(f"[ERRO] Area '{area}' nao suportada")
    allowed = AREA_STAGES[area]
    if stage == "clean":
        stage_clean()
        return
    if stage not in allowed:
        fail(f"[ERRO] Stage '{stage}' nao suportado para area '{area}'")
    if stage == "lint":
        stage_lint()
        return
    if stage == "validate":
        stage_validate()
        return
    if stage == "security":
        stage_security()
        return
    if stage in {"test", "pytest"}:
        stage_test(coverage_fail_under)
        return
    stage_build()


def main() -> None:
    parser = argparse.ArgumentParser(description="Script Net Health Quality Gate")
    parser.add_argument("--area", choices=AREAS, default="python")
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--coverage-fail-under", type=int, default=100)
    parser.add_argument(
        "--config-text",
        nargs="?",
        const="all",
        choices=["all", "json", "yaml"],
    )
    args = parser.parse_args()
    if args.config_text is not None:
        if args.area != "python":
            parser.error("--config-text exige --area python")
        use_app_cwd()
        run_config_text(str(args.stage), str(args.config_text))
        print("\n[SUCESSO] Estagio concluido com sucesso.")
        return
    use_app_cwd()
    _dispatch(args.area, args.stage, args.coverage_fail_under)
    print("\n[SUCESSO] Estagio concluido com sucesso.")


if __name__ == "__main__":
    main()
