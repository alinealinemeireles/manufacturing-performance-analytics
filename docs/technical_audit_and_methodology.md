# Auditoria Técnica Pós-Correção — Manufacturing Performance Analytics

## Parecer

**Aprovado com correções incorporadas — versão 01.**

A auditoria foi estruturada como uma revisão multidisciplinar envolvendo Engenharia da Qualidade, Engenharia Industrial, Manutenção/Confiabilidade, Lean Manufacturing, Six Sigma, Engenharia de Dados e Ciência de Dados.

## Correções incorporadas

1. **Six Big Losses:** perda de qualidade corrigida para `Runtime × Performance × (1 − Quality)`; evita dupla contagem com perda de velocidade. *(Nota de atualização: esta correção originalmente só cobria o gráfico da Parte 4.7 — `gold.six_big_losses_monthly` carregava a fórmula antiga com dupla contagem. Ver [`post_fix_independent_audit.md`](post_fix_independent_audit.md) para a correção que unificou as duas superfícies em `lib/etl_lib.py::compute_six_big_losses`.)*
2. **RTY:** renomeado conceitualmente como proxy/teórico, condicionado à independência e compatibilidade das populações/rotas.
3. **TOC:** utilização de capacidade passou a ser explicitamente um **proxy para candidatura à restrição**; restrição sistémica exige confirmação por throughput/WIP/starvation/blocking.
4. **FMEA:** caracterizada como análise FMEA simplificada/orientada por dados; não é apresentada como reprodução integral da metodologia AIAG-VDA.
5. **CoQ:** valores são explicitamente modelos económicos ilustrativos, não contabilidade industrial.
6. **Causalidade:** associações observacionais foram reescritas como associações; linguagem causal foi reservada a desenho experimental ou evidência convergente compatível com mecanismo.
7. **Manutenção:** a conclusão sobre SS-001 passou a priorizar tendência temporal + overhaul; Weibull isolada não é usada para declarar desgaste em equipamento reparável.
8. **PM:** ausência de associação entre `DaysSincePM` e falhas não é interpretada como prova de ineficácia da PM.
9. **OEE:** 85% passou a ser benchmark externo contextual, não meta universal.
10. **Performance >100%:** permanece visível via `PerformanceVsNominal`; o OEE utiliza performance limitada a 100% para preservar a interpretação clássica do indicador.
11. **Documentação:** README atualizado e relatório de causa-raiz/plano de ação adicionado.
12. **Engenharia de Dados:** adicionado caminho para testes automatizados e estrutura de pacote na próxima evolução.

## Limitações que permanecem deliberadamente declaradas

- Dataset sintético; causas-raiz de referência são conhecidas por construção.
- Ausência de rastreabilidade unitária completa limita RTY físico.
- Ausência de pedidos recebidos limita inferências sobre sistema puxado/push.
- Exposição de manutenção deve migrar de tempo calendário para horas de operação/ciclos.
- Alguns modelos ML são de apoio/triagem e não estão prontos para automação autónoma.
- CoQ usa premissas de custo e requer integração financeira para ROI real.

## Critério de qualidade do relatório

Uma conclusão é considerada robusta quando:

`Dado → Medida correta → Controle de confundimento → Teste/efeito → Mecanismo → Ação → Verificação → Controle`

Se algum elo estiver ausente, a conclusão é classificada como hipótese, associação ou proxy, e não como causa-raiz confirmada.
