"""RG-SGQ-14 — Controlo de saídas não conformes e concessões (ISO 9001:2026 8.7.1 a)–d), 8.7.2 a)–d)).
Cada não conformidade do dataset (fact_nonconformance) é ligada ao lote (disposição), ao cliente que recebeu o lote (fact_sales),
à CAPA (fact_capa) e à autoridade que decidiu."""
import datetime as dt
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

TRAT = ["a) Correção (retrabalho / triagem) com reverificação", "b) Segregação / sucata", "b) Devolução ao fornecedor", "b) Contenção (quarentena)",
        "c) Informação ao cliente", "d) Aceitação sob concessão"]


def dados():
    nc = Q.nonconformance()
    capa = Q.capa()
    lots = Q.lot_dispositions().set_index("Lote")
    rm = Q.rm_lots().set_index("MaterialLotId")
    sales = Q.rd("fact_sales_processed.csv")
    cli_wo = sales.groupby("WorkOrder").CustomerId.agg(lambda s: "; ".join(sorted(set(s))))
    capa_by_nc = capa.groupby("RelatedNCId").CAPAId.first()
    rows, conc = [], []
    kc = 0
    for r in nc.sort_values(["Date", "NCId"]).itertuples():
        rel = r.RelatedRecordId
        prod, qtd, natureza, disp, insp, wo = None, None, None, None, None, None
        if rel in lots.index:
            L = lots.loc[rel]
            if isinstance(L, pd.DataFrame):
                L = L.iloc[0]
            prod, qtd, disp, insp, wo = L.Produto, int(L.LotSize), L.DispositionDetail, L.Inspector, L.WorkOrder
            natureza = L.Remarks if L.Remarks != "—" else ("Característica por variáveis fora de controlo" if L.VariablesDecision == "Nonconforming" else "Defeitos acima do Ac")
        elif rel in rm.index:
            M = rm.loc[rel]
            if isinstance(M, pd.DataFrame):
                M = M.iloc[0]
            prod, qtd, insp = f"{M.Material} ({M.SupplierId})", int(M.ReceivedQtyKg), M.Inspector
            natureza = f"{int(M.CharacteristicsFailed)} de {int(M.CharacteristicsTested)} características fora de especificação"
            disp = {"Rejected": "RM-Rejected", "Accepted With Deviation": "RM-Deviation", "Accepted": "RM-Accepted"}[M.FinalDecision]
        src = r.Source
        if src == "Lot Concession/Deviation" or disp in ("Approved - Released on Deviation",):
            trat, acao, aut = TRAT[5], "Lote libertado por concessão com restrição de uso/cliente", GQ
        elif src == "Lot Rework" or disp == "Approved - Reworked":
            trat, acao, aut = TRAT[0], "Triagem 100% / retrabalho e reinspeção do lote", insp or INSP
        elif disp == "RM-Rejected":
            trat, acao, aut = TRAT[2], "Lote de MP devolvido; SCAR ao fornecedor", CMP_ + " + " + GQ
        elif disp == "RM-Deviation":
            trat, acao, aut = TRAT[5], "MP aceite por derrogação com ajuste de processo", GQ
        elif disp == "RM-Accepted" or src == "Incoming Inspection":
            trat, acao, aut = TRAT[3], "Quarentena até reensaio; aceite após reensaio", insp or TLAB
        elif src in ("Customer Complaint", "Customer Audit"):
            trat, acao, aut = TRAT[4], "Cliente informado; contenção do stock", GQ
        elif disp == "Rejected - Segregated":
            trat, acao, aut = TRAT[1], "Lote segregado para triagem; peças NC para moagem", insp or INSP
        else:
            trat, acao, aut = TRAT[1], "Lote rejeitado e enviado para moagem (sucata)", insp or INSP
        cid = None
        clientes = cli_wo.get(wo) if wo else None
        if trat == TRAT[5]:
            kc += 1
            cid = f"CONC-{kc:04d}"
            dnc = dt.date.fromisoformat(r.Date)
            precisa = "Sim" if clientes else "Não"
            aprov = None
            if precisa == "Sim":
                aprov = dnc + dt.timedelta(days=1 + kc % 3) if kc % 9 != 0 else None   # 1 em 9 sem aprovação do cliente (REL-26-03)
            conc.append(dict(ID_Concessao=cid, ID_NC=r.NCId, Data=dnc, Lote=rel, Produto=prod, Quantidade=qtd, Clientes_Lote=clientes,
                             Defeitos_Criticos=int(lots.loc[rel].CriticalDefects) if rel in lots.index and not isinstance(lots.loc[rel], pd.DataFrame) else 0,
                             Requer_Aprovacao_Cliente=precisa, Data_Aprovacao_Cliente=aprov, Restricao="Uso limitado ao cliente que aceitou; identificação 'CONCESSÃO' na palete",
                             Aprovado_Internamente_Por=GQ))
        rows.append(dict(ID_NC=r.NCId, Data_Detecao=dt.date.fromisoformat(r.Date), Mes=r.Date[:7], Tipo={"Internal": "Interna", "External": "Externa"}[r.Type],
                         Origem=Q.T_ORIGEM_NC.get(src, src), Local=Q.T_AREA.get(r.Area, r.Area), Processo=Q.T_PROC.get(r.Process, r.Process),
                         Categoria=Q.T_CAT_NC.get(r.Category, r.Category), Severidade=Q.T_SEV[r.Severity], Registo_Relacionado=rel, Produto_Material=prod,
                         Quantidade=qtd, Descricao=natureza, Tratamento=trat, Acao_Tomada=acao, Autoridade=aut, ID_Concessao=cid,
                         Reverificado="Sim" if trat == TRAT[0] else ("N.A." if trat != TRAT[0] else "Não"), Clientes_Lote=clientes, ID_CAPA=capa_by_nc.get(r.NCId)))
    return rows, conc


def build(out):
    rows, conc = dados()
    b = Book("RG-SGQ-14", "Controlo de Saídas Não Conformes e Concessões",
             activities="Identificar e controlar as saídas não conformes (produto, matéria-prima, após entrega), decidir o tratamento (a–d), registar a autoridade que decidiu e as concessões, e ligar à ação corretiva.",
             clauses="8.7.1 a) correção, b) segregação/contenção/devolução/suspensão, c) informação ao cliente, d) concessão; verificação após correção; 8.7.2 a)–d) (natureza, ações, concessões, autoridade); 8.6 (libertação só com aprovação da autoridade e, quando aplicável, do cliente)",
             purpose=f"Registo de TODAS as não conformidades do dataset entre {PER_INI} e {PER_FIM} ({len(rows)}), com o lote/material, a natureza, o tratamento 8.7.1 aplicado, a autoridade que decidiu, a reverificação, os clientes que receberam o lote e a CAPA; e registo das {len(conc)} concessões com o controlo da aprovação do cliente.",
             links=[("RG-SGQ-13 tbl_libertacao", "Disposição do lote."), ("RG-SGQ-18 tbl_capa", "Ação corretiva (ID_CAPA)."), ("RG-SGQ-12 tbl_scar", "Devoluções de MP a fornecedores."),
                    ("RG-SGQ-03 REL-26-03", "Caso de concessão sem autorização do cliente.")],
             guidance=[("ISO/TC 176 APG — Nonconformity (control of nonconforming outputs)", "Distinguir o tratamento da saída (8.7) da ação sobre a causa (10.2); evidência da autoridade que decide e da concessão."),
                       ("Academy — cap. 160 (5 Porquês, 8D, CAPA)", "Correção ≠ ação corretiva: a correção trata o lote; a CAPA elimina a causa."),
                       ("iso9001help.co.uk — Nonconforming outputs", "Registo com natureza, disposição, concessão e quem decidiu.")])
    b.add_list("Tratamento", TRAT)
    b.add_list("Severidade", ["Crítica", "Maior", "Menor"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("SimNaoNA", ["Sim", "Não", "N.A."])
    b.add_list("SimNao", ["Sim", "Não"])

    # nomes de coluna comuns ao RG-SGA-07 tbl_nc: ID_NC, Data_Detecao, Origem, Processo, Local, Descricao, Severidade, Controlo_Qualidade
    cols = [col("ID_NC", 9, key="PK", desc="NC (dataset)."), col("Data_Detecao", 11, "date", desc="Data de deteção."), col("Mes", 8, desc="aaaa-mm."), col("Tipo", 8, desc="Interna / externa."),
            col("Origem", 24, desc="Origem."), col("Local", 14, desc="Área / local de deteção."), col("Processo", 7, dv="Processo", desc="Processo."), col("Categoria", 26, desc="Categoria."),
            col("Severidade", 8, dv="Severidade", desc="Severidade."), col("Registo_Relacionado", 22, desc="Lote ou lote de MP (dataset)."), col("Produto_Material", 22, desc="Produto / material.", req=False),
            col("Quantidade", 9, "num0", desc="Quantidade do lote (un ou kg).", req=False), col("Descricao", 30, desc="Natureza da NC (8.7.2 a).", req=False),
            col("Tratamento", 30, dv="Tratamento", desc="Tratamento 8.7.1 a)–d)."), col("Acao_Tomada", 36, desc="Ações tomadas (8.7.2 b)."),
            col("Autoridade", 26, desc="Autoridade que decidiu (8.7.2 d)."), col("ID_Concessao", 10, desc="Concessão (8.7.2 c).", key="FK → tbl_concessoes", req=False),
            col("Reverificado", 8, dv="SimNaoNA", desc="Conformidade reverificada após correção (8.7.1)."), col("Clientes_Lote", 18, desc="Clientes que receberam o lote (fact_sales).", req=False),
            col("ID_CAPA", 10, desc="CAPA associada (fact_capa).", key="FK → RG-SGQ-18", req=False),
            col("Controlo_Qualidade", 22, f=('=IF(@ID_NC@="","",IF(@Autoridade@="","FALTA autoridade",IF(AND(LEFT(@Tratamento@,2)="a)",@Reverificado@<>"Sim"),"FALTA reverificação",'
                                    'IF(AND(LEFT(@Tratamento@,2)="d)",@ID_Concessao@=""),"FALTA concessão",IF(AND(@Severidade@<>"Menor",@ID_CAPA@=""),"Sem CAPA (avaliar 10.2)","OK")))))'),
                desc="Regras de 8.7.2 e ligação a 10.2.")]
    b.table("Registo_SNC", "tbl_snc", cols, rows, "Registo de saídas não conformes (8.7.2).",
            title="SAÍDAS NÃO CONFORMES — TRATAMENTO E AUTORIDADE (8.7)", subtitle=f"Todas as NC do dataset {PER_INI} a {PER_FIM} · Lote, disposição, clientes e CAPA ligados por ID · Controlo calculado",
            cf=[("Tratamento", {"concessão": "orange", "Correção": "yellow", "Devolução": "blue"}), ("Severidade", {"Crítica": "red", "Maior": "orange"}),
                ("Controlo_Qualidade", {"FALTA": "red", "Sem CAPA": "yellow", "OK": "green"})], row_height=15, freeze_col=1)

    ccols = [col("ID_Concessao", 10, key="PK", desc="Concessão."), col("ID_NC", 9, desc="NC.", key="FK → tbl_snc"), col("Data", 11, "date", desc="Data."), col("Lote", 22, desc="Lote."),
             col("Produto", 20, desc="Produto."), col("Quantidade", 9, "num0", desc="Quantidade."), col("Clientes_Lote", 18, desc="Clientes que receberam o lote.", req=False),
             col("Defeitos_Criticos", 7, "int", desc="Defeitos críticos na amostra."), col("Requer_Aprovacao_Cliente", 9, dv="SimNao", desc="O produto vai para cliente?"),
             col("Data_Aprovacao_Cliente", 11, "date", desc="Aprovação escrita do cliente (8.6; 8.7.1 d).", req=False), col("Restricao", 34, desc="Restrição de uso."),
             col("Aprovado_Internamente_Por", 20, desc="Autoridade interna."),
             col("Controlo_Qualidade", 26, f=('=IF(@ID_Concessao@="","",IF(AND(@Requer_Aprovacao_Cliente@="Sim",@Data_Aprovacao_Cliente@=""),"FALTA aprovação do cliente",'
                                    'IF(@Defeitos_Criticos@>0,"Defeito crítico — só com aprovação do cliente e da Direção","OK")))'), desc="Controlo das concessões.")]
    b.table("Concessoes", "tbl_concessoes", ccols, conc, "Concessões (aceitação de produto não conforme) com a aprovação do cliente (8.7.1 d; 8.7.2 c).",
            title="CONCESSÕES (8.7.1 d)", subtitle="Uma concessão sem aprovação do cliente é uma libertação não autorizada (8.6) · Defeitos críticos exigem aprovação da Direção",
            cf=[("Controlo_Qualidade", {"FALTA": "red", "crítico": "orange", "OK": "green"})], row_height=15)

    ws = b.sheet("Resumo_SNC", "Resumo mensal calculado por tratamento e controlo.")
    title(ws, "RESUMO DAS SAÍDAS NÃO CONFORMES — calculado")
    heads = ["Mês"] + [t.split(" (")[0].split(" / ")[0] for t in TRAT] + ["Total", "Críticas", "Com falhas de controlo"]
    header_row(ws, 3, heads, widths=[9] + [14] * len(TRAT) + [8, 8, 12])
    T = lambda c_: f"tbl_snc[{c_}]"
    for i, m in enumerate(MESES):
        r = 4 + i
        cell(ws, r, 1, m)
        for j, t in enumerate(TRAT):
            cell(ws, r, 2 + j, f'=COUNTIFS({T("Mes")},$A{r},{T("Tratamento")},"{t}")', fmt="0")
        cell(ws, r, 2 + len(TRAT), f'=COUNTIF({T("Mes")},$A{r})', fmt="0", bold=True)
        cell(ws, r, 3 + len(TRAT), f'=COUNTIFS({T("Mes")},$A{r},{T("Severidade")},"Crítica")', fmt="0")
        cell(ws, r, 4 + len(TRAT), f'=COUNTIFS({T("Mes")},$A{r},{T("Controlo_Qualidade")},"<>OK")', fmt="0")
    r = 4 + len(MESES)
    cell(ws, r, 1, "Total", bold=True)
    for c_ in range(2, 5 + len(TRAT)):
        L = get_column_letter(c_)
        cell(ws, r, c_, f"=SUM({L}4:{L}{r - 1})", fmt="0", bold=True)
    cell(ws, r + 2, 1, "Concessões sem aprovação do cliente", bold=True, border=False)
    cell(ws, r + 2, 5, '=COUNTIF(tbl_concessoes[Controlo_Qualidade],"FALTA*")', fmt="0", bold=True)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
