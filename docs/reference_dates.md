# Datas de referência — uma linha do tempo oficial para Analytics, SGQ e SGA

> Pergunta de auditor que este documento responde: *"Qual é a data de referência do sistema, e por que o
> notebook tem dados até dezembro de 2026 se os registos do SGI fecham em agosto?"*

| Elemento | Data / janela | Onde está definido |
|---|---|---|
| **Data de referência do SGI** (fecho dos registos para a revisão pela gestão) | **2026-09-28** | `SGI_…/SGI_Sistema-de-gestao-da-qualidade/_build/sgqlib.py` (`DATA_REF`) |
| Reunião de revisão pela gestão do SGA | 2026-09-23 | `SGI_…/SGA_Sistema-de-gestao-ambiental/_build/sgalib.py` (`DATA_REF`) |
| Período de dados dos registos SGQ e SGA (meses fechados) | 2025-07-01 a **2026-08-31** (SGA reconstrói mar–jun/2025 a partir de faturas, marcados como estimativa) | `sgqlib.py` (`PER_INI`, `PER_FIM`), `envdata.py` (`MESES`) |
| **Janela do dataset analítico** (produção) | **2025-07-01 a 2026-12-30** | `datasets/bronze/`, `docs/dataset_facts.md` |
| Eventos de fecho (decisão de lote, fecho de CAPA, resolução de reclamação) | até 90 dias depois da janela de produção (última CAPA fechada em 2027-02) | `contracts/data_contract.yaml` (`closing_events_tolerance_days`) |
| Expansão de portfólio (4 máquinas novas) | produção a partir de 2026-07-06 | `docs/simulation_storylines.md` |

## Como as duas janelas convivem

- **Os registos do SGI mostram o que se sabia à data de referência.** O SGQ só usa meses fechados até
  2026-08-31 e recalcula o estado de CAPAs e reclamações **à data de referência**: uma CAPA que no dataset
  fecha depois de 2026-09-28 aparece no SGQ como aberta/atrasada (`qdata.py`).
- **O dataset analítico é um cenário sintético que se estende 3 meses além da data de referência**
  (outubro–dezembro de 2026 é uma janela simulada "à frente"). Isso é deliberado: as storylines de
  causa-raiz (desgaste de molde, reforma, deterioração da SS-001, endurecimento de AQL da storyline F em
  outubro/2026) precisam de história completa — antes, durante e depois — para que o pipeline possa ser
  validado contra uma verdade conhecida. **Não é dado observado de uma fábrica real**, e nenhum número do
  notebook deve ser lido como "o que aconteceu" após 2026-09-28.
- Consequência prática: um KPI do notebook para 2026 inteiro e o mesmo KPI num registo SGQ **não devem
  bater** — o SGQ fecha em agosto, o notebook vai até dezembro. Para comparar, filtrar o notebook até
  2026-08-31.

## Regra de governança

1. Toda nova peça do SGI declara `DATA_REF` e o período de dados usado.
2. Todo número citado no README ou num relatório diz de que janela vem.
3. Se um dia o dataset for reduzido para terminar na data de referência, esta tabela é o único lugar a
   atualizar — e `tests/test_dataset_facts.py` sinaliza os documentos que citarem a janela antiga.
