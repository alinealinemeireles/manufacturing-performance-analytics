import datetime as dt
import os
import pandas as pd
from sgalib import *
from dims import *
from envdata import ROOT
import sga_extra as X

DAV = dt.date(2026, 7, 20)

CRIT = [
    ("CRIT-01", "Conteúdo reciclado certificado por terceiros (EuCertPlast, RecyClass ou ISCC PLUS) ou declaração de origem e rastreabilidade de lote (resina virgem)", 0.25, "Aquisição de matéria-prima", "Sim",
     "0 sem declaração · 1 declaração própria · 2 declaração com rastreabilidade de lote · 3 certificação por terceiros"),
    ("CRIT-02", "Sistema de gestão ambiental certificado (ISO 14001) ou EMAS", 0.20, "Aquisição (processo do fornecedor)", "Não",
     "0 nenhum · 1 em implementação · 2 certificado sem objetivos publicados · 3 certificado/EMAS com objetivos e desempenho publicados"),
    ("CRIT-03", "Prevenção de perdas de granulado (Operation Clean Sweep ou certificação ao abrigo do regulamento UE)", 0.15, "Aquisição e transporte", "Sim",
     "0 nenhuma medida · 1 compromisso OCS · 2 OCS com auditoria interna · 3 certificação por terceiros"),
    ("CRIT-04", "Pegada de carbono do produto (kgCO2e/kg, ISO 14067 ou EPD)", 0.15, "Aquisição de matéria-prima", "Não",
     "0 sem dados · 1 dado genérico · 2 PCF declarado · 3 PCF verificado por terceiros ou EPD"),
    ("CRIT-05", "Distância e modo de transporte até à Plasticom", 0.10, "Transporte", "Não",
     "0 > 5.000 km marítimo+rodoviário · 1 > 1.500 km · 2 Península Ibérica > 300 km · 3 ≤ 300 km"),
    ("CRIT-06", "Embalagem retornável / logística reversa (big bags, octabins, paletes)", 0.10, "Transporte e fim de vida da embalagem", "Não",
     "0 embalagem descartável · 1 reciclável · 2 retornável em parte · 3 sistema retornável implementado"),
    ("CRIT-07", "Conformidade de produto: FDS REACH atualizadas e declaração de metais pesados/substâncias (PPWR)", 0.05, "Aquisição e uso", "Não",
     "0 sem FDS · 1 FDS desatualizada · 2 FDS atualizada · 3 FDS + declaração PPWR/contacto alimentar"),
]
SCORES = {  # SUP: (c1..c7), distancia_km, modo, volume_t, criticidade
    "SUP-001": ((2, 3, 3, 2, 0, 1, 3), 8200, "Marítimo + rodoviário", 95, "Alta"),
    "SUP-002": ((3, 3, 3, 3, 1, 2, 3), 2150, "Rodoviário", 160, "Alta"),
    "SUP-003": ((2, 3, 2, 1, 0, 1, 3), 8300, "Marítimo + rodoviário", 70, "Média"),
    "SUP-004": ((3, 3, 2, 2, 1, 2, 3), 1900, "Marítimo curto + rodoviário", 100, "Alta"),
    "SUP-005": ((1, 1, 0, 0, 0, 0, 1), 11800, "Marítimo + rodoviário", 60, "Alta"),
    "SUP-006": ((2, 3, 3, 2, 1, 2, 3), 1850, "Rodoviário", 90, "Média"),
    "SUP-007": ((2, 3, 2, 2, 2, 2, 3), 950, "Rodoviário", 120, "Alta"),
    "SUP-008": ((2, 2, 1, 1, 3, 3, 3), 175, "Rodoviário", 25, "Média"),
    "SUP-009": ((2, 2, 1, 1, 0, 1, 3), 7900, "Marítimo + rodoviário", 30, "Média"),
    "SUP-010": ((3, 3, 2, 2, 2, 2, 3), 600, "Rodoviário", 45, "Alta"),
}
EVID = {
    "CRIT-01": {3: "Certificado EuCertPlast/RecyClass válido", 2: "Declaração de origem com n.º de lote", 1: "Declaração do fornecedor sem rastreabilidade", 0: "Sem evidência"},
    "CRIT-02": {3: "Certificado ISO 14001 + relatório de sustentabilidade", 2: "Certificado ISO 14001 válido", 1: "Declaração de implementação", 0: "Sem evidência"},
    "CRIT-03": {3: "Certificado de auditoria OCS por terceiros", 2: "Compromisso OCS + auditoria interna", 1: "Carta de compromisso OCS", 0: "Sem medidas"},
    "CRIT-04": {3: "PCF verificado / EPD", 2: "PCF declarado", 1: "Valor genérico de base de dados", 0: "Sem dados"},
    "CRIT-05": {3: "≤ 300 km", 2: "Península Ibérica", 1: "Europa > 1.500 km", 0: "Fora da Europa"},
    "CRIT-06": {3: "Octabins retornáveis", 2: "Big bags retornáveis em parte", 1: "Embalagem reciclável", 0: "Embalagem descartável"},
    "CRIT-07": {3: "FDS + declaração PPWR/contacto alimentar", 2: "FDS atualizada", 1: "FDS com mais de 3 anos", 0: "Sem FDS"},
}

OUTROS = [
    ("TRP-01", "Transportes Lis (distribuição a clientes)", "Transportador", "Frota Euro VI ou superior; consolidação de cargas e reporte de tCO2e/t.km", "Idade média da frota; licença de transporte; relatório anual de emissões", "Emissões do transporte (fase Distribuição)"),
    ("OGR-01", "Recicladora de plásticos (scrap e filme)", "Operador de gestão de resíduos", "Licença válida para os códigos LER entregues; operação de reciclagem R3", "Licença; e-GAR confirmadas; certificado de reciclagem", "Fim de vida: resíduo convertido em matéria-prima secundária"),
    ("OGR-06", "Operador de resíduos perigosos", "Operador de gestão de resíduos", "Licença para 08 03 12*, 15 01 10*, 15 02 02*; valorização preferencial (R13→R1/R2)", "Licença; e-GAR; destino final", "Fim de vida dos resíduos perigosos"),
    ("LIM-01", "Empresa de limpeza industrial", "Prestador de serviços", "Uso de produtos com rótulo ecológico; formação em segregação de resíduos", "Lista de produtos e FDS; registo de formação", "Operação: químicos e resíduos gerados nas instalações"),
]


def build(out):
    sup = pd.read_csv(os.path.join(ROOT, "datasets", "dim", "dim_supplier.csv"), encoding="utf-8-sig")
    b = Book("RG-SGA-11", "Avaliação Ambiental de Fornecedores e Perspetiva de Ciclo de Vida",
             activities="Atividade 4.4 — Critérios Ambientais na Seleção de Fornecedores (fornecedor crítico: SUP-004 TransAtlantic Polymers, HDPE-PCR e rPET; critérios CRIT-01 e CRIT-03).",
             clauses="8.1 Planeamento e controlo operacional — controlar ou influenciar processos, produtos e serviços fornecidos externamente (ISO 14001:2026); 6.1.2 (perspetiva de ciclo de vida); 4.3",
             purpose="Definir critérios ambientais ponderados para selecionar e avaliar fornecedores, registar a pontuação por critério com evidência e classificar cada fornecedor (A/B/C) com decisão de compra. Liga a escolha do fornecedor à fase a montante do ciclo de vida do produto.",
             links=[("Dataset da fábrica", "IDs SUP-xxx de datasets/dim/dim_supplier.csv (permite cruzar com reclamações a fornecedores e lotes fora de especificação)."),
                    ("RG-SGA-02 Riscos", "RO-05 (qualidade/alegações de PCR) é tratado por esta avaliação (PAM-26-16).")])
    b.add_list("Criticidade", ["Alta", "Média", "Baixa"])
    b.add_list("Score", [0, 1, 2, 3])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("TipoFornecedor", ["Resina / matéria-prima", "Masterbatch", "Transportador", "Operador de gestão de resíduos", "Prestador de serviços", "Fornecedor de produtos químicos"])

    ccols = [col("ID_Criterio", 9, desc="Critério.", key="PK"), col("Criterio", 60, desc="Critério ambiental."), col("Peso", 7, "pct", desc="Peso na pontuação."),
             col("Fase_Ciclo_Vida", 24, desc="Fase do ciclo de vida influenciada."), col("Selecionado_Atv_4_4", 10, dv="SimNao", desc="Um dos 2 critérios da Atividade 4.4."),
             col("Escala_0a3", 60, desc="Como pontuar (0 a 3).")]
    b.table("Criterios", "tbl_criterios", ccols, [dict(zip([c["name"] for c in ccols], c)) for c in CRIT], "Critérios ambientais ponderados (soma dos pesos = 100%).",
            cf=[("Selecionado_Atv_4_4", {"Sim": "purple"})], row_height=45)

    frows = []
    for _, s in sup.iterrows():
        sc, dist, modo, vol, crit = SCORES[s.SupplierId]
        frows.append(dict(ID_Fornecedor=s.SupplierId, Nome=s.SupplierName, Pais=s.Country, Materiais=s.MaterialsSupplied,
                          Tipo="Masterbatch" if "Masterbatch" in s.MaterialsSupplied else "Resina / matéria-prima", Tipo_Contrato=s.ContractType,
                          Anos_Fornecedor=int(s.YearsAsSupplier), Criticidade=crit, Distancia_km=dist, Modo_Transporte=modo, Volume_t_ano=vol))
    fcols = [
        col("ID_Fornecedor", 10, desc="ID do fornecedor (dataset).", key="PK"), col("Nome", 30, desc="Nome."), col("Pais", 12, desc="País."),
        col("Materiais", 18, desc="Materiais fornecidos."), col("Tipo", 18, dv="TipoFornecedor", desc="Tipo."), col("Tipo_Contrato", 18, desc="Tipo de contrato."),
        col("Anos_Fornecedor", 9, "int", desc="Anos como fornecedor."), col("Criticidade", 9, dv="Criticidade", desc="Criticidade ambiental/negócio."),
        col("Distancia_km", 10, "num0", desc="Distância até à Plasticom (km)."), col("Modo_Transporte", 20, desc="Modo de transporte."),
        col("Volume_t_ano", 9, "num0", desc="Volume anual comprado (t)."),
        col("tCO2e_Transporte_Est", 11, "num1", f='=@Volume_t_ano@*@Distancia_km@*IF(ISNUMBER(SEARCH("Marítimo +",@Modo_Transporte@)),0.016,IF(ISNUMBER(SEARCH("Marítimo curto",@Modo_Transporte@)),0.04,0.075))/1000', desc="Estimativa de emissões do transporte (t.km × fator: rodoviário 0,075; misto marítimo 0,016; marítimo curto 0,04 kgCO2e/t.km)."),
        col("Pontuacao", 9, "pct", f='=SUMIF(tbl_avaliacao_fornecedor[ID_Fornecedor],@ID_Fornecedor@,tbl_avaliacao_fornecedor[Pontos_Ponderados])', desc="Pontuação ponderada (0-100%)."),
        col("Classe", 7, f='=IF(@Pontuacao@>=0.75,"A",IF(@Pontuacao@>=0.5,"B","C"))', desc="A ≥ 75%; B 50-74%; C < 50%."),
        col("Decisao", 22, f='=IF(@Classe@="A","Aprovado",IF(@Classe@="B","Aprovado com plano de melhoria","Condicionado: reduzir compras / substituir"))', desc="Decisão de compra."),
        col("Criterio_Mais_Fraco", 12, f='=IFERROR(INDEX(tbl_avaliacao_fornecedor[ID_Criterio],MATCH(@ID_Fornecedor@&"|"&_xlfn.MINIFS(tbl_avaliacao_fornecedor[Score],tbl_avaliacao_fornecedor[ID_Fornecedor],@ID_Fornecedor@),tbl_avaliacao_fornecedor[Chave],0)),"")', desc="Critério com menor pontuação (prioridade de melhoria)."),
        col("Data_Avaliacao", 11, "date", desc="Data da avaliação."), col("Proxima_Avaliacao", 11, "date", f='=EDATE(@Data_Avaliacao@,IF(@Classe@="C",6,12))', desc="Reavaliação: 6 meses (C) ou 12 meses."),
    ]
    fcols += X.forn_cols()
    X.outros_lists(b)
    for r in frows:
        r["Data_Avaliacao"] = DAV
        r.update(dict(zip(["IDs_Aspetos", "Tipo_Controlo", "Extensao_Controlo"], X.FORN_CTRL[r["ID_Fornecedor"]])))
    b.table("Fornecedores", "tbl_fornecedores", fcols, frows, "Fornecedores de resina e masterbatch com pontuação, classe e decisão calculadas.",
            title="AVALIAÇÃO AMBIENTAL DE FORNECEDORES — PLASTICOM", subtitle="Pontuação = Σ (score 0-3 ÷ 3 × peso) · Classe A ≥ 75% · B 50-74% · C < 50%",
            cf=[("Classe", {"A": "green", "B": "yellow", "C": "red"})], row_height=30, freeze_col=2)
    arows = []
    for sid, (sc, *_rest) in SCORES.items():
        for (cid, *_c), s in zip(CRIT, sc):
            arows.append(dict(ID_Fornecedor=sid, ID_Criterio=cid, Score=s, Evidencia=EVID[cid][s], Data=DAV, Avaliador="Responsável de Compras + Gestor do SGA"))
    acols = [col("ID_Fornecedor", 10, desc="Fornecedor.", key="FK → tbl_fornecedores"), col("ID_Criterio", 9, desc="Critério.", key="FK → tbl_criterios"),
             col("Score", 7, "int", dv="Score", desc="Pontuação 0-3."),
             col("Peso", 7, "pct", f='=INDEX(tbl_criterios[Peso],MATCH(@ID_Criterio@,tbl_criterios[ID_Criterio],0))', desc="Peso do critério."),
             col("Pontos_Ponderados", 10, "pct1", f='=@Score@/3*@Peso@', desc="Score ÷ 3 × peso."),
             col("Evidencia", 40, desc="Evidência recolhida."), col("Data", 11, "date", desc="Data."), col("Avaliador", 30, desc="Avaliadores."),
             col("Chave", 12, f='=@ID_Fornecedor@&"|"&@Score@', desc="Chave técnica (fornecedor|score).")]
    b.table("Avaliacao_Fornecedor", "tbl_avaliacao_fornecedor", acols, arows, "Pontuação por fornecedor × critério (formato longo, com evidência).",
            cf=[("Score", "@=0", "red"), ("Score", "@=3", "green")])

    ocols = [col("ID", 8, desc="Identificador.", key="PK"), col("Fornecedor", 34, desc="Fornecedor/prestador."), col("Tipo", 26, dv="TipoFornecedor", desc="Tipo."),
             col("Criterios_Ambientais", 50, desc="Critérios ambientais exigidos."), col("Evidencia_Exigida", 40, desc="Evidência."), col("Fase_Ciclo_Vida", 36, desc="Fase influenciada.")]
    base_names = [c["name"] for c in ocols]
    ocols += X.outros_cols()
    b.table("Outros_Fornecedores", "tbl_outros_fornecedores", ocols, X.outros_rows(OUTROS, base_names),
            "Transportadores, operadores de resíduos e prestadores de serviços: critérios ambientais e tipo/extensão do controlo (ISO 14001:2026 8.1).",
            cf=[("Resultado", {"Não conforme": "red", "reservas": "orange", "Conforme": "green", "Por verificar": "yellow"}),
                ("Alerta", {"Ação": "red", "vencida": "orange", "Sem": "yellow", "OK": "green"})], row_height=40, extra_rows=10)

    ws = b.sheet("Resumo_Atividade_4_4", "Ficha da Atividade 4.4 para o fornecedor crítico SUP-004 (calculada).", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 4.4 — CRITÉRIOS AMBIENTAIS NA SELEÇÃO DE FORNECEDORES"
    ws["A1"].font = F_TITLE
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 100
    F = lambda f: b.ref("tbl_fornecedores", f)
    m = f'MATCH("SUP-004",{F("ID_Fornecedor")},0)'
    r = 3
    form_block(ws, r, "Fornecedor crítico", f'=INDEX({F("ID_Fornecedor")},{m})&" — "&INDEX({F("Nome")},{m})&" ("&INDEX({F("Materiais")},{m})&", "&INDEX({F("Pais")},{m})&")"', vw=1); r += 1
    form_block(ws, r, "Porque é crítico", "Fornece o HDPE-PCR e o rPET das gamas com conteúdo reciclado (≈ 100 t/ano): a qualidade e a origem do reciclado determinam o scrap, as alegações ambientais aos clientes e o cumprimento das metas do PPWR.", vw=1, height=45); r += 1
    C = lambda f: b.ref("tbl_criterios", f)
    for k, cid in enumerate(["CRIT-01", "CRIT-03"], 1):
        mc = f'MATCH("{cid}",{C("ID_Criterio")},0)'
        form_block(ws, r, f"Critério {k}", f'=INDEX({C("Criterio")},{mc})', vw=1, height=32); r += 1
        form_block(ws, r, f"Porquê (critério {k})", ["Garante que o material é realmente reciclado e rastreável (evita alegações falsas — Diretiva (UE) 2024/825) e que o PCR tem qualidade estável, reduzindo scrap e energia desperdiçada.",
                                                      "Garante que o fornecedor não perde granulado para o ambiente no fabrico, no enchimento de big bags e no transporte (microplásticos a montante), antecipando o regulamento europeu de granulados."][k - 1], vw=1, height=45); r += 1
    form_block(ws, r, "Pontuação / classe / decisão", f'=TEXT(INDEX({F("Pontuacao")},{m}),"0%")&" — Classe "&INDEX({F("Classe")},{m})&" — "&INDEX({F("Decisao")},{m})', vw=1); r += 1
    form_block(ws, r, "Impacto no ciclo de vida",
               "Ao comprar PCR certificado a um fornecedor com prevenção de perdas de granulado, a fase de 'Aquisição de matéria-prima' (a montante) passa a usar menos recurso fóssil virgem e menos energia (o PCR tem pegada ≈ 50-70% inferior ao virgem) e deixa de gerar microplásticos. A embalagem que a Plasticom vende passa a ter conteúdo reciclado comprovado, o que ajuda o cliente a cumprir o PPWR e fecha o ciclo no 'Fim de Vida' (a embalagem usada volta a ser matéria-prima).",
               vw=1, height=90); r += 1
    form_block(ws, r, "Logística reversa (auto-estudo)", "Com o SUP-004 foi acordado devolver os big bags vazios na viagem de retorno do camião (critério CRIT-06): o fornecedor reutiliza-os até 5 vezes, o que evita ≈ 1,2 t/ano de resíduo 15 01 02 na Plasticom.", vw=1, height=45)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
