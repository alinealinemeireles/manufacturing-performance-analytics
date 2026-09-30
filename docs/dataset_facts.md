# Dataset facts (gerado automaticamente)

> **Não editar à mão.** Gerado por `python scripts/dataset_facts.py` a partir de `datasets/bronze/` e
> `datasets/dim/`. `tests/test_dataset_facts.py` falha se este arquivo ficar desatualizado ou se o
> README citar uma contagem diferente destas.

| Fato | Valor |
|---|---|
| Tabelas fato brutas (bronze) | 22 |
| Dimensões (arquivos em `datasets/dim/` + derivadas na Parte 2) | 15 (10 arquivos + 5 derivadas) |
| Processos | 4 |
| Máquinas | 22 |
| Ordens de produção (únicas, bronze) | 16,397 |
| Produtos — frascos/potes | 149 |
| Produtos — tampas | 36 |
| Clientes | 18 |
| Fornecedores | 10 |
| Janela de produção | 2025-07-01 a 2026-12-30 |

## Máquinas por processo

| Processo | Máquinas |
|---|---|
| Blow Molding | 10 |
| Hot Foil Stamping | 2 |
| Injection Molding | 8 |
| Screen Printing | 2 |

## Linhas por tabela bronze

| Tabela | Linhas (brutas, com duplicatas deliberadas) |
|---|---|
| `fact_bottle_attribute_inspection_cq_raw` | 31,133 |
| `fact_bottle_disposition_lot_cq_raw` | 3,880 |
| `fact_bottle_inspection_variables_cq_raw` | 190,004 |
| `fact_cap_attribute_inspection_cq_raw` | 17,880 |
| `fact_cap_disposition_lot_cq_raw` | 2,606 |
| `fact_cap_inspection_variable_cq_raw` | 129,780 |
| `fact_capa_raw` | 814 |
| `fact_customer_complaints_raw` | 210 |
| `fact_doe_im002_raw` | 27 |
| `fact_downtime_raw` | 142,163 |
| `fact_gage_rr_study_raw` | 90 |
| `fact_ink_attribute_inspection_cq_raw` | 13,388 |
| `fact_ink_disposition_lot_cq_raw` | 2,082 |
| `fact_material_consumption_raw` | 16,787 |
| `fact_nonconformance_raw` | 1,330 |
| `fact_process_parameters_raw` | 12,579 |
| `fact_production_plan_raw` | 16,397 |
| `fact_production_raw` | 16,427 |
| `fact_raw_material_inspection_raw` | 6,969 |
| `fact_raw_material_lot_disposition_raw` | 1,896 |
| `fact_sales_raw` | 8,548 |
| `fact_supplier_complaints_raw` | 80 |
