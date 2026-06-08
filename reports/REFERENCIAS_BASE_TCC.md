# Referências Bibliográficas para Embasamento do TCC

Este documento lista as referências fundamentais para sustentar as decisões metodológicas e os achados técnicos deste trabalho.

## 1. O Simulador e o Módulo LoRaWAN
*Estas referências validam o uso do ns-3 e do módulo signetlabdei como ferramentas científicas aceitas.*

*   **MAGRIN, F.; CAPONE, S.; ZORZI, M.** "A High-Fidelity LoRaWAN Simulator for ns-3". In: *Proceedings of the 10th International Conference on Simulation Tools and Techniques (SIMUTools)*, 2017.
    *   *Importância:* É o "paper mãe" do módulo que você usou. Deve ser citado na Metodologia.
*   **VAN DE BEEK, K. et al.** "Scalability of LoRaWAN for Scholarly Networks". *IEEE Communications Magazine*, 2017.
    *   *Importância:* Discute os limites do protocolo e valida o uso de simulações para estudar redes massivas.

## 2. Padrões e Parâmetros Regionais (AU915)
*Justificam a configuração de 64 canais e a potência de 30 dBm.*

*   **LoRa Alliance.** "LoRaWAN Regional Parameters v1.0.3". 2018.
    *   *Importância:* Documento oficial que define o plano de frequências AU915 utilizado no Brasil.
*   **ANATEL.** "Ato nº 14.448 - Requisitos Técnicos para Avaliação da Conformidade de Equipamentos de Radiocomunicação de Radiação Restrita".
    *   *Importância:* Base legal para o uso das frequências de 915 MHz no Brasil.

## 3. Fundamentação Matemática (Dilatação Temporal)
*Dão autoridade científica à sua estratégia de escala de tempo.*

*   **LITTLE, J. D. C.** "A Proof for the Queuing Formula: L = λW". *Operations Research*, v. 9, n. 3, p. 383–387, 1961.
    *   *Importância:* A base teórica da sua dilatação temporal. Se a taxa de chegada ($\lambda$) por canal é mantida, a probabilidade de colisão é preservada.
*   **ALOHA Protocol (Abramson, 1970):** ABRAMSON, N. "The ALOHA System: Another Alternative for Computer Communications". *AFIPS Conference Proceedings*, 1970.
    *   *Importância:* Explica a matemática das colisões de pacotes que o seu modelo emula.

## 4. Limitações de Hardware e Saturação (M/M/8)
*Explicam cientificamente por que a simulação física divergiu aos 5.000 nós.*

*   **SEMTECH.** "SX1301 Digital Baseband Chip for LoRa Gateways - Datasheet".
    *   *Importância:* Documenta a existência de apenas 8 processadores de símbolos (demoduladores). É a prova de que o gargalo de hardware que detectamos é real.
*   **AUGUSTIN, A. et al.** "A Study of LoRa: Long Range & Low Power Networks for the Internet of Things". *Sensors*, 2016.
    *   *Importância:* Um estudo clássico que detalha o efeito de captura e a sensibilidade dos receptores LoRa.

## 5. Pesquisas de Escalabilidade no Brasil
*Dão contexto local ao seu trabalho.*

*   **SOUZA, R. et al.** "Performance Evaluation of LoRaWAN in Brazilian Agricultural Scenarios". *Journal of Communications and Information Systems*, 2020.
    *   *Importância:* Ajuda a contextualizar o uso do AU915 em cenários de longa distância e alta densidade.
