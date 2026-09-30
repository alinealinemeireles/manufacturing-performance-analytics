import datetime as dt
from sgalib import *
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None

# Estado das ações no fecho do ano (31/12/2026): (evolução, data de fecho[, resultado da eficácia, data da avaliação])
# As ações com prazo até 31/12/2026 foram concluídas (algumas com atraso), exceto PAM-26-28 e PAM-26-35 (atrasadas).
FECHO_2026 = {
    "PAM-26-01": (1, "2026-12-15"), "PAM-26-02": (1, "2026-12-15"), "PAM-26-03": (1, "2026-10-28", "Eficaz", "2026-12-10"),
    "PAM-26-05": (1, "2026-10-29", "Eficaz", "2026-12-15"), "PAM-26-06": (1, "2026-10-30", "Eficaz", "2026-12-20"),
    "PAM-26-07": (1, "2026-10-06", "Eficaz", "2026-12-10"), "PAM-26-08": (1, "2026-11-10", "Eficaz", "2026-12-10"),
    "PAM-26-09": (1, "2026-12-18"), "PAM-26-10": (1, "2026-12-22"), "PAM-26-11": (0.75, ""), "PAM-26-12": (0.5, ""), "PAM-26-13": (0.25, ""),
    "PAM-26-14": (0.25, ""), "PAM-26-15": (1, "2026-10-14", "Eficaz", "2026-12-05"), "PAM-26-16": (1, "2026-12-20"), "PAM-26-17": (1, "2026-11-25"),
    "PAM-26-18": (0.75, ""), "PAM-26-19": (1, "2026-10-20", "Eficaz", "2026-12-05"), "PAM-26-20": (1, "2026-10-23", "Eficaz", "2026-11-20"),
    "PAM-26-21": (1, "2026-12-11", "Eficaz", "2026-12-11"), "PAM-26-22": (0.25, ""), "PAM-26-23": (0.5, ""), "PAM-26-24": (0.25, ""),
    "PAM-26-25": (1, "2026-12-18"), "PAM-26-26": (1, "2026-12-04"), "PAM-26-27": (1, "2026-09-29", "Eficaz", "2026-11-30"), "PAM-26-28": (0.75, ""),
    "PAM-26-29": (0.5, ""), "PAM-26-30": (1, "2026-12-10"), "PAM-26-31": (1, "2026-12-17"), "PAM-26-32": (1, "2026-10-27", "Eficaz", "2026-12-15"),
    "PAM-26-33": (1, "2026-10-30"), "PAM-26-34": (1, "2026-11-27"), "PAM-26-35": (0.75, ""),
}

FONTES = ["Análise SWOT", "Matriz de Riscos e Oportunidades", "Matriz de Aspetos Ambientais", "Tabela de Legislação", "Política Ambiental",
          "Objetivos Ambientais", "Reclamações / partes interessadas", "Ronda Ambiental Mensal", "Auditoria Interna", "Revisão pela Gestão",
          "Monitorização e Medição", "Caixa de Sugestões / Kaizen", "Incidente / Emergência"]

# (ID, N_mod, Abertura, Fonte, ID_Origem, Plano_Ant, Ocorrencia, Investigacao, Causa_Raiz, Cat6M, Acao, Tipo, Hierarquia,
#  Resp, Inicio, Prazo, Evol, Fecho, ImpRisco, ID_RO, Custo, Poupanca, BenefTxt, BenefQ, BenefU, Eficacia, DataEf, ResEf, Atv)
PAM = [
    ("PAM-26-01", "01/26", "2026-06-15", "Objetivos Ambientais", "OBJ-01", "Não",
     "Consumo específico de eletricidade elevado (≈ 110 kWh/1.000 un); o ar comprimido representa ≈ 14% da energia, com fugas audíveis e pressão de rede de 7,5 bar.",
     "1. Porquê consumo alto no ar comprimido? Compressores em carga mesmo com poucas máquinas a trabalhar.\n2. Porquê? Fugas na rede ≈ 25% do caudal (teste de vazio ao fim de semana).\n3. Porquê não são reparadas? Só se reparam as fugas audíveis, quando alguém se queixa.\n4. Porquê? A manutenção preventiva não inclui a rede de ar e não há indicador que mostre a perda.",
     "Ausência de um programa de gestão de fugas e de indicador do ar comprimido.", "Método",
     "Campanha trimestral de deteção de fugas por ultrassom (etiquetar e reparar em ≤ 15 dias), reduzir a pressão de 7,5 para 6,8 bar e instalar variador de velocidade no compressor CMP-02.",
     "M", "Engenharia", "Gerente de Manutenção", "2026-07-01", "2026-12-31", 0.25, "", "Sim", "RO-02", 14000, 24500,
     "Menos energia no ar comprimido", 175, "MWh/ano",
     "Eficaz se as fugas em teste de vazio forem < 10% do caudal e o KPI-01 ≤ 106 kWh/1.000 un em média no 1.º trimestre de 2027.", "2027-04-15", "Por avaliar", "3.5 (ação 1 — objetivo)"),
    ("PAM-26-02", "02/26", "2026-04-20", "Matriz de Riscos e Oportunidades", "RO-02", "Não",
     "Risco significativo RO-02 (nível -6): sem submedição de energia e água, o desempenho e a eficácia das ações não são demonstráveis.",
     "1. Porquê não sabemos o consumo por processo? Só há contador geral.\n2. Porquê? O projeto elétrico original não previa submedição.\n3. Porquê nunca foi instalada? Nunca foi orçamentada.\n4. Porquê? O benefício não era visível sem dados (círculo vicioso).",
     "Falta de infraestrutura de medição por processo (decisão de investimento adiada).", "Medição",
     "Instalar 6 analisadores de energia (Injeção, Sopro, Decoração, Compressores, Arrefecimento, Geral) e 3 contadores de água com telemetria, ligados ao Power BI; procedimento de validação mensal (fatura vs soma dos submedidores).",
     "M", "Engenharia", "Gerente de Manutenção", "2026-06-01", "2026-12-31", 0.50, "", "Sim", "RO-02", 24000, 0,
     "Dados por processo para gerir energia e água", None, "",
     "Eficaz se ≥ 90% do consumo tiver submedição e a diferença fatura vs soma dos submedidores for ≤ 3% durante 3 meses.", "2027-03-31", "Por avaliar", "3.5 (ação 2 — risco)"),
    ("PAM-26-03", "03/26", "2026-09-10", "Tabela de Legislação", "LEG-05", "Não",
     "NC legal: não existe avaliação acústica após a substituição dos compressores (fev/2026); a última (2023) já não representa o funcionamento noturno.",
     "1. Porquê não há avaliação? Ninguém a pediu após a troca dos compressores.\n2. Porquê? A alteração foi tratada só como investimento técnico.\n3. Porquê? O pedido de alteração não tem checklist ambiental/legal.\n4. Porquê? A gestão de mudanças (6.3) ainda não está implementada.",
     "Controlo de mudanças sem avaliação de requisitos ambientais e legais.", "Método",
     "Contratar avaliação acústica (critério de incomodidade, período noturno) a laboratório acreditado.",
     "C1", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-15", "2026-10-31", 0.50, "", "Sim", "RO-12", 1800, 0,
     "Confirmação da conformidade acústica", None, "",
     "Eficaz se o relatório demonstrar o cumprimento do critério de incomodidade noturno ou, se não cumprir, for aberta ação C2 com atenuação.", "2026-11-15", "Por avaliar", "—"),
    ("PAM-26-04", "04/26", "2026-09-15", "Ronda Ambiental Mensal", "NC-SGA-26-03", "Não",
     "Kit antipoluição da zona de injeção/serigrafia com selo quebrado, praticamente vazio e sem registo de utilização.",
     "Ver investigação em PAM-26-05 (5 porquês).", "Ausência de regra de reporte e reposição após uso do kit.", "Método",
     "Repor imediatamente o kit (absorventes, barreiras, luvas, sacos), selar com selo numerado, inspecionar a zona para vestígios de derrame e encaminhar os absorventes usados como 15 02 02*.",
     "C1", "Administrativa", "Responsável de Armazém e Logística", "2026-09-15", "2026-09-16", 1.0, "2026-09-16", "Sim", "RO-10", 180, 0,
     "Capacidade de resposta a derrames reposta", None, "",
     "Eficaz se o kit estiver completo e selado na verificação de 22/09/2026.", "2026-09-22", "Eficaz", "6.1 (Tarefa 2 — C1)"),
    ("PAM-26-05", "05/26", "2026-09-15", "Ronda Ambiental Mensal", "NC-SGA-26-03", "Não",
     "Kit antipoluição com selo quebrado, vazio e sem registo de utilização (derrame não reportado).",
     "1. Porquê o kit está vazio? Foi usado para conter um derrame e não foi reposto.\n2. Porquê não foi reposto? O utilizador não informou o armazém nem o SGA.\n3. Porquê não informou? A IT-SGA-01 termina na limpeza: não diz que é preciso registar e pedir reposição.\n4. Porquê a IT não prevê? Foi escrita só para a resposta; não há responsável pela reposição nem stock mínimo.\n5. Porquê não foi detetado antes? A ronda só verificava a presença do kit (não o selo nem o conteúdo) e a formação de derrames só ensinou a usar o kit.",
     "Falha de procedimento (IT-SGA-01 sem etapa pós-uso, sem stock mínimo nem responsável pela reposição) e de formação (ciclo pós-utilização não ensinado).", "Método",
     "1) Rever IT-SGA-01: passo obrigatório pós-uso (registar incidente, pedir reposição, selar). 2) Stock mínimo de 2 kits no armazém com ponto de encomenda. 3) Selo numerado e verificação semanal do conteúdo na ronda (RON-06). 4) Formação toolbox de 15 min nos 3 turnos, com exercício prático.",
     "C2", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-17", "2026-10-31", 0.25, "", "Sim", "RO-10", 950, 0,
     "Resposta eficaz a derrames; incidentes rastreados", None, "",
     "Eficaz se, em 3 rondas mensais consecutivas, 100% dos kits estiverem completos e selados e 100% das utilizações tiverem registo de incidente.", "2027-01-31", "Por avaliar", "6.1 (Tarefa 2 — C2)"),
    ("PAM-26-06", "06/26", "2026-09-18", "Caixa de Sugestões / Kaizen", "KZ-01", "Não",
     "Oportunidade de melhoria: na pausa de refeição do turno 3 (80 min, sem equipa de rendição) as máquinas de injeção e sopro ficam aquecidas e em vazio.",
     "Hábito: manter a máquina quente para arrancar mais depressa; não existe modo standby padronizado.", "Rotina de pausa não padronizada.", "Método",
     "1) Definir o modo standby por máquina (resistências a 60%, bomba hidráulica desligada, chiller em modo eco). 2) Etiqueta 'Pausa 3.º turno' no painel. 3) Checklist de pausa assinado pelo chefe de turno. 4) Medir a poupança com a submedição (PAM-26-02).",
     "M", "Administrativa", "Gerente de Produção", "2026-10-01", "2026-11-30", 0.0, "", "Não", "", 300, 3700,
     "Menos energia em vazio (≈ 2,9 tCO2e/ano)", 26, "MWh/ano",
     "Eficaz se ≥ 90% das pausas do turno 3 tiverem standby registado e a poupança medida for ≥ 1.500 kWh/mês.", "2027-02-28", "Por avaliar", "6.2 (Tarefa 2 — M)"),
    ("PAM-26-07", "07/26", "2026-09-08", "Monitorização e Medição", "MED-06", "Não",
     "Desvio: consumo de solvente de limpeza na serigrafia +15% em jun–ago/2026 face a mar–mai/2026, com produção estável.",
     "Hipóteses em RG-SGA-13 (folha Analise_Desvio_5_2).", "Em investigação.", "Método",
     "Conter e investigar: pesagem diária do solvente por máquina e turno; fechar e identificar todos os recipientes; observar a limpeza nos 3 turnos; conferir inventário e compras de jun–ago.",
     "C1", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-08", "2026-09-30", 0.75, "", "Sim", "", 0, 0,
     "Travar a subida do consumo e das emissões de COV", None, "",
     "Eficaz se as causas forem confirmadas com dados até 30/09/2026 e o consumo diário voltar a ≤ 0,165 kg/1.000 peças.", "2026-10-15", "Por avaliar", "5.2 (Parte 1)"),
    ("PAM-26-08", "08/26", "2026-09-23", "Monitorização e Medição", "MED-06", "Não",
     "Desvio de +15% no solvente de limpeza (confirmado): limpezas com recipiente aberto e aumento de limpezas após o overhaul da SS-001.",
     "Causas confirmadas na investigação PAM-26-07: (1) recipientes abertos no posto → evaporação; (2) após o overhaul de jul/2026, a nova rasqueta exige mais limpezas; (3) limpeza por hábito em cada mudança de turno.",
     "Método de limpeza não normalizado e recipientes inadequados.", "Método",
     "Dispensadores de segurança com tampa (2 por máquina); norma de limpeza (quando limpar e volume máximo); afinação da rasqueta da SS-001; formação dos operadores de serigrafia.",
     "C2", "Engenharia", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-24", "2026-11-15", 0.0, "", "Sim", "", 1600, 900,
     "Menos COV emitidos e menos resíduos perigosos", 120, "kg solvente/ano",
     "Eficaz se o KPI-06 ≤ 0,160 kg/1.000 peças durante 3 meses consecutivos.", "2027-02-28", "Por avaliar", "5.2 (Parte 1)"),
    ("PAM-26-09", "09/26", "2026-04-20", "Matriz de Riscos e Oportunidades", "RO-01", "Não",
     "Oportunidade significativa RO-01 (nível 9): usar a infraestrutura de dados industriais para gestão ambiental.",
     "—", "—", "—",
     "Painel ambiental em Power BI com energia, água, resíduos (LER), solventes e KPI por máquina/turno/mês; relatório mensal automático para a gestão.",
     "M", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-05-01", "2026-12-31", 0.50, "", "Sim", "RO-01", 6000, 0,
     "Decisões baseadas em dados", None, "",
     "Eficaz se ≥ 80% dos KPI ambientais tiverem carregamento automático e o painel for usado na reunião mensal durante 3 meses.", "2027-03-31", "Por avaliar", "—"),
    ("PAM-26-10", "10/26", "2026-09-10", "Tabela de Legislação", "LEG-09", "Não",
     "NC legal PPWR: só 9 de 22 famílias com documentação técnica e declaração UE de conformidade (aplicável desde 12/08/2026).",
     "1. Porquê só 41%? O trabalho começou em junho/2026.\n2. Porquê tão tarde? O PPWR não estava na matriz legal até 2026.\n3. Porquê? A vigilância legal não acompanhava regulamentos europeus de produto.",
     "Vigilância legal limitada a legislação nacional ambiental de instalação.", "Método",
     "Plano de conformidade PPWR: ensaios de metais pesados por família, dossier técnico e declaração UE para as 13 famílias em falta (prioridade por volume); incluir EUR-Lex na vigilância legal mensal.",
     "C2", "Administrativa", "Responsável de R&D", "2026-09-15", "2026-12-31", 0.25, "", "Sim", "RO-06", 26000, 0,
     "Conformidade legal do produto", 13, "famílias",
     "Eficaz se 100% das famílias tiverem declaração UE de conformidade em 31/12/2026 e a vigilância legal mensal incluir EUR-Lex.", "2027-01-15", "Por avaliar", "5.4 (decisão D2)"),
    ("PAM-26-11", "11/26", "2026-07-01", "Objetivos Ambientais", "OBJ-06", "Não",
     "Perdas de granulado para a rede pluvial; 6 de 14 pontos críticos com contenção.",
     "—", "—", "—",
     "Programa Operation Clean Sweep: filtros nas 9 sarjetas, tabuleiros de descarga de big bags, aspirador industrial, kits de recolha e inspeção semanal do perímetro.",
     "M", "Engenharia", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-07-01", "2027-03-31", 0.50, "", "Sim", "RO-07", 14000, 0,
     "Menos microplásticos no meio aquático", None, "",
     "Eficaz se 100% dos pontos críticos tiverem contenção e não houver granulado nas sarjetas em 12 inspeções semanais consecutivas.", "2027-06-30", "Por avaliar", "—"),
    ("PAM-26-12", "12/26", "2026-07-01", "Objetivos Ambientais", "OBJ-02", "Não",
     "Scrap ≈ 31 t/ano e taxa de reintegração de ≈ 37% (scrap misturado por cor e polímero).",
     "—", "—", "—",
     "Segregar o scrap na fonte com caixas coloridas por polímero/cor, receitas de arranque validadas após mudança de molde e Pareto mensal de scrap por máquina.",
     "M", "Administrativa", "Gerente de Produção", "2026-07-01", "2027-06-30", 0.25, "", "Sim", "RO-11", 8500, 15000,
     "Menos polímero virgem e menos resíduos", 4, "t/ano",
     "Eficaz se o KPI-03 ≤ 0,423 kg/1.000 un e a reintegração ≥ 45% no 2.º trimestre de 2027.", "2027-07-31", "Por avaliar", "—"),
    ("PAM-26-13", "13/26", "2026-09-23", "Revisão pela Gestão", "RG-26-D01", "Não",
     "Consumo de solvente em subida e AAS de COV (IRA 40); o solvente usado é enviado como resíduo perigoso.",
     "—", "—", "—",
     "Adquirir e instalar uma unidade de recuperação de solvente (destilador de 60 L) na serigrafia, com reutilização do solvente recuperado.",
     "M", "Substituição", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-10-15", "2027-03-31", 0.0, "", "Sim", "", 12500, 3100,
     "Menos compra de solvente e menos resíduo 08 03 12*", 450, "kg/ano",
     "Eficaz se ≥ 60% do solvente usado for recuperado e o resíduo 08 03 12* baixar ≥ 40% no 2.º trimestre de 2027.", "2027-07-31", "Por avaliar", "5.4 (decisão D1)"),
    ("PAM-26-14", "14/26", "2026-06-15", "Objetivos Ambientais", "OBJ-05", "Não",
     "Água da torre de arrefecimento ≈ 80% do consumo; purga manual por tempo e não por qualidade da água.",
     "—", "—", "—",
     "Controlo automático da purga da torre por condutividade e estudo de torre adiabática em circuito fechado.",
     "M", "Engenharia", "Diretor Industrial", "2026-11-01", "2027-06-30", 0.0, "", "Sim", "RO-04", 65000, 3800,
     "Menos água de rede", 900, "m³/ano",
     "Eficaz se o KPI-02 normalizado pela temperatura baixar ≥ 10% face ao mesmo período do ano anterior.", "2027-10-31", "Por avaliar", "—"),
    ("PAM-26-15", "15/26", "2026-09-17", "Auditoria Interna", "CONST-03", "Não",
     "NC menor de auditoria: contentor de absorventes contaminados (15 02 02*) sem identificação LER e sem tampa no parque de resíduos.",
     "1. Porquê sem etiqueta? O contentor foi trocado e o novo não foi etiquetado.\n2. Porquê? Não há etiquetas LER padronizadas em stock.\n3. Porquê não foi detetado? A ronda de resíduos não verifica identificação e tampas dos perigosos.",
     "Ausência de etiquetas padronizadas e de ponto de verificação na ronda.", "Material",
     "Etiquetas LER padronizadas para todos os contentores; contentores de perigosos com tampa; incluir verificação no ponto RON-08.",
     "C2", "Administrativa", "Responsável de Armazém e Logística", "2026-09-18", "2026-10-15", 0.50, "", "Não", "", 400, 0,
     "Resíduos perigosos corretamente identificados e fechados", None, "",
     "Eficaz se 100% dos contentores de perigosos estiverem identificados e fechados em 3 rondas consecutivas.", "2026-12-31", "Por avaliar", "5.3 (Parte 1)"),
    ("PAM-26-16", "16/26", "2026-04-20", "Matriz de Riscos e Oportunidades", "RO-05", "Não",
     "Risco significativo RO-05: resina fora de especificação e conteúdo reciclado não verificado (SUP-005 e PCR).",
     "—", "—", "—",
     "Aplicar a avaliação ambiental de fornecedores (RG-SGA-11) aos 10 fornecedores de resina e exigir certificação EuCertPlast/RecyClass para PCR.",
     "M", "Administrativa", "Responsável de Compras", "2026-05-01", "2026-12-31", 0.50, "", "Sim", "RO-05", 2000, 0,
     "Fornecedores avaliados e conteúdo reciclado comprovado", 10, "fornecedores",
     "Eficaz se ≥ 90% das compras de resina forem a fornecedores classificados A ou B.", "2027-03-31", "Por avaliar", "—"),
    ("PAM-26-17", "17/26", "2026-09-17", "Auditoria Interna", "CONST-05", "Não",
     "NC menor de auditoria (6.3): a substituição dos compressores não passou por avaliação de impactes ambientais e requisitos legais.",
     "Ver PAM-26-03: o pedido de alteração não tem checklist ambiental/legal.",
     "Processo de gestão de mudanças (6.3) inexistente.", "Método",
     "Criar o formulário de pedido de alteração com checklist ambiental e legal (aspetos, requisitos, riscos, emergência) e aprovação do SGA antes de qualquer alteração de equipamento, processo ou layout.",
     "C2", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-20", "2026-11-30", 0.0, "", "Sim", "RO-12", 0, 0,
     "Mudanças planeadas sem novos impactes não avaliados", None, "",
     "Eficaz se 100% das alterações de out/2026–mar/2027 tiverem checklist ambiental aprovado antes da execução.", "2027-04-15", "Por avaliar", "5.3 (Parte 1)"),
    ("PAM-26-18", "18/26", "2026-09-23", "Revisão pela Gestão", "RG-26-D04", "Não",
     "Oportunidade RO-09: autoconsumo fotovoltaico para reduzir emissões do âmbito 2 e o custo de energia.",
     "—", "—", "—",
     "Estudo de viabilidade de uma UPAC de ≈ 1 MWp na cobertura, com candidatura a financiamento.",
     "M", "Substituição", "Diretor Financeiro", "2026-10-01", "2027-03-31", 0.0, "", "Sim", "RO-09", 4000, 0,
     "Decisão de investimento fundamentada", 1400, "MWh/ano (potencial)",
     "Eficaz se o estudo for apresentado à gestão com decisão registada em ata até 31/03/2027.", "2027-04-30", "Por avaliar", "5.4 (decisão D4)"),
    ("PAM-26-19", "19/26", "2026-09-17", "Auditoria Interna", "CONST-01", "Não",
     "NC menor de auditoria: 3 bidões de 200 L de óleo hidráulico novo pousados no chão do armazém de químicos, sem bacia de retenção (2 bacias para 5 bidões).",
     "1. Porquê no chão? As bacias existentes estavam cheias.\n2. Porquê? A compra de óleo passou a ser feita em lotes maiores (desconto de quantidade).\n3. Porquê não se ajustou a contenção? A decisão de compra não considerou a capacidade de armazenagem com retenção.",
     "Capacidade de retenção não dimensionada para o stock máximo; compras sem critério de armazenagem.", "Material",
     "Adquirir 2 bacias de retenção de 4 bidões; definir lotação máxima por bacia sinalizada no local; incluir 'capacidade de retenção' no pedido de compra de químicos.",
     "C2", "Engenharia", "Responsável de Armazém e Logística", "2026-09-18", "2026-10-15", 0.50, "", "Sim", "RO-10", 1200, 0,
     "Contenção de derrames no armazém", None, "",
     "Eficaz se 100% dos recipientes > 20 L estiverem em bacia em 3 rondas consecutivas.", "2026-12-31", "Por avaliar", "5.3 (Parte 1)"),
    ("PAM-26-20", "20/26", "2026-09-17", "Auditoria Interna", "CONST-06", "Não",
     "NC menor de auditoria (9.1.1): a balança de plataforma do parque de resíduos (EQP-02) não é verificada desde 03/2024 (periodicidade anual).",
     "1. Porquê não foi verificada? Não constava do plano de calibração.\n2. Porquê? Foi comprada pela logística e não foi registada como equipamento de medição ambiental.",
     "Inventário de equipamentos de monitorização incompleto.", "Medição",
     "Verificar a balança com massas-padrão (entidade acreditada); registar todos os equipamentos de medição ambiental no RG-SGA-13 com periodicidade e alerta.",
     "C2", "Administrativa", "Gerente da Qualidade", "2026-09-18", "2026-10-31", 0.25, "", "Não", "", 350, 0,
     "Dados de resíduos (MIRR) fiáveis", None, "",
     "Eficaz se 100% dos equipamentos do RG-SGA-13 estiverem dentro do prazo de calibração/verificação em 31/12/2026.", "2027-01-15", "Por avaliar", "5.3 (Parte 1)"),
    ("PAM-26-21", "21/26", "2026-09-17", "Auditoria Interna", "CONST-10", "Não",
     "NC menor de auditoria (8.2): nunca foi realizado simulacro de derrame; no simulacro de incêndio (11/2025) a válvula de corte pluvial demorou 9 min (meta ≤ 5 min).",
     "1. Porquê só simulacro de incêndio? O plano de simulacros cumpre só o SCIE.\n2. Porquê? Os cenários ambientais (derrame, águas de combate) não foram incluídos no plano de emergência.",
     "Plano de simulacros não cobre os cenários ambientais de emergência.", "Método",
     "Incluir no plano anual 2 simulacros de derrame (armazém de químicos e serigrafia) e treino trimestral de fecho da válvula de corte pelo turno.",
     "C2", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-20", "2026-12-15", 0.0, "", "Sim", "RO-08", 800, 0,
     "Resposta a emergências ambientais testada", None, "",
     "Eficaz se o simulacro de derrame tiver contenção em ≤ 10 min e a válvula de corte for fechada em ≤ 5 min.", "2027-01-31", "Por avaliar", "5.3 (Parte 1)"),
    ("PAM-26-22", "22/26", "2026-09-22", "Objetivos Ambientais", "OBJ-07", "Não",
     "Autoavaliação RecyClass: 4 SKUs de PVC e 8 de PETG em classe F (sem fluxo de reciclagem) — não poderão ser colocados no mercado a partir de 2030.",
     "—", "—", "—",
     "Plano de substituição: PVC → PET (moldes FR-007/019/022) e PETG → PET ou PP, validado com os clientes; parar novos projetos em PVC/PETG.",
     "M", "Substituição", "Responsável de R&D", "2026-10-01", "2027-12-31", 0.0, "", "Sim", "RO-06", 42000, 0,
     "SKUs recicláveis (grau ≥ C)", 12, "SKUs",
     "Eficaz se 0 SKUs de PVC/PETG estiverem ativos em 31/12/2027 sem perda de clientes.", "2028-03-31", "Por avaliar", "—"),
    ("PAM-26-23", "23/26", "2026-09-22", "Objetivos Ambientais", "OBJ-07", "Não",
     "7 SKUs com masterbatch preto de negro de carbono (Matte Black) não são detetados por NIR na triagem → classe F.",
     "—", "—", "—",
     "Substituir o masterbatch preto por pigmento preto detetável por NIR (SUP-008) e validar com ensaio de triagem num reciclador.",
     "M", "Substituição", "Responsável de Compras", "2026-10-15", "2027-03-31", 0.0, "", "Sim", "RO-06", 6000, 0,
     "SKUs pretos recicláveis", 7, "SKUs",
     "Eficaz se os 7 SKUs forem identificados corretamente no ensaio de triagem NIR.", "2027-04-30", "Por avaliar", "—"),
    ("PAM-26-24", "24/26", "2026-09-22", "Objetivos Ambientais", "OBJ-07", "Não",
     "SKUs de PET/rPET com serigrafia ou hot foil direto e rótulos com adesivo não lavável ficam abaixo do grau C; a autoavaliação não está certificada.",
     "—", "—", "—",
     "Redesenhar a decoração de PET (rótulo PE/PP ou tinta destintável validada), exigir adesivo lavável a 80 °C nas especificações de rótulo dos clientes e pedir certificação RecyClass das 3 famílias de maior volume.",
     "M", "Substituição", "Responsável de R&D", "2026-11-01", "2028-06-30", 0.0, "", "Sim", "RO-06", 37000, 0,
     "SKUs de PET em grau A–C e certificação", 17, "SKUs",
     "Eficaz se o KPI-18 ≥ 90% em 31/12/2027 e 3 famílias tiverem certificado RecyClass.", "2028-01-31", "Por avaliar", "—"),
    ("PAM-26-25", "25/26", "2026-09-22", "Matriz de Riscos e Oportunidades", "RO-05", "Não",
     "Certificado de rPET do SUP-004 (CERT-03) expirado em 30/06/2026: o conteúdo reciclado declarado não é comprovável; a meta de 35% (art. 7.º) exige mais PCR certificado.",
     "1. Porquê expirou? O fornecedor não renovou a auditoria EuCertPlast.\n2. Porquê não foi detetado? Não havia controlo de validade dos certificados.",
     "Ausência de controlo de validade dos certificados de reciclado.", "Método",
     "Controlo mensal de validade (tbl_certificados_pcr); exigir EN 15343 em todos os lotes de PCR; suspender a alegação ALG-05; plano para subir o PCR de 12% para 35% até 2030 (incl. reciclado químico ISCC PLUS para alimentar).",
     "C2", "Administrativa", "Responsável de Compras", "2026-09-23", "2026-12-31", 0.25, "", "Sim", "RO-05", 1500, 0,
     "Conteúdo reciclado comprovado", 3, "certificados",
     "Eficaz se 100% dos materiais com PCR tiverem certificado válido durante 6 meses seguidos.", "2027-06-30", "Por avaliar", "—"),
    ("PAM-26-26", "26/26", "2026-09-22", "Tabela de Legislação", "LEG-19", "Não",
     "Requisitos por verificar: uso dos frascos alimentares para bebidas (tampas presas), óleos minerais nas tintas (França) e reutilização de paletes (PPWR art. 29.º).",
     "—", "—", "—",
     "Obter declaração de utilização de CUST-015/016, declaração MOSH/MOAH das tintas e estudo de pool de paletes com retorno para clientes em Portugal.",
     "M", "Administrativa", "Responsável de R&D", "2026-09-23", "2026-11-30", 0.25, "", "Sim", "RO-06", 1000, 0,
     "Aplicabilidade confirmada", 3, "requisitos",
     "Eficaz se os 3 requisitos tiverem estado confirmado na matriz (tbl_requisitos_emb) até 30/11/2026.", "2026-12-15", "Por avaliar", "—"),
    ("PAM-26-27", "27/26", "2026-09-22", "Tabela de Legislação", "LEG-18", "Não",
     "Alegações no site e catálogo proibidas pela Diretiva 2024/825 a partir de 27/09/2026 ('eco-friendly', '100% recicláveis', 'neutra em carbono').",
     "1. Porquê existem? Foram criadas pelo marketing em 2023.\n2. Porquê não foram revistas? PR-SGA-14 só foi emitido em 09/2026.",
     "Comunicações comerciais sem validação ambiental.", "Método",
     "Retirar ALG-01, 02 e 08 do site e catálogo; suspender ALG-05; formar a área comercial no PR-SGA-14.",
     "C1", "Eliminação", "Diretor Geral (Gestão de Topo)", "2026-09-23", "2026-09-27", 0.5, "", "Sim", "RO-06", 500, 0,
     "Sem alegações enganosas", 4, "alegações",
     "Eficaz se, na verificação de 30/09/2026, não existir nenhuma alegação com estado Retirar/Proibida no site e catálogo.", "2026-09-30", "Por avaliar", "—"),
    ("PAM-26-28", "28/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "REACH: polímeros importados do Reino Unido (SUP-004) e de Singapura (SUP-005) sem representante único — a Plasticom é importadora sem registo dos monómeros/aditivos ≥ 1 t/ano; PVC spot sem declaração de ftalatos/chumbo.",
     "1. Porquê sem RU? Nunca foi pedido na qualificação do fornecedor.\n2. Porquê? O critério de compra só pedia FDS e certificado de qualidade; o Brexit mudou o estatuto do SUP-004 sem revisão.",
     "Qualificação de fornecedores sem verificação do papel REACH (importador vs utilizador a jusante).", "Método",
     "Obter carta de RU (SUP-004) ou comprar via importador UE; manter suspensas as compras spot do SUP-005 e analisar os SKUs de PVC; incluir 'origem EEE / RU' no critério CRIT-07 de fornecedores (RG-SGA-21 tbl_registo_reach).",
     "C2", "Administrativa", "Responsável de Compras", "2026-09-24", "2026-11-30", 0.0, "", "Sim", "RO-05", 800, 0,
     "Substâncias registadas na cadeia", 2, "fornecedores",
     "Eficaz se 0 lacunas em tbl_registo_reach (RG-SGA-21) em 31/12/2026.", "2027-01-15", "Por avaliar", "—"),
    ("PAM-26-29", "29/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "Tinta UV do ensaio na SS-002 (ALT-2025-01) contém fotoiniciador 71868-10-5 (Repr. 1B, SVHC) — mistura H360FD; sem lista de trabalhadores expostos (DL 301/2000).",
     "1. Porquê entrou? O ensaio avaliou COV e energia, não a toxicidade.\n2. Porquê? A aprovação de químicos novos não tinha verificação de CMR/SVHC (antes do PR-SGA-16).",
     "Aprovação de produtos químicos sem triagem CMR/SVHC.", "Material",
     "Substituir por tinta UV sem fotoiniciadores Repr. 1B; até lá: 3 operadores formados, sem grávidas/lactantes, lista de expostos e vigilância da saúde; triagem CMR/SVHC obrigatória na aprovação (PR-SGA-16).",
     "C2", "Substituição", "Responsável de R&D", "2026-09-24", "2026-12-31", 0.0, "", "Sim", "RO-10", 3000, 0,
     "Eliminação de CMR 1A/1B", 1, "produtos",
     "Eficaz se 0 produtos CMR 1A/1B no inventário (RG-SGA-21) em 31/12/2026.", "2027-01-31", "Por avaliar", "—"),
    ("PAM-26-30", "30/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "Limpa-moldes em aerossol com n-hexano (SVHC desde 02/2026; Repr. 2, STOT RE 2) pulverizado sem captação (prioridade P1); uso industrial fora do cenário de exposição do fornecedor.",
     "—", "—", "—",
     "Substituir por limpa-moldes sem n-hexano (base de ésteres/álcool) validado em 2 moldes; medir n-hexano até à substituição.",
     "C2", "Substituição", "Gerente de Manutenção", "2026-09-24", "2026-12-15", 0.0, "", "Sim", "RO-10", 600, 0,
     "SVHC eliminada da manutenção", 1, "produtos",
     "Eficaz se o produto for retirado do inventário e dos armários até 15/12/2026.", "2027-01-15", "Por avaliar", "—"),
    ("PAM-26-31", "31/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "Cenários de exposição do solvente de limpeza (CE-01) e do diluente (CE-02) não cumpridos na SS-001: limpeza manual 2 h/turno sem captação; CE-02 com o prazo de 12 meses (art. 39.º) ultrapassado.",
     "1. Porquê? A SS-001 é a máquina antiga sem mesa aspirante.\n2. Porquê não se tratou? Os CE recebidos com as FDS nunca eram comparados com o uso real.",
     "Ausência de verificação dos cenários de exposição.", "Método",
     "Instalar mesa aspirante na SS-001; luvas de butilo; verificar cada CE recebido em tbl_ce_reach (RG-SGA-21) no prazo de 12 meses.",
     "C2", "Engenharia", "Gerente de Produção", "2026-09-24", "2026-12-31", 0.0, "", "Sim", "RO-10", 9500, 0,
     "Exposição a COV reduzida", None, "",
     "Eficaz se a medição de 11/2026 na SS-001 der índice de exposição < 0,1 (teste preliminar NP EN 689).", "2027-01-31", "Por avaliar", "—"),
    ("PAM-26-32", "32/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "Formação obrigatória em falta: 2 operadores de serigrafia sem formação em diisocianatos (anexo XVII, entrada 74) e técnicos de utilidades com formação em biocidas vencida.",
     "1. Porquê? Os novos operadores começaram antes da formação.\n2. Porquê? O acolhimento não bloqueia tarefas que exigem formação legal prévia.",
     "Acolhimento sem verificação de formações obrigatórias por tarefa.", "Mão de obra",
     "Formar os 2 operadores antes de usarem a tinta 2K; renovar a formação em biocidas (FOR-12); tornar FOR-13 obrigatória no acolhimento da serigrafia (RG-SGA-08).",
     "C2", "Administrativa", "Responsável de Recursos Humanos", "2026-09-24", "2026-10-31", 0.0, "", "Não", "", 900, 0,
     "Trabalhadores formados", 5, "trabalhadores",
     "Eficaz se 0 registos pendentes ou fora de validade de FOR-12 e FOR-13 no RG-SGA-08 em 30/11/2026.", "2026-11-30", "Por avaliar", "—"),
    ("PAM-26-33", "33/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "Armazenagem e EPI de químicos: hipoclorito (EUH031) na mesma bacia do anti-incrustante ácido (ARM-04); sala de baterias sem viseira facial (CE-08, prazo do art. 39.º ultrapassado); 6 locais de químicos fora do armazém sem ponto de ronda.",
     "1. Porquê? Os produtos da torre foram entregues juntos pelo fornecedor.\n2. Porquê não se detetou? A ronda só cobria o armazém principal e a serigrafia.",
     "Ronda ambiental sem cobertura dos locais de químicos fora do armazém.", "Método",
     "Bacias separadas e sinalização da incompatibilidade na torre; viseira facial na sala de carga; novo ponto de ronda RON-11 (RG-SGA-10) para torre, oficina, gases, gasóleo, laboratório e baterias.",
     "C2", "Engenharia", "Gerente de Manutenção", "2026-09-24", "2026-10-31", 0.0, "", "Sim", "RO-10", 900, 0,
     "Contenção e segregação de químicos", 6, "locais",
     "Eficaz se as 2 primeiras rondas RON-11 (out. e nov./2026) forem conformes.", "2026-12-15", "Por avaliar", "—"),
    ("PAM-26-34", "34/26", "2026-09-24", "Tabela de Legislação", "LEG-06", "Não",
     "Informação de fornecedores incompleta: 6 FDS a corrigir ou atualizar (2 de 2021), 7 declarações SVHC desatualizadas ou em falta (lista de 253 entradas), D4/D5/D6 do desmoldante por confirmar e verificação da lista candidata de junho/2026 em atraso (OBR-19).",
     "1. Porquê? Os pedidos aos fornecedores não tinham prazo nem seguimento.\n2. Porquê? Não havia registo da versão da lista coberta por cada declaração.",
     "Gestão da informação de fornecedores sem controlo de versão.", "Método",
     "Pedidos formais com prazo de 30 dias; declaração com n.º de entradas da lista coberta (RG-SGA-21 tbl_declaracoes); compras bloqueadas para produtos sem FDS válida; verificação semestral da lista (OBR-19).",
     "C2", "Administrativa", "Responsável de Compras", "2026-09-24", "2026-11-30", 0.0, "", "Não", "", 0, 0,
     "Informação REACH completa", 13, "documentos",
     "Eficaz se 0 FDS 'Pedir correção' e 0 declarações 'Desatualizada/Em falta' em 31/12/2026.", "2027-01-15", "Por avaliar", "—"),
    ("PAM-26-35", "35/26", "2026-09-24", "Tabela de Legislação", "LEG-22", "Não",
     "Avaliação de riscos químicos incompleta: 5 produtos perigosos sem avaliação (retardador, removedor de emulsão, trava-roscas, cianoacrilato, anti-incrustante); acetaldeído da purga das ISBM e n-hexano sem medição.",
     "—", "—", "—",
     "Completar as avaliações (RG-SGA-21 tbl_risco_quimico) e medir acetaldeído e n-hexano com laboratório acreditado (NP EN 689).",
     "C2", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-09-24", "2026-11-30", 0.0, "", "Sim", "RO-10", 2500, 0,
     "Riscos químicos avaliados", 7, "avaliações/medições",
     "Eficaz se todos os produtos perigosos tiverem avaliação e as 2 medições tiverem conclusão em 31/12/2026.", "2027-01-15", "Por avaliar", "—"),
    # ações ambientais que existiam só no registo corporativo RG-SGA-02 (PAC 202629 e PAC 202628) — transferidas em 24/09/2026 (fonte única: PAM)
    ("PAM-26-36", "36/26", "2026-12-15", "Matriz de Riscos e Oportunidades", "LEG-03", "Não",
     "Risco R32 (RG-SGA-02): título de utilização de recursos hídricos e condições de descarga do efluente ainda não disponibilizados; aplicabilidade a confirmar.",
     "—", "—", "—",
     "Verificação documental do título de recursos hídricos e das condições de descarga; parecer técnico quando aplicável (antes PAC 202629 no RG-SGA-02).",
     "C2", "Administrativa", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-12-15", "2027-02-26", 0.25, "", "Sim", "", 1500, 0,
     "Conformidade legal em água", None, "",
     "Eficaz se o título e as condições de descarga estiverem confirmados e arquivados e não houver NC legal em água.", "2027-03-31", "Por avaliar", "—"),
    ("PAM-26-37", "37/26", "2026-12-15", "Matriz de Riscos e Oportunidades", "LEG-01", "Não",
     "Risco R31 (RG-SGA-02): obrigações do RGGR (MIRR/SILiAmb, e-GAR) dependentes de rotina manual; scrap elevado.",
     "—", "—", "—",
     "Checklist das obrigações de resíduos do calendário RG-SGA-04 (OBR-01, OBR-02) e auditoria trimestral de evidências (antes PAC 202628 no RG-SGA-02).",
     "M", "Administrativa", "Técnico de Qualidade/Ambiente", "2026-12-15", "2027-02-26", 0.25, "", "Sim", "", 0, 0,
     "Obrigações de resíduos cumpridas", None, "",
     "Eficaz se 100% das obrigações de resíduos forem cumpridas no prazo em 2 trimestres seguidos.", "2027-06-30", "Por avaliar", "—"),
]


def build(out):
    b = Book("RG-SGA-06", "Plano de Ações de Melhoria — PAM 2026 (Mod.G.10.00)",
             activities="Atividade 3.5 (ações 01/26 e 02/26); Atividade 6.1 Tarefa 2 (04/26 C1 e 05/26 C2); Atividade 6.2 Tarefa 2 (06/26 M); ações de 5.2 (07/26, 08/26), 5.3 (15/26, 17/26) e 5.4 (10/26, 13/26, 18/26).",
             clauses="6.1.5 Planeamento de ações; 6.2.2; 10.1 Melhoria contínua; 10.2 Não conformidade e ação corretiva (ISO 14001:2026)",
             purpose="Documento mestre de todas as ações do SGA (objetivos, riscos, aspetos, NC, auditorias, revisão pela gestão, Kaizen). Classifica o tipo de ação (C1 correção, C2 ação corretiva, M melhoria), mantém a análise de causas, o responsável, o prazo, a evolução, o impacto nos riscos e a avaliação da eficácia. Estados, atrasos, payback e alertas são calculados.",
             links=[("Origens", "ID_Origem aponta para OBJ (RG-SGA-05), RO (RG-SGA-02), LEG (RG-SGA-04), NC (RG-SGA-07), MED (RG-SGA-13), CONST (RG-SGA-14), RG (RG-SGA-15) e KZ (RG-SGA-16)."),
                    ("Mod.G.10.00", "A folha Mod.G.10.00_Vista reproduz o formato do curso (evolução 25/50/75/100%) a partir da tabela.")])
    b.add_list("Fonte", FONTES)
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("TipoAcao", ["C1", "C2", "M"])
    b.add_list("Hierarquia", ["Eliminação", "Substituição", "Engenharia", "Administrativa", "EPI"])
    b.add_list("Cat6M", ["Método", "Máquina", "Material", "Mão de obra", "Medição", "Meio ambiente", "—"])
    b.add_list("Evolucao", [0, 0.25, 0.5, 0.75, 1])
    b.add_list("Eficacia", ["Por avaliar", "Eficaz", "Não eficaz"])
    b.add_list("Funcao", FUNC_NAMES)

    cols = [
        col("ID_Acao", 10, desc="Identificador da ação.", key="PK", dom="PAM-AA-nn"),
        col("N_Acao_Mod", 7, desc="N.º no formato do Mod.G.10.00 (nn/AA)."),
        col("Data_Abertura", 11, "date", desc="Data de registo."),
        col("Fonte_Doc_Afetado", 20, dv="Fonte", desc="Fonte / documento afetado (legenda do Mod.G.10.00)."),
        col("ID_Origem", 11, desc="ID do registo de origem.", key="FK → vários registos"),
        col("Proveniente_Plano_Anterior", 10, dv="SimNao", desc="Se transita do plano anterior."),
        col("NC_Ocorrencia", 44, desc="Não conformidade / ocorrência / oportunidade."),
        col("Investigacao_Causas", 52, desc="Investigação de causas (5 porquês)."),
        col("Causa_Raiz", 36, desc="Causa raiz."),
        col("Categoria_Causa_6M", 11, dv="Cat6M", desc="Categoria Ishikawa (6M)."),
        col("Acao_Descricao", 52, desc="Ação a implementar."),
        col("Tipo_Acao", 7, dv="TipoAcao", desc="C1 correção (resolve o imediato); C2 ação corretiva (elimina a causa); M melhoria (proativa)."),
        col("Hierarquia_Controlo", 13, dv="Hierarquia", desc="Nível na hierarquia de eficácia (Eliminação > Substituição > Engenharia > Administrativa > EPI)."),
        col("Responsavel", 26, dv="Funcao", desc="Responsável."),
        col("Data_Inicio", 11, "date", desc="Início."),
        col("Prazo", 11, "date", desc="Prazo."),
        col("Evolucao", 8, "pct", dv="Evolucao", desc="Evolução (0, 25, 50, 75, 100%)."),
        col("Data_Fecho", 11, "date", desc="Data de conclusão.", req=False),
        col("Estado", 11, f='=IF(@Evolucao@>=1,IF(@Data_Fecho@>@Prazo@,"Concluída com atraso","Concluída"),IF(@Prazo@<DataRef,"Atrasada",IF(@Evolucao@=0,"Planeada","Em curso")))', desc="Estado calculado face à data de referência."),
        col("Dias_para_Prazo", 9, "int", f='=IF(@Evolucao@>=1,"",@Prazo@-DataRef)', desc="Dias até ao prazo (negativo = atraso)."),
        col("Impacto_Riscos", 9, dv="SimNao", desc="Sim se a ação altera a pontuação da matriz de riscos."),
        col("ID_RO_Afetado", 9, desc="Risco/oportunidade afetado.", key="FK → RG-SGA-02", req=False),
        col("Custo_Previsto_EUR", 11, "eur", desc="Custo previsto (CAPEX + OPEX)."),
        col("Poupanca_Anual_EUR", 11, "eur", desc="Poupança anual estimada.", req=False),
        col("Payback_Meses", 9, "num1", f='=IF(OR(@Poupanca_Anual_EUR@="",@Poupanca_Anual_EUR@=0),"",@Custo_Previsto_EUR@/@Poupanca_Anual_EUR@*12)', desc="Retorno do investimento (meses)."),
        col("Beneficio_Ambiental", 30, desc="Benefício ambiental esperado."),
        col("Beneficio_Quantidade", 10, "num0", desc="Quantidade do benefício.", req=False),
        col("Beneficio_Unidade", 14, desc="Unidade do benefício.", req=False),
        col("Criterio_Eficacia", 46, desc="Observações: 'Eficaz se...'."),
        col("Data_Avaliacao_Eficacia", 11, "date", desc="Data prevista/real da avaliação da eficácia."),
        col("Resultado_Eficacia", 11, dv="Eficacia", desc="Resultado da avaliação da eficácia."),
        col("Controlo_Qualidade", 20, f=('=IF(AND(@Tipo_Acao@="C2",@Causa_Raiz@=""),"FALTA causa raiz (C2)",IF(@Criterio_Eficacia@="","FALTA critério de eficácia",'
                                         'IF(AND(@Estado@="Concluída",@Resultado_Eficacia@="Por avaliar",@Data_Avaliacao_Eficacia@<DataRef),"Avaliar eficácia","OK")))'),
            desc="Regras de qualidade do registo."),
        col("Atividade_Curso", 16, desc="Atividade do curso a que a linha responde (— = ação do SGA sem exercício associado).", req=False),
    ]
    rows = []
    for p in PAM:
        (i, n, ab, fo, orig, pa, oc, inv, cr, c6, ac, tp, hi, rs, ini, pz, ev, fe, imp, ro, cu, po, bt, bq, bu, ef, def_, ref_, atv) = p
        if i in FECHO_2026:   # estado no fecho do ano (31/12/2026)
            f_ = FECHO_2026[i]
            ev, fe = f_[0], f_[1]
            if len(f_) > 2:
                ref_, def_ = f_[2], f_[3]
        rows.append(dict(ID_Acao=i, N_Acao_Mod=n, Data_Abertura=d(ab), Fonte_Doc_Afetado=fo, ID_Origem=orig, Proveniente_Plano_Anterior=pa,
                         NC_Ocorrencia=oc, Investigacao_Causas=inv, Causa_Raiz=cr, Categoria_Causa_6M=c6, Acao_Descricao=ac, Tipo_Acao=tp,
                         Hierarquia_Controlo=hi, Responsavel=rs, Data_Inicio=d(ini), Prazo=d(pz), Evolucao=ev, Data_Fecho=d(fe),
                         Impacto_Riscos=imp, ID_RO_Afetado=ro or None, Custo_Previsto_EUR=cu, Poupanca_Anual_EUR=po or None,
                         Beneficio_Ambiental=bt, Beneficio_Quantidade=bq, Beneficio_Unidade=bu or None, Criterio_Eficacia=ef,
                         Data_Avaliacao_Eficacia=d(def_), Resultado_Eficacia=ref_, Atividade_Curso=atv))
    b.table("PAM", "tbl_pam", cols, rows, "Plano de Ações de Melhoria (registo mestre, 1 linha por ação).",
            title="PLANO DE AÇÕES DE MELHORIA — PAM n.º 01/2026 (Mod.G.10.00) — PLASTICOM",
            subtitle="C1 = Correção · C2 = Ação corretiva · M = Melhoria · Estado, atraso, payback e controlo de qualidade calculados · Data de referência 2026-12-31",
            cf=[("Tipo_Acao", {"C1": "orange", "C2": "red", "M": "blue"}),
                ("Estado", {"Atrasada": "red", "com atraso": "orange", "Concluída": "green", "Em curso": "yellow", "Planeada": "gray"}),
                ("Resultado_Eficacia", {"Não eficaz": "red", "Eficaz": "green"}),
                ("Controlo_Qualidade", {"FALTA": "red", "Avaliar": "yellow", "OK": "green"}),
                ("Atividade_Curso", {"3.5": "purple", "6.1": "purple", "6.2": "purple"})],
            row_height=150, freeze_col=2)

    # vista Mod.G.10.00
    ws = b.sheet("Mod.G.10.00_Vista", "Plano no formato do modelo do curso (Mod.G.10.00), calculado a partir de tbl_pam, para impressão/fórum.", tab_color="C00000")
    heads = ["Nº Ação", "Fonte / Doc. Afecto", "Proveniente Plano Anterior?", "Não conformidade / Ocorrência", "Investigação Causas",
             "Ações (Descrição) C1|C2|M", "Resp.", "Prazo", "25", "50", "75", "100", "Prazo / Data Fecho", "Impacto Riscos?", "Avaliação da Eficácia"]
    doc_header(ws, "RG-SGA-06", "PLANO DE AÇÕES DE MELHORIA", "PM n.º 01/2026", len(heads))
    ws.cell(row=4, column=9, value="Evolução (%)").font = F_BOLD
    header_row(ws, 5, heads, widths=[8, 18, 10, 34, 46, 44, 18, 11, 4, 4, 4, 4, 12, 9, 40])
    T = lambda f: b.ref("tbl_pam", f)
    for k in range(len(PAM)):
        r, i = 6 + k, k + 1
        vals = [f'=INDEX({T("N_Acao_Mod")},{i})', f'=INDEX({T("Fonte_Doc_Afetado")},{i})&" ("&INDEX({T("ID_Origem")},{i})&")"',
                f'=INDEX({T("Proveniente_Plano_Anterior")},{i})', f'=INDEX({T("NC_Ocorrencia")},{i})',
                f'=INDEX({T("Investigacao_Causas")},{i})&IF(INDEX({T("Causa_Raiz")},{i})="—",""," CAUSA RAIZ: "&INDEX({T("Causa_Raiz")},{i}))',
                f'="("&INDEX({T("Tipo_Acao")},{i})&") "&INDEX({T("Acao_Descricao")},{i})', f'=INDEX({T("Responsavel")},{i})',
                f'=INDEX({T("Prazo")},{i})'] + \
               [f'=IF(INDEX({T("Evolucao")},{i})>={p},"X","")' for p in (0.25, 0.5, 0.75, 1)] + \
               [f'=IF(INDEX({T("Data_Fecho")},{i})="","—",INDEX({T("Data_Fecho")},{i}))', f'=INDEX({T("Impacto_Riscos")},{i})',
                f'="A avaliar em: "&TEXT(MONTH(INDEX({T("Data_Avaliacao_Eficacia")},{i})),"00")&"/"&YEAR(INDEX({T("Data_Avaliacao_Eficacia")},{i}))&" — "&INDEX({T("Criterio_Eficacia")},{i})&" ["&INDEX({T("Resultado_Eficacia")},{i})&"]"']
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.font, c.border = Font(name=FONT, size=9), BORDER
            c.alignment = CENTER if j in (0, 2, 7, 8, 9, 10, 11, 12, 13) else WRAP_TOP
            if j in (7, 12):
                c.number_format = "dd/mm/yyyy"
            if 8 <= j <= 11:
                c.fill = PatternFill("solid", fgColor="E2EFDA")
        ws.row_dimensions[r].height = 170
    ws.freeze_panes = "B6"
    r = 7 + len(PAM)
    for lab, txt in [("Fonte / Doc. Afecto", "Análise SWOT, Matriz de AA (Aspetos), Tabela de Legislação, Política, Objetivos, Reclamações, Rondas, Auditorias, Revisão pela Gestão."),
                     ("Tipo de Ação", "C1 — Correção: resolver o problema imediato (ex.: limpar o derrame). C2 — Ação corretiva: eliminar a causa para não voltar a acontecer (ex.: mudar a válvula que verteu). M — Melhoria: ação proativa para melhorar o desempenho."),
                     ("Impacto nos Riscos", "'Sim' se a ação altera a pontuação na Matriz de Riscos (ex.: reduz a probabilidade de um acidente).")]:
        ws.cell(row=r, column=1, value=lab).font = F_BOLD
        c = ws.cell(row=r, column=3, value=txt)
        c.alignment = WRAP_TOP
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=15)
        ws.row_dimensions[r].height = 30
        r += 1
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = "5:5"

    # painel
    ws = b.sheet("Painel", "Indicadores do PAM (calculados): ações por tipo, estado e fonte; custos, poupanças e cumprimento de prazos.")
    ws["A1"] = "PAINEL DO PLANO DE AÇÕES — calculado"
    ws["A1"].font = F_TITLE
    header_row(ws, 3, ["Tipo", "N.º ações", "Concluídas", "Atrasadas", "Custo (€)", "Poupança anual (€)"], widths=[34, 11, 11, 11, 13, 16])
    for k, t in enumerate(["C1", "C2", "M"]):
        r = 4 + k
        ws.cell(row=r, column=1, value={"C1": "C1 — Correção", "C2": "C2 — Ação corretiva", "M": "M — Melhoria"}[t])
        ws.cell(row=r, column=2, value=f'=COUNTIF({T("Tipo_Acao")},"{t}")')
        ws.cell(row=r, column=3, value=f'=COUNTIFS({T("Tipo_Acao")},"{t}",{T("Estado")},"Concluída*")')
        ws.cell(row=r, column=4, value=f'=COUNTIFS({T("Tipo_Acao")},"{t}",{T("Estado")},"Atrasada")')
        ws.cell(row=r, column=5, value=f'=SUMIF({T("Tipo_Acao")},"{t}",{T("Custo_Previsto_EUR")})').number_format = "#,##0 €"
        ws.cell(row=r, column=6, value=f'=SUMIF({T("Tipo_Acao")},"{t}",{T("Poupanca_Anual_EUR")})').number_format = "#,##0 €"
    ws.cell(row=7, column=1, value="TOTAL").font = F_BOLD
    for j in range(2, 7):
        L = get_column_letter(j)
        c = ws.cell(row=7, column=j, value=f"=SUM({L}4:{L}6)")
        c.font = F_BOLD
        if j >= 5:
            c.number_format = "#,##0 €"
    header_row(ws, 9, ["Fonte", "N.º ações"])
    for k, f in enumerate(FONTES):
        ws.cell(row=10 + k, column=1, value=f)
        ws.cell(row=10 + k, column=2, value=f'=COUNTIF({T("Fonte_Doc_Afetado")},"{f}")')
    r = 11 + len(FONTES)
    ws.cell(row=r, column=1, value="% ações não atrasadas").font = F_BOLD
    c = ws.cell(row=r, column=2, value=f'=1-COUNTIF({T("Estado")},"Atrasada")/COUNTA({T("ID_Acao")})')
    c.number_format = "0%"
    ws.cell(row=r + 1, column=1, value="Evolução média do plano").font = F_BOLD
    c = ws.cell(row=r + 1, column=2, value=f'=AVERAGE({T("Evolucao")})')
    c.number_format = "0%"
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
