import datetime as dt
from sgalib import *
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None

# (ID, Cenario, Local, Causas, Impacte, Aspeto, P(1-3), G(1-3), Prevencao, Meios, IT, Resp, Comunicacao, Freq_simulacro)
CEN = [
    ("EMG-01", "Derrame de produtos químicos (tintas, solventes, óleos)", "Armazém de químicos; serigrafia; oficina",
     "Queda na movimentação; rotura de embalagem; trasfega sem bacia", "Contaminação do solo e da água (rede pluvial → rio Lis); emissão de COV; resíduo perigoso",
     "AA-005; AA-017", 2, 3, "Bacias de retenção; recipientes fechados; kits selados; formação FOR-03", "Kits antipoluição KIT-01 a KIT-05; tampões de sarjeta; EPI",
     "IT-SGA-01", "Chefe de turno + Gestor do SGA", "Interna imediata; entidade gestora e APA se atingir a rede", "Semestral"),
    ("EMG-02", "Incêndio no armazém de matérias-primas / granulado", "Armazém de MP e silos",
     "Curto-circuito; trabalho a quente; propagação de incêndio rural", "Fumos tóxicos; águas de combate contaminadas; dano à floresta envolvente",
     "AA-034", 1, 3, "Deteção automática; SCIE; faixa de gestão de combustível; licença de trabalhos a quente", "Extintores; RIA; válvula de corte pluvial VC-01; bacia de retenção de águas de combate",
     "IT-SGA-02", "Chefe de emergência", "112 / bombeiros; ANEPC; vizinhos; APA", "Anual"),
    ("EMG-03", "Fuga de óleo hidráulico em máquina", "Injeção e sopro (ISBM-005)",
     "Mangueira envelhecida; vedante; sobrepressão", "Contaminação do solo; resíduo perigoso", "AA-009; AA-013", 2, 2,
     "Manutenção por horas de operação; tabuleiros de retenção", "Absorventes; tabuleiro; kit KIT-02", "IT-SGA-01", "Técnico de Manutenção", "Interna", "Anual"),
    ("EMG-04", "Fuga de gás fluorado (chiller CH-01)", "Utilidades", "Corrosão; vibração; falha de brasagem", "Emissão de GEE (R410A, GWP 2088)",
     "AA-025", 1, 2, "Controlo de fugas semestral por técnico certificado", "Detetor de fugas; contacto do técnico certificado", "—", "Gerente de Manutenção", "Interna; registo do equipamento", "—"),
    ("EMG-05", "Descarga anómala de efluente (biocida da torre)", "Torre de arrefecimento TR-01", "Sobredosagem de biocida; purga descontrolada",
     "Contaminação do coletor e da ETAR municipal", "AA-024", 1, 2, "Dosagem automática com alarme", "Válvula de fecho da purga; recipientes para amostra", "—", "Técnico de Utilidades",
     "Entidade gestora da drenagem", "Anual"),
    ("EMG-06", "Perda massiva de granulado (big bag rasgado no exterior)", "Zona de descarga de big bags", "Rasgo do big bag; manobra de empilhador",
     "Microplásticos na rede pluvial e no meio aquático", "AA-003", 2, 2, "Tabuleiros de descarga; filtros de sarjeta", "Aspirador industrial; vassouras; tampões de sarjeta", "IT-SGA-01", "Operador de Armazém / Empilhador", "Interna", "Anual"),
]

IT_PASSOS = [
    ("1. Alerta", "Dar o alerta: gritar 'DERRAME!' e avisar o chefe de turno (ext. 222). Se houver fogo, cheiro forte ou feridos, ligar 112 e ativar o alarme.", "Quem deteta", 1, "Telefone interno / botoneira"),
    ("2. Proteção", "Afastar pessoas e fontes de ignição (parar máquinas próximas, não fumar, não usar telemóvel junto a solventes). Consultar a FDS do produto.", "Quem deteta + chefe de turno", 2, "FDS no ponto de uso"),
    ("3. Proteção", "Vestir o EPI do kit: luvas nitrílicas, óculos, máscara se o produto for volátil.", "Equipa de 1.ª intervenção", 2, "EPI do kit antipoluição"),
    ("4. Parar a fonte", "Se for seguro: levantar o recipiente, fechar a válvula ou colocar o recipiente danificado dentro de uma bacia.", "Equipa de 1.ª intervenção", 3, "Bacia de retenção móvel"),
    ("5. Contenção", "Tapar as sarjetas e ralos próximos com o tampão do kit e rodear o derrame com as barreiras absorventes (do exterior para o interior).", "Equipa de 1.ª intervenção", 5, "Tampões de sarjeta; barreiras"),
    ("6. Absorção", "Cobrir o líquido com almofadas/granulado absorvente até não haver líquido livre. Não usar água.", "Equipa de 1.ª intervenção", 10, "Almofadas e granulado absorvente"),
    ("7. Recolha", "Recolher o absorvente com a pá antifaísca para o saco/contentor do kit; fechar e etiquetar como LER 15 02 02* (ou 08 03 12* para tinta).", "Equipa de 1.ª intervenção", 20, "Pá antifaísca; sacos; etiquetas LER"),
    ("8. Encaminhamento", "Colocar o contentor no parque de resíduos perigosos (em bacia, fechado) e informar o Responsável de Armazém.", "Operador + Responsável de Armazém", 30, "Parque de resíduos perigosos"),
    ("9. Comunicação", "Se o produto chegou à rede pluvial ou ao solo não impermeável: fechar a válvula de corte VC-01, avisar o Gestor do SGA, que comunica à entidade gestora/APA.", "Chefe de turno + Gestor do SGA", 30, "Válvula de corte VC-01; lista de contactos"),
    ("10. Pós-uso (obrigatório)", "Registar o incidente (formulário INC), pedir a reposição do kit ao armazém e voltar a selar o kit com selo numerado. O kit nunca fica incompleto.", "Quem usou o kit + Responsável de Armazém", 60, "Formulário INC; stock mínimo de 2 kits; selos numerados"),
    ("11. Investigação", "O Gestor do SGA investiga a causa (5 Porquês) e abre ação no PAM se necessário.", "Gestor do SGA", 2880, "RG-SGA-07 / RG-SGA-06"),
]

MEIOS = [
    ("KIT-01", "Kit antipoluição 120 L", "Armazém de químicos", "EMG-01", "2026-12-14", "Completo e selado (selo 00412)"),
    ("KIT-02", "Kit antipoluição 60 L", "Oficina de manutenção", "EMG-03", "2026-12-14", "Completo e selado (selo 00413)"),
    ("KIT-03", "Kit antipoluição 60 L", "Zona injeção/serigrafia", "EMG-01", "2026-12-14", "Completo e selado (selo 00447); verificação mensal com registo pós-uso (IT-SGA-01 rev. 01)"),
    ("KIT-04", "Kit antipoluição 60 L", "Serigrafia SS-002", "EMG-01", "2026-12-14", "Completo e selado (selo 00415)"),
    ("KIT-05", "Kit antipoluição 60 L", "Parque de resíduos", "EMG-01", "2026-12-14", "Completo e selado (selo 00416)"),
    ("VC-01", "Válvula de corte da rede pluvial", "Caixa de saída pluvial (portão sul)", "EMG-02", "2026-12-11", "Operacional; manobra em 4 min no simulacro de 11/12/2026"),
    ("BR-01", "Bacia de retenção de águas de combate (300 m³)", "Logradouro sul", "EMG-02", "2026-12-11", "Seca e limpa"),
    ("TMP-01", "Tampões de sarjeta magnéticos (6 un.)", "Armazém de químicos / kits", "EMG-01", "2026-12-14", "Em bom estado"),
]

SIM = [
    ("SIM-2025-01", "2025-11-14", "EMG-02", "Incêndio no armazém de MP", 48, 6, 9, "Evacuação em 6 min (meta ≤ 8 min). Válvula de corte fechada em 9 min (meta ≤ 5 min): chave guardada na portaria.", "Parcialmente eficaz", "PAM-26-21"),
    ("SIM-2026-01", "2026-03-20", "EMG-06", "Big bag rasgado na zona de descarga", 6, None, 25, "Granulado recolhido em 25 min; 1 sarjeta sem filtro.", "Parcialmente eficaz", "PAM-26-11"),
    ("SIM-2026-02", "2026-11-26", "EMG-01", "Derrame de 20 L de solvente no armazém de químicos", 14, None, 7, "Contenção com o KIT-01 em 7 min (meta ≤ 10 min); tampões de sarjeta colocados; registo pós-uso da IT-SGA-01 rev. 01 cumprido.", "Eficaz", "PAM-26-21"),
    ("SIM-2026-03", "2026-12-11", "EMG-02", "Incêndio no armazém de MP com retenção das águas de combate", 52, 5, 4, "Evacuação em 5 min; VC-01 fechada em 4 min (meta ≤ 5 min) com a chave na caixa junto à portaria; BR-01 disponível.", "Eficaz", "PAM-26-21"),
]


def build(out):
    b = Book("RG-SGA-12", "Preparação e Resposta a Emergências Ambientais",
             activities="Atividade 4.5 — Definição de Cenário de Emergência e Resposta: cenário EMG-01 (derrame de produtos químicos), Instrução de Trabalho IT-SGA-01 rev. 01 e equipamento crítico (kit antipoluição).",
             clauses="8.2 Preparação e resposta a emergências (alinhada com 6.1.2 — situações de emergência potenciais, ISO 14001:2026); 7.2; 7.4",
             purpose="Identificar os cenários de emergência ambiental credíveis, avaliá-los, definir prevenção, meios e resposta (instrução de trabalho passo a passo com tempos-alvo), inventariar os meios críticos e registar simulacros com tempos reais para avaliar a eficácia.",
             links=[("RG-SGA-03 Aspetos", "Aspetos em condição de emergência (AA-005, AA-017, AA-034...)."), ("RG-SGA-07 NC", "NC-SGA-26-03 (kit) e NC-SGA-26-09 (simulacros) originaram a revisão 01 da IT-SGA-01.")])
    b.add_list("Escala13", [1, 2, 3])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Fase", ["1. Alerta", "2. Proteção", "3. Proteção", "4. Parar a fonte", "5. Contenção", "6. Absorção", "7. Recolha", "8. Encaminhamento", "9. Comunicação", "10. Pós-uso (obrigatório)", "11. Investigação"])
    b.add_list("ResultadoSim", ["Eficaz", "Parcialmente eficaz", "Não eficaz", "Planeado"])

    ccols = [col("ID_Cenario", 8, desc="Cenário.", key="PK"), col("Cenario", 34, desc="Cenário de emergência."), col("Local", 24, desc="Onde."),
             col("Causas", 30, desc="Causas prováveis."), col("Impacte_Potencial", 36, desc="Impacte ambiental potencial."),
             col("IDs_Aspetos", 12, desc="Aspetos associados.", key="FK → RG-SGA-03"),
             col("Probabilidade", 8, "int", dv="Escala13", desc="1 remota – 3 frequente."), col("Gravidade", 8, "int", dv="Escala13", desc="1 local/contida – 3 externa/grave."),
             col("Criticidade", 8, "int", f="=@Probabilidade@*@Gravidade@", desc="P × G (1-9)."),
             col("Prioridade", 9, f='=IF(@Criticidade@>=6,"Alta",IF(@Criticidade@>=3,"Média","Baixa"))', desc="Prioridade do cenário."),
             col("Prevencao", 36, desc="Medidas preventivas."), col("Meios_Resposta", 36, desc="Meios de resposta."),
             col("Instrucao_Trabalho", 10, desc="IT aplicável."), col("Responsavel", 24, desc="Quem coordena."),
             col("Comunicacao", 30, desc="A quem comunicar."), col("Freq_Simulacro", 10, desc="Frequência de simulacro."),
             col("Ultimo_Simulacro", 11, "date", f='=IFERROR(IF(_xlfn.MAXIFS(tbl_simulacros[Data],tbl_simulacros[ID_Cenario],@ID_Cenario@,tbl_simulacros[Resultado],"<>Planeado")=0,"",_xlfn.MAXIFS(tbl_simulacros[Data],tbl_simulacros[ID_Cenario],@ID_Cenario@,tbl_simulacros[Resultado],"<>Planeado")),"")', desc="Data do último simulacro realizado."),
             col("Alerta", 22, f='=IF(@Freq_Simulacro@="—","",IF(OR(@Ultimo_Simulacro@="",@Ultimo_Simulacro@=0),"Nunca testado",IF(DataRef-@Ultimo_Simulacro@>IF(@Freq_Simulacro@="Semestral",183,365),"Simulacro em atraso","OK")))', desc="Alerta de teste periódico (8.2)."),
             col("Selecionado_Atv_4_5", 9, desc="Cenário da Atividade 4.5.")]
    cn = [c["name"] for c in ccols if not c["f"]]
    rows = []
    for c in CEN:
        dd = dict(zip([n for n in cn if n != "Selecionado_Atv_4_5"], c))
        dd["Selecionado_Atv_4_5"] = "Sim" if c[0] == "EMG-01" else "Não"
        rows.append(dd)
    b.table("Cenarios", "tbl_cenarios", ccols, rows, "Cenários de emergência ambiental avaliados (P × G) com meios, IT e alerta de simulacro.",
            title="CENÁRIOS DE EMERGÊNCIA AMBIENTAL — PLASTICOM", subtitle="Criticidade = Probabilidade × Gravidade · Alerta calculado face à frequência de simulacro",
            cf=[("Prioridade", {"Alta": "red", "Média": "yellow", "Baixa": "green"}), ("Alerta", {"Nunca": "red", "atraso": "orange", "OK": "green"}),
                ("Selecionado_Atv_4_5", {"Sim": "purple"})], row_height=70, freeze_col=2)

    pcols = [col("ID_IT", 9, desc="Instrução de trabalho.", key="FK"), col("Passo", 6, "int", desc="N.º do passo."), col("Fase", 20, dv="Fase", desc="Fase da resposta."),
             col("Acao", 80, desc="O que fazer."), col("Responsavel", 30, desc="Quem."), col("Tempo_Alvo_min", 9, "int", desc="Tempo-alvo acumulado desde o alerta (min)."),
             col("Recurso", 34, desc="Equipamento/material necessário.")]
    prow = [dict(ID_IT="IT-SGA-01", Passo=k + 1, Fase=f, Acao=a, Responsavel=r, Tempo_Alvo_min=t, Recurso=m) for k, (f, a, r, t, m) in enumerate(IT_PASSOS)]
    b.table("IT_Passos", "tbl_it_passos", pcols, prow, "Passos da IT-SGA-01 rev. 01 em formato de tabela (base da instrução impressa).", row_height=45)

    mcols = [col("ID_Meio", 8, desc="Meio de resposta.", key="PK"), col("Descricao", 36, desc="Equipamento."), col("Localizacao", 30, desc="Onde está."),
             col("ID_Cenario", 9, desc="Cenário.", key="FK → tbl_cenarios"), col("Ultima_Verificacao", 11, "date", desc="Última verificação (ronda)."),
             col("Estado", 50, desc="Estado na última verificação."),
             col("Dias_desde_Verif", 9, "int", f="=DataRef-@Ultima_Verificacao@", desc="Dias desde a verificação."),
             col("Alerta", 14, f='=IF(@Dias_desde_Verif@>31,"Verificar","OK")', desc="Verificação mensal no mínimo.")]
    b.table("Meios_Resposta", "tbl_meios", mcols, [dict(ID_Meio=m[0], Descricao=m[1], Localizacao=m[2], ID_Cenario=m[3], Ultima_Verificacao=d(m[4]), Estado=m[5]) for m in MEIOS],
            "Inventário de meios críticos de resposta e estado da última verificação.", cf=[("Alerta", {"Verificar": "red", "OK": "green"})], row_height=30)

    scols = [col("ID_Simulacro", 11, desc="Simulacro.", key="PK"), col("Data", 11, "date", desc="Data."), col("ID_Cenario", 9, desc="Cenário.", key="FK → tbl_cenarios"),
             col("Descricao", 36, desc="Situação simulada."), col("Participantes", 9, "int", desc="N.º participantes.", req=False),
             col("Tempo_Evacuacao_min", 10, "int", desc="Tempo de evacuação (min).", req=False), col("Tempo_Contencao_min", 10, "int", desc="Tempo até contenção / fecho da válvula (min).", req=False),
             col("Licoes_Aprendidas", 50, desc="Resultados e lições."), col("Resultado", 14, dv="ResultadoSim", desc="Resultado."), col("ID_PAM", 10, desc="Ação resultante.", key="FK → RG-SGA-06")]
    b.table("Simulacros", "tbl_simulacros", scols, [dict(ID_Simulacro=s[0], Data=d(s[1]), ID_Cenario=s[2], Descricao=s[3], Participantes=s[4], Tempo_Evacuacao_min=s[5],
                                                        Tempo_Contencao_min=s[6], Licoes_Aprendidas=s[7], Resultado=s[8], ID_PAM=s[9]) for s in SIM],
            "Registo de simulacros com tempos medidos (eficácia da resposta).", cf=[("Resultado", {"Não": "red", "Parcial": "orange", "Eficaz": "green", "Planeado": "gray"})], row_height=45)

    # Instrução de trabalho impressa
    ws = b.sheet("IT-SGA-01_Derrames", "Instrução de Trabalho IT-SGA-01 rev. 01 — Resposta a derrames de produtos químicos (formato de impressão/fórum).", tab_color="C00000")
    doc_header(ws, "IT-SGA-01", "INSTRUÇÃO DE TRABALHO — RESPOSTA A DERRAMES DE PRODUTOS QUÍMICOS", "IT-SGA-01 rev. 01", 6)
    for L, w in zip("ABCDEF", (7, 20, 70, 26, 10, 28)):
        ws.column_dimensions[L].width = w
    r = 5
    for lab, txt in [("Objetivo", "Conter, recolher e comunicar qualquer derrame de tinta, solvente, óleo ou outro químico, evitando que chegue ao solo, à rede pluvial ou ao rio Lis."),
                     ("Âmbito", "Armazém de químicos, serigrafia, hot foil, oficina de manutenção, injeção, sopro e parque de resíduos. Derrames até ≈ 200 L; acima disso ou com fogo: ativar o Plano de Emergência Interno (112)."),
                     ("Cenário", "EMG-01 — Derrame de produtos químicos (aspetos AA-005 e AA-017, condição de EMERGÊNCIA)."),
                     ("Equipamento crítico", "KIT ANTIPOLUIÇÃO (selado): 12 almofadas absorventes, 2 barreiras, granulado absorvente, tampão de sarjeta, pá antifaísca, sacos e etiquetas LER, luvas nitrílicas, óculos, máscara, esta instrução. Localização: KIT-01 a KIT-05 (ver planta)."),
                     ("Alteração rev. 01", "Acrescentado o passo 10 (pós-uso obrigatório: registar, repor, selar) e a verificação semanal do selo e conteúdo — resposta à NC-SGA-26-03.")]:
        form_block(ws, r, lab, txt, lw=2, vw=4, height=48)
        r += 1
    r += 1
    header_row(ws, r, ["Passo", "Fase", "O que fazer", "Quem", "Até (min)", "Recurso"])
    P = lambda f: b.ref("tbl_it_passos", f)
    for k in range(len(IT_PASSOS)):
        r += 1
        for j, fld in enumerate(["Passo", "Fase", "Acao", "Responsavel", "Tempo_Alvo_min", "Recurso"]):
            c = ws.cell(row=r, column=j + 1, value=f'=INDEX({P(fld)},{k + 1})')
            c.font, c.border = Font(name=FONT, size=10, bold=(j == 1)), BORDER
            c.alignment = CENTER if j in (0, 4) else WRAP_TOP
            if k == 9:
                c.fill = PatternFill("solid", fgColor=CF_COLORS["yellow"][0])
        ws.row_dimensions[r].height = 48
    r += 2
    for lab, txt in [("NUNCA", "Lavar o derrame com água para a sarjeta · deixar o kit incompleto ou sem selo · misturar absorventes contaminados com lixo comum."),
                     ("Contactos", "Chefe de turno ext. 222 · Gestor do SGA 912 000 101 · Portaria (válvula de corte VC-01) ext. 200 · Emergência 112."),
                     ("Aprovação", "Elaborado: Gestor do SGA/EHS · Aprovado: Diretor Industrial · Data: 23/09/2026 · Substitui: rev. 00 (24/05/2024)")]:
        form_block(ws, r, lab, txt, lw=2, vw=4, height=36)
        r += 1
    ws.page_setup.orientation = "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
