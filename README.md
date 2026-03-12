
# Análise de Escalabilidade em Redes LoRaWAN no NS-3

Este repositório contém o código-fonte e os scripts de automação desenvolvidos para o Trabalho de Conclusão de Curso (TCC) intitulado **"Análise de Escalabilidade em Redes LoRaWAN: Um Estudo Comparativo de Estratégias de Alocação de Spreading Factors no NS-3"**.

**Autor:** Nícolas Rafael Silva Alves  
**Curso:** Tecnologia em Análise e Desenvolvimento de Sistemas (ADS)  
**Instituição:** Instituto Federal de Educação, Ciência e Tecnologia do Piauí (IFPI) - Campus Teresina Central  
**Orientador:** Prof. Me. Francisco Marcelino Almeida de Araújo  
**Ano:** 2025

---

## 📌 Visão Geral do Projeto

O objetivo desta pesquisa é avaliar a escalabilidade de uma rede LoRaWAN sob alta densidade de nós (massiva IoT), comparando duas abordagens de alocação de *Spreading Factors* (SF):

1. **Cenário 1 (Alocação Estática):** Os SFs (7 a 12) são distribuídos com base na distância euclidiana do *End Device* até o *Gateway*, simulando anéis concêntricos de cobertura.
2. **Cenário 2 (Alocação Dinâmica - ADR):** Utiliza o algoritmo *Adaptive Data Rate* (ADR) do *Network Server* para otimizar dinamicamente o SF com base nas condições do canal físico.

A simulação computacional foi desenvolvida em **C++** sobre o simulador de redes de eventos discretos **NS-3**, e a automação da campanha estocástica foi construída em **Bash**.

---

## 📁 Estrutura do Repositório

Como as boas práticas recomendam não versionar o núcleo do NS-3 (por ser muito pesado), este repositório contém apenas as contribuições intelectuais diretas da pesquisa:

```text
├── src/
│   └── lora-tcc-nicolas.cc       # Código-fonte principal da simulação (C++)
├── scripts/
│   ├── run_campaign.sh           # Automação das 330 rodadas estocásticas (Bash)
│   ├── sync_from_ns3.sh          # Script utilitário para sincronizar atualizações do NS-3
│   └── analyze_results.py        # Processamento de dados e cálculo do Índice de Jain (Python)
├── results/                      # Diretório gerado pela campanha contendo os .csv e .txt
└── README.md                     # Documentação do projeto

```

---

## 🛠️ Tecnologias e Dependências

Para reproduzir este projeto, o seguinte ambiente é necessário:

* **OS:** Linux (Ubuntu 22.04/24.04) ou Windows 11 com WSL 2.
* **Simulador:** NS-3 (Versão 3.45).
* **Módulo:** `lorawan` (signetlabdei v0.3.4).
* **Linguagens:** C++17, Bash, Python 3.10+.
* **Bibliotecas Python:** `pandas`, `numpy`.

---

## 🚀 Como Executar a Simulação

### 1. Preparação do Ambiente

Certifique-se de ter o NS-3 configurado e compilado com o módulo LoRaWAN na sua máquina.

### 2. Integração do Código

Copie o arquivo de simulação para a pasta de desenvolvimento (scratch) do seu NS-3:

```bash
cp src/lora-tcc-nicolas.cc /caminho/para/o/seu/ns-3-dev/scratch/

```

### 3. Execução de um Cenário Específico (Teste Rápido)

Dentro do diretório do NS-3, execute:

```bash
./ns3 run "lora-tcc-nicolas --nNodes=100 --scenario=1"

```

*(Parâmetros: `--nNodes` aceita qualquer número inteiro; `--scenario` aceita 1 para Estático e 2 para Dinâmico/ADR).*

### 4. Execução da Campanha Estocástica (Completa)

Para executar a metodologia completa do trabalho (5 densidades × 2 cenários × 33 sementes independentes), copie o script de campanha para a raiz do NS-3 e execute:

```bash
cp scripts/run_campaign.sh /caminho/para/o/seu/ns-3-dev/
cd /caminho/para/o/seu/ns-3-dev/
./run_campaign.sh

```

⚠️ **Aviso:** A campanha completa pode demorar várias horas dependendo do processador. Os dados extraídos serão guardados na pasta `results_tcc/`.

---

## 📊 Análise de Dados

Após a conclusão da campanha, o arquivo `energia_consolidada.csv` e os *logs* individuais de pacotes (`tracker_*.txt`) estarão disponíveis.

Para extrair o *Packet Delivery Ratio* (PDR) e calcular o Índice de Justiça de Jain, execute o script em Python:

```bash
python3 scripts/analyze_results.py

```

## 📄 Licença

Este projeto é software livre e está licenciado sob a **GNU General Public License v3.0 (GPLv3)**. 
Isto significa que tens a liberdade de usar, estudar, partilhar e modificar o código, desde que mantenhas a mesma licença e os devidos créditos abertos.

Vê o ficheiro [LICENSE](LICENSE) para mais detalhes. Como este projeto utiliza o simulador NS-3, herda a filosofia de software livre, garantindo que o conhecimento científico permaneça acessível à comunidade acadêmica.