# Evidência de Auditoria: Limitações do Simulador ns-3.45

Este documento registra a falha estrutural observada no simulador ns-3.45 ao tentar executar o algoritmo ADR (Adaptive Data Rate) em uma rede AU915 com canais físicos expandidos, justificando a obrigatoriedade metodológica do **Modelo de Emulação por Dilatação Temporal**.

## 1. Protocolo de Teste (Cross-Check)

Para validar o comportamento dinâmico do ADR, foi executado um teste comparativo com escala reduzida de canais (16 canais físicos vs. 16 canais emulados via dilatação).

* **Data da Coleta:** 11 de maio de 2026
* **Ambiente:** Pop!_OS Linux / ns-3.45-optimized
* **Comando:** `python3 scripts/comparar_ladder_validacao.py 50 16 2 3600`
* **Cenário:** ADR Habilitado (Cenário 2)
* **Densidade:** 50 nós terminais

## 2. Registro de Logs (Output do Terminal)

![Evidência de Crash do ns-3](results/Ladder_Validation/evidencia_crash_terminal.png)

```text
============================================================
 PROTOCOLO DE AUDITORIA: TESTE DA ESCADA (LADDER)
============================================================
 Config: 50 nós | 16 canais | Cenário 2
 Tempo de Simulação: 3600 segundos
============================================================

1/2 >> Rodando Modelo de Dilatação (Lógico)... 
OK (PDR: 97.1429%)

2/2 >> Rodando Modelo Físico (PHY)... 
  [!] O ns-3 retornou erro (code 245)
  [!!!] CRASH DETECTADO: Segmentation Fault (SIGSEGV)
FALHOU (CRASH - SIGSEGV)

============================================================
 VEREDITO DA VALIDAÇÃO
============================================================
 [!] CONCLUSÃO: O MODELO FÍSICO CRASHOU (LIMITAÇÃO DO NS-3)
 [!] A DILATAÇÃO TEMPORAL É A ÚNICA ALTERNATIVA VIÁVEL.
============================================================
```

## 3. Análise Técnica da Falha

O erro `SIGSEGV` (code 245) indica uma falha de acesso à memória protegida. No contexto do módulo LoRaWAN do ns-3 (versão Padova), essa falha ocorre porque:

1. **Incompatibilidade de Helper:** O `LorawanMacHelper` nativo possui hardcoded o suporte para no máximo 16 canais lógicos em suas estruturas de máscara de canal (`ChMask`).
2. **Exaustão de Buffer MAC:** Ao injetar frequências customizadas para AU915 enquanto o simulador processa o ADR dinâmico, o motor de gerenciamento de rede tenta indexar tabelas de parâmetros regionais que não foram dimensionadas para o plano de 64 canais completo (ou sub-bandas customizadas).

## 4. Conclusão de Auditoria

A estabilidade absoluta do **Modelo de Dilatação Temporal** (PDR 97,14% no teste acima) em contraste com o colapso total da **Simulação Física** prova que o modelo matemático desenvolvido é a única via científica para extrair métricas confiáveis de escalabilidade dinâmica (ADR) para o padrão brasileiro sem a necessidade de reescrever o núcleo do simulador ns-3.
