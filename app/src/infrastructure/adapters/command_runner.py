"""Runner de comandos com allowlist de binarios Windows."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass


ALLOWED_BINARIES = frozenset({"ipconfig", "ping", "arp", "route", "netstat", "nslookup", "tracert"})


@dataclass(frozen=True)
class CommandResult:
    """Resultado de uma execucao allowlisted."""

    argv: tuple[str, ...]
    returncode: int | None
    stdout: str
    stderr: str
    skipped: bool
    timed_out: bool


class AllowlistedCommandRunner:
    """Executa argv fixos sem shell."""

    def run(self, argv: list[str], timeout: float) -> CommandResult:
        """Corre o comando ou marca skipped/timeout."""
        frozen = tuple(argv)
        if not argv or argv[0] not in ALLOWED_BINARIES:
            return CommandResult(frozen, None, "", "", skipped=True, timed_out=False)
        binary = shutil.which(argv[0])
        if binary is None:
            return CommandResult(frozen, None, "", "", skipped=True, timed_out=False)
        encoding = "oem" if sys.platform == "win32" else None
        try:
            completed = subprocess.run(  # noqa: S603
                [binary, *argv[1:]],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                encoding=encoding,
                errors="replace",
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return CommandResult(frozen, None, stdout, stderr, skipped=False, timed_out=True)
        return CommandResult(
            frozen,
            completed.returncode,
            completed.stdout or "",
            completed.stderr or "",
            skipped=False,
            timed_out=False,
        )
