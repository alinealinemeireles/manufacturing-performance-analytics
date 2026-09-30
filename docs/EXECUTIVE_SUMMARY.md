# Sumário Executivo — leitura de 5 minutos

> **O que é:** um protótipo de *Manufacturing Intelligence* para uma fábrica de embalagens plásticas
> (22 máquinas, 4 processos, 18 meses), que integra Engenharia da Qualidade, Lean, manutenção,
> estatística, engenharia de dados e Machine Learning. O objetivo não é um dashboard: é fechar o ciclo
> **dado → evidência → causa-raiz → ação → controlo → verificação de eficácia**.
>
> **O que não é:** descoberta causal numa fábrica real. O dataset é sintético, com causas-raiz embutidas
> e documentadas; o projeto prova que o método as recupera ([`reference_dates.md`](reference_dates.md),
> [`simulation_storylines.md`](simulation_storylines.md)).

## A pergunta

*Como transformar dados industriais em decisões verificáveis de melhoria contínua — integrando
desempenho, qualidade, manutenção e os requisitos ISO 9001/14001 — de forma que cada decisão tenha
evidência, ação, controlo e verificação de eficácia?*

## Arquitetura em uma linha

```text
CSV bronze (sujo) → limpeza Python → DATA QUALITY GATE (contrato: ~240 regras) → SQL Server silver/gold
      → OEE · SPC/Cpk · MSA · Six Big Losses · confiabilidade · DOE · ML com baseline
      → plano de ação com critério de eficácia → registos SGQ/SGA gerados do mesmo dado
```

## 5 números

| KPI | Valor | Leitura |
|---|---|---|
| **OEE da planta** (ponderado) | **78,2%** — Disponibilidade 88,2% · Performance 90,8% · Qualidade 97,7% | Disponibilidade é o pilar mais fraco |
| **Maior perda de disponibilidade** | Falta de material, utilidades ou operador: **10.221 h** vs. avarias de equipamento: 6.863 h | A máquina para mais **à espera** do que **avariada** — o alvo é abastecimento e organização do trabalho antes de manutenção |
| **Capacidade de processo** | **0 de 726** grupos máquina × molde × produto × característica com Cpk ≥ 1,33 no período | Planta estatisticamente marginal, não "capaz com exceções" |
| **Sistema de medição** | %GRR = 4,05%, ndc = 34 | A variação observada é do processo, não do instrumento — o SPC pode ser lido |
| **Qualidade do dado** | 0 violações bloqueantes; 6 avisos documentados | Nenhum KPI é calculado sobre dado que quebra o contrato |

## 3 casos — do sintoma à ação verificável

**1. IM-002 — Short Shot (Six Sigma + DOE).** A IM-002 tem taxa de Short Shot de 1,35%, 3,5× a média da
injeção, e Cpk de peso muito abaixo da frota **depois de controlar o mix de produto**. Um DOE fatorial
mostrou efeito significativo da velocidade de injeção, da temperatura do barril **e da sua interação**; o
melhor vértice reduziu a taxa para 0,11% (−92%, medido). **Ação:** corrida de confirmação → novo padrão
operacional → plano de controlo e SPC reforçado. **Eficácia:** a confirmação reproduz o ótimo e o Cpk de
peso sobe de forma sustentada. É a iniciativa mais bem provada do projeto — evidência experimental, não
só associação.

**2. M-SOP-007 — desgaste de molde (SPC + manutenção).** Flash + fuga sobem de 0,52% para 0,74% (1,4×)
antes da reforma de junho/2026 e caem depois dela. O indicador antecedente certo não é o calendário, é o
**número de unidades desde a última reforma**. **Ação:** gatilho de reforma por ciclos acumulados; alerta
quando a taxa ≥ 2× a linha de base por 2 meses.

**3. SUP-005 → matéria-prima → defeito → cliente (qualidade de fornecedores).** O fornecedor SUP-005
(compra *spot*) tem 74,5% de aprovação em 259 lotes, abaixo do limiar de 85%. A ligação com o cliente é
real mas parcial: ~67% das reclamações rastreáveis vêm de ordens com sinal interno de qualidade pior que a
mediana; a correlação mensal agregada não é significativa — e o projeto diz isso em vez de esconder.
**Ação:** inspeção de receção reforçada e requalificação do fornecedor; rastreabilidade por lote
(`LotId`) já garantida pelo contrato de dados.

## O que os dados **não** sustentam (e o projeto diz)

- **Machine Learning:** cada um dos 6 modelos foi comparado com a regra simples que substituiria; **só 1
  (taxa de sucata por ordem, +14%) supera-a de forma material**. A "previsão de produção" com R² 0,998
  empata com *plano × cumprimento histórico* (o mérito é do plano), e a manutenção preditiva (ROC-AUC 0,58)
  não bate a taxa histórica de avarias da máquina — com histórico de paragens apenas, sem sensores, o dado
  não sustenta manutenção preditiva. Resultado negativo reportado como tal.
- **Eficácia de CAPA:** a redução de NC depois da CAPA deixa de ser significativa quando se removem janelas
  antes/depois sobrepostas — associação, não prova.
- **Valores em €:** cenários condicionados a custos unitários declarados, não contabilidade.

## Onde aprofundar

[`kpi_lineage.md`](kpi_lineage.md) · [`client_root_cause_action_plan.md`](client_root_cause_action_plan.md) ·
[`sgi_analytics_integration.md`](sgi_analytics_integration.md) · [`audit_2026-09-29.md`](audit_2026-09-29.md) ·
notebook completo: [`manufacturing_performance_analytics.ipynb`](../manufacturing_performance_analytics.ipynb)
