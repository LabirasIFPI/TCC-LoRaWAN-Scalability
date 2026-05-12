# Escalabilidade LoRaWAN: Estudo de Alocação de SF via Dilatação Temporal

Este repositório contém a infraestrutura de pesquisa para o TCC focado na escalabilidade massiva de redes LoRaWAN (Plano AU915/Brasil) utilizando o simulador **ns-3.45**.

**Autor:** Nícolas Rafael Silva Alves  
**Orientador:** Prof. Me. Francisco Marcelino Almeida de Araújo  
**Instituição:** IFPI - Campus Teresina Central  

---

## 📌 Diferenciais Científicos

O projeto introduz duas inovações metodológicas para superar as limitações do simulador ns-3:

1.  **Modelo de Dilatação Temporal:** Uma técnica baseada na Lei de Little que permite emular a capacidade de 64 canais físicos (AU915) utilizando apenas 3 canais lógicos, reduzindo drasticamente o custo computacional e contornando bugs de memória do simulador.
2.  **Auditoria de Saturação (M/M/8):** Um framework de validação que utiliza Teoria das Filas para quantificar a divergência entre a capacidade lógica (MAC) e os limites físicos do hardware (demoduladores Semtech SX1301).

---

## 📁 Estrutura Organizada

```text
├── src/                   # Código-fonte C++ (Modelos de Simulação)
├── scripts/               # Orquestração em Python e Bash
├── reports/               # Evidências, Auditorias e Análises Técnicas
├── results/               # Saídas das campanhas (CSV, Gráficos, Reports)
├── deploy_to_ns3.sh       # Utilitário para injetar código no ambiente ns-3
├── requirements.txt       # Dependências Python para análise
└── README.md              # Documentação principal
```

---

## 🚀 Como Executar

### 1. Preparação
Instale as dependências de análise:
```bash
pip install -r requirements.txt
```

### 2. Deploy para ns-3
Configure o caminho do seu ns-3 no arquivo `deploy_to_ns3.sh` e execute:
```bash
chmod +x deploy_to_ns3.sh
./deploy_to_ns3.sh
```

### 3. Campanhas de Simulação (Batch)
Para executar a campanha estendida (330 simulações com Teorema do Limite Central):
```bash
./scripts/run_campaign.sh BR
./scripts/run_campaign.sh EU
```

### 4. Geração de Resultados e Gráficos
Para gerar todos os gráficos comparativos, de barras empilhadas e os intervalos de confiança (95%):
```bash
python3 scripts/gerar_analise_completa.py
python3 scripts/gerar_suite_graficos_final.py
```

### 5. Validação Cross-Check (Ladder Test)
Para validar o modelo de dilatação contra a simulação física real (ex: 50 nós, 16 canais, cenário ADR):
```bash
python3 scripts/comparar_ladder_validacao.py 50 16 2 3600
```
*O script detectará automaticamente se o ns-3 sofrer falha de segmentação (SIGSEGV), gerando o relatório de necessidade do modelo.*

---

## 🔬 Documentação Técnica

Para uma compreensão profunda da metodologia, consulte os relatórios na pasta `reports/`:

*   [Auditoria Crítica de Validação](reports/ANALISE_AUDITORIA_CRITICA.md): Explicação matemática das divergências.
*   [Evidência de Crash do ns-3](reports/EVIDENCIA_CRASH_NS3.md): Prova documental da instabilidade do modelo físico.
*   [Contexto da Dilatação Temporal](reports/CONTEXTO_PROJETO_TCC.md): Fundamentação teórica do modelo.

---

## 📄 Licença

Este projeto está licenciado sob a **GNU General Public License v3.0 (GPLv3)**.