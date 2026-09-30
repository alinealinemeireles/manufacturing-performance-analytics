// Documento Word: atividades da Lusitana Móveis e questões teóricas (SGA Plasticom, ISO 14001:2026)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, AlignmentType,
  WidthType, ShadingType, BorderStyle, LevelFormat, Header, Footer, PageNumber, TableOfContents, PageBreak,
} = require("docx");

const OUT = process.argv[2];
const FONT = "Arial";
const HEAD = "1F4E5F";
const BAND = "DCEBEF";
const W = 9638; // largura útil A4 com margens de 2 cm (DXA)

const p = (text, opts = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...opts, children: runs(text) });
function runs(text) {
  if (Array.isArray(text)) return text;
  // **negrito** simples
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((t) => t.startsWith("**") ? new TextRun({ text: t.slice(2, -2), bold: true }) : new TextRun(t));
}
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 }, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 }, children: [new TextRun(t)] });
const bullet = (t, level = 0) => new Paragraph({ numbering: { reference: "bullets", level }, spacing: { after: 60 }, children: runs(t) });
const num = (t, ref = "numbers") => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60 }, children: runs(t) });
const border = { style: BorderStyle.SINGLE, size: 4, color: "B7C4C9" };
const borders = { top: border, bottom: border, left: border, right: border };

function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, head) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: HEAD, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: head ? [new TextRun({ text: t, bold: true, color: "FFFFFF", size: 19 })] : runs(t).map((r) => r) })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(String(c), widths[i], false)) }))],
  });
}
function box(title, lines) {
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: [W],
    rows: [new TableRow({ children: [new TableCell({
      borders, width: { size: W, type: WidthType.DXA }, shading: { fill: BAND, type: ShadingType.CLEAR, color: "auto" },
      margins: { top: 100, bottom: 100, left: 160, right: 160 },
      children: [new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: title, bold: true, color: HEAD })] }), ...lines.map((l) => p(l))],
    })] })],
  });
}
const gap = () => new Paragraph({ spacing: { after: 60 }, children: [] });

const content = [];
// capa
content.push(new Paragraph({ spacing: { before: 2400, after: 240 }, children: [new TextRun({ text: "PLASTICOM — SISTEMA DE GESTÃO AMBIENTAL", bold: true, size: 36, color: HEAD })] }));
content.push(new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: "Atividades sobre a Lusitana Móveis e questões teóricas", size: 30 })] }));
content.push(p("NP EN ISO 14001:2026 · UC00557 — Implementar e monitorizar sistemas de gestão ambiental (Módulos 4 a 6)"));
content.push(p("Documento DOC-SGA-01 · Versão 01 · 23/09/2026"));
content.push(p("Complemento dos registos Excel do SGA da fábrica simulada Plasticom (pasta Registos_SGA_Plasticom). As atividades aplicadas à Empresa Projeto (Plasticom) estão nos ficheiros Excel; este documento responde às questões da Lusitana Móveis, às questões teóricas e aos auto-estudos."));
content.push(new Paragraph({ children: [new PageBreak()] }));
content.push(new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-2" }));
content.push(new Paragraph({ children: [new PageBreak()] }));

// 0 mapa
content.push(h1("0. Onde está cada atividade"));
content.push(p("As tabelas Excel são registos do SGA e, ao mesmo tempo, uma base de dados: cada registo é uma Tabela Excel com cabeçalho na linha 1 (ou 4, quando tem título), IDs únicos e ligações por chave entre ficheiros. O ficheiro SGA-00_Indice_Modelo_Dados.xlsx contém o catálogo completo e a verificação de integridade."));
content.push(table(["Atividade", "Tema", "Ficheiro / local"], [
  ["3.1", "Riscos e oportunidades", "SGA-02 → Resumo_Atividade_3_1"],
  ["3.2", "Aspetos e impactes", "SGA-03 → Resumo_Atividade_3_2 e Mod.G.07.00_Matriz"],
  ["3.3", "Requisitos legais", "SGA-04 → Mod.G.06.02_Vista"],
  ["3.4", "Objetivos SMART", "SGA-05 → Resumo_Atividade_3_4"],
  ["3.5", "Plano de ações", "SGA-06 → Mod.G.10.00_Vista (01/26 e 02/26)"],
  ["4.1", "Competências", "SGA-08 → Resumo_Atividade_4_1 + secção 1 deste documento"],
  ["4.2", "Comunicação e documentação", "SGA-09 → Resumo_Atividade_4_2 + secção 2"],
  ["4.3", "Ronda ambiental", "SGA-10 → Pontos_Controlo e Checklist_Ronda_Impressao + secção 3"],
  ["4.4", "Fornecedores", "SGA-11 → Resumo_Atividade_4_4 + secção 4"],
  ["4.5", "Emergência", "SGA-12 → IT-SGA-01_Derrames + secção 5"],
  ["5.1", "Monitorização", "SGA-13 → Plano_Monitorizacao e Equipamentos_Calibracao"],
  ["5.2", "Desempenho", "Parte 1: SGA-13 → Analise_Desvio_5_2 · Parte 2: secção 6"],
  ["5.3", "Auditoria interna", "Parte 1: SGA-14 → Checklist_Constatacoes · Parte 2: secção 7"],
  ["5.4", "Revisão pela gestão", "SGA-15 → Convocatoria_Impressao (I) e Ata_Impressao (II)"],
  ["6.1", "NC e 5 Porquês", "SGA-07 → RNC_Formulario; SGA-06 → PAM-26-04 (C1) e PAM-26-05 (C2)"],
  ["6.2", "Kaizen", "SGA-16 → Resumo_Atividade_6_2; SGA-06 → PAM-26-06"],
  ["6.3", "EMAS", "SGA-16 → EMAS_Indicadores e EMAS_Transparencia + secção 8"],
], [1100, 2700, 5838]));

// 1
content.push(h1("1. Atividade 4.1 — Competência vs consciencialização"));
content.push(box("Resposta (ponto 5)", [
  "**Competência** é a capacidade demonstrada de executar corretamente uma tarefa (saber fazer), resultado de educação, formação, experiência e soft skills; **consciencialização** é compreender porque é que a tarefa importa: conhecer a política ambiental, o aspeto significativo do posto, as consequências dos desvios e o próprio contributo para o desempenho ambiental (querer fazer e entender o porquê).",
]));
content.push(gap());
content.push(p("Exemplo na Plasticom (função selecionada no Excel: Operador de Serigrafia, aspeto AA-014 — COV):"));
content.push(bullet("**Competência:** 9.º ano, formação FOR-01 (químicos/FDS), FOR-02 (limpeza de ecrãs com dispensador de segurança), FOR-03 (derrames) e 6 meses de experiência acompanhada. Verifica-se com teste prático no posto."));
content.push(bullet("**Consciencialização:** saber que deixar a lata de solvente aberta aumenta as emissões de COV, o consumo de solvente e o risco de incêndio — e que foi exatamente isso que explicou parte do desvio de +15% em 2026. Verifica-se pela observação do comportamento 3 meses depois (latas fechadas)."));
content.push(p("Fórmula da competência usada na matriz: **Competência = Educação + Formação + Experiência + Soft skills** (ISO 14001:2026, 7.2). A consciencialização (7.3) aplica-se a todas as pessoas que trabalham sob o controlo da organização, incluindo temporários — a NC-SGA-26-08 mostra o que acontece quando um temporário entra no posto sem ela."));

// 2
content.push(h1("2. Atividade 4.2 — Documento obsoleto vs documento em vigor"));
content.push(p("**Documento em vigor** é a versão aprovada, identificada (código, título, revisão e data) e registada como atual na lista mestra; é a única que pode estar nos pontos de uso. **Documento obsoleto** é qualquer versão anterior substituída ou retirada: pode ser conservado como registo histórico, mas nunca deve ser usado para trabalhar."));
content.push(p("Como evitar o uso de versões antigas (aplicado na Plasticom, RG-SGA-09):"));
content.push(bullet("Lista mestra única com o estado de cada documento (Em vigor / Em revisão / Obsoleto) e alerta automático de revisão vencida."));
content.push(bullet("Distribuição controlada: a versão eletrónica é a controlada; as cópias impressas dos postos são registadas e substituídas na mesma data da aprovação."));
content.push(bullet("Retirada física das cópias antigas e carimbo 'OBSOLETO' nas que ficam arquivadas."));
content.push(bullet("Verificação no terreno: nas rondas e auditorias compara-se a versão encontrada com a versão em vigor (em 16/09/2026 encontrou-se a IT-SER-03 rev. 00 no posto SS-001 quando a rev. 01 estava em vigor)."));
content.push(bullet("Comunicação da alteração às pessoas afetadas (toolbox) antes de a nova versão entrar em uso."));
content.push(p("Elementos obrigatórios verificados em qualquer documento: (1) identificação — título e código; (2) estado de revisão — versão e data; (3) aprovação — quem aprovou e quando. Complementares: indicação de 'em vigor' e ponto de uso, legibilidade e proteção/retirada dos obsoletos."));

// 3
content.push(h1("3. Atividade 4.3 — Auto-estudo: impacto energético das fugas de ar comprimido"));
content.push(p("O ar comprimido é uma das utilidades mais caras da fábrica: só cerca de 10-15% da energia elétrica absorvida pelo compressor se transforma em trabalho útil no ponto de uso; o resto perde-se sobretudo em calor. Por isso cada litro de ar desperdiçado custa muito mais do que parece."));
content.push(bullet("Numa rede industrial sem programa de manutenção, as fugas representam tipicamente 20-30% do caudal produzido (na Plasticom, o teste de vazio indicou ≈ 25%)."));
content.push(bullet("Ordem de grandeza (a 6-7 bar): um orifício de 1 mm consome ≈ 0,3 kW, um de 3 mm ≈ 3 kW e um de 5 mm ≈ 8 kW de potência do compressor. Em laboração contínua (≈ 7.000 h/ano a 0,14 €/kWh), uma única fuga de 3 mm custa ≈ 3.000 €/ano e ≈ 2,3 tCO2e."));
content.push(bullet("Cada bar a mais na pressão de rede aumenta o consumo em ≈ 7%: baixar de 7,5 para 6,8 bar poupa ≈ 5%."));
content.push(p("Na Plasticom, os compressores consomem ≈ 975 MWh/ano (≈ 14% da eletricidade). A ação PAM-26-01 (deteção por ultrassom, reparação em ≤ 15 dias, redução de pressão e variador de velocidade) tem uma poupança estimada de ≈ 175 MWh/ano (≈ 24.500 €) e um payback de ≈ 7 meses — por isso a rede de ar é um ponto de controlo semanal da ronda (RON-03)."));

// 4
content.push(h1("4. Atividade 4.4 — Auto-estudo: logística reversa"));
content.push(p("**Logística reversa** é o conjunto de processos que fazem voltar produtos, embalagens ou materiais do destino para a origem (ou para outro produtor), para reutilização, reciclagem ou eliminação adequada. Fecha o ciclo de vida e evita que a embalagem se torne resíduo."));
content.push(p("Aplicação às embalagens dos fornecedores da Plasticom:"));
content.push(bullet("**Big bags e octabins retornáveis:** o camião que entrega resina leva os big bags vazios de volta ao fornecedor (acordado com o SUP-004); cada big bag é reutilizado até 5 vezes, evitando ≈ 1,2 t/ano de resíduo 15 01 02."));
content.push(bullet("**Paletes em pool** (circuito de paletes normalizadas trocadas entre empresas) em vez de paletes de uso único."));
content.push(bullet("**Recipientes de tinta e solvente:** devolução dos bidões IBC ao fornecedor para lavagem e reenchimento, reduzindo as embalagens contaminadas (15 01 10*)."));
content.push(bullet("**Com os clientes:** caixas e separadores retornáveis nas rotas ibéricas (aspeto benéfico AA-041)."));
content.push(p("Para funcionar é preciso: critério contratual (CRIT-06 na avaliação de fornecedores), espaço de armazenagem para as embalagens vazias, controlo de limpeza/contaminação e registo das quantidades devolvidas para medir o benefício."));

// 5
content.push(h1("5. Atividade 4.5 — Auto-estudo: válvula de corte da rede de águas pluviais"));
content.push(p("Num incêndio industrial, a água e as espumas usadas pelos bombeiros arrastam produtos químicos, resíduos de combustão e plásticos fundidos. Sem barreira, estas **águas de combate contaminadas** seguem pela rede de águas pluviais diretamente para linhas de água (no caso da Plasticom, para o rio Lis) ou para o solo — um incêndio pode transformar-se num desastre ambiental maior do que o próprio fogo."));
content.push(p("A **válvula de corte** instalada na saída da rede pluvial fecha a ligação ao meio recetor e retém as águas dentro da instalação (na rede e numa bacia de retenção), para serem analisadas e encaminhadas como resíduo. Para ser eficaz:"));
content.push(bullet("deve estar sinalizada, acessível e com a manobra atribuída a uma função presente em todos os turnos (portaria/chefe de turno);"));
content.push(bullet("deve ser testada periodicamente (a Plasticom testa-a na ronda mensal RON-05) e treinada em simulacro;"));
content.push(bullet("a capacidade de retenção (rede + bacia BR-01 de 300 m³) deve ser dimensionada para o volume de água de combate previsível;"));
content.push(bullet("o plano de emergência deve dizer quando fechar (ao primeiro alerta de incêndio ou derrame significativo) e quando reabrir (após análise)."));
content.push(p("No simulacro de 14/11/2025 a válvula demorou 9 minutos a ser fechada (a chave estava na portaria), acima da meta de 5 minutos — originou a ação PAM-26-21."));

// 6
content.push(h1("6. Atividade 5.2 — Parte 2: o KPI da energia solar na Lusitana Móveis"));
content.push(table(["Mês", "Ago", "Set", "Out", "Nov", "Dez"], [["Produção fotovoltaica (kWh)", "8 500", "6 000", "4 500", "3 200", "2 500"]], [2638, 1400, 1400, 1400, 1400, 1400]));
content.push(h2("6.1 Análise do dado — é um problema de manutenção?"));
content.push(p("**Não, a queda é esperada e tem causa natural (sazonalidade).** A produção de um painel fotovoltaico é proporcional à radiação solar que recebe. Entre agosto e dezembro, em Portugal:"));
content.push(bullet("os dias ficam mais curtos (≈ 14 h de luz em agosto para ≈ 9 h em dezembro);"));
content.push(bullet("o sol está mais baixo no horizonte, a radiação atravessa mais atmosfera e incide nos painéis com um ângulo menos favorável;"));
content.push(bullet("há mais dias nublados e chuvosos no outono e inverno."));
content.push(p("Por isso a radiação disponível em dezembro é tipicamente cerca de um terço da de agosto — exatamente a proporção observada (2.500 / 8.500 ≈ 29%). Uma queda contínua e suave de mês para mês, alinhada com o calendário, é a assinatura da sazonalidade e não de uma avaria (uma avaria ou sujidade provocaria uma quebra brusca ou uma diferença face ao esperado para aquela radiação). Abrir uma não conformidade à manutenção seria tratar um **falso problema**."));
content.push(p("Para confirmar tecnicamente, compara-se a energia produzida com a energia esperada para a radiação medida (piranómetro local ou dados PVGIS). Exemplo ilustrativo para uma instalação de 50 kWp:"));
content.push(table(["Mês", "Produção (kWh)", "Radiação no plano (kWh/m²)*", "Energia teórica = radiação × 50 kWp", "Performance Ratio"], [
  ["Agosto", "8 500", "215", "10 750", "79%"], ["Setembro", "6 000", "152", "7 600", "79%"], ["Outubro", "4 500", "114", "5 700", "79%"],
  ["Novembro", "3 200", "81", "4 050", "79%"], ["Dezembro", "2 500", "63", "3 150", "79%"],
], [1500, 1600, 2300, 2438, 1800]));
content.push(p("* Valores de radiação ilustrativos (potência instalada assumida de 50 kWp). Com um Performance Ratio estável (≈ 79%), a instalação está a converter a luz disponível com a mesma eficiência todos os meses: não há degradação nem falha de manutenção."));
content.push(h2("6.2 Reflexão sobre o KPI"));
content.push(p("**Não faz sentido** usar o 'total de kWh produzidos mensalmente' para avaliar a eficácia e a melhoria contínua do SGA, porque:"));
content.push(bullet("depende sobretudo de um fator externo e não controlável (meteorologia e estação do ano), e não do desempenho da organização;"));
content.push(bullet("com a potência instalada fixa, a produção não pode 'aumentar continuamente' — a meta é impossível por definição e gera alarmes falsos todos os outonos e alegrias falsas todas as primaveras;"));
content.push(bullet("a comparação mês a mês consecutivo mistura estações; mesmo a comparação anual depende de anos mais ou menos solarengos;"));
content.push(bullet("não mostra o objetivo real do investimento (reduzir a pegada carbónica e a dependência da rede): 8.500 kWh podem ser muito ou pouco consoante o consumo da fábrica."));
content.push(p("Um indicador mal definido leva a decisões erradas: aqui, abrir uma NC e gastar recursos de manutenção sem necessidade."));
content.push(h2("6.3 Proposta de KPI alternativo"));
content.push(table(["KPI", "Fórmula", "O que mostra"], [
  ["Taxa de cobertura solar (autossuficiência)", "kWh solares autoconsumidos ÷ kWh totais consumidos pela fábrica × 100 (%)", "Quanto do consumo é satisfeito pelo sol — liga produção e consumo; melhora se a fábrica consumir menos ou deslocar consumos para as horas de sol."],
  ["Performance Ratio (PR)", "kWh produzidos ÷ (radiação no plano kWh/m² × potência de pico kWp) × 100 (%)", "Eficiência técnica da instalação independente do tempo; deve manter-se estável (ex.: ≥ 78%); uma descida indica sujidade, sombra ou avaria — aí sim, ação de manutenção."],
  ["Emissões evitadas", "kWh solares × fator de emissão da rede (tCO2e)", "Contributo para o objetivo de descarbonização (comparar em base anual)."],
], [2600, 3600, 3438]));
content.push(p("Recomendação: usar o **Performance Ratio** para a manutenção (controlo operacional) e a **taxa de cobertura solar anual** (ou do mesmo mês do ano anterior) como indicador de desempenho ambiental na revisão pela gestão."));

// 7
content.push(h1("7. Atividade 5.3 — Parte 2: cláusulas das constatações da Lusitana Móveis"));
content.push(table(["Constatação", "Cláusula principal em incumprimento", "Justificação"], [
  ["1 — Operadores da área de vernizes não sabem onde está o kit antipoluição nem participaram em simulacros.",
   "**8.2 Preparação e resposta a emergências**",
   "A organização deve preparar a resposta (incluindo formação) e testar periodicamente as ações de resposta planeadas. Relacionadas: 7.2 Competência e 7.3 Consciencialização."],
  ["2 — Objetivo 'Reduzir 15% a eletricidade' sem definição do que fazer, recursos, responsável e prazos.",
   "**6.2 Objetivos ambientais e planeamento para os atingir (6.2.2)**",
   "Ao planear como atingir os objetivos, a organização deve determinar o que será feito, os recursos necessários, quem será responsável, quando será concluído e como os resultados serão avaliados."],
  ["3 — Análises ao efluente exigidas pela licença deixaram de ser feitas há 2 anos; não há avaliação da conformidade desde 2024.",
   "**9.1.2 Avaliação da conformidade**",
   "A organização deve avaliar o cumprimento das suas obrigações de conformidade com a frequência definida e manter evidência. Há também incumprimento da própria licença (obrigação de conformidade, 6.1.3) e do controlo operacional (8.1)."],
], [3400, 2600, 3638]));

// 8
content.push(h1("8. Atividade 6.3 — ISO 14001 e EMAS (enquadramento teórico)"));
content.push(p("As respostas aplicadas à Plasticom (os indicadores mais críticos e o receio da gestão sobre a transparência) estão no ficheiro SGA-16, folhas EMAS_Indicadores e EMAS_Transparencia. Síntese das diferenças:"));
content.push(table(["Tema", "ISO 14001:2026", "EMAS (Reg. (CE) 1221/2009)"], [
  ["Natureza", "Norma internacional voluntária; certificação por organismo acreditado.", "Regulamento europeu voluntário; registo público na APA após verificação por verificador acreditado."],
  ["Comunicação externa", "Decidida pela organização (auditoria 'fechada').", "Declaração Ambiental pública, validada e atualizada anualmente."],
  ["Desempenho", "Exige melhoria do SGA para melhorar o desempenho.", "Exige melhoria demonstrada do desempenho com indicadores principais (energia, materiais, água, resíduos, biodiversidade, emissões)."],
  ["Conformidade legal", "Compromisso de cumprir e avaliação da conformidade.", "Demonstração de conformidade legal; o regulador confirma a ausência de incumprimentos."],
  ["Trabalhadores", "Consulta e participação através da comunicação (7.4).", "Envolvimento ativo e documentado dos trabalhadores."],
  ["Relação", "—", "Inclui todos os requisitos da ISO 14001 (quem tem EMAS cumpre a ISO 14001, não o contrário)."],
], [1900, 3869, 3869]));
content.push(p("Indicadores principais do EMAS para a Plasticom (valores de set/2025 a ago/2026, ver SGA-16): eficiência energética (≈ 7.170 MWh; 55% renovável), eficiência dos materiais (≈ 826 t), água (≈ 9.400 m³), resíduos (≈ 131 t; 2,1 t perigosos), biodiversidade (4,5 ha de terreno, 3,2 ha impermeabilizados) e emissões (≈ 796 tCO2e; ≈ 1,2 t de COV). Os mais críticos para a Plasticom são a **energia** e os **materiais** (o polímero é o maior fluxo e define o PPWR), seguidos das **emissões** (GEE da eletricidade e COV da serigrafia) e dos **resíduos**."));

// 9
content.push(h1("9. Principais alterações da ISO 14001:2026 aplicadas neste SGA"));
content.push(table(["Cláusula", "Alteração", "Onde foi aplicada"], [
  ["4.1 / 4.2", "Condições ambientais obrigatórias no contexto (clima, poluição, recursos naturais, biodiversidade, saúde dos ecossistemas), nos dois sentidos.", "SGA-01 (colunas Condicao_Ambiental_ISO2026 e Direcao_Efeito)"],
  ["4.3 / 6.1.2", "Perspetiva de ciclo de vida reforçada; situações de emergência distinguidas das anormais.", "SGA-03 (fases do ciclo de vida; condição Emergência)"],
  ["6.1.4 / 6.1.5", "Riscos e oportunidades e planeamento de ações em subcláusulas próprias.", "SGA-02 e SGA-06"],
  ["6.3", "Novo requisito: planeamento de alterações.", "NC-SGA-26-06, PAM-26-17, decisão RG-26-D05, PR-SGA-06"],
  ["7.4 / 7.5", "Comunicação que permite aos trabalhadores contribuir para a melhoria; informação documentada 'disponível'.", "SGA-09 (COM-01, COM-08) e SGA-16 (Kaizen)"],
  ["8.1", "Controlar ou influenciar processos, produtos e serviços fornecidos externamente.", "SGA-11 (avaliação ponderada de fornecedores)"],
  ["9.1.1 / 9.2.2", "Avaliar desempenho e eficácia do SGA; objetivos definidos para cada auditoria.", "SGA-13, SGA-05 (progresso) e SGA-14 (coluna Objetivo)"],
  ["9.3", "Revisão pela gestão em 9.3.1 Generalidades, 9.3.2 Entradas e 9.3.3 Resultados.", "SGA-15 (agenda ligada às alíneas da 9.3.2 e decisões por tipo de resultado da 9.3.3)"],
  ["10", "Melhoria contínua (10.1) e não conformidade e ação corretiva (10.2) reorganizadas.", "SGA-06, SGA-07"],
], [1400, 4600, 3638]));

// 10
content.push(h1("10. Pressupostos e limitações"));
content.push(bullet("A Plasticom é uma fábrica simulada. Produção, rejeições, horas de marcha, máquinas, operadores e fornecedores vêm do dataset do projeto; os dados ambientais foram derivados com fatores documentados (SGA-13, folha Parametros) e os meses de mar–jun/2025 foram reconstruídos (marcados)."));
content.push(bullet("Números de relatórios, licenças e evidências legais são simulados para fins didáticos. A aplicabilidade legal deve ser confirmada em fontes oficiais (Diário da República, EUR-Lex); o número do regulamento europeu sobre perdas de granulado deve ser confirmado."));
content.push(bullet("O fator de emissão da eletricidade (0,110 kgCO2e/kWh) é uma aproximação e deve ser substituído pelo valor anual publicado."));
content.push(bullet("As videoaulas da plataforma não foram consultadas; foram usadas as apresentações em PDF dos OA 3.1 a 6.3 e os modelos do curso."));

const doc = new Document({
  creator: "Gestor(a) do SGA / EHS",
  title: "SGA Plasticom — Lusitana Móveis e questões teóricas",
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, font: FONT, color: HEAD }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 25, bold: true, font: FONT, color: "2F5F6F" }, paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Plasticom · SGA ISO 14001:2026 · DOC-SGA-01", size: 16, color: "6B7F86" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Página ", size: 16 }), new TextRun({ children: [PageNumber.CURRENT], size: 16 })] })] }) },
    children: content,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("ok", OUT); });
