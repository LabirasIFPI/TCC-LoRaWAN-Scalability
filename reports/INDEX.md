# 📚 Índice da Documentação Técnica

**TCC Nícolas Rafael Silva Alves — IFPI**  
*Análise de Escalabilidade em Redes LoRaWAN Massivas (ns-3.45)*

Este índice organiza os documentos técnicos do repositório por categoria e ordem de leitura recomendada.

---

## 1. Leitura Obrigatória — Entender o Projeto

Comece por aqui para compreender o contexto, os parâmetros e a inovação metodológica.

| # | Documento | Descrição |
|---|---|---|
| 1 | [CONTEXTO_PROJETO_TCC.md](CONTEXTO_PROJETO_TCC.md) | Visão geral completa: objetivo, parâmetros fixos, métricas, formato CSV, pipeline de execução e resultados consolidados (33 sementes). |
| 2 | [METODOLOGIA_DILATACAO_FORMAL.md](METODOLOGIA_DILATACAO_FORMAL.md) | Fundamentação matemática formal do Modelo de Dilatação Temporal, incluindo prova de convergência (Delta Zero). |

---

## 2. Validação e Auditoria

Documentos que provam a validade científica do modelo e identificam seus limites.

| # | Documento | Descrição |
|---|---|---|
| 3 | [VALIDACAO_CROSSCHECK.md](VALIDACAO_CROSSCHECK.md) | **Documento-mestre**. Detalha o código de validação com 64 canais físicos, técnica de bypass, diferenças técnicas, critérios de convergência e evidência de crash ADR. |
| 4 | [ANALISE_CROSSCHECK_BR64CH.md](ANALISE_CROSSCHECK_BR64CH.md) | Análise detalhada da campanha BR64CH (165 simulações). Inclui diagnóstico de saturação via modelo de filas M/D/c/c (Erlang-B) e verificação de integridade seed-a-seed. |
| 5 | [ANALISE_AUDITORIA_CRITICA.md](ANALISE_AUDITORIA_CRITICA.md) | Auditoria profunda dos limites do modelo: saturação de hardware, falácia PHY/SNIR, assimetria ADR e incompressibilidade energética. Define o envelope de confiança. |
| 6 | [EVIDENCIA_CRASH_NS3.md](EVIDENCIA_CRASH_NS3.md) | Prova documental (com captura de tela) do crash `SIGSEGV` do ns-3 ao executar ADR com 64 canais físicos. Justifica a obrigatoriedade da Dilatação Temporal. |

---

## 3. Resultados

| # | Documento | Descrição |
|---|---|---|
| 7 | [SUMARIO_FINAL_RESULTS.md](SUMARIO_FINAL_RESULTS.md) | Sumário executivo: PDR, energia, Jain Index e lista de gráficos de referência. |

---

## 4. Referências

| # | Documento | Descrição |
|---|---|---|
| 8 | [REFERENCIAS_BASE_TCC.md](REFERENCIAS_BASE_TCC.md) | Referências bibliográficas organizadas por tema: simulador, padrões AU915, fundamentação matemática, hardware SX1301 e pesquisas brasileiras. |

---

## Notas

- Os documentos foram redigidos entre abril e maio de 2026, durante o desenvolvimento do TCC.
- As evidências visuais (capturas de tela do terminal) estão na pasta [`images/`](images/).
- Para a árvore completa do repositório e instruções de execução, consulte o [README.md](../README.md).
