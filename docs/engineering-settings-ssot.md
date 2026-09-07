# Settings SSOT (`.env`)

Configuracao runtime vive em variaveis de ambiente na raiz do repositorio. Nao ha `config/settings.json` neste esqueleto.

## Arquivos

| Arquivo | Papel |
|---------|-------|
| `.env` | Valores locais (nunca commitado) |
| `.env.example` | Catalogo sem segredos reais |
| `infrastructure/config/settings.py` | Loader tipado |

Testes: `SNH_DISABLE_DOTENV=1` (tambem em `app/tests/conftest.py`).

## Variaveis

| Var | Default | Papel |
|-----|---------|-------|
| `SNH_APP_NAME` | `script-net-health` | Nome validado em `AppIdentity` (`--status`) |
| `SNH_LOG_LEVEL` | `INFO` | Nivel do root logger |
| `SNH_DISABLE_DOTENV` | `0` | `1`/`true`/`yes` pula load do `.env` |
| `SNH_PROBE_TIMEOUT_SECONDS` | `5` | Timeout de cada probe |
| `SNH_PING_COUNT` | `3` | Pacotes ICMP |
| `SNH_WAN_PING_TARGET` | `1.1.1.1` | Alvo ICMP WAN |
| `SNH_DNS_PROBE_NAME` | `example.com` | Nome para `nslookup` |
| `SNH_ENABLE_TRACEROUTE` | `0` | `1`/`true`/`yes` habilita `tracert` |
| `SNH_TRACERT_TIMEOUT_SECONDS` | `30` | Timeout proprio do `tracert` (o default de probe e curto demais) |
| `SNH_HTTP_PROBE_URL` | vazio | GET opcional; vazio = skip |
| `SNH_TCP_PROBE_PORT` | `443` | Handshake TCP no alvo WAN |
| `SNH_ENABLE_SPEEDTEST` | `1` | `0` desliga medicao urllib de download/upload |
| `SNH_SPEEDTEST_BYTES` | `2000000` | Tamanho do payload de medicao |
| `SNH_SPEEDTEST_TIMEOUT_SECONDS` | `20` | Timeout GET/POST de throughput |
| `SNH_SPEEDTEST_DOWNLOAD_URL` | vazio | Vazio = Cloudflare `__down?bytes=` |
| `SNH_SPEEDTEST_UPLOAD_URL` | vazio | Vazio = Cloudflare `__up` |
| `SNH_MIN_DOWNLOAD_MBPS` | `0` | `0` so mede; `>0` marca aplicacao degradada se ficar abaixo |
| `SNH_MIN_UPLOAD_MBPS` | `0` | Idem para upload |

## Fluxo de mudanca

1. Atualizar `.env.example` se a var for nova.
2. Ajustar `Settings.from_env` e testes de config.
3. Documentar aqui + rule `snh-settings-ssot`.
4. Rodar gates.

Skill: `snh-settings-change`.
