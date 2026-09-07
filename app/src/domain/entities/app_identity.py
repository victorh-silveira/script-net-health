"""Identidade validada da aplicacao."""

from __future__ import annotations

from dataclasses import dataclass

from domain.exceptions import DomainError


@dataclass(frozen=True)
class AppIdentity:
    """Nome e versao da aplicacao."""

    name: str
    version: str

    def __post_init__(self) -> None:
        """Valida nome e versao nao vazios."""
        if not self.name.strip():
            raise DomainError("nome da aplicacao nao pode ser vazio")
        if not self.version.strip():
            raise DomainError("versao da aplicacao nao pode ser vazia")
