# Auditoria Independente Pós-Correção — Six Big Losses e Revisão Multidisciplinar

**Projeto:** Manufacturing Performance Analytics
**Escopo desta auditoria:** correção de um bug confirmado em `gold.six_big_losses_monthly`, mais uma revisão multidisciplinar independente do projeto inteiro (Engenharia da Qualidade, Engenharia Industrial, Manutenção, Lean, Six Sigma, Engenharia de Dados, Ciência de Dados), com uma regra dura de evidência: **todo número citado abaixo foi localizado no output real e executado do notebook (`manufacturing_performance_analytics.ipynb`, reexecutado do início ao fim, 420 células, 0 erros) ou em consulta SQL direta ao warehouse — nunca de memória ou aproximação.** Onde um número não pôde ser verificado, isso é declarado explicitamente em vez de estimado.

Esta auditoria complementa — e em um ponto, corrige — [`technical_audit_and_methodology.md`](technical_audit_and_methodology.md).

---

## 1. Bug confirmado e correção

`gold.six_big_losses_monthly` (carga do warehouse, antiga Parte 3.7) calculava `QualityLossHours` como `RunTimeHours * (1 - Quality)` — a fórmula **antiga**, com dupla contagem entre perda de velocidade e perda de qualidade. A fórmula corrigida (`RunTimeHours * Performance.clip(lower=0) * (1 - Quality).clip(lower=0)`) já existia no mesmo notebook, na Parte 4.7 (BQ-026), usada apenas para gerar o gráfico `04_06_six_big_losses.png` — ou seja, **o gráfico estava certo, mas a tabela gold persistida, que é por definição arquitetural deste projeto a camada "pronta para negócio" consultável por BI, carregava o valor com dupla contagem.**

Além disso, `tests/test_analytics_invariants.py::test_quality_loss_is_not_double_counted_with_speed_loss` recalculava a fórmula correta isoladamente dentro do próprio teste, sem importar nada de `lib/etl_lib.py` ou do notebook — por isso o teste passava mesmo com o bug presente.

### Correção aplicada

1. Nova função única `compute_six_big_losses(production_df, downtime_df, group_columns)` em `lib/etl_lib.py` — fonte única para as 5 categorias mensuráveis das Seis Grandes Perdas (Quebras, Setup/troca, Paradas breves/idling, Perda de velocidade, Perda de qualidade), parametrizável por nível de agregação (`["Month", "Process"]` para a tabela gold, `["Process"]` ou `[]` para os usos da Parte 4.7).
2. Os dois cálculos duplicados no notebook (carga do gold e Parte 4.7 — chart + tabela por processo) foram substituídos por chamadas a essa função. Nenhuma fórmula de Six Big Losses permanece inline no notebook.
3. `gold.six_big_losses_monthly` foi recarregada. Verificação direta (SQL):

   | LossCategory | Horas (gold, pós-correção) |
   |---|---|
   | Quebras (falha não planejada) | 16.316,41 |
   | Perda de velocidade | 13.948,71 |
   | Paradas breves / idling | 8.618,24 |
   | Setup / troca | 3.962,19 |
   | Perda de qualidade (sucata) | 3.822,54 |

   Estes valores batem, à hora, com a soma por processo impressa pela própria Parte 4.7 do notebook reexecutado (célula 135): Quebras 16.317h, Velocidade 13.949h, Paradas breves 8.618h, Setup/Troca 3.962h, Qualidade 3.822h.
4. O teste foi reescrito para importar e chamar `compute_six_big_losses` de verdade, com um DataFrame sintético pequeno (`RunTimeHours=10, Performance=0.8, Quality=0.9`) — falha explicitamente se a fórmula antiga (`RunTimeHours * (1 - Quality)`, que daria 1,0h em vez de 0,8h) for reintroduzida. Verificado manualmente: reintroduzir a fórmula antiga faz o teste falhar (`0.8 != 0.19999999999999973` de diferença).

### Segunda auditoria independente — outras tabelas gold

Uma varredura dedicada nas outras 3 tabelas gold (`kpi_scorecard_monthly`, `oee_weekly_by_machine`, `cpk_summary_by_characteristic`) não encontrou o mesmo padrão de bug: `kpi_scorecard_monthly` é lida de volta verbatim (nunca recalculada); `oee_weekly_by_machine` e `cpk_summary_by_characteristic` nunca são relidas depois de carregadas (saídas write-only para BI externo, sem segunda fórmula para divergir); `compute_oee_components` e `compute_process_capability` são chamados uma única vez cada, e toda leitura posterior (gold e Parte 4+) lê as mesmas colunas persistidas. O bug do Six Big Losses foi uma violação isolada de uma convenção que o projeto, no resto do código, já impõe consistentemente (ponto único de cálculo, ou alternativas explicitamente rotuladas lado a lado).

### Achado colateral (não relacionado ao bug acima)

Comparado ao render anterior de `04_06_six_big_losses.png` (antes desta sessão), a categoria plant-wide "Perda de qualidade" mudou de 4.174h para 3.823h nesta reexecução — apesar de a fórmula da Parte 4.7 ser textualmente idêntica entre as duas execuções (confirmado por diff de código) e os indicadores de Availability/Performance/Quality/OEE por processo (Parte 4.1) baterem exatamente entre as duas execuções, aos 3 decimais impressos. Não foi possível confirmar a causa raiz dentro do escopo desta sessão; a hipótese mais provável é sensibilidade de ponto flutuante no termo `(1 - Quality)` (pequeno, ~2,4% em média — pequenas diferenças relativas de Quality na 4ª/5ª casa decimal se amplificam nesse termo), combinada com o ambiente Python local ter sido reconstruído do zero nesta sessão (o `.venv` original do projeto não existe mais nesta máquina; as versões de pandas/numpy/scikit-learn usadas agora são as mais recentes disponíveis, não necessariamente as mesmas do run original). **Registrado explicitamente como não totalmente investigado, em vez de omitido.**

---

## 2. Revisão multidisciplinar independente (números verificados no output real)

### Engenharia da Qualidade / Six Sigma

OEE de planta 79,1% (Disponibilidade 87,4%, Performance 92,7%, Qualidade 97,6% — célula 106), corretamente distinto da média simples por ordem (76,5%, explicitamente rotulada como *não* sendo o OEE da planta). Capacidade de processo: **0% dos 190 grupos** máquina×molde×característica (40 de tampa + 150 de frasco; célula 71 e reconferência SQL direta em `gold.cpk_summary_by_characteristic`) cravam Cpk ≥ 1,33 — nenhum grupo é capaz, em nenhum domínio. DOE fatorial na IM-002 (GLM binomial, célula 330): velocidade de injeção (p=0,0000) e temperatura do barril (p=0,0000) são significativas, assim como sua interação (p=0,0203); tempo de resfriamento não é (p=0,3598).

### Manutenção / Confiabilidade

Pior MTBF: ISBM-005 (8,6h); pior MTTR: SS-001 (2,2h) — célula 122. Weibull: ISBM-005 tem o β mais alto (1,299; η=14,7h; N=968 falhas) — sinal de desgaste mais forte e mais rápido da frota; SS-001 (β=0,785), SS-002 (β=0,829) e HF-001 (β=0,827) têm β<1, ou seja, falha não predominantemente por desgaste nessas três. Efetividade de PM: GLM Poisson (Falhas ~ DiasDesdeÚltimaPM + Máquina) não encontra associação significativa (coeficiente=0,00009; **p=0,973**; razão de dispersão 0,92, sem superdispersão relevante — célula 130) — corretamente reportado como "sem associação detectada", não como "PM provada ineficaz".

### Engenharia Industrial / Lean

Takt vs. taxa real (célula 150): Sopro — takt 1.499,47 u/h vs. real 2.857,37 u/h (razão 1,91×); Injeção — takt 1.830,44 vs. real 4.249,76 (razão 2,32×). Lei de Little (célula 161): WIP implícito de 20.597 unidades entre Sopro e Decoração, das quais aproximadamente 7.261 unidades (~35%) estão em estoque intermediário, sem estar sendo processadas.

### Ciência de Dados / Machine Learning

Métrica real de teste por modelo, do resumo consolidado do próprio notebook (célula 395):

| Modelo | Algoritmo | Métrica |
|---|---|---|
| Previsão de produção | Ridge | R²=0,998 |
| Previsão de parada | Ridge | R²=0,868 |
| Previsão de rejeitos | XGBoost | R²=0,890 |
| Taxa de sucata | XGBoost | R²=0,588 (sem leakage) |
| Qualidade de lote | LogisticRegression | ROC-AUC=0,689 |
| Manutenção preditiva | LogisticRegression | ROC-AUC=0,593 |

Auditoria de vazamento (BQ-079, células 390-391): remover as features vazadas (`ActualCycleTimeSec`, `Availability`) do modelo de sucata muda R² de 0,587 para 0,588 — diferença desprezível; essas features já tinham correlação quase nula com o alvo (-0,027 e 0,009). Divulgação honesta de trade-off de custo (célula 384): no threshold de validação ótimo (0,01) para o modelo de qualidade de lote, o custo esperado cai 98% (R$419.378 → R$10.388), mas exige reinspecionar 100% dos 1.575 lotes de teste (1.385 falsos positivos) para zerar falsos negativos — não é um ganho "de graça".

### Engenharia de Dados

Linhas carregadas nas 4 tabelas gold (log de carga + reconferência SQL): `kpi_scorecard_monthly` 18, `oee_weekly_by_machine` 1.422, `cpk_summary_by_characteristic` 190, `six_big_losses_monthly` 328.

---

## 3. Achado documental — número stale no README (mesma família de falha, em documentação)

`README.md`, Seção 7, citava **"0% dos 140 grupos máquina×molde×característica de tampa"** cravam Cpk ≥ 1,33. A alegação qualitativa (0% capaz) está correta e reverificada — mas "140" não corresponde a nenhum recorte real dos dados atuais: `gold.cpk_summary_by_characteristic` tem 40 grupos de domínio Cap (tampa), 150 de domínio Bottle (frasco), 190 no total. Corrigido para "190 grupos (40 de tampa + 150 de frasco)" — commit `5031d8d`.

Esse é o mesmo tipo de falha do bug do Six Big Losses (um número que deveria vir de uma única fonte de verdade, mas foi escrito/copiado manualmente em outro lugar e ficou defasado) — só que em documentação, não em código de produção. Reforça o valor de citar números com a fonte executável ao lado, não de memória.

---

## 4. Buscado e não verificável (declarado, não estimado)

- Nenhuma célula imprime MAE/RMSE explicitamente para os modelos de regressão — apenas R² aparece no resumo consolidado e nas tabelas de comparação de modelo. Não estimado.
- Não foi encontrada nenhuma outra inconsistência do tipo "mesmo número, calculado duas vezes, com valores diferentes apresentados como se medissem a mesma coisa" além do já documentado nas Seções 1 e 3 acima.
- A causa raiz exata do achado colateral da Seção 1 (4.174h → 3.823h entre execuções) não foi confirmada dentro do escopo desta sessão.

---

## 5. Nota de atualização sobre `technical_audit_and_methodology.md`

O item 1 daquele documento ("Six Big Losses: perda de qualidade corrigida para `Runtime × Performance × (1 − Quality)`; evita dupla contagem com perda de velocidade") descrevia corretamente a Parte 4.7 do notebook, mas **não cobria `gold.six_big_losses_monthly`**, que só foi corrigida nesta sessão. Esta auditoria substitui aquele item por: a correção agora vale para as duas superfícies (gráfico e tabela gold), através de uma única função compartilhada (`compute_six_big_losses`), eliminando a possibilidade de nova divergência entre elas.
