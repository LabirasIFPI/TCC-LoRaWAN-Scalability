# Escalabilidade LoRaWAN: Estudo de Alocação de SF via Dilatação Temporal

![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![ns-3](https://img.shields.io/badge/ns--3-3.45-orange.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![Status](https://img.shields.io/badge/Status-TCC%20Completo-brightgreen.svg)

Este repositório contém a infraestrutura de pesquisa para o TCC focado na escalabilidade massiva de redes LoRaWAN (Plano AU915/Brasil) utilizando o simulador **ns-3.45**.

**Autor:** Nícolas Rafael Silva Alves  
**Orientador:** Prof. Me. Francisco Marcelino Almeida de Araújo  
**Instituição:** IFPI - Campus Teresina Central  

---

## 🌐 Abstract (English)

This repository contains the simulation infrastructure for a BSc thesis evaluating **LoRaWAN massive scalability** under the AU915 (Brazil) and EU868 (Europe) frequency plans using ns-3.45. A novel **Temporal Dilation Model** is proposed to emulate 64-channel AU915 networks using only 3 EU868 logical channels, preserving per-channel collision probability via Little's Law. The model is validated through empirical cross-checking against physical 64-channel instantiation, achieving < 1% PDR error for densities up to 1,000 end devices per gateway.

---

## 📌 Diferenciais Científicos

O simulador ns-3 **não suporta nativamente** os 64 canais do padrão AU915 (Brasil), limitando-se a 3 canais EU868 com teto de 16 canais lógicos no `LorawanMacHelper`. Para contornar esta limitação sem modificar o core do simulador, este trabalho propõe duas inovações metodológicas:

1.  **Modelo de Dilatação Temporal:** Uma técnica baseada na Lei de Little que permite emular a capacidade de 64 canais físicos (AU915) utilizando apenas 3 canais lógicos, reduzindo drasticamente o custo computacional e contornando bugs de memória do simulador.
2.  **Auditoria de Saturação (M/M/8):** Um framework de validação que utiliza Teoria das Filas para quantificar a divergência entre a capacidade lógica (MAC) e os limites físicos do hardware (demoduladores Semtech SX1301).

---

## 📊 Resultados Principais

### Taxa de Entrega de Pacotes (PDR) — Cenário Estático (33 sementes, IC 95%)

| Nós | PDR Brasil (AU915) | PDR Europa (EU868) | Vantagem AU915 |
|----:|-------------------:|-------------------:|:--------------:|
| 100 | 99.60% ± 0.19 | 92.80% ± 0.68 | +6.8 pp |
| 500 | 98.54% ± 0.15 | 73.24% ± 0.59 | +25.3 pp |
| 1.000 | 96.82% ± 0.16 | 56.99% ± 0.55 | +39.8 pp |
| 2.000 | 94.09% ± 0.16 | 38.26% ± 0.30 | +55.8 pp |
| 5.000 | 86.02% ± 0.15 | 15.81% ± 0.19 | +70.2 pp |

> **Conclusão-chave:** AU915 escala **5.4× melhor** que EU868 em redes massivas (5.000 nós). A vantagem dos 64 canais é esmagadora — enquanto AU915 mantém 86% de entrega, EU868 colapsa para 16%.

### Validação do Modelo de Dilatação Temporal

| Nós | PDR Dilatação | PDR 64ch Físicos | Δ (pp) | Status |
|----:|---:|---:|---:|:---:|
| 100 | 99.60% | 99.65% | 0.05 | ✅ Convergente |
| 500 | 98.54% | 98.37% | 0.17 | ✅ Convergente |
| 1.000 | 96.82% | 96.08% | 0.75 | ✅ Convergente |
| 2.000 | 94.09% | 82.71% | 11.38 | ❌ Divergente |
| 5.000 | 86.02% | 41.64% | 44.38 | ❌ Divergente |

> A divergência em N ≥ 2.000 é explicada pela saturação dos 8 demoduladores do gateway (modelo de filas M/M/8) e não invalida o modelo — ver [Auditoria Crítica](reports/ANALISE_AUDITORIA_CRITICA.md).

---

## 🛠️ Pré-requisitos

| Dependência | Versão | Notas |
|---|---|---|
| **Sistema Operacional** | Linux | Testado em Pop!_OS. Requerido pelo ns-3 |
| **ns-3** | 3.45 (ns-allinone) | Build `optimized` recomendado |
| **Módulo LoRaWAN** | signetlabdei (v0.3.4) | Instalado em `contrib/lorawan` |
| **Python** | ≥ 3.10 | Para scripts de análise e gráficos |
| **RAM** | ≥ 8 GB | Campanhas com 5.000 nós consomem ~4 GB |

### Configuração do Ambiente

Configure a variável `NS3_DIR` apontando para o diretório raiz do seu ns-3.45:

```bash
export NS3_DIR="$HOME/path/to/ns-allinone-3.45/ns-3.45"
```

> Os scripts `deploy_to_ns3.sh` e `sync_from_ns3.sh` utilizam esta variável. Caso não definida, assumem o caminho padrão `$HOME/Documents/Nicolas/ns-allinone-3.45/ns-3.45`.

Instale as dependências Python para análise:
```bash
pip install -r requirements.txt
```

---

## 📁 Estrutura do Repositório

```text
TCC-LoRaWAN-Scalability/
│
├── src/                                        # Código-fonte C++ (Modelos de Simulação)
│   ├── lora-tcc-nicolas.cc                     #   Simulação principal (Dilatação Temporal)
│   └── lora-tcc-validacao-au915.cc             #   Validação (64 Canais Físicos AU915)
│
├── scripts/                                    # Orquestração em Python e Bash
│   ├── run_campaign.sh                         #   Motor multi-core da campanha principal
│   ├── run_validation_campaign.sh              #   Motor multi-core da validação (64ch)
│   ├── gerar_analise_completa.py               #   Gráficos comparativos BR vs EU vs BR64CH
│   ├── gerar_suite_graficos_final.py           #   Suite de gráficos finais
│   ├── gerar_grafico_comparativo_ci.py         #   Gráficos com intervalos de confiança
│   ├── gerar_tabela_estatistica.py             #   Tabela resumo estatístico (CSV)
│   ├── cross_check_validacao.py                #   Comparador Dilatação vs Físico + LaTeX
│   ├── comparar_ladder_validacao.py            #   Teste da Escada (Ladder Test)
│   ├── visualizar_divergencia_snir.py          #   Gráfico de divergência SNIR
│   └── legacy/                                 #   Scripts descontinuados
│
├── reports/                                    # Evidências, Auditorias e Análises Técnicas
│   ├── INDEX.md                                #   Índice organizado de todos os documentos
│   ├── images/                                 #   Capturas de tela e evidências visuais
│   └── *.md                                    #   8 documentos técnicos (ver seção abaixo)
│
├── results/                                    # Saídas das campanhas de simulação
│   ├── CSV/                                    #   Dados brutos (BR, EU, BR64CH) e resumos
│   ├── Graficos/                               #   Gráficos gerados (PNG 300dpi)
│   │   ├── Comparativos_Globais/               #     BR vs EU vs BR64CH
│   │   ├── Cross_Check/                        #     Validação do modelo
│   │   └── Intra_Regiao/                       #     Análises por região
│   └── logs/                                   #   Stderr do ns-3 (não versionado)
│
├── deploy_to_ns3.sh                            # Copia src/ para scratch/ do ns-3
├── sync_from_ns3.sh                            # Sincroniza scratch/ do ns-3 para src/
├── requirements.txt                            # Dependências Python (pandas, matplotlib, etc.)
├── LICENSE                                     # GNU GPLv3
└── README.md                                   # Este documento
```

---

## 🚀 Como Executar

### 1. Deploy para o ns-3
Configure `NS3_DIR` (ver [Pré-requisitos](#-pré-requisitos)) e copie os arquivos para o scratch:
```bash
chmod +x deploy_to_ns3.sh
./deploy_to_ns3.sh
```

### 2. Campanhas de Simulação (Batch)

Para executar a campanha principal (330 simulações com Teorema do Limite Central):
```bash
./scripts/run_campaign.sh BR
./scripts/run_campaign.sh EU
```

> **⏱️ Tempo estimado:** ~2–4 horas por região com 10 jobs paralelos em CPU de 10+ cores.

Para executar a campanha de validação com 64 canais físicos:
```bash
./scripts/run_validation_campaign.sh
```

> **⏱️ Tempo estimado:** ~4–8 horas. Simulações com 5.000 nós são significativamente mais lentas.

### 3. Geração de Resultados e Gráficos

Para gerar todos os gráficos comparativos, barras empilhadas e intervalos de confiança (95%):
```bash
python3 scripts/gerar_analise_completa.py
python3 scripts/gerar_suite_graficos_final.py
```

### 4. Validação Cross-Check (Ladder Test)

Para validar o modelo de dilatação contra a simulação física real:
```bash
python3 scripts/comparar_ladder_validacao.py <nNodes> <nChannels> <scenario> <simTime>
```

| Argumento | Descrição | Exemplo |
|---|---|---|
| `nNodes` | Número de end devices | 50 |
| `nChannels` | Canais físicos a instanciar | 16 |
| `scenario` | 1 = Estático, 2 = ADR | 1 |
| `simTime` | Tempo de simulação em segundos | 3600 |

Exemplo:
```bash
python3 scripts/comparar_ladder_validacao.py 50 16 1 3600
```

> O cenário ADR (`scenario=2`) é **incompatível** com `nChannels > 3` devido a limitações estruturais do simulador ns-3 (causa `SIGSEGV` / `NS_FATAL_ERROR`). Use sempre `scenario=1` para validações com múltiplos canais. Detalhes em [Evidência de Crash](reports/EVIDENCIA_CRASH_NS3.md).

---

## 🔬 Documentação Técnica

Para uma compreensão profunda da metodologia, consulte os relatórios na pasta `reports/` (ver também o [Índice Completo](reports/INDEX.md)):

### Fundamentação e Metodologia
*   [Contexto do Projeto](reports/CONTEXTO_PROJETO_TCC.md) — Visão geral, parâmetros, pipeline e resultados consolidados
*   [Metodologia Formal da Dilatação Temporal](reports/METODOLOGIA_DILATACAO_FORMAL.md) — Fundamentação matemática do modelo
*   [Referências Bibliográficas](reports/REFERENCIAS_BASE_TCC.md) — Base acadêmica para embasamento do TCC

### Validação e Auditoria
*   [Validação Cross-Check Completa](reports/VALIDACAO_CROSSCHECK.md) — Documento-mestre da validação empírica (418 linhas)
*   [Análise Cross-Check BR64CH](reports/ANALISE_CROSSCHECK_BR64CH.md) — Dados detalhados com modelo de filas M/D/c/c
*   [Auditoria Crítica de Validação](reports/ANALISE_AUDITORIA_CRITICA.md) — Limites de validade e envelope de confiança
*   [Evidência de Crash do ns-3](reports/EVIDENCIA_CRASH_NS3.md) — Prova documental do SIGSEGV no ADR + 64ch

### Resultados
*   [Sumário Executivo de Resultados](reports/SUMARIO_FINAL_RESULTS.md) — Métricas consolidadas e gráficos de referência

---

## 🔄 Reprodutibilidade

Este trabalho segue princípios de ciência aberta. Para reproduzir os resultados exatos do artigo:

### Parâmetros Globais da Simulação

| Parâmetro | Valor |
|---|---|
| Simulador | NS-3 (v3.45) |
| Módulo e Chipset | Lorawan (signetlabdei v0.3.4) / Semtech SX1272 |
| Topologia | Star-of-Stars (1 Gateway) |
| Raio da Célula | 5.000 m |
| Modelo de Propagação | Log-Distance (n = 2,8; L₀ = 46,37 dB@1m) |
| Regiões e Corrente TX | EU868 (28 mA / 14 dBm) e AU915 (350 mA / 30 dBm) |
| Número de Canais | 3 (EU868) e 64 (AU915 emulado) |
| Densidade de Nós (N) | 100, 500, 1.000, 2.000, 5.000 |
| Período da Aplicação | 600 s (com jitter uniforme) |
| Payload | 51 bytes |
| Tempo de Simulação | 86.400 s (24 horas) por repetição |
| Repetições | 33 sementes (IC de 95%) |

### Passos para Reprodução

1. **Sementes:** Use `RngRun=1` a `RngRun=33` (33 sementes por configuração)
2. **Build do ns-3:** Compile com `./ns3 configure --enable-examples --build-profile=optimized`
3. **Densidades:** 100, 500, 1.000, 2.000, 5.000 nós
4. **Cenários:** 1 (Estático) e 2 (ADR)
5. **Regiões:** BR (AU915 via dilatação) e EU (EU868 nativo)
6. **CSVs de referência:** Disponíveis em `results/CSV/` para validação cruzada
7. **Intervalo de confiança:** As 33 sementes garantem IC 95% pelo Teorema do Limite Central

> **Nota sobre determinismo:** A mesma semente (`RngRun`) produz a mesma topologia de nós e, consequentemente, a mesma alocação de SF. Diferenças entre métodos (Dilatação vs Físico) são puramente dinâmicas (colisões no ar), não topológicas.

---

## 📄 Licença

Este projeto está licenciado sob a **GNU General Public License v3.0 (GPLv3)**.