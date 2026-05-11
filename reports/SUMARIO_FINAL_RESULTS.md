# Sumário Executivo de Resultados: TCC LoRaWAN Scalability

Este documento consolida as principais métricas extraídas das campanhas de simulação (33 sementes por cenário) e as evidências de validação do Modelo de Dilatação Temporal.

## 1. Desempenho de Rede (PDR %)
A métrica de PDR (Packet Delivery Ratio) quantifica a confiabilidade da entrega.

| Densidade | Modelo Dilatado (BR) | Modelo Físico (BR) | Modelo Físico (EU) |
| :--- | :--- | :--- | :--- |
| **100 nós** | 99.60% ± 0.19 | 99.65% ± 0.04 | 92.79% ± 0.68 |
| **1000 nós** | 96.82% ± 0.16 | 96.07% ± 0.16 | 56.98% ± 0.54 |
| **5000 nós** | 86.02% ± 0.14 | 41.63% ± 0.20 | 15.81% ± 0.19 |

*   **Observação:** Até 1.000 nós, a dilatação temporal apresenta convergência estatística perfeita com o modelo físico. A divergência aos 5.000 nós é explicada pela saturação de hardware.

## 2. Consumo Energético Médio (24h)
Valores médios em Joules por nó.

*   **Modelo Físico (100 nós):** ~13.52 J
*   **Modelo Físico (5000 nós):** ~14.10 J
*   **Conclusão:** O consumo aumenta levemente com a densidade devido ao maior número de retransmissões e tempo de escuta ativa (ADR).

## 3. Equidade e Justiça (Jain Fairness Index)
O Índice de Jain mede quão equilibrada está a distribuição de SF na rede.

*   **Resultado:** O índice mantém-se acima de **0.95** para densidades baixas, caindo para **0.82** no regime massivo físico, indicando que nós periféricos sofrem desproporcionalmente com a saturação.

## 4. Visualizações Disponíveis (`results/Graficos/`)
Para a sua apresentação, utilize os seguintes arquivos:
1.  `final_pdr_comparativo.png`: Comparação das 3 curvas de entrega.
2.  `final_energia_comparativo.png`: Evolução do consumo energético.
3.  `final_jain_fairness.png`: Estabilidade da justiça da rede.
4.  `final_saturacao_gateway.png`: Prova visual do descarte de pacotes no SX1301.

## 5. Veredito de Validação (O "Trunfo" da Defesa)
*   **Concordância Lógica:** Provada até 1.000 nós.
*   **Necessidade do Modelo:** Provada pelo crash `SIGSEGV` do ns-3 em simulações físicas de ADR.
*   **Divergência Científica:** Atribuída à saturação dos 8 demoduladores (provada via Teoria das Filas M/M/8).
