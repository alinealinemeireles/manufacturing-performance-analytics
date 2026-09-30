# Integração SGI (ISO 9001 + ISO 14001) ↔ Manufacturing Analytics

> O projeto tem três blocos — o notebook analítico, os registos do SGQ (ISO 9001) e os do SGA (ISO 14001).
> Este documento mostra **onde já estão ligados pelo mesmo dado**, a cadeia requisito → evidência →
> eficácia para os requisitos que o analytics sustenta, e o que ainda falta ligar.

## 1. O que já está ligado (fonte única: `datasets/silver/`)

Os registos do SGI **não têm dados próprios inventados para os indicadores operacionais**: os geradores
`_build/` leem a mesma camada silver que o notebook, depois do Data Quality Gate.

| Registo | Lê do dataset | Usa para |
|---|---|---|
| SGQ-02 Processos / infraestrutura | `fact_production`, `fact_downtime`, `dim_machine`, `dim_mold` | horas de marcha, OEE, avarias de equipamento e horas de paragem efetiva por máquina (7.1.3) |
| SGQ-04 Riscos | inspeções por variáveis, `dim_machine_profile` | evidência de risco por máquina (deteção automática de defeitos) |
| SGQ-05 Objetivos / KPI | produção, vendas, reclamações, CAPA, lotes de MP, decisões de lote, reclamações a fornecedor | séries mensais dos KPI da qualidade |
| SGQ-09 Metrologia / MSA | `fact_gage_rr_study` | estudo Gage R&R (7.1.5) |
| SGQ-10 Requisitos do cliente | vendas, reclamações, clientes | encomendas expedidas e revisão de requisitos (8.2.3), CPMU por cliente |
| SGQ-12 Fornecedores | lotes de MP, reclamações a fornecedor, fornecedores | avaliação de fornecedores (8.4) |
| SGQ-13 Produção / rastreabilidade / libertação | decisões de lote | libertação de produto (8.6), rastreabilidade (8.5.2) |
| SGQ-14 Saídas não conformes | NC, CAPA, decisões de lote, lotes de MP, vendas | tratamento de saídas não conformes (8.7) |
| SGQ-15 Reclamações / satisfação | reclamações, vendas, clientes | satisfação do cliente (9.1.2) |
| SGQ-16 Auditoria interna | reclamações, NC | amostras de auditoria |
| SGQ-18 NC / CAPA | CAPA | ação corretiva (10.2) |
| SGQ-19 Melhoria / Custo da Qualidade | reclamações, decisões de lote, lotes de MP | melhoria contínua (10.3) |
| SGA-13 Monitorização e medição | `fact_production` (horas de marcha, rejeições), `fact_downtime` (mudanças de molde) | energia, água e resíduos rateados por horas de marcha |
| SGA-19 ESG / GEE | derivado do SGA-13 + `dim_bottle`, `dim_cap` | emissões (kgCO₂e) e massa de produto |

**Consequência:** uma correção no dado propaga-se para o SGI. As correções de 2026-09-29 (vendas da
expansão, paragem efetiva, classificação de avarias) mudam insumos do SGQ-10/13/15 e do SGA-13/19 —
por isso os registos são regenerados (`python _build/build_all.py` em cada subsistema) depois de o
notebook reescrever a silver.

## 2. Cadeia requisito → evidência → eficácia (ISO 9001)

| Requisito | Processo / risco | Controlo | Dado → KPI | Evidência | Critério de eficácia |
|---|---|---|---|---|---|
| 7.1.5 Recursos de monitorização e medição | Medição não confiável gera decisão errada | Gage R&R antes de ler SPC/capacidade | `fact_gage_rr_study` → %GRR, ndc | Parte 9.2; SGQ-09 | %GRR < 10% (aceitável), 10–30% condicional |
| 8.4 Fornecedores externos | MP fora de especificação (SUP-005) | Inspeção de receção, scorecard | `fact_raw_material_*` → taxa de aprovação, defeito a jusante por fornecedor | Parte 6.3/6.4b; SGQ-12 | Taxa de aprovação ≥ meta; defeito a jusante sem diferença significativa vs. frota |
| 8.5.1 Produção em condições controladas | Processo instável/incapaz (IM-002, ISBM-003) | Plano de controlo, cartas X̄/R, Western Electric | inspeção por variáveis → Cpk, LatestCpk, regras WE | Parte 5; gold `cpk_summary_by_characteristic` | Processo estável **e** LatestCpk ≥ 1,33 |
| 8.5.2 Identificação e rastreabilidade | Reclamação sem lote de origem | `LotId` de 16 caracteres | `BR-LOTID-TRACE` (contrato) | Data Quality Gate; SGQ-13 | 100% das expedições rastreáveis à ordem |
| 8.6 Libertação de produtos | Lote rejeitado chega ao cliente | Decisão de lote AQL antes da expedição | `BR-RELEASE`, `BR-SHIP-AFTER-DECISION` | Data Quality Gate; SGQ-13 | 0 lotes rejeitados expedidos; 0 expedições antes da decisão |
| 8.7 Saídas não conformes | Segregação falha | Registo de NC, disposição | `fact_nonconformance` | SGQ-14 | 100% das rejeições com NC |
| 9.1.2 Satisfação do cliente | Reclamação recorrente | Tratamento de reclamação | reclamações ÷ expedido → CPMU | Parte 6.1; SGQ-15 | CPMU em tendência descendente |
| 9.1.3 Análise e avaliação | Decisão sem evidência | Notebook, classes de evidência | todos os KPI de `docs/kpi_lineage.md` | Partes 4–12 | Nenhuma conclusão mais forte que o método |
| 9.3 Revisão pela gestão | Gestão sem visão integrada | Scorecard mensal | `gold.kpi_scorecard_monthly` | SGQ-17 | Entradas 9.3.2 cobertas por dado |
| 10.2 NC e ação corretiva | CAPA ineficaz / recorrência | Verificação de eficácia | NC antes/depois por processo × categoria; `CAPA-EFF` | Parte 6.8; SGQ-18 | Redução **robusta** (sobrevive ao teste sem sobreposição de janelas) mantida ≥ 3 meses |
| 10.3 Melhoria contínua | Melhoria sem prova | DMAIC + DOE + corrida de confirmação | DOE IM-002 → taxa de Short Shot | Partes 8–9; SGQ-19 | Confirmação reproduz o ótimo do DOE; SPC reforçado depois |

## 3. O que ainda falta ligar (próximos passos, por ordem de valor)

1. **Analytics ← SGA (o sentido inverso):** o notebook ainda não consome os dados ambientais. Os
   indicadores de maior valor já são calculáveis com o que existe: kWh e kgCO₂e **por mil unidades boas**
   por máquina (SGA-13 rateia energia por horas de marcha; o notebook tem unidades boas por máquina),
   e **kg de sucata por tonelada produzida** (rejeitado × massa unitária de `dim_bottle`/`dim_cap`). O caso
   natural é a IM-002: o DOE que reduz Short Shot reduz sucata, e portanto energia e CO₂ por unidade boa.
2. **Revisão pela gestão integrada:** uma única vista com as entradas da cláusula 9.3 dos dois sistemas
   (qualidade, produção, manutenção, ambiente, riscos, ações) lida da gold + dos registos SGA — hoje estão
   em SGQ-17 e SGA-15 separados.
3. **Riscos com indicador:** ligar cada risco do SGA-02/SGQ-04 a um KPI do contrato (ex.: risco
   "libertação indevida de lote" → `BR-RELEASE`), para que a avaliação de eficácia do tratamento de risco
   seja um número e não uma opinião.
