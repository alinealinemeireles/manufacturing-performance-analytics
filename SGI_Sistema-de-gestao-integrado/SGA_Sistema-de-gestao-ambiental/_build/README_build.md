# Geração dos registos do SGA Plasticom (ISO 14001:2026)

Scripts que geram a pasta `../Registos_SGA_Plasticom/`.

| Script | Saída |
|---|---|
| `build_all.py` | Gera os registos Excel (SGA-01 a SGA-17), recalcula-os no Microsoft Excel (COM), faz o pós-processamento (tabela dinâmica e segmentações do SGA-17) e gera o índice `SGA-00` com a verificação de integridade. O SGA-02 é mantido manualmente (registo corporativo) e não é regerado — ver `MANUAL` |
| `build_17_dupla_materialidade.py` | SGA-17: dupla materialidade (temas, IRO, evidências, partes interessadas, painel). `python build_17_dupla_materialidade.py <saida.xlsx>` gera, recalcula e pós-processa |
| `build_18_alteracoes.py` | SGA-18: planeamento de alterações (ISO 14001:2026, 6.3) com checklist de avaliação em colunas |
| `build_19_esg_ambiental.py` | SGA-19: ESG ambiental — fatores de emissão, inventário mensal de GEE (âmbitos 1, 2 LB/MB, 3), Calculadora_GEE com simulador 2030, metas, pegada por produto, substâncias, indicadores VSME/ESRS/GRI/SASB/CDP e matriz de requisitos ESG-E. Lê SGA-07 e SGA-13 já gerados (correr depois deles) |
| `build_20_reciclabilidade.py` | SGA-20: reciclabilidade de embalagens — avaliação RecyClass por SKU (campos da ferramenta online + regras DfR em tbl_regras_dfr → classe A–F, taxa de reciclabilidade, grau PPWR indicativo), conteúdo reciclado face ao art. 7.º, famílias PPWR, matriz legal/normativa de produto (verificação da matriz do ChatGPT), aplicabilidade SKU × requisito, vendas por país, embalagens de expedição (RAP), certificados PCR, alegações, maturidade, painel com tabela dinâmica. `resumo()` alimenta RG-SGA-04/05/17/19 |
| `build_21_quimicos.py` | SGA-21: gestão de produtos químicos — papel REACH, inventário (42 produtos) com perigos das frases H e balanço de COV, componentes e SVHC, FDS (Reg. 2020/878), cenários de exposição, registo/importação, declarações de fornecedores, avaliação de risco químico (DL 24/2012, DL 301/2000), medições NP EN 689, armazenagem, Seveso, matriz legal de químicos. `resumo()` dá COV e substâncias preocupantes aos RG-SGA-16/17/19. Formação, calendário, ações e SVHC em embalagens ficam nos registos donos (08, 04, 06, 20) — ver SGA-00 Matriz_Fonte_Unica |
| `build_docs.py` | Documentos controlados em Word na pasta `../Documentos_SGA_Plasticom/`: MAN-SGA-01 (manual e âmbito), PR-SGA-01 a 12, IT-SGA-02, IT-SER-03 |
| `sga_extra.py` | Tabelas e colunas complementares para a ISO 14001:2026 numa fábrica real (partes interessadas 4.2, RACI 5.3, incidentes, comunicações externas, manutenção ambiental/F-gas, controlo de processos externos 8.1, faturas em `tbl_meses`, análises laboratoriais) |
| `sga_requisitos.py` | Matriz de requisitos ISO 14001:2026 → documento → evidência → estado e índice de prontidão (folhas do SGA-00) |
| `build_word.js` | Documento Word com as atividades da Lusitana Móveis e as questões teóricas (`node build_word.js <saida.docx>`, requer o pacote npm `docx`) |
| `sgalib.py` | Biblioteca comum: tabelas Excel, validação, formatação condicional, LEIA-ME, dicionário de dados |
| `dims.py` | Dimensões partilhadas (processos, funções, cláusulas ISO 14001:2026) |
| `envdata.py` | Base de dados ambiental mensal derivada de `datasets/silver` (fatores em `PARAMS`) |
| `recalc.py` | Recalcula no Excel e lista erros de fórmula |

Requisitos: Python com openpyxl, pandas, numpy e pywin32; Microsoft Excel (para o recálculo).

## Fonte única (24/09/2026)
Cada assunto é registado num só ficheiro (ver `SGA-00 Matriz_Fonte_Unica`). Totais partilhados são calculados uma vez no código: GEE em `build_19_esg_ambiental.totais_gee()`, COV e substâncias em `build_21_quimicos.resumo()`, parâmetros em `envdata.P`.
