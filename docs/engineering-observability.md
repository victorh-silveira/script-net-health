# Observabilidade e Logging

Diretrizes e padrões para logging e rastreabilidade operacional no **Script Net Health**.

## Princípios de Logging

1. **Separação por Camadas:**
   - Emissão de logs é exclusiva das camadas de `presentation` e `infrastructure`.
   - Proibido emitir logs ou instanciar loggers dentro das camadas de `domain` e `application`.

2. **Níveis de Log e Semântica:**
   - `DEBUG`: Detalhes finos de parsing e argumentos sanitizados de subprocessos.
   - `INFO`: Mensagens operacionais sucintas sobre início e término de execuções.
   - `WARNING`: Anomalias recuperáveis ou timeouts previstos em probes opcionais.
   - `ERROR`: Falhas de sistema ou violações de allowlist.

3. **Proteção Contra Dump em Nível INFO:**
   - O stdout bruto retornado pelos utilitários Windows (ex: saída completa do `ipconfig` ou `ping`) **nunca** deve ser impresso no log em nível `INFO`.
   - As transcrições completas são encapsuladas no objeto de domínio `ProbeTranscript` e apresentadas exclusivamente na Seção 5 do relatório final de diagnóstico via CLI.

4. **Tratamento de Dados Sensíveis:**
   - Nenhum segredo, credencial de rede ou token deve ser gravado em arquivos de log ou emitido no console.
