# Observabilidade e logs

## API

```python
from infrastructure.logging.events import log_event

log_event(logger, logging.INFO, "snh.app.started", name=identity.name)
```

Domain e use cases **nao** emitem logs. Setup do root logger: `presentation.logging.setup.configure_logging`.

## Eventos estaveis

| Evento | Quando |
|--------|--------|
| `snh.app.started` | Inicio de `--status` |
| `snh.app.finished` | Sucesso de `--status` |
| `snh.app.failed` | Falha de `--status` |
| `snh.diagnose.started` | Inicio do diagnostico |
| `snh.diagnose.finished` | Diagnostico emitido |
| `snh.diagnose.failed` | Falha no diagnostico |
| `snh.probe.started` | Probe allowlisted iniciada |
| `snh.probe.finished` | Probe concluida (sem stdout/body) |
| `snh.probe.failed` | Probe timeout/exit/HTTP/TCP/speedtest falhou |
| `snh.probe.skipped_binary` | Binario ausente |
| `snh.probe.skipped_traceroute` | Tracert desligado |
| `snh.probe.skipped_speedtest` | Throughput desligado |

## Regras

- Caminho feliz do diagnostico: `snh.diagnose.started` + `snh.diagnose.finished` (probes em INFO sem stdout).
- Stdout integral das probes vai no relatorio (secao 5), nunca no log INFO.
- Sem dump de payload JSON nem body HTTP em INFO.
- URLs com query: `?***` via `redact_url`.
- Campos `anon_key` / `token` / `secret` / `password` / `authorization` viram `***`.
- `exc_info` apenas quando o logger estiver em DEBUG.
- Loggers `urllib3`, `requests`, `httpx` e `httpcore` em WARNING+.
- Sem emojis. Logs em PT-BR no sentido dos eventos (nomes estaveis em snake_case).

Rule: `snh-logging`.
