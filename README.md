# Manufacturing Performance Analytics — Raio-X de Melhoria Contínua (Versão 01)

> © 2026 Aline Meireles. Todos os direitos reservados. Este repositório é público para leitura e
> avaliação (ex.: recrutadores, gestores de contratação, engenheiros revisando este trabalho) — ver
> [`LICENSE`](LICENSE). Cópia, redistribuição ou reuso de qualquer parte deste conteúdo sem
> autorização não são permitidos.

### Manufacturing Intelligence, Quality Analytics & Industrial Data Science

O objetivo não é apenas responder **"o que aconteceu?"**, mas avançar sistematicamente para:

> **O que está acontecendo? → Onde está o problema? → Por que está acontecendo? → Qual evidência
> sustenta a causa-raiz? → Qual ação deve ser tomada? → Como comprovar que a ação funcionou?**

`Engenharia da Qualidade` · `Engenharia Industrial` · `Lean Manufacturing` · `Six Sigma` ·
`Manutenção e Confiabilidade` · `Estatística` · `Engenharia de Dados` · `Ciência de Dados`

**Projeto de análise de dados e engenharia da qualidade** para uma fábrica de embalagens
plásticas (frascos soprados, tampas injetadas, decoração por serigrafia e hot stamping). Não é um
exercício de treinamento nem um trabalho de consultoria — é um projeto integrador de **melhoria
contínua**: um time virtual multidisciplinar (Engenharia da Qualidade, Melhoria Contínua,
Engenharia Industrial, Manutenção, Lean Manufacturing, Six Sigma, Estatística, Ciência de Dados,
Análise de Dados e Engenharia de Dados) faz um raio-X completo da fábrica a partir do dataset
Versão 00 (18 meses de produção, qualidade, manutenção, fornecedores e clientes). O time fecha com
uma recomendação de investimento, com prova e controle.

**Está tudo em um único notebook Jupyter**: [`manufacturing_performance_analytics.ipynb`](manufacturing_performance_analytics.ipynb)
(pareado com [`manufacturing_performance_analytics.py`](manufacturing_performance_analytics.py) em
formato jupytext, a fonte editável) é o relatório inteiro — importação e diagnóstico dos dados
brutos, limpeza, carga em um data warehouse SQL Server em arquitetura medalhão (bronze/silver/
gold), controle estatístico de processo, Lean/Seis Grandes Perdas, DMAIC, Teoria das Restrições,
ferramentas avançadas da qualidade (FMEA, MSA/Gage R&R, DOE), confiabilidade (MTBF/MTTR/Weibull),
Índice de Risco Operacional e seis modelos de Machine Learning, tudo em um único documento, na
ordem em que efetivamente acontece — como se faz em um notebook Databricks. Os scripts SQL
aparecem embutidos no notebook (células `%%sql` reais, executadas contra o SQL Server) exatamente
no ponto em que são usados, sem arquivos `.sql` soltos duplicando o mesmo conteúdo.

O notebook segue a ordem cronológica em que o projeto foi construído (Parte 0 a 12), mas também
traz, logo no topo, um segundo índice que agrupa o mesmo conteúdo em seis blocos temáticos —
Production Performance, Quality Analytics, Maintenance Analytics, Process & Machine Analytics,
Customer Quality e Decision Analytics — para quem quer navegar por tema em vez de por ordem
histórica (ver Seção 6 abaixo).

## 1. O time virtual e a pergunta central

**Pergunta central**: *o monitoramento integrado de indicadores de produção, qualidade e
manutenção é capaz de sustentar decisões em tempo real para reduzir perdas e melhorar a
eficiência?*

Mais oito perguntas gerais orientam o raio-X, cada uma respondida com evidência (consulta real +
cálculo + conclusão) no notebook:

1. Qual é o desempenho operacional da fábrica, e quais fatores mais afetam a produtividade e a
   qualidade?
2. Quais máquinas, turnos e operadores mostram mais variação de desempenho e impacto na qualidade?
3. Como os sinais de produção se relacionam com reclamações reais de clientes?
4. A fábrica opera dentro da sua capacidade e estabilidade de processo?
5. Quais são as principais perdas, e onde a melhoria contínua deveria ser priorizada?
6. Quais são os principais gargalos, e onde a melhoria contínua deveria ser priorizada?
7. Como a saúde operacional é monitorada em tempo real?
8. É possível antecipar desvios antes que afetem a produção?

Além dessas, o notebook responde **mais de 80 perguntas de negócio adicionais**, organizadas em
dez seções temáticas (Qualidade, Engenharia de Processo, Produção/Operações, Lean Manufacturing,
Kaizen, Six Sigma/DMAIC, Estatística da Qualidade, Estatística de Produção, Ferramentas Avançadas
da Qualidade, e um bloco complementar de governança de dado/ML/causalidade/síntese) — cada uma
citada literalmente dentro do notebook, imediatamente antes da análise que a responde. Ver a
seção 6 abaixo para o índice completo por Parte.

### 1B. As mesmas perguntas, vistas por área técnica

| Área | Exemplos de pergunta respondida no notebook |
|---|---|
| **Performance industrial** | Qual o OEE da operação e qual componente pesa mais? Onde estão as Seis Grandes Perdas? Qual processo é candidato a restrição de capacidade? |
| **Qualidade** | Quais máquinas/características têm mais variabilidade? O processo é estável (SPC) e capaz (Cpk/Ppk)? O sistema de medição contribui para a variação observada (Gage R&R)? Existe efeito de máquina após controlar o mix de produto? |
| **Manutenção** | Qual o MTBF/MTTR por máquina? Há sinal de desgaste (forma β de Weibull)? A manutenção preventiva atual está associada a menos falha? |
| **Lean Manufacturing** | Onde estão as perdas dominantes por processo? Qual operação tem mais potencial de SMED? Qual o WIP implícito pela Lei de Little? Qual recurso é candidato a restrição (TOC)? |
| **Ciência de Dados** | É possível prever produção/rejeito/falha com validação temporal (`TimeSeriesSplit`, walk-forward)? Existe vazamento de dado (*data leakage*) entre feature e alvo? O modelo supera uma baseline operacional simples? |

## 2. Fonte dos dados

O dataset **Versão 00** — 18 meses (2025-07-01 a 2026-12-30) de produção, parada de máquina,
inspeções de qualidade, reclamações de clientes e não conformidades — está versionado como CSVs em
[`datasets/bronze/`](datasets/bronze/) e é a fonte de dado congelada deste projeto. Ele foi
construído para validar o pipeline analítico (SPC, Six Sigma, Machine Learning) contra causas-raiz
conhecidas e nomeadas (uma máquina com variação de espessura crescente, um molde que desgasta e é
reformado, um operador com alta variabilidade mas sem viés, um fornecedor desproporcionalmente
ruim, episódios completos de refação de lote, e mais), documentadas de ponta a ponta em
[`docs/simulation_storylines.md`](docs/simulation_storylines.md) — permitindo conferir cada achado
do notebook contra uma verdade de referência conhecida. Não é extraído de uma fábrica real; valores
absolutos (R$, OEE%, Cpk) devem ser lidos nesse contexto de validação metodológica, não como
benchmark de uma planta real.

- **Período**: 18 meses, 2025-07-01 a 2026-12-30
- **Escala**: 4 processos, 18 máquinas, 3 turnos, dezenas de milhões de unidades produzidas
  (somadas em ~17.000 ordens de produção)
- **Tabelas**: 22 tabelas fato brutas + 15 dimensões; além das camadas Silver/Gold, o projeto mantém saídas de Machine Learning.
  A contagem física final deve ser lida a partir do DDL/warehouse gerado pelo notebook, evitando que a documentação
  fique defasada quando uma tabela analítica é acrescentada., cobrindo produção, parada, controle
  de qualidade (tampas/frascos/tinta+hot foil), vendas, reclamações, fornecedores e CAPA

## 3. Arquitetura (medalhão: bronze / silver / gold)

| Camada | O que é aqui | Onde vive |
|---|---|---|
| **Bronze** | Bruto, como chegou, deliberadamente sujo (branco disfarçado, grafia mista, linhas duplicadas, quantidades negativas) | `datasets/bronze/*.csv` — **arquivos apenas, nunca carregado no SQL Server** |
| **Silver** | Limpo, conformado, deduplicado, uma linha por evento de negócio | `datasets/silver/*.csv` (Parte 2 do notebook) → SQL Server, consultável como `silver.*` |
| **Gold** | Agregados prontos para negócio: uma linha por (dimensão × período), ou saída de modelo em grão de decisão | Só no SQL Server, `gold.*` |

As tabelas físicas usam o nome `dbo.fact_*_processed`/`dbo.dim_*`; `silver.*` e `gold.*` são views
sobre elas (algumas passthrough 1:1, outras com a janela de 52 semanas móveis ou agregação real) —
todo o DDL, a carga e a criação de views está na Parte 3 do notebook, com o SQL de verdade visível
em células `%%sql` ou como string Python executada, na ordem em que acontece.

Fluxo resumido, do dado bruto à ação corretiva (ver Seções 5A e 6 para o detalhe de cada etapa):

```text
DADOS INDUSTRIAIS (bronze)
        │
        ▼
LIMPEZA E DATA QUALITY (Parte 2)
        │
        ▼
WAREHOUSE SQL SERVER -- silver / gold (Parte 3)
        │
   ┌────┼──────────────┐
   ▼    ▼               ▼
  OEE  QUALIDADE   MANUTENÇÃO (Partes 4-6)
   │    │               │
   └────┼───────────────┘
        ▼
CONTROLE ESTATÍSTICO E CAPACIDADE (Parte 5)
        │
        ▼
INVESTIGAÇÃO DE CAUSA-RAIZ -- Kaizen / TOC / DMAIC / FMEA / DOE (Partes 7-9)
        │
        ▼
AÇÃO CORRETIVA, CONTROLE E VERIFICAÇÃO DE EFICÁCIA (docs/client_root_cause_action_plan.md)
```

## 4. Tecnologias usadas

- **Limpeza e engenharia de features**: Python (pandas, numpy)
- **Banco de dados**: SQL Server (autenticação do Windows), carregado via `pyodbc` com cursor
  `fast_executemany`, SQL embutido no notebook via [`jupysql`](https://jupysql.ploomber.io/)
  (`%%sql`) e via `lib/db_lib.py`
- **Estatística**: Python (scipy, statsmodels, matplotlib/seaborn) — controle estatístico de
  processo, capacidade de processo (Cp/Cpk/Cpm), ANOVA/Tukey, teste de Bartlett, regras de
  sequência de Western Electric, DOE fatorial, Gage R&R — tudo em um único kernel, sem depender de
  R instalado para reproduzir o projeto
- **Machine Learning**: scikit-learn + XGBoost, cada modelo escolhido por `GridSearchCV` sob
  `TimeSeriesSplit` entre três famílias de algoritmo (linear regularizado, Random Forest,
  XGBoost) — nunca um único modelo de hiperparâmetro fixo. SHAP para interpretabilidade de modelo
  de árvore.
- **Controle de versão**: Git

### 4B. Indicadores calculados, por área

| Área | Indicadores |
|---|---|
| **OEE** | Availability, Performance, Quality, `PerformanceVsNominal`, OEE (planta/processo/máquina×produto×turno) |
| **Qualidade** | FPY, RTY (proxy), Defect Rate, Scrap Rate, Cp/Cpk/Pp/Ppk/Cpm, cartas X-barra/R (Western Electric), Pareto, AQL, MSA/Gage R&R |
| **Manutenção** | MTBF, MTTR, frequência de falha, downtime, forma/escala de Weibull, matriz de criticidade MTBF×MTTR |
| **Lean / Eng. Industrial** | Takt time vs. taxa real, cycle time, utilização de capacidade, candidato a restrição (TOC), SMED, VSM, Lei de Little (WIP), Seis Grandes Perdas |

## 5A. Relatório cliente e registro de causas-raiz

A versão pós-auditoria inclui dois artefatos destinados à leitura executiva e à execução das ações:

- [`docs/client_root_cause_action_plan.md`](docs/client_root_cause_action_plan.md) — relatório cliente, com cadeia de evidência, causas-raiz, contenção, correção, prevenção, KPIs e critérios de eficácia.
- [`docs/root_cause_action_register.csv`](docs/root_cause_action_register.csv) — registro estruturado para acompanhamento das ações.
- [`docs/technical_audit_and_methodology.md`](docs/technical_audit_and_methodology.md) — parecer técnico e limites metodológicos pós-auditoria.

A regra de governança é: **não encerrar uma causa apenas porque o KPI melhorou; é necessário demonstrar o mecanismo, a intervenção, a eficácia e o controle de recorrência.**

## 5. Como rodar o projeto

1. Crie/ative o ambiente virtual e instale as dependências:
   ```
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```
2. `.env` na raiz do projeto (já no `.gitignore`) com as configurações de conexão do SQL Server:
   ```
   SQLSERVER_HOST=localhost
   SQLSERVER_DB=ManufacturingPerformanceAnalytics
   SQLSERVER_DRIVER=ODBC Driver 18 for SQL Server
   ```
   O servidor deve rodar com autenticação do Windows (sem usuário/senha necessário) — ajuste
   `lib/db_lib.py` se seu SQL Server usar login SQL.
3. Rode `manufacturing_performance_analytics.ipynb` do início ao fim, uma vez — o notebook cria o
   banco, o schema e as views sozinho (idempotente, seguro para reexecutar). Não é necessário rodar
   nenhum script SQL manualmente antes.

## 6. Estrutura do notebook, Parte por Parte

| Parte | Conteúdo | Papel principal |
|---|---|---|
| 0 | Orientação: SIPOC, time virtual, enquadramento qualitativo do problema (BQ-071) | Gerente da Qualidade |
| 1 | Importar e diagnosticar os dados brutos | Engenheiro(a) de Dados |
| 2 | Limpeza dos dados (Python): produção, paradas, QC, QA | Engenheiro(a) de Processo/Dados |
| 3 | Warehouse SQL Server: schema, DDL, carga, views 52 semanas, camada gold | Engenheiro(a) de Dados |
| 3B | Project Charter: baseline, meta, oportunidade em R$ (BQ-072) | Gerente da Qualidade |
| 4 | Raio-X operacional: OEE (planta, processo, máquina×produto×turno), TPM/Six Big Losses (5 categorias mensuráveis + 1 lacuna de dado), MTBF/MTTR por máquina, matriz de criticidade MTBF×MTTR, custo de indisponibilidade, efetividade de manutenção preventiva, confiabilidade Weibull, utilização, velocidade real vs. ideal, microparadas, VSM (BQ-073), SMED (BQ-074) | Eng. de Processo / Lean / Manutenção |
| 5 | Controle estatístico de processo e capacidade: X-barra/R, Western Electric, Cp/Cpk/Pp/Ppk/Cpm, ANOVA com blocking, Bartlett, AQL, viés de inspetor, FPY, yield, fluxo de qualidade, hotspots de defeito, Machine Effect vs. Product Mix, benchmark interno, OEE escondendo deterioração | Engenheiro(a) da Qualidade / Black Belt |
| 6 | Garantia da qualidade: CPMU, scorecard de fornecedor, Fornecedor→Material→Qualidade a jusante, CAPA, NC→CAPA→Recorrência, Custo da Qualidade, Manufacturing Loss Pareto, rastreabilidade (BQ-075), sinal interno associado a reclamação (Seção 6.9; teste formal de indicador antecedente fica na Parte 10) | Eng. da Qualidade de Fornecedores/Clientes |
| 7 | Kaizen e Teoria das Restrições: ranking de eventos, 5 Porquês, fábrica escondida, restrição de Goldratt (BQ-060) | Especialista em Lean |
| 8 | Six Sigma / DMAIC completo aplicado à IM-002 | Black Belt Six Sigma |
| 9 | Ferramentas avançadas: FMEA (M-SOP-007), MSA/Gage R&R, DOE fatorial, Weibull (P10 exploratório de confiabilidade da SS-001, não uma política de PM) | Eng. da Qualidade / Black Belt |
| 10 | Estatística de produção: defasagens, indicador antecedente, sazonalidade, previsibilidade | Cientista de Dados |
| 11 | Machine Learning: 3 previsões semanais + 3 modelos de risco, auditoria de vazamento (BQ-079) | Cientista de Dados / Eng. de ML |
| 12 | Síntese: as 8 perguntas gerais respondidas juntas, Índice de Risco Operacional, custo da não-qualidade por máquina, recomendação de investimento (BQ-078), controle | Todo o time |

O notebook também traz, no topo, um segundo índice que agrupa o mesmo conteúdo por tema em vez de
por ordem cronológica:

| Bloco | Tema | Onde está |
|---|---|---|
| 01 — Production Performance | OEE (planta, processo, máquina×produto×turno), Seis Grandes Perdas, velocidade real vs. ideal, microparadas, capacidade, SMED | Parte 4 |
| 02 — Quality Analytics | SPC, Western Electric, Cp/Cpk/Pp/Ppk/Cpm, FPY, yield, fluxo de qualidade, hotspots de defeito, Machine Effect vs. Product Mix, benchmark interno | Parte 5 |
| 03 — Maintenance Analytics | MTBF/MTTR por máquina, matriz de criticidade MTBF×MTTR, custo de indisponibilidade, efetividade de PM, confiabilidade Weibull, vida útil de molde | Parte 4; Parte 5 (BQ-016) |
| 04 — Process & Machine Analytics | Machine Effect vs. Product Mix (GLM), confundimento (ANOVA), variação de operador, benchmark interno | Parte 5 |
| 05 — Customer Quality | Rastreabilidade de reclamação, early-warning, scorecard de fornecedor, Fornecedor→Material→Qualidade a jusante, NC→CAPA→Recorrência | Parte 6 |
| 06 — Decision Analytics | Índice de Risco Operacional, custo da não-qualidade por máquina, Manufacturing Loss Pareto financeiro, impacto financeiro, recomendação única | Parte 6; Parte 12 |

Cada Parte cita, literalmente, as perguntas de negócio que responde (identificadas por `BQ-XXX`
quando aplicável) imediatamente antes da análise — não há um documento separado de perguntas: a
pergunta e a resposta vivem juntas, no mesmo lugar, dentro do próprio notebook (ver o índice
completo na primeira célula markdown do notebook).

## 7. Principais resultados

*(Da Parte 12, com base no dataset Versão 00, 18 meses.)*

- **OEE de planta ≈ 79,1%** (agregação ponderada por tempo/capacidade/unidades — Disponibilidade
  87,4%, Performance 92,7%, Qualidade 97,6%) — Disponibilidade é o pilar mais fraco em todo
  processo, ou seja, parada não planejada — não velocidade nem sucata — é o maior gap estrutural
  até a classe mundial (85%).
- **A capacidade de processo é amplamente marginal**: 0% dos 140 grupos máquina×molde×característica
  de tampa cravam Cpk ≥ 1,33 — mesmo restringindo aos grupos que passam no gate de estabilidade
  (causa especial ausente), o Cpk máximo observado continua bem abaixo de 1,33 — não é "tudo capaz,
  com algumas exceções", é uma planta estatisticamente marginal como um todo, com máquinas nomeadas
  (IM-002) mensuravelmente piores que essa linha de base já modesta.
- **Machine Effect sobrevive ao controle de mix de produto**: mesmo controlando material e
  capacidade do produto fabricado (o `ProductId` exato é confundido 1:1 com a máquina, então não dá
  para usá-lo diretamente), a máquina continua explicando a taxa de defeito de forma altamente
  significativa — não é "azar de receber produto difícil".
- **O vínculo entre sinais de produção e reclamações reais é real, mas parcial**: ~67% das
  reclamações rastreáveis vêm de uma ordem com qualidade interna abaixo da mediana; o resto não
  mostra esse sinal — consistente com a dependência de amostragem AQL documentada ao longo do
  projeto. Testado formalmente (não só por um caso), o sinal é estatisticamente real, mas fraco:
  um alerta baseado só em taxa de rejeição interna captura uma fração pequena das reclamações
  futuras.
- **A CAPA reduz não conformidade no teste simples, mas o resultado não sobrevive a uma checagem
  de robustez mais rigorosa**: comparar a contagem de NC antes vs. depois da CAPA (não só se a
  categoria "aconteceu de novo") mostra uma redução estatisticamente significativa — mas boa parte
  das CAPAs fechadas da mesma combinação processo×categoria têm janelas de antes/depois que se
  sobrepõem no calendário, o que pode inflar esse resultado por pseudo-replicação; restrito a uma
  amostra sem essa sobreposição possível, o resultado deixa de ser significativo. Reportado como um
  exemplo de por que uma checagem de robustez pode reverter uma conclusão que parecia sólida no
  teste principal — não como uma CAPA comprovadamente eficaz.
- **Um achado que uma carta de média sozinha perderia por completo**: um operador (OP-INJ-003)
  mostra uma diferença de variância altamente significativa (teste de Bartlett) com um efeito muito
  mais fraco no deslocamento da média do processo — inconsistência, não viés — e o Gage R&R (Parte 9)
  confirma que isso é sinal de processo real, não artefato do instrumento de medição.
- **Um Índice Relativo de Priorização Operacional** (normalizado dentro da própria frota — não uma
  medida probabilística de risco) combina qualidade, manutenção, produção e reclamação de
  cliente num único ranking por máquina — IM-002, ISBM-003 e ISBM-005 lideram o combinado, cada
  uma puxada por um ângulo diferente (cliente, qualidade, manutenção) que um painel só de OEE
  deixaria escondido atrás de métricas mais visíveis.
- **Seis modelos de Machine Learning** transformam o monitoramento histórico em um prospectivo,
  com honestidade sobre onde cada um é forte ou fraco. Previsão de produção é forte (R²≈0,998,
  mas condicionada ao plano de produção informado como feature — não uma previsão de capacidade
  "às cegas"). Manutenção preditiva tem discriminação **fraca/marginal** (ROC-AUC≈0,59, quase
  aleatório; a classe "falha amanhã" é majoritária nos dados, não rara, o que muda a leitura do
  PR-AUC) — o modelo aponta a ISBM-005 como maior risco no último dia de dados, batendo com o
  padrão de causa-raiz documentado para essa máquina (`docs/simulation_storylines.md`), o que
  mostra que o modelo recupera esse sinal conhecido, mas não garante o mesmo desempenho fora deste
  dataset de referência.
- **Uma iniciativa recomendada, com evidência convergente de múltiplas Partes independentes**:
  executar uma corrida de confirmação da condição identificada por um estudo DOE fatorial (Parte 9)
  na IM-002 e, se confirmada, formalizá-la como novo padrão operacional — com controle via
  monitoramento SPC reforçado (Parte 5) e atualização do plano de controle (Parte 9) — pequena em
  R$ isolada, mas a iniciativa mais bem provada deste raio-X.

## 8. Limitações

- **O que este projeto demonstra, e o que não demonstra**: as causas-raiz (IM-002, ISBM-005,
  SS-001, SUP-005, M-SOP-007, OP-INJ-003, etc.) são conhecidas de antemão por construção do dataset
  Versão 00, então o objetivo não é demonstrar descoberta causal independente em dados de uma
  fábrica real — é demonstrar a capacidade do pipeline analítico (estatística, Six Sigma, ML) de
  **recuperar sinais de causa-raiz conhecidos** contra uma verdade de referência (ver Seção 2). Isso
  é uma validação de método legítima e valiosa para portfólio, mas é uma alegação mais estreita do
  que "descoberta causal em produção real" — a distinção importa para quem for avaliar o projeto.
- **Regra editorial deste projeto**: nenhuma conclusão deve ser mais forte do que o método
  estatístico que a sustenta. Onde uma frase do notebook ou deste README ficar mais confiante do
  que a evidência (ex.: "restrição real" quando o dado só sustenta "candidata a restrição sob um
  proxy"; "economia" quando o número é um cenário condicionado a confirmação pendente), a leitura
  correta é a versão mais cautelosa descrita na seção correspondente do notebook, não o título.
- 18 meses de histórico ainda não é suficiente para aprender sazonalidade multi-anual real (a
  Parte 10 decompõe sazonalidade semanal com confiança, mas não anual).
- A decomposição de Custo da Qualidade (Parte 3B/6) usa custos unitários declarados,
  ilustrativos, não dados reais de contabilidade — a *forma* da distribuição é o achado legítimo,
  não os valores absolutos em R$.
- Um dashboard de BI está fora do escopo desta fase — este projeto entrega o notebook (a análise
  completa) e o warehouse; uma camada de dashboard é uma decisão para uma fase posterior.

## 9. Próximos passos recomendados

*(Detalhado com números e evidência na Parte 12.4 do notebook; resumo executivo abaixo.)*

**Melhorias técnicas para a próxima iteração**:
- **Processamento**: migrar o cálculo pesado (OEE, Weibull) de Python/pandas para stored procedures
  SQL ou orquestração (ex.: Databricks Jobs) reduziria footprint de memória e tempo de execução em
  escala de produção.
- **Critério IsCapable**: complementar a classificação atual (baseada no Cpk mais recente) com um
  alerta específico para quedas bruscas de Cpk, não só o valor absoluto.
- **Weibull**: calcular o tempo entre falhas a partir de `RunTimeHours` (horas efetivas de operação)
  em vez de tempo de calendário, para uma forma (β) mais precisa.
- **Custo da Qualidade**: integrar dados financeiros reais, ou ao menos uma taxa de custo-máquina/
  hora real, para que o ROI de melhorias possa ser calculado com precisão (hoje os valores em R$ são
  ilustrativos, ver Seção 8).
- **Six Big Losses**: implementar captura de dado para a perda de "startup/yield", hoje não
  mensurável, fechando a lacuna do framework.
- **Custo de PM**: comparar o custo da manutenção preventiva (mão de obra, peças) com o custo da
  indisponibilidade evitada, para otimizar a frequência de PM.
- **Weibull → política de PM**: traduzir a forma (β) já calculada por máquina em direcionamento de
  manutenção — β > 1 (desgaste, ex.: ISBM-005) favorece manutenção baseada em horas de uso; β ≈ 1
  favorece manutenção condicionada (monitoramento de condição).
- **Modelos de ML → ação**: conectar a previsão à decisão operacional (ex.: o modelo de ScrapRate
  alertando a equipe de qualidade com antecedência sobre um lote de alta probabilidade de sucata),
  não só reportar a métrica de teste.
- **Publicar `etl_lib`, `stats_lib` e `db_lib` como um pacote Python mínimo, com testes unitários** —
  eleva o projeto de "notebook reprodutível" para produto de engenharia de dados.

**Recomendações finais para a fábrica**:
1. **Crítico** — revisar o programa de Manutenção Preventiva: auditar escopo e execução, já que a
   Weibull indica modo de falha predominantemente de desgaste na maioria das máquinas, e a PM atual
   pode não estar atacando esse modo corretamente.
2. **Foco na máquina de maior prioridade combinada** (Índice de Risco Operacional, Parte 12.1b) —
   plano de engenharia específico para o problema identificado, conforme o padrão apurado nesta
   análise.
3. **Iniciativas Lean direcionadas por processo**, não uma solução única — a perda dominante do Six
   Big Losses muda por processo (Parte 4).
4. **Integrar o Data Quality Scorecard ao pipeline de dados**, para monitorar continuamente a
   qualidade do dado de produção.
5. **Validar a acurácia dos modelos antes de qualquer sistema de recomendação**, depois construir um
   loop de ação (ex.: alerta de sucata ~2h antes do resultado final do lote).

## 10. Estrutura do repositório

```
manufacturing_performance_analytics.ipynb   o notebook único -- tudo vive aqui
manufacturing_performance_analytics.py      fonte jupytext (formato "percent") do notebook acima
lib/
  etl_lib.py       limpeza / LotId / OEE / SPC / AQL / QA
  db_lib.py        engine SQL Server + carga em massa + execução de script SQL
  ml_lib.py        split treino/teste, métricas, comparação de modelos, persistência
  stats_lib.py     X-barra/R, regras de Western Electric, Pareto, teste de proporção (Python puro)
datasets/
  bronze/          dados brutos Versão 00 (congelado, versionado -- fonte de dado deste projeto)
  dim/             dimensões que chegam prontas da engenharia (versionado)
  silver/          dados limpos + previsões de ML + resumos JSON entre Partes -- não versionado
                    (regenerado pelas Partes 1-2 do notebook a partir de bronze/)
models/            os 6 modelos de Machine Learning treinados (.pkl)
reports/           todo gráfico gerado pelo notebook, exportado como .png
docs/
  data_dictionary.md         schema e referência de rastreabilidade
  simulation_storylines.md   referência de causas-raiz para validação metodológica
README.md
requirements.txt
.env               configurações de conexão do SQL Server (não versionado)
.gitignore
```

## 11. Autoria

Projeto individual — **Aline Meireles**, Engenharia de Qualidade Industrial | Industrial Data
Analytics | Manufacturing Intelligence | Continuous Improvement.

`Quality Engineering` · `Industrial Analytics` · `Six Sigma` · `Lean Manufacturing` · `SPC` ·
`OEE` · `Data Analytics` · `Python` · `SQL` · `Machine Learning` · `ISO 9001` ·
`Continuous Improvement`

## 12. O que este projeto demonstra

Mais do que construir gráficos e um pipeline SQL, o objetivo é demonstrar a transição de dado bruto
até ação corretiva verificada, integrando as disciplinas do time virtual (Seção 1):

```text
DADO → INFORMAÇÃO → EVIDÊNCIA → DIAGNÓSTICO → CAUSA-RAIZ → AÇÃO → CONTROLE → VERIFICAÇÃO DE EFICÁCIA
```

Com a ressalva editorial da Seção 8: nenhuma conclusão aqui é mais forte do que o método estatístico
que a sustenta, e as causas-raiz recuperadas são conhecidas por construção do dataset sintético —
o que este projeto valida é a capacidade do *pipeline* de recuperá-las, não uma descoberta causal
inédita em dados de fábrica real.

## 13. Pós-auditoria — Versão 01

A Versão 01 incorpora uma auditoria multidisciplinar com foco em rigor de causa-raiz. As principais mudanças são:

- correção da decomposição quantitativa das Six Big Losses para evitar dupla contagem;
- RTY explicitamente tratado como proxy/teórico quando não há rastreabilidade física completa;
- TOC tratado como candidatura à restrição até existir prova de impacto no throughput sistémico;
- FMEA explicitamente classificada como simplificada/orientada por dados;
- linguagem causal separada de associação observacional;
- manutenção reparável tratada com maior cautela na interpretação de Weibull e PM;
- OEE benchmark externo separado da meta interna;
- criação de relatório cliente e registro estruturado de causas-raiz e ações;
- criação de testes automatizados básicos para invariantes críticos do cálculo de OEE/perdas;
- adição de `pyproject.toml` para aproximar o projeto de uma estrutura de engenharia de software reproduzível.
