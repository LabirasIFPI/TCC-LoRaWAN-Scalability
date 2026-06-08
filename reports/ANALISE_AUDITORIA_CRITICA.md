# Análise Profunda: Auditoria Técnica e Limites de Validade

Este documento sintetiza a auditoria técnica realizada sobre o **Modelo de Emulação por Dilatação Temporal**, identificando as causas raízes da divergência observada em cenários massivos (5.000 nós) e estabelecendo o envelope de confiança científica do trabalho.

## 1. O Veredito da Saturação (Gargalo de Hardware)

A divergência mais crítica (PDR de 86% na emulação vs. 41% no físico) é explicada pela **Teoria das Filas (M/M/8)** aplicada ao chipset concentrador Semtech SX1301.

*   **Capacidade de Hardware:** O gateway real possui apenas 8 caminhos de recepção (demoduladores).
*   **O Erro da Emulação:** Ao dilatar o tempo em 21,33x, a taxa de chegada instantânea de pacotes ($\lambda_{GW\_emulado}$) cai drasticamente (~0,39 pacotes/s). Isso torna a probabilidade de saturação (mais de 8 pacotes simultâneos) virtualmente **nula**.
*   **A Realidade Física:** Em 5.000 nós, a taxa real ($\lambda_{GW\_real}$) é de ~8,33 pacotes/s. A probabilidade de um pacote encontrar os 8 demoduladores ocupados e ser descartado por "surdez institucional" é de **44,9%**.
*   **Conclusão:** A emulação descreve um cenário de **"Hardware Ideal"**, enquanto a simulação física captura o limite real do silício.

## 2. A Falácia PHY/SNIR (Camada Física)

A dilatação temporal cria uma "Câmara Anecoica Virtual", limpando o espectro de forma artificial.

*   **Noise Floor Cumulativo:** Na rede massiva de 64 canais, a energia RF de 5.000 dispositivos eleva o piso de ruído de forma permanente. A dilatação, ao isolar os pacotes no tempo, induz o motor de interferência do ns-3 a reportar SNRs (Signal-to-Noise Ratio) ilusoriamente limpas.
*   **Rejeição de Canal Adjacente (ACI):** A emulação em 3 canais afasta as frequências, neutralizando o vazamento espectral entre canais vizinhos (espaçamento de 200 kHz no AU915). Isso mascara o problema **Near-Far**, onde um nó próximo "esmaga" a recepção de um nó distante em um canal vizinho.

## 3. Assimetria do ADR e Half-Duplex

O comparativo entre o cenário Estático e ADR é afetado pela dilatação na Camada MAC:

*   **Cegueira de Downlink:** O gateway é *Half-Duplex*. No mundo real, enviar um comando ADR (Downlink) impede a recepção de uplinks. 
*   **Vantagem Cega:** Na dilatação, as janelas de silêncio dilatadas permitem que os comandos ADR trafeguem sem quase nenhuma colisão com o tráfego de subida, o que favorece injustamente o desempenho do ADR no modelo emulado.

## 4. Incompressibilidade Energética (FSM)

A auditoria invalida a "Retro-Escala Linear" do consumo de energia para fins de engenharia eletrônica rigorosa.

*   **Custos Fixos de Transição:** O dreno de corrente para Wake-up do rádio, estabilização de cristal (PLL) e transição TX-to-RX é um valor **fixo por pacote**. 
*   **O Erro:** Ao multiplicar o consumo final por 21,33, o modelo escala tempos de *Idle/Sleep* como se fossem tempos ativos de rádio, ignorando a natureza não-linear da Máquina de Estados Finitos (FSM) do transceptor SX1272.

## 5. Envelope de Validade

A auditoria não invalida o trabalho, mas o reclassifica em termos de rigor científico:

1.  **Zona de Convergência (N ≤ 1.000):** O modelo é estatisticamente convergente com o físico, sendo uma ferramenta válida de predição.
2.  **Limite Assintótico Superior (N > 1.000):** Para densidades extremas, o modelo deve ser interpretado como a **Capacidade Lógica Máxima do Protocolo**, representando o desempenho ideal na ausência de restrições de hardware e ruído analógico.
3.  **Diferencial Acadêmico:** A capacidade de quantificar a lacuna entre o "Lógico" (86%) e o "Físico" (41%) é o maior achado do TCC, demonstrando maturidade em Engenharia de Telecomunicações.

---

*Documento de auditoria — TCC Nícolas Rafael Silva Alves, IFPI — Atualizado em 08/06/2026*
