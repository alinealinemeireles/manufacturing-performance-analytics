"""RG-SGA-18 — Planeamento de alterações (ISO 14001:2026, cláusula 6.3 — nova).

tbl_alteracoes: uma linha por alteração (equipamento, processo, produto, material, requisito legal, organização, SGA), com a
checklist de avaliação do PR-SGA-06 em colunas Sim/Não/N.A., completude calculada e alerta de alterações implementadas sem avaliação.
"""
import datetime as dt
from sgalib import *
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None
SGA, DIND, DG, PROD, MAN, QUA, LOG, CMP, RD, RH, FIN = FUNC_NAMES[:11]
CHK = ["Aspetos_Ambientais", "Obrigacoes_Conformidade", "Riscos_Oportunidades", "Licenciamento_Comunicacao_Autoridade",
       "Competencias_Formacao", "Documentos_a_Atualizar", "Comunicacao_Partes_Interessadas", "Emergencia_e_Controlo_Operacional",
       "Fornecedores_Processos_Externos", "Recursos_e_Prazos"]
CHK_DESC = ["Os aspetos e impactes (normal, anormal, emergência) foram revistos? (6.1.2)",
            "As obrigações de conformidade foram identificadas e avaliadas? (6.1.3)",
            "Os riscos e oportunidades da alteração foram avaliados? (6.1.4)",
            "É necessária licença, comunicação ou avaliação legal prévia (ex.: SIR, ruído)?",
            "Foram definidas competências e formação para quem opera a alteração? (7.2, 7.3)",
            "Foram identificados os documentos a atualizar (procedimentos, IT, registos)? (7.5)",
            "Foram consultadas/informadas as partes interessadas relevantes? (4.2, 7.4)",
            "Foram revistos os controlos operacionais e os cenários de emergência? (8.1, 8.2)",
            "Há fornecedores ou processos externos afetados e com controlo definido? (8.1)",
            "Foram assegurados recursos, responsáveis e prazos? (7.1)"]

# (ID, data pedido, origem, tipo, descrição, motivo, requerente, checklist (10 × S/N/NA), impacto previsto, aspetos, legal, RO,
#  recursos €, aprovador, data aprovação, data implementação, verificação pós, data verificação, estado, lição aprendida)
# checklist: 10 respostas separadas por espaço (S = Sim, N = Não, NA = não aplicável), pela ordem de CHK
ALT = [
    ("ALT-2025-01", "2025-05-06", "Interna", "Material", "Introdução de tintas UV de baixo teor de solvente na SS-002 (ensaio).", "Reduzir COV e solvente de limpeza.", PROD,
     "S S S NA S S NA S S S", "Menos COV; novo resíduo de tinta UV.", "AA-014; AA-015", "LEG-04; LEG-06", "", 6500, DIND, "2025-05-20", "2025-06-15",
     "Consumo de solvente −9% no ensaio; FDS no posto.", "2025-09-30", "Verificada", "Avaliar a cura UV (energia) antes de alargar à SS-001."),
    ("ALT-2025-02", "2025-08-28", "Externa", "Material", "Troca do fornecedor de HDPE-PCR (SUP-004 como principal).", "Descontinuação do fornecedor anterior.", CMP,
     "S S S NA NA S NA S S S", "Qualidade do lote e declarações de conteúdo reciclado.", "AA-001", "LEG-09", "RO-05", 0, DIND, "2025-09-05", "2025-10-01",
     "Certificado RecyClass por lote verificado em 100% dos lotes de out–dez/2025.", "2026-01-15", "Verificada", "Exigir auditoria ao reciclador antes da troca."),
    ("ALT-2025-03", "2025-11-19", "Interna", "Equipamento", "Reparação do chiller CH-01 e recarga de R410A após fuga.", "Fuga detetada no controlo semestral (INC-2025-07).", MAN,
     "S S S S NA S NA S S S", "Emissão de GEE evitada; resíduos de gás recuperado.", "AA-025", "LEG-07", "", 1450, DIND, "2025-11-19", "2025-11-19",
     "Verificação pós-reparação conforme (OT-2025-20).", "2025-12-16", "Verificada", "Avaliar substituição por fluido de baixo GWP no fim de vida."),
    ("ALT-2026-01", "2026-01-12", "Interna", "Equipamento", "Substituição dos compressores CMP-01/02 por unidades de velocidade variável.", "Eficiência energética (OBJ-01).", MAN,
     "N N N S N N N N S S", "Menos energia; possível aumento do ruído noturno (novo ponto de descarga de ar).", "AA-021; AA-022", "LEG-02; LEG-05; LEG-08", "RO-12", 78000, DIND, "2026-01-20", "2026-02-02",
     "Poupança confirmada por M&V (−14,8% kWh/Nm³, RG-SGE-11); ruído conforme após barreira acústica (AC-2026-112, 28/10/2026).", "2026-11-05", "Verificada",
     "Alteração aprovada sem checklist ambiental: origem da NC-SGA-26-01 e do PR-SGA-06."),
    ("ALT-2026-02", "2026-02-24", "Interna", "Produto", "Lançamento das famílias FR-011/012-PET-400.", "Novos contratos de cosmética.", RD,
     "S S S NA S S S S S S", "Mais scrap no arranque; famílias a incluir na documentação PPWR.", "AA-011; AA-037; AA-038", "LEG-09", "RO-06", 42000, DG, "2026-03-06", "2026-04-01",
     "Scrap das primeiras semanas acima da média; famílias incluídas no OBJ-04.", "2026-07-15", "Verificada", "Prever corridas de afinação no plano de scrap."),
    ("ALT-2026-03", "2026-03-30", "Interna", "Processo", "Expansão das linhas alimentar e farmacêutica (potes e tampas).", "Estratégia comercial 2026.", DG,
     "S S S S S S S S S S", "Novos requisitos de contacto; mais energia; novos resíduos de limpeza.", "AA-007; AA-010; AA-042", "LEG-06; LEG-09", "RO-06", 185000, DG, "2026-04-20", "2026-06-01",
     "Checklist completa; auditoria de cliente farmacêutico sem constatações ambientais.", "2026-08-31", "Verificada", "Modelo de avaliação completa a replicar."),
    ("ALT-2026-04", "2026-06-10", "Interna", "SGA", "Revisão da política ambiental (rev. 02): biodiversidade e ciclo de vida.", "Transição para a ISO 14001:2026.", SGA,
     "NA NA NA NA S S S NA NA S", "", "", "", "", 0, DG, "2026-06-19", "2026-06-26", "Política comunicada; versão obsoleta retirada.", "2026-07-10", "Verificada", ""),
    ("ALT-2026-05", "2026-07-01", "Externa", "Requisito legal", "Aplicação do PPWR (Reg. (UE) 2025/40) desde 12/08/2026.", "Nova obrigação de conformidade.", RD,
     "S S S NA S S S S S S", "Documentação técnica e declaração UE de conformidade por família.", "AA-038", "LEG-09", "RO-06", 26000, DG, "2026-07-10", "2026-08-12",
     "17 de 22 famílias com documentação técnica e declaração UE em 22/12/2026; 5 famílias em 2027.", "", "Em implementação", ""),
    ("ALT-2026-06", "2026-08-20", "Interna", "Infraestrutura", "Filtros nas sarjetas e bacias de descarga (Operation Clean Sweep).", "Perdas de granulado (INC-2026-09).", SGA,
     "S S S NA S S NA S NA S", "Menos perdas de granulado para a rede pluvial.", "AA-003", "LEG-10", "RO-07", 9500, DIND, "2026-08-27", "2026-10-15",
     "Autoavaliação OCS de 15/12/2026: 11 de 14 pontos com contenção; rondas RON-09 com 10% de não conformidades (40% antes).", "2026-12-15", "Verificada", ""),
    ("ALT-2026-07", "2026-09-05", "Interna", "Infraestrutura", "Central fotovoltaica de autoconsumo (UPAC ≈ 1 MWp).", "Estratégia de descarbonização.", FIN,
     "S S S S N N S NA S S", "Menos emissões do âmbito 2; resíduos de obra; carga na cobertura.", "AA-031; AA-032", "LEG-02; LEG-08", "RO-09", 780000, "", "", "",
     "Estudo de viabilidade entregue a 30/11/2026 (≈ 1 400 MWh/ano); decisão de investimento e candidatura em 2027 (RD-E-26-D06).", "", "Em avaliação", ""),
    ("ALT-2026-08", "2026-09-24", "Externa", "SGA", "Transição do SGA para a ISO 14001:2026 (6.3, 8.1, 9.2.2, 9.3).", "Nova edição da norma.", SGA,
     "S NA S NA N S S S NA S", "", "", "", "", 3500, DG, "2026-09-24", "2026-11-25", "Formulário de alteração com checklist ambiental em uso desde 25/11/2026 (PAM-26-17).", "", "Implementada — por verificar", "Inclui a aprovação do PR-SGA-06 e deste registo."),
    ("ALT-2026-09", "2026-09-30", "Interna", "Processo", "Modo standby obrigatório das injetoras e ISBM nas pausas e paragens > 30 min (KZ-01).", "Eficiência energética (OBJ-01; SGE PA-E-03).", "Gerente de Produção",
     "S S NA NA S S S NA NA S", "Menos energia em vazio; sem efeito na qualidade (arranque validado).", "AA-007; AA-010", "LEG-08", "RO-02", 0, DIND, "2026-10-01", "2026-10-05",
     "Poupança verificada pelo SGE (MV-02: ≈ 36 MWh em out–dez/2026); rondas RON-10 com 7% de não conformidades.", "2026-12-20", "Verificada", "Primeira alteração com a checklist ambiental + energia."),
    ("ALT-2026-10", "2026-11-10", "Interna", "Equipamento", "Redução da pressão da rede de ar comprimido de 7,4 para 6,8 bar.", "Eficiência energética (SGE PA-E-02).", "Técnico de Utilidades",
     "S NA NA NA S S S NA NA S", "Menos energia e menos fugas; risco de falta de pressão em máquinas exigentes (validado).", "AA-021", "LEG-08", "RO-02", 0, DIND, "2026-11-12", "2026-11-16",
     "Sem queixas das máquinas; potência específica 0,106 kWh/Nm³ na semana de 07/12 (RG-SGE-11).", "2026-12-09", "Verificada", ""),
]


def parse_chk(s):
    out = [{"S": "Sim", "N": "Não", "NA": "N.A."}[t] for t in s.split()]
    assert len(out) == 10, s
    return out


def build(out):
    b = Book("RG-SGA-18", "Planeamento de Alterações (Gestão de Mudanças)", version="00", date=dt.date(2026, 9, 24),
             activities="Complemento ISO 14001:2026 (cláusula 6.3 nova) — não é atividade do curso.",
             clauses="6.3 Planeamento de alterações; 6.1.2; 6.1.3; 6.1.4; 7.5; 8.1",
             purpose=("Registar e avaliar, antes da implementação, cada alteração que afete ou possa afetar o SGA (equipamentos, processos, produtos, "
                      "materiais, requisitos legais, organização e o próprio SGA), com a checklist do PR-SGA-06, aprovação, verificação pós-implementação "
                      "e lições aprendidas — para que o SGA continue a atingir os resultados pretendidos."),
             links=[("PR-SGA-06", "Procedimento de planeamento de alterações (Documentos_SGA_Plasticom)."),
                    ("RG-SGA-03 Aspetos", "IDs_Aspetos → tbl_aspetos."), ("RG-SGA-04 Legal", "ID_Legal → tbl_legal."),
                    ("RG-SGA-02 Riscos e oportunidades", "ID_RO → coluna 'ID RO (SGA)' de tbRiscos/tbOportunidades."),
                    ("RG-SGA-07 NC", "Alterações sem avaliação que geraram NC (ex.: ALT-2026-01 → NC-SGA-26-01).")])
    b.add_list("Origem", ["Interna", "Externa"])
    b.add_list("TipoAlteracao", ["Equipamento", "Processo", "Produto", "Material", "Infraestrutura", "Requisito legal", "Organizacional", "SGA"])
    b.add_list("Resposta", ["Sim", "Não", "N.A."])
    b.add_list("EstadoAlt", ["Em avaliação", "Aprovada", "Em implementação", "Implementada — por verificar", "Verificada", "Rejeitada"])
    b.add_list("Funcao", FUNC_NAMES)
    chk_cols = [col(c, 11, dv="Resposta", desc=q) for c, q in zip(CHK, CHK_DESC)]
    rng = [f"@{c}@" for c in CHK]
    sim = "+".join(f'({x}="Sim")' for x in rng)
    nao = "+".join(f'({x}="Não")' for x in rng)
    cols = [
        col("ID_Alteracao", 11, desc="Identificador (ALT-AAAA-nn).", key="PK"),
        col("Data_Pedido", 11, "date", desc="Data do pedido."),
        col("Origem", 9, dv="Origem", desc="Interna ou externa (Nota 1 da 6.3)."),
        col("Tipo", 14, dv="TipoAlteracao", desc="Tipo de alteração."),
        col("Descricao", 44, desc="Alteração proposta."),
        col("Motivo", 30, desc="Motivo / necessidade."),
        col("Requerente", 24, dv="Funcao", desc="Quem pede."),
    ] + chk_cols + [
        col("N_Sim", 6, "int", f=f'=IF(@ID_Alteracao@="","",{sim})', desc="Perguntas respondidas com Sim."),
        col("N_Nao", 6, "int", f=f'=IF(@ID_Alteracao@="","",{nao})', desc="Perguntas respondidas com Não (lacunas de avaliação)."),
        col("Completude_Checklist", 9, "pct", f='=IF(@ID_Alteracao@="","",IFERROR(@N_Sim@/(@N_Sim@+@N_Nao@),""))', desc="Sim ÷ (Sim + Não)."),
        col("Impacto_Ambiental_Previsto", 34, desc="Efeitos ambientais previstos.", req=False),
        col("IDs_Aspetos", 16, desc="Aspetos afetados.", key="FK → tbl_aspetos", req=False),
        col("ID_Legal", 16, desc="Requisitos legais afetados.", key="FK → tbl_legal", req=False),
        col("ID_RO", 8, desc="Risco/oportunidade.", key="FK → RG-SGA-02", req=False),
        col("Recursos_EUR", 11, "eur", desc="Investimento/custo previsto."),
        col("Aprovador", 24, dv="Funcao", desc="Quem aprova.", req=False),
        col("Data_Aprovacao", 11, "date", desc="Data de aprovação.", req=False),
        col("Data_Implementacao", 11, "date", desc="Data de implementação.", req=False),
        col("Verificacao_Pos_Implementacao", 36, desc="Resultado da verificação após a implementação.", req=False),
        col("Data_Verificacao", 11, "date", desc="Data da verificação.", req=False),
        col("Estado", 18, dv="EstadoAlt", desc="Estado."),
        col("Licao_Aprendida", 34, desc="Lição aprendida.", req=False),
        col("Dias_Pedido_Aprovacao", 8, "int", f='=IF(OR(@Data_Aprovacao@="",@Data_Pedido@=""),"",@Data_Aprovacao@-@Data_Pedido@)', desc="Tempo de decisão (dias)."),
        col("Alerta", 22, f=('=IF(@ID_Alteracao@="","",IF(AND(@Data_Implementacao@<>"",N(@N_Nao@)>0),"Implementada com avaliação incompleta",'
                              'IF(AND(@Data_Implementacao@<>"",@Data_Verificacao@=""),"Verificação pós em falta",IF(AND(@Data_Implementacao@="",@Data_Aprovacao@=""),"A aguardar decisão","OK"))))'),
            desc="Alerta de gestão da mudança."),
    ]
    rows = []
    for a in ALT:
        (i, dp, og, tp, de, mo, rq, chk, imp, asp, leg, ro, eur, apr, dap, dim, ver, dver, est, lic) = a
        x = dict(ID_Alteracao=i, Data_Pedido=d(dp), Origem=og, Tipo=tp, Descricao=de, Motivo=mo, Requerente=rq, Impacto_Ambiental_Previsto=imp or None,
                 IDs_Aspetos=asp or None, ID_Legal=leg or None, ID_RO=ro or None, Recursos_EUR=eur, Aprovador=apr or None, Data_Aprovacao=d(dap),
                 Data_Implementacao=d(dim), Verificacao_Pos_Implementacao=ver or None, Data_Verificacao=d(dver), Estado=est, Licao_Aprendida=lic or None)
        x.update(dict(zip(CHK, parse_chk(chk))))
        rows.append(x)
    b.table("Alteracoes", "tbl_alteracoes", cols, rows,
            "Registo de alterações com a checklist de avaliação do PR-SGA-06, aprovação e verificação pós-implementação (1 linha por alteração).",
            title="PLANEAMENTO DE ALTERAÇÕES — REGISTO E AVALIAÇÃO (ISO 14001:2026, 6.3)",
            subtitle="Checklist em colunas (Sim / Não / N.A.) · Uma alteração implementada com respostas 'Não' gera alerta · ALT-2026-01 originou a NC-SGA-26-01 (ruído)",
            cf=[("Alerta", {"incompleta": "red", "falta": "orange", "aguardar": "yellow", "OK": "green"}),
                ("Estado", {"Verificada": "green", "por verificar": "orange", "Rejeitada": "gray"})] + [(c, {"Não": "red"}) for c in CHK],
            row_height=48, extra_rows=40, freeze_col=1)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
