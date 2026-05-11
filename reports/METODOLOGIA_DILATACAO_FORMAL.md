# Fundamentação Metodológica: Modelo de Dilatação Temporal

Este documento apresenta a descrição formal do artifício metodológico utilizado para a avaliação da escalabilidade LoRaWAN no plano de frequências AU915, visando a integração direta no texto da monografia.

## 1. O Problema da Escala de Canais no ns-3.45
O simulador Network Simulator 3 (ns-3), embora robusto, apresenta limitações arquiteturais no suporte a planos de frequência massivos (64 canais), como o padrão brasileiro AU915. O módulo `lorawan` oficial restringe a configuração de *helpers* a um teto de 16 canais lógicos, impossibilitando a instanciação direta da malha completa de 64 canais em simulações dinâmicas (ADR).

## 2. A Abstração por Dilatação Temporal
Para contornar esta restrição, propôs-se um modelo de emulação baseado na equivalência de carga de rede ($\lambda$). A premissa fundamental reside na manutenção da probabilidade de colisão do protocolo ALOHA, que é uma função direta da carga oferecida normalizada ($G$).

Utilizando a **Lei de Little** e os princípios de processos estocásticos de Poisson, estabeleceu-se um fator de escala para o domínio do tempo:

$$F_{escala} = \frac{C_{alvo}}{C_{base}}$$

Onde:
*   $C_{alvo} = 64$ (Canais físicos AU915 brasileiros).
*   $C_{base} = 3$ (Canais lógicos padrão do simulador).
*   $F_{escala} \approx 21,33$

### 2.1. Transformação do Período de Aplicação
Para que a rede de 3 canais emule o comportamento de colisão de uma rede de 64 canais com o mesmo número de nós, o período de geração de tráfego original ($T$) deve ser dilatado proporcionalmente:

$$T' = T \times F_{escala}$$

Desta forma, a taxa de chegada de pacotes por canal permanece idêntica à do mundo real, garantindo que o motor de colisão do simulador processe a mesma densidade de sobreposição espectral, preservando a validade estatística do Packet Delivery Ratio (PDR).

## 3. Validação e Envelope de Confiança
A validade desta abstração foi confirmada através de um protocolo de *Cross-Check* (Teste da Escada), comparando o modelo dilatado com simulações físicas reais em escalas menores (16 canais).

*   **Convergência:** Erro residual < 1% para densidades de até 1.000 nós.
*   **Limitação Identificada:** O modelo representa o **Limite Assintótico Superior de Capacidade Lógica**, abstraindo saturações de rádio e ruído térmico cumulativo que são exclusivos da implementação física de hardware em regimes extremos (> 2.000 nós).

## 4. Rigor Estatístico
Todos os resultados apresentados derivam de campanhas estocásticas compostas por **33 sementes pseudoaleatórias independentes** por cenário, garantindo um Intervalo de Confiança de 95% e aderência ao Teorema do Limite Central.
