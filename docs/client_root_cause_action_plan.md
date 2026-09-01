# Relatório Executivo ao Cliente — Diagnóstico de Causas-Raiz e Plano de Ação

**Projeto:** Manufacturing Performance Analytics  
**Versão:** 01 — pós-auditoria multidisciplinar  
**Escopo:** Qualidade, Produção, Lean, Six Sigma, Manutenção/Confiabilidade, Engenharia de Dados e Ciência de Dados

---

## 1. Objetivo do relatório

Este relatório transforma o raio-X analítico em um **registro de causas-raiz e ações**, orientado para decisão. O objetivo não é apenas mostrar quais KPIs estão abaixo da meta, mas responder, para cada problema relevante:

1. **O que está acontecendo?**
2. **Onde acontece?**
3. **Qual mecanismo explica o comportamento?**
4. **Quais hipóteses foram eliminadas?**
5. **Qual é a causa-raiz mais provável/testável?**
6. **O que deve ser feito imediatamente?**
7. **Como comprovar que a ação funcionou?**
8. **Como impedir a recorrência?**

### Regra de evidência

O dataset é **sintético e deliberadamente construído com causas-raiz conhecidas**. Portanto, este documento diferencia explicitamente:

- **Causa-raiz de referência:** mecanismo que foi deliberadamente embutido no dataset para validação metodológica.
- **Evidência analítica:** sinal que o pipeline conseguiu recuperar independentemente.
- **Confirmação de campo:** inspeção, experimento ou validação operacional que seria obrigatória numa fábrica real.

Assim, o relatório não transforma uma verdade conhecida do dataset em uma falsa alegação de diagnóstico de uma fábrica real.

---

# 2. Parecer multidisciplinar consolidado

A equipe virtual conclui que os problemas não devem ser tratados como uma lista de sintomas independentes. Há **quatro mecanismos sistémicos** que se repetem:

### Mecanismo A — Processo fora de controlo/capacidade

Máquinas específicas apresentam dispersão e/ou centralização inadequadas. O caso mais forte é **IM-002**, cuja qualidade é baixa sem deterioração equivalente de disponibilidade. O caminho correto é processo → mecanismo → parâmetro → confirmação experimental → SPC.

### Mecanismo B — Falha de manutenção/reliabilidade e envelhecimento físico

**SS-001** mostra deterioração temporal de frequência e duração das falhas antes do overhaul. **M-SOP-007** mostra aumento de defeitos com exposição/ciclos e recuperação após reforma. A causa não deve ser tratada apenas como “baixa OEE”; deve ser relacionada ao mecanismo físico e ao ciclo de vida do ativo.

### Mecanismo C — Controlo reativo em vez de prevenção/detecção antecipada

A inspeção AQL consegue decidir sobre amostras/lotes, mas não substitui indicadores antecedentes de processo. Em M-SOP-007, um gatilho baseado em ciclos/tendência poderia ter criado uma intervenção antes da refação do lote.

### Mecanismo D — Variabilidade de entrada/matéria-prima e parâmetros ocultos

**SUP-005**, o lote de PP associado a **SS-002** e o índice de velocidade associado a **HF-001** mostram que problemas podem atravessar fronteiras funcionais. O diagnóstico precisa conectar fornecedor → material → processo → defeito → cliente, e não atribuir automaticamente a causa ao operador ou à máquina.

---

# 3. Registro de causas-raiz

| ID | Problema | Local | Causa-raiz de referência | Evidência recuperada | Status de causalidade | Ação prioritária | KPI de eficácia |
|---|---|---|---|---|---|---|---|
| RC-01 | Variabilidade de espessura | ISBM-003 | Instabilidade de programação do parison, com aumento da dispersão e viés para ombro fino | RangeR ≈ 2,6× pares; Cpk/controle e episódio de refação convergem | **Forte; confirmar em campo** | Verificar programação do parison, atuadores/controle, calibração e condição do processo; executar Cpk antes/depois | Cpk, RangeR, taxa de Thickness OOC |
| RC-02 | Flash aumenta com ciclos | IM-004 / molde | Campanhas longas entre setups permitem acumulação de desgaste; risco de Flash cresce com unidades desde setup | Defeito sobe entre mudanças e cai após changeover | **Causalidade de desenho do dataset; confirmável experimentalmente** | Criar contador de ciclos/unidades desde setup; definir limite técnico e inspeção de condição | Flash DPMO vs ciclos; FPY |
| RC-03 | Adhesion spike | SS-002 / FR-007-PP-350 | Janela marginal de resina PP de fornecedor problemático | Defeitos ~8–9× maiores na janela; lote de matéria-prima fora de especificação associado | **Forte associação temporal/material** | Segregar lote, reforçar incoming QC, rastrear lote de resina e executar teste de confirmação por lote | Adhesion DPMO por material/lote |
| RC-04 | Foil Transfer em alta velocidade | HF-001 | Velocidade elevada reduz janela de processo e aumenta defeito de transferência | Correlação com menor ActualCycleTimeSec e reject rate superior | **Evidência experimental/sintética; confirmar parâmetro em linha** | Registrar velocidade real por ordem; definir janela operacional e alarmes | Foil Transfer DPMO vs velocidade |
| RC-05 | Short Shot / Weight | IM-002 | Banda de aquecimento marginal; combinação de temperatura e velocidade inadequada | IM-002 com pior qualidade; DOE mostra efeitos de temperatura, velocidade e interação; MSA adequado | **Mais forte evidência causal do projeto; confirmação independente pendente** | Corrida de confirmação DOE; atualizar parâmetros e plano de controle somente após replicação | Short Shot %, Cpk Weight, FPY |
| RC-06 | Muitas paradas, qualidade normal | ISBM-005 | Envelhecimento hidráulico | Frequência de paradas ≈2,3× baseline; rejeição próxima da frota | **Forte associação de manutenção** | Inspeção hidráulica, análise de condição, plano de componentes críticos e exposição por horas | MTBF, MTTR, disponibilidade |
| RC-07 | Confiabilidade em queda | SS-001 | Desgaste de rolete/rasqueta + backlog de manutenção | Frequência e MTTR sobem até 2026-07; overhaul reduz ambos | **Forte evidência temporal; confirmar modo físico** | Inspeção mecânica; eliminar backlog; PM por condição/modo de falha; confirmar 6 meses | MTBF, MTTR, falhas/100 h |
| RC-08 | Prémio de defeito no turno 2 | Todos | Multiplicador de fadiga/handover no dataset | Rejeição ≈2,9% vs ~2,2%/2,4% | **Associação; mecanismo operacional requer validação** | Estudar handover, carga, pausas, staffing, parâmetros e supervisão; não culpar operador sem estudo | FPY por turno ajustado por produto/máquina |
| RC-09 | 8 refações de lote | Vários | Episódios deliberadamente construídos em torno das causas RC-01..RC-07 | Reemissão de lote após rejeição, mesma rota, condições corretivas | **Forte como validação do dataset** | Eliminar causas upstream; rastrear custo de refação como métrica de fábrica escondida | Rework rate, redo hours, redo units |
| RC-10 | Variabilidade de medição/execução do operador | OP-INJ-003 | Alta dispersão, não viés de média | RangeR ≈2× pares; média semelhante | **Forte evidência de variabilidade; não de viés** | Treino/standard work e estudo de método; verificar ergonomia e técnica; repetir Gage R&R por característica se necessário | RangeR, FPY, variação intra-subgrupo |
| RC-11 | Fornecedor desproporcionalmente ruim | SUP-005 | Processo de fornecimento com maior probabilidade de lote fora de especificação | Rejeição de incoming muito superior aos pares e complaints maiores | **Forte associação fornecedor→entrada** | Supplier CAPA, auditoria de processo, plano de contingência e critério de aprovação/descredenciamento | Incoming FPY, PPM/OOS, complaints |
| RC-12 | Mold wear | M-SOP-007 | Desgaste acumulado do molde com ciclos; reforma reinicia condição | Flash/Leakage crescem com exposição e caem após reforma | **Forte evidência de mecanismo no dataset** | Manutenção baseada em condição/ciclos; indicador antecedente; reforma preventiva por condição | Defect rate vs ciclos, Cpk, RPN/AP |
| RC-13 | Parâmetro oculto | HF-001 / Injeção | Velocidade de linha/ciclo influencia throughput e qualidade, mas não é registrada | Relação recuperada por ActualCycleTimeSec | **Causa de governança de dado + processo** | Instrumentar velocidade/pressão/temperatura por ordem e timestamp | Cobertura de parâmetros, alarmes, FPY |
| RC-14 | Reclamações parcialmente explicadas | Clientes | Apenas parte das reclamações nasce de escapes de qualidade; restante é logística/outros | Rastreabilidade mostra mistura de causas | **Forte evidência de heterogeneidade** | Classificar complaint taxonomy e ligar cada reclamação a lote/ordem/defeito/cliente | CPMU por categoria; % complaints rastreáveis |

---

# 4. Plano de ação por causa-raiz

## RC-01 — ISBM-003: instabilidade de espessura

**Hipótese de mecanismo:** instabilidade do programa do parison/controle de espessura.

### Contenção
- Segregar lotes recentes da ISBM-003 quando Thickness estiver fora de controlo.
- Aumentar frequência de verificação somente enquanto a causa estiver sendo tratada.
- Não substituir contenção por inspeção permanente: o objetivo é voltar ao controlo do processo.

### Correção
1. Verificar programação do parison e consistência dos perfis.
2. Verificar atuadores, sensores e resposta do controlador.
3. Confirmar condição mecânica do cabeçote e componentes associados.
4. Comparar Cpk e RangeR antes/depois.

### Critério de eficácia
- processo sob controlo;
- Cpk ≥ critério definido pelo cliente para a característica;
- ausência de tendência de aumento de RangeR por janela operacional;
- sustentação por pelo menos 3–6 meses ou quantidade de subgrupos previamente definida.

### Prevenção
Adicionar indicador de tendência de RangeR/Cpk ao plano de controlo e manutenção.

---

## RC-02 — IM-004: Flash versus ciclos

O indicador mais importante não é “mês”. É:

> **unidades/ciclos acumulados desde o último setup/reforma.**

### Ação
Criar um contador de exposição do molde:

`CiclosDesdeSetup → Flash DPMO → condição do molde`

### Gatilho recomendado
O limite não deve ser escolhido por conveniência. Deve ser estimado a partir da curva defeito × ciclos e confirmado em campo.

### Controle
- contador automático;
- inspeção de condição antes do limite;
- plano de troca/reforma baseado em condição;
- SPC do defeito.

---

## RC-03 — SS-002 / SUP-005: Adhesion

### Causa-raiz
Entrada de matéria-prima marginal combinada com sensibilidade do processo de decoração.

### Ação
O problema deve ser atacado em **duas barreiras**:

**Fornecedor:**
- CAPA de fornecedor;
- auditoria;
- especificação e critério de aceitação;
- rastreabilidade de lote.

**Processo:**
- confirmação do efeito do lote de PP em Adhesion;
- controle de parâmetros de serigrafia;
- segregação de lotes de risco.

### Não fazer
Não concluir que “a serigrafia é ruim” apenas porque o defeito apareceu nela. A evidência aponta para uma interação entrada × processo.

---

## RC-04 — HF-001: velocidade e transferência de foil

### Causa-raiz
Janela de processo estreita em alta velocidade.

### Ação
Instrumentar a velocidade real por ordem. A `ActualCycleTimeSec` é um excelente proxy retrospectivo, mas não deve continuar sendo o único registro.

### Controle
Definir:

`Velocidade → Foil Transfer DPMO`

com limite operacional validado experimentalmente.

---

# 5. RC-05 — IM-002: principal caso de causa-raiz comprovável

Esta é a recomendação técnica central do projeto.

## Evidências convergentes

1. IM-002 aparece como hotspot de qualidade.
2. A disponibilidade não explica o problema.
3. O efeito de máquina permanece após controle do mix.
4. MSA/Gage R&R é adequado para Weight.
5. DOE mostra efeitos de temperatura e velocidade e interação entre elas.
6. O melhor cenário experimental reduz a taxa de Short Shot de aproximadamente **1,35% para 0,11%** dentro do experimento.

## Interpretação correta

Isso é **evidência experimental de efeito causal dentro do domínio estudado**, mas ainda não é prova de sustentabilidade em produção.

## Plano de ação

### Fase 1 — confirmação
Executar corrida independente, fora das observações usadas no DOE.

### Fase 2 — estabilidade
Após confirmar o parâmetro:
- repetir em diferentes ordens;
- verificar produtos representativos;
- monitorar Cpk/Weight;
- monitorar Short Shot;
- verificar interação com lote de material.

### Fase 3 — padronização
Somente depois da confirmação:
- atualizar standard work;
- atualizar plano de controlo;
- atualizar FMEA;
- criar limite de reação;
- treinar operadores/manutenção/processo.

### Fase 4 — sustentação
SPC + auditoria de parâmetros + revisão periódica do Cpk.

---

# 6. RC-06 / RC-07 — manutenção e confiabilidade

## ISBM-005

O problema é predominantemente de disponibilidade, não de qualidade.

**Não atacar com mais inspeção de produto.**

Atacar com:
- análise hidráulica;
- inspeção de condição;
- histórico de componentes;
- horas de operação;
- MTBF/MTTR;
- criticidade do ativo.

## SS-001

A evidência temporal é mais forte do que a Weibull isolada.

O padrão é:

`desgaste/backlog → frequência de falha ↑ + MTTR ↑ → overhaul → frequência/MTTR ↓`

### Ação
- eliminar backlog;
- identificar modos de falha dominantes;
- substituir inspeção calendarizada genérica por PM orientada ao modo de falha;
- acompanhar falhas por 100 horas de operação;
- usar NHPP/Crow-AMSAA se a análise de tendência de falhas continuar sendo necessária.

### Importante
A análise de `DaysSincePM` não demonstrou efeito estatístico. Isso **não prova que PM seja inútil**; indica que a eficácia da PM não pode ser inferida por esse indicador isolado.

---

# 7. RC-10 — OP-INJ-003: variabilidade sem viés

A causa não deve ser descrita como “operador defeituoso”.

O sinal é:

> **RangeR alto com média semelhante.**

Isso caracteriza maior variabilidade intra-subgrupo.

### Ação
- observar execução do standard work;
- verificar método de medição e sequência de operação;
- verificar ergonomia;
- observar handover;
- repetir estudo por característica crítica.

### Critério
Reduzir RangeR sem deslocar a média do processo.

---

# 8. RC-11 — SUP-005: ação de fornecedor

### Contenção
- reforço temporário de incoming inspection;
- segregação de lotes;
- bloqueio conforme critérios de especificação.

### Correção
Supplier CAPA deve atacar:
- causa de OOS;
- controle de processo do fornecedor;
- capacidade do fornecedor;
- rastreabilidade de lote.

### Prevenção
Scorecard com:
- PPM/OOS;
- taxa de aprovação;
- severidade;
- recorrência;
- lead time de CAPA.

O descredenciamento deve ser baseado em critérios previamente aprovados e em tamanho amostral suficiente.

---

# 9. RC-12 — M-SOP-007: modelo de manutenção baseado em condição

Este caso é o melhor exemplo de **Quality + Maintenance + Data** trabalhando juntos.

### Sinal
Defeitos `Flash/Leakage` crescem com exposição do molde e caem após reforma.

### Mudança recomendada
Sair de:

> “inspecionar quando o lote apresentar problema”

para:

> “monitorar exposição + tendência + condição e agir antes do escape”.

### Novo indicador

`CiclosDesdeReforma`

com:
- limite de alerta;
- limite de ação;
- inspeção de condição;
- registro da reforma;
- reset automático do contador.

---

# 10. Lean — prioridades por processo

Não existe uma única Six Big Loss dominante para toda a fábrica.

A regra de decisão deve ser:

> **Perda dominante do processo × custo × frequência × facilidade de eliminação × efeito no cliente.**

### Kaizen
Cada evento deve ter:

**Problema → causa → contramedida → métrica → prazo → dono → confirmação.**

Evitar Kaizen baseado somente em brainstorming sem validação de dados.

---

# 11. TOC — como confirmar o verdadeiro gargalo

A utilização de capacidade identifica **candidatos à restrição**, não prova sozinha a restrição.

Para confirmar:

1. identificar recurso com menor folga;
2. verificar WIP antes/depois;
3. verificar starvation/blocking;
4. medir throughput do sistema;
5. testar se elevar o recurso aumenta o throughput global.

Portanto, Injection Molding é a **principal candidata** sob o proxy de utilização, mas a confirmação deve usar throughput sistémico.

---

# 12. OEE — interpretação gerencial

OEE médio ≈ **79,1%** é uma linha de base útil.

A referência de 85% deve ser tratada como **benchmark externo de contexto**, não como lei universal nem como meta obrigatória.

A prioridade deve ser:

1. melhorar a perda dominante;
2. validar impacto no OEE;
3. comparar com histórico interno;
4. somente depois comparar com benchmark externo.

---

# 13. Six Big Losses — regra quantitativa corrigida

A versão corrigida evita dupla contagem:

### Perda de velocidade

`Runtime × (1 − Performance)`

### Perda de qualidade

`Runtime × Performance × (1 − Quality)`

Assim, a perda de qualidade é calculada sobre a capacidade efetivamente produzida no nível de performance observado.

As duas são **horas equivalentes de capacidade**, não horas físicas adicionais de parada.

A perda de startup continua como lacuna de instrumentação até existir dado específico.

---

# 14. RTY — interpretação corrigida

O RTY calculado no projeto é um **RTY proxy/teórico**.

Ele é útil para mostrar o efeito multiplicativo de perdas de primeira passagem, mas não deve ser apresentado como rendimento físico comprovado do produto final sem rastreabilidade das mesmas populações/rotas.

Para transformar em RTY operacional real:

`Lote/Unidade → Sopro → Decoração → Tampa → Produto Final`

precisa ser rastreável de forma consistente.

---

# 15. Custo da Qualidade — decisão financeira

O valor de aproximadamente **R$ 2,52 milhões** é um **modelo ilustrativo sob premissas de custo**, não custo contabilístico da fábrica.

O número de Avaliação é grande porque o projeto usa o volume de amostragem como proxy de custo.

### Não concluir
> “A fábrica gasta 45,4% do faturamento em qualidade.”

### Concluir
> “Sob as premissas económicas ilustrativas do modelo, o CoQ equivale a aproximadamente 45,4% do faturamento do período.”

Para investimento real, integrar:
- custo de mão de obra;
- laboratório;
- inspeção;
- equipamento;
- sucata;
- retrabalho;
- devolução;
- frete;
- atendimento de reclamação;
- garantia;
- custo de oportunidade.

---

# 16. Machine Learning — papel correto

Os modelos devem ser tratados como **sistemas de apoio à decisão**, não como substitutos da engenharia.

### Produção
R² alto representa previsão **condicional ao plano**, não previsão autónoma de demanda.

### Manutenção preditiva
ROC-AUC ≈ 0,593 é fraco; não justifica implantação autónoma.

### Qualidade de lote
ROC-AUC ≈ 0,689 e baixo recall no threshold padrão indicam uso como **ranking/triagem**, não bloqueio automático.

### Governança
Antes de produção:
- baseline;
- validação temporal;
- threshold económico;
- drift;
- recalibração;
- monitoramento de falso positivo/falso negativo.

---

# 17. Plano integrado 30–60–90 dias

| Horizonte | Ações | Resultado esperado |
|---|---|---|
| 0–30 dias | Confirmar IM-002; inspeção ISBM-003; inspeção SS-001; contenção SUP-005; instrumentar ciclos M-SOP-007 | Contenção e confirmação das hipóteses principais |
| 31–60 dias | DOE/parametrização IM-002; ação de fornecedor; manutenção por modo de falha; contador de ciclos; revisão dos planos de controlo | Causas tratadas e controles preventivos implantados |
| 61–90 dias | SPC sustentado; auditoria de eficácia; atualização FMEA; revisão de PM; dashboard de causa-raiz; ML em shadow mode | Sustentação e prevenção de recorrência |

---

# 18. Matriz de governança

| Ação | Qualidade | Produção | Manutenção | Lean/Six Sigma | Dados |
|---|---|---|---|---|---|
| IM-002 DOE | A/R | R | C | A/R | C |
| ISBM-003 espessura | A/R | R | C | C | C |
| M-SOP-007 | A/R | C | A/R | C | R |
| SS-001 | C | C | A/R | C | R |
| SUP-005 | A/R | C | - | C | R |
| HF-001 | R | A/R | C | C | A/R |
| SPC | A/R | R | C | A | R |
| ML | C | C | C | C | A/R |

**A = Accountable; R = Responsible; C = Consulted.**

---

# 19. Critérios para encerrar uma causa-raiz

Nenhuma causa deve ser considerada encerrada apenas porque o KPI melhorou.

O encerramento exige:

1. **Causa física/processual definida.**
2. **Evidência pré-ação.**
3. **Ação corretiva implementada.**
4. **Resultado melhor que baseline.**
5. **Teste estatístico ou desenho temporal adequado quando aplicável.**
6. **Ausência de efeito adverso em CTQs relacionados.**
7. **Controle atualizado.**
8. **Responsável definido.**
9. **Janela de eficácia cumprida.**
10. **Risco de recorrência reavaliado.**

---

# 20. Parecer final ao cliente

A análise integrada não aponta para uma única “causa da fábrica”. Ela aponta para **causas-raiz específicas e mecanismos diferentes**, que exigem contramedidas diferentes.

As prioridades mais fortes são:

### 1. IM-002 — processo/parametrização
É o caso com maior nível de evidência causal porque MSA, análise de máquina/mix e DOE convergem para o mesmo mecanismo.

### 2. ISBM-003 — estabilidade do processo
A dispersão de espessura é suficientemente anormal para justificar investigação física da programação do parison e confirmação de Cpk/RangeR.

### 3. SS-001 — confiabilidade/manutenção
O padrão temporal de degradação seguido de recuperação após overhaul é forte evidência de problema de condição/manutenção.

### 4. M-SOP-007 / IM-004 — desgaste dependente de exposição
A organização da manutenção deve migrar de inspeção reativa para condição/ciclos/tendência.

### 5. SUP-005 — qualidade de entrada
O fornecedor é uma causa upstream que pode gerar problemas downstream e deve ser tratado com Supplier CAPA, não somente com inspeção adicional na fábrica.

### 6. Governança de dados/processo
Parâmetros críticos hoje inferidos retrospectivamente devem ser registrados no momento em que ocorrem.

## Conclusão

O principal ganho deste projeto não é o dashboard. É a capacidade de transformar sinais dispersos em uma **cadeia de evidência que começa no sintoma, elimina confundidores, identifica o mecanismo, propõe um teste de confirmação e termina num controle preventivo**.

A recomendação da equipe é **não financiar dezenas de ações simultaneamente**. Deve-se executar primeiro a confirmação e correção das causas com maior força de evidência e impacto operacional, principalmente IM-002, ISBM-003, SS-001, M-SOP-007 e SUP-005, enquanto se fecha a instrumentação necessária para tornar os próximos diagnósticos ainda mais causais e menos dependentes de proxies.

> **Princípio de decisão:** não corrigir o KPI; corrigir o mecanismo que produz o KPI.
