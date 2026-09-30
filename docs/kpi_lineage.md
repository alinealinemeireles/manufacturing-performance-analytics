# KPI Lineage — de onde vem cada número

> Pergunta que este documento responde: **"De onde veio este KPI?"** — para cada indicador crítico, a
> definição, a fonte bruta, a função única que o calcula, onde fica persistido e o teste que o protege.
> Regra do projeto: **uma fonte única de verdade por KPI crítico** — a fórmula vive numa função de
> `lib/`, e notebook, camada gold e testes chamam a mesma função (nunca recalculam inline). O caso que
> motivou a regra: `gold.six_big_losses_monthly` já teve uma fórmula de perda de qualidade diferente da do
> gráfico da Parte 4.7 (dupla contagem com a perda de velocidade — ver `docs/post_fix_independent_audit.md`).

## 1. Cadeia de camadas

```text
datasets/bronze/*.csv            dado bruto, deliberadamente sujo (versionado)
        │  Parte 2 — lib/etl_lib.py (limpeza, LotId, OEE, SPC)
        ▼
datasets/silver/*.csv            limpo, 1 linha por evento de negócio
        │  Data Quality Gate — lib/data_quality.py + contracts/data_contract.yaml
        │  (regra "block" falhou → o notebook para aqui; nada é carregado)
        ▼
SQL Server dbo.*_processed  →  views silver.*   (Parte 3.6/3.8)
        │  Parte 3.7
        ▼
SQL Server gold.*                agregados por dimensão × período
        ▼
Partes 4–12 (análise), docs/, SGI (registos SGQ/SGA leem datasets/silver)
```

## 2. KPIs críticos

| KPI | Definição | Fonte bronze | Função única (`lib/`) | Silver / Gold | Teste | Classe de evidência |
|---|---|---|---|---|---|---|
| **Availability** | Tempo em operação ÷ tempo de produção planeado. **Planeado** (`PlannedTimeHours`) = janela **real** da ordem − paragens planeadas que não são troca (refeição, limpeza, PM); **operação** (`RunTimeHours`) = planeado − paragem não planeada − setup/troca, em minutos **efetivos** (decisão D1, 2026-09-30; as horas do plano ficam em `PlannedHours`) | `fact_production_plan_raw`, `fact_downtime_raw` | `etl_lib.compute_oee_components` + `compute_effective_downtime` | `silver.fact_production.Availability`; `gold.kpi_scorecard_monthly` (ponderado) | `test_etl_lib.py::test_oee_identity_and_bounds`, `::test_availability_uses_effective_not_summed_downtime`, `::test_order_without_plan_keeps_a_finite_availability`, `::test_oee_time_base_is_the_real_window_not_the_plan`, `::test_setup_is_an_availability_loss…` | Métrica |
| **Performance** | (peças ÷ h em operação) ÷ capacidade nominal (`dim_machine_setup`), **limitada a 1** | `fact_production_raw`, `dim_machine_setup` | `compute_oee_components` | `Performance`; `PerformanceVsNominal` (sem limite, vazio quando `DowntimeExceedsPlan`) | `test_oee_components_are_bounded...`, `::test_downtime_reaching_planned_time_is_flagged...` | Métrica |
| **Quality (OEE)** | (produzido − rejeitado) ÷ produzido | `fact_production_raw` | `compute_oee_components` | `Quality` | `test_oee_identity_and_bounds` | Métrica |
| **OEE** | A × P × Q por ordem; na gold, **ponderado** por tempo/capacidade/unidades (não média de ordens) | as três acima | `compute_oee_components`; `_weighted_oee_monthly` (Parte 3.7) | `silver.fact_production.OEE`; `gold.kpi_scorecard_monthly.OEE` e `MeanOEEPerOrder` lado a lado | `PROD-OEE` no contrato; `test_oee_identity_and_bounds` | Métrica |
| **Six Big Losses (h)** | 5 categorias mensuráveis (tabela 3) | produção + paragens | `etl_lib.compute_six_big_losses` | `gold.six_big_losses_monthly`; gráfico 04_06 | `test_analytics_invariants.py::test_quality_loss_is_not_double_counted...` | Métrica (velocidade/qualidade = horas-equivalentes) |
| **Paragem efetiva (min)** | Parte de cada evento não coberta por um evento anterior na mesma máquina (união dos intervalos) | `fact_downtime_raw` | `etl_lib.compute_effective_downtime` | `silver.fact_downtime.EffectiveDowntimeMin` | `test_effective_downtime_counts_overlapping_events_once`; `DT-EFF` no contrato | Métrica |
| **MTBF** | Horas em operação ÷ n.º de **avarias de equipamento** | produção + paragens | `etl_lib.classify_stoppage` (o que conta como avaria) | `gold.kpi_scorecard_monthly.MTBFHours` | `test_only_equipment_failures_count_as_breakdowns` | Métrica |
| **MTTR** | Duração média (por evento) das avarias de equipamento | `fact_downtime_raw` | `classify_stoppage` | `gold.kpi_scorecard_monthly.MTTRHours` | idem | Métrica |
| **Cp / Cpk** | Tolerância ÷ 6σ_within; σ_within = R̄/d2, por máquina × molde × produto × característica | `fact_*_inspection_variable*_raw` | `etl_lib.compute_process_capability` | colunas `Cp`, `Cpk` (valor do período, repetido em cada linha do grupo) | `test_spc_capability.py::test_cp_cpk_from_within_subgroup_sigma` | Métrica — **só interpretável se o processo estiver estável e o MSA aceitável** (ver 4) |
| **Pp / Ppk / Cpm** | σ total das medições individuais (M1..Mn), não das médias de subgrupo | idem | `compute_process_capability(measurement_columns=...)` | colunas `Pp`, `Ppk`, `Cpm` | `test_pp_ppk_use_individual_measurements...` | Métrica |
| **LatestCpk / IsCapable** | Cpk dos **últimos 25 subgrupos** (janela móvel); `IsCapable` = LatestCpk ≥ 1,33 | idem | `etl_lib.summarize_capability_over_time` | `gold.cpk_summary_by_characteristic` (`PeriodCpk`, `LatestCpk`, `PctWindowsBelowTarget`) | `test_capability_over_time_sees_a_recent_drop...` | Métrica |
| **Limites de controlo X̄/R + Western Electric** | X̄ ± A2·R̄; regras 1–4 | idem | `etl_lib.compute_control_limits`, `stats_lib.apply_western_electric_rules` | `XBarUCL/LCL`, `OutOfControlXBar` | `test_xbar_r_control_limits...`, `test_western_electric_rule_*` | Métrica |
| **"FPY" (gold)** | Fração de **lotes** aprovados na decisão final | `fact_*_disposition_lot_cq_raw` | Parte 3.7 | `gold.kpi_scorecard_monthly.FPY` | — | **Proxy** — é taxa de aceitação de lote (AQL), não FPY de unidades; RTY idem (proxy, ver README) |
| **Scrap %** | Σ rejeitado ÷ Σ produzido | `fact_production_raw` | Parte 3.7 | `gold.kpi_scorecard_monthly.ScrapPct` | `PROD-REJ` no contrato | Métrica |
| **DPU / DPMO** | Defeitos ÷ amostra (1 oportunidade por unidade) × 10⁶ | `fact_*_attribute_inspection_cq_raw` | `etl_lib.compute_attribute_indicators` | colunas `DPU`, `DPMO` | `test_attribute_indicators` | Métrica |
| **CPMU** | Reclamações ÷ milhão de unidades expedidas | `fact_customer_complaints_raw`, `fact_sales_raw` | `etl_lib.compute_complaints_per_million_shipped`; Parte 3.7 | `gold.kpi_scorecard_monthly.CPMU` | `BR-RELEASE`, `BR-SHIP-AFTER-DECISION` (a expedição que é o denominador tem de ser válida) | Métrica |
| **CAPA em atraso** | CAPA fechada depois do prazo, ou aberta com prazo vencido | `fact_capa_raw` | Parte 2.4 (`IsOverdue`) | `gold.kpi_scorecard_monthly.CAPAOverdueRate` | `CAPA-CLOSE` no contrato | Métrica |
| **Eficácia de CAPA** | NC antes vs. depois, com teste de robustez de sobreposição de janelas | NC + CAPA | Parte 6 | — | `CAPA-EFF` (aviso) | **Associação** — não prova causal (sem grupo de controlo) |
| **Índice Relativo de Priorização Operacional** | Min-max dentro da frota de 4 componentes (qualidade, manutenção, produção, cliente) | vários | Parte 12.1b | — | — | **Priorização relativa** — não é probabilidade de falha nem risco probabilístico; ler sempre com os 4 componentes |
| **Custo da Qualidade / cenários €** | Quantidades medidas × custos unitários **declarados** | vários | Parte 3B/6/12 | — | — | **Cenário económico condicionado às premissas**, não evidência financeira |
| **WIP (Lei de Little)** | Throughput do fluxo (h de calendário) × lead time | produção + genealogia | Parte 4.14b | — | — | **WIP equivalente estimado**, não medido |
| **Previsões de ML** | ver Parte 11 | silver | `ml_lib.tune_*` + `group_rate_baseline` | `dbo.ml_predictions_*`; `datasets/silver/ml_models_vs_baseline.csv` | `test_ml_lib.py` | Previsão — só recomendada se supera a baseline de forma material |

## 3. Six Big Losses — o que é medido, o que é proxy, o que falta

| Perda (Nakajima/JIPM) | Estado | Como é quantificada | Nota |
|---|---|---|---|
| Avarias (breakdown) | **Medida** | Paragem efetiva de eventos `UnplannedFailure` (mecânica, elétrica/controlo) | Desde 2026-09-29 **só avarias de equipamento**: falta de material, de utilidades, de fita/tinta e de operador deixaram de contar como avaria |
| Setup / ajustes | **Medida** | Paragem efetiva de eventos `IsChangeoverSetup` | |
| Paradas breves / idling | **Medida** | Restante paragem não planeada: microparagens **e** paragens por falta de material/utilidades/operador (máquina saudável, mas parada) | "Idling" no sentido TPM inclui a máquina à espera de material |
| Perda de velocidade | **Medida (horas-equivalentes)** | `RunTimeHours × (1 − Performance)` | Não são horas de relógio, são capacidade perdida |
| Defeitos / retrabalho | **Medida (horas-equivalentes)** | `RunTimeHours × Performance × (1 − Quality)` | Escalada pela Performance para não contar duas vezes |
| Arranque / rendimento (startup/yield) | **Não mensurável** | — | Nenhuma coluna isola sucata de arranque; recomendado instrumentar (README §9) |
| Microparagens < 1 min | **Parcial** | Só o que o operador regista como evento | Sem sinal de máquina (PLC), microparagens muito curtas ficam invisíveis |

## 4. Hierarquia de validade para capacidade (regra do projeto)

```text
MSA / Gage R&R aceitável  →  processo estável (X̄/R + Western Electric)  →  distribuição/pressupostos
        →  Cp/Cpk/Pp/Ppk  →  análise de causas  →  melhoria
```

Um Cpk baixo **não** é, por si, "máquina ruim": pode vir de média deslocada (Cp ≫ Cpk), variação
excessiva (Cp baixo), especificação estreita, mistura de produtos/moldes/máquinas no mesmo grupo,
medição ruim (%GRR alto) ou processo instável (Cpk sem significado estatístico). A Parte 5 aplica o
gate de estabilidade antes de ler capacidade, e o grão do cálculo é sempre máquina × molde × produto ×
característica para não misturar especificações.

## 5. Classes de evidência usadas em todo o projeto

| Classe | Significa | Exemplo |
|---|---|---|
| **Fato** | Registo do dado, contado | "16.397 ordens de produção" |
| **Métrica** | Cálculo definido sobre fatos, com fórmula e fonte únicas | OEE, Cpk, MTBF |
| **Proxy** | Métrica que aproxima um conceito que o dado não mede diretamente | "FPY" por lote, RTY, WIP de Little, utilização como candidatura a restrição |
| **Associação** | Relação estatística observada, sem desenho que exclua confundidores | NC antes/depois de CAPA, sinal interno ↔ reclamação |
| **Evidência causal** | Intervenção controlada ou desenho que isola o efeito | DOE fatorial da IM-002 (Parte 9), **após** corrida de confirmação |

Toda frase do README e dos relatórios deve usar a palavra da classe correta — nenhuma conclusão mais
forte do que o método que a sustenta.

## 6. Duas durações de paragem, dois usos

| Coluna | Soma de vários eventos = | Usar para |
|---|---|---|
| `DowntimeDurationMin` | soma das durações (pode contar a mesma hora 2–3×, porque o registo tem eventos sobrepostos) | estatísticas **por evento**: MTTR, distribuição de tempo de reparação, Pareto por motivo |
| `EffectiveDowntimeMin` | tempo de máquina **realmente** perdido (união dos intervalos) | **tempo**: Disponibilidade/OEE, horas das Six Big Losses, custo de indisponibilidade |
