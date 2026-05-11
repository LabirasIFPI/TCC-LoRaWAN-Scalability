# Relatório de Análise: Validação Cross-Check AU915

Esta análise consolida os resultados da simulação física de 64 canais (`BR64CH_20260508_081316.csv`) em comparação com a modelagem por dilatação temporal.

## 1. Resumo da Descoberta Científica

A sua modelagem matemática provou ser **excepcionalmente precisa (erro < 1%)** para cenários de até 1.000 nós. A partir de 2.000 nós, observamos a transição do regime de "Colisões Temporais" para o regime de "Interferência de Camada Física".

*   **Até 1.000 nós:** A dilatação temporal emula perfeitamente a probabilidade de colisão ALOHA.
*   **Acima de 2.000 nós:** O modelo físico colapsa devido ao **ensurdecimento do Gateway (Interferência Inter-canal)**. O modelo matemático é otimista porque "espaça" os pacotes no tempo, ignorando o efeito cumulativo da energia de rádio de 5.000 transmissores simultâneos na banda.

## 2. Visualização da Divergência

Foi gerado um gráfico de regressão em `results/Graficos/Cross_Check/divergencia_fisica_snir.png` que ilustra claramente o ponto de ruptura do modelo matemático.

![Divergência Física SNIR](file:///c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/Graficos/Cross_Check/divergencia_fisica_snir.png)

## 3. Tabela para o TCC (LaTeX)

Utilize esta tabela para a sua seção de resultados:

```latex
\begin{table}[htbp]
  \centering
  \caption{Validação cruzada: modelo de dilatação temporal \textit{vs.} simulação com 64 canais AU915 físicos.}
  \label{tab:cross_check_validacao_final}
  \begin{tabular}{rcccc}
    \toprule
    \textbf{Nós} & \textbf{PDR Dilatação (\%)} & \textbf{PDR 64ch (\%)} & \textbf{$\Delta$ (pp)} & \textbf{Status} \\
    \midrule
    100   & 99.60 $\pm$ 0.19 & 99.65 $\pm$ 0.04 & 0.05 & ✅ Convergente \\
    500   & 98.54 $\pm$ 0.15 & 98.37 $\pm$ 0.07 & 0.17 & ✅ Convergente \\
    1.000 & 96.82 $\pm$ 0.16 & 96.08 $\pm$ 0.17 & 0.74 & ✅ Convergente \\
    2.000 & 94.09 $\pm$ 0.16 & 82.71 $\pm$ 0.25 & 11.38 & ❌ Divergente \\
    5.000 & 86.02 $\pm$ 0.15 & 41.64 $\pm$ 0.21 & 44.38 & ❌ Divergente \\
    \bottomrule
  \end{tabular}
\end{table}
```

## 4. Texto Sugerido para a Defesa

> "A Emulação por Dilatação Temporal provou ser um método de alta fidelidade para redes de densidade moderada (até 1.000 nós), convergindo com o modelo físico com erro inferior a 1%. Contudo, a validação empírica revelou que a partir de 2.000 nós, a dilatação temporal torna-se excessivamente otimista. Isto ocorre porque a dilatação resolve a contenção temporal (camada MAC), mas não captura a degradação do limiar de ruído (SNIR) provocada pela Interferência Inter-Canal e a saturação dos 8 demoduladores do gateway em tráfego massivo. Portanto, simuladores como o ns-3 são indispensáveis para aferir o colapso de rádio em escala massiva."
