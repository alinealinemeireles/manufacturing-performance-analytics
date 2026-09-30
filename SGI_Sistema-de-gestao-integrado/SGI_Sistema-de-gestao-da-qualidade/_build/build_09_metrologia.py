"""RG-SGQ-09 — Metrologia: inventário de equipamentos de medição, confirmação metrológica, calibrações, fora de tolerância e MSA.
ISO 9001:2026 7.1.5.1 (evidência de adequação), 7.1.5.2 a)–c) e avaliação retrospetiva quando o equipamento não é apto; 8.5.1 b).
ISO 10012:2026 (sistema de gestão da medição: requisitos metrológicos, confirmação metrológica, adequação ao uso, risco de decisão).
Gage R&R com os dados reais do estudo GRR-CAP-WEIGHT-001 (dataset) calculado por fórmulas (método da média e amplitude, AIAG MSA)."""
import datetime as dt
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

# inventário: (prefixo, equipamento, tipo de confirmação, locais [(local, processo)], característica, tolerância da característica (±, na unidade), unidade,
#              resolução, EMA, U típica, intervalo meses, laboratório)
INV = [
    ("BAL1", "Balança 0,01 g", "Calibração externa", [("ISBM-001", "SOP"), ("ISBM-003", "SOP"), ("ISBM-005", "SOP"), ("ISBM-006", "SOP"), ("ISBM-009", "SOP"), ("Laboratório", "LAB")],
     "Peso do frasco", 0.9, "g", 0.01, 0.05, 0.012, 12, "Lab. acreditado L0045"),
    ("BAL3", "Balança analítica 0,001 g", "Calibração externa", [("Laboratório", "LAB"), ("IM-002", "INJ"), ("IM-007", "INJ")], "Peso da tampa", 0.9, "g", 0.001, 0.005, 0.0015, 12, "Lab. acreditado L0045"),
    ("PAQ", "Paquímetro digital 0–150 mm", "Calibração externa", [("Laboratório", "LAB"), ("Posto sopro", "SOP"), ("Posto injeção", "INJ"), ("Receção", "REC")],
     "Altura / diâmetro", 0.30, "mm", 0.01, 0.03, 0.012, 12, "Lab. acreditado L0112"),
    ("CAL", "Calibre passa/não passa de gargalo e rosca", "Verificação interna", [("24/410", "LAB"), ("28/410", "LAB"), ("28/415", "LAB"), ("38/400 (potes)", "LAB")],
     "Diâmetro do gargalo / rosca", 0.20, "mm", None, 0.01, 0.003, 12, "Verificação interna com blocos-padrão calibrados"),
    ("ESP", "Medidor de espessura por ultrassons", "Calibração externa", [("Laboratório", "LAB"), ("ISBM-003", "SOP")], "Espessura de parede", 0.10, "mm", 0.01, 0.02, 0.008, 12, "Lab. acreditado L0112"),
    ("PRV", "Proveta graduada 1 000 ml classe A", "Verificação interna", [("Laboratório", "LAB"), ("Laboratório 2", "LAB")], "Volume de transbordo", 15, "ml", 5, 5, 1.5, 36, "Verificação gravimétrica interna"),
    ("LKT", "Equipamento de ensaio de estanquidade", "Verificação interna", [("Laboratório", "LAB"), ("ISBM-009", "SOP"), ("ISBM-010", "SOP")], "Estanquidade (fuga)", None, "mbar", 0.1, 1.0, 0.3, 6,
     "Verificação com fuga calibrada (padrão rastreável)"),
    ("D65", "Cabine de luz D65", "Verificação interna", [("Laboratório", "LAB"), ("Posto sopro", "SOP"), ("Posto decoração", "SER")], "Defeitos visuais e cor", None, "lux", 10, 100, 30, 12,
     "Luxímetro calibrado + horas das lâmpadas"),
    ("TRQ", "Torquímetro digital de tampas", "Calibração externa", [("Laboratório", "LAB"), ("Posto injeção", "INJ")], "Binário de abertura / força de remoção", 4.0, "N·cm", 0.1, 0.4, 0.12, 12, "Lab. acreditado L0203"),
    ("TBT", "Equipamento de ensaio do anel de inviolabilidade", "Calibração externa", [("Laboratório", "LAB")], "Força de rotura das pontes", 5.0, "N", 0.1, 0.5, 0.15, 12, "Lab. acreditado L0203"),
    ("MIG", "Célula de migração + balança de resíduo", "Verificação interna", [("Laboratório", "LAB")], "Migração global", 2.0, "mg/dm²", 0.1, 0.5, 0.2, 12, "Verificação com ensaio interlaboratorial"),
    ("UTM", "Máquina universal de ensaios", "Calibração externa", [("Laboratório", "LAB")], "Carga de empilhamento / tensão", 20, "kgf", 0.1, 1.0, 0.3, 12, "Lab. acreditado L0203"),
    ("DRP", "Banco de ensaio de queda ASTM D2463", "Verificação interna", [("Laboratório", "LAB")], "Altura de queda", 50, "mm", 1, 5, 2, 24, "Verificação dimensional interna"),
    ("COL", "Colorímetro", "Calibração externa", [("Laboratório", "LAB")], "Cor (ΔE)", 1.0, "ΔE", 0.01, 0.1, 0.04, 12, "Fabricante (placas de referência)"),
    ("MFI", "Plastómetro (índice de fluidez)", "Calibração externa", [("Laboratório de receção", "REC")], "MFI da resina", 0.10, "g/10 min", 0.001, 0.01, 0.004, 12, "Lab. acreditado L0301"),
    ("KFT", "Titulador Karl Fischer", "Verificação interna", [("Laboratório de receção", "REC")], "Humidade da resina", 150, "ppm", 1, 15, 5, 6, "Padrão de água certificado"),
    ("DEN", "Coluna de densidade", "Verificação interna", [("Laboratório de receção", "REC")], "Densidade", 0.004, "g/cm³", 0.0001, 0.0004, 0.00015, 12, "Esferas-padrão certificadas"),
    ("TH", "Termo-higrómetro", "Calibração externa", [("Nave de sopro (TH-01)", "SOP"), ("Armazém de resinas (TH-02)", "REC")], "Temperatura / humidade ambiente", 2.0, "°C", 0.1, 0.5, 0.2, 12, "Lab. acreditado L0045"),
]


def inventario():
    rows, hist = [], []
    k = 0
    base = dt.date(2025, 10, 1)
    for pref, eq, tipo, locais, carac, tol, un, res, ema, u, inter, lab in INV:
        for j, (loc, proc) in enumerate(locais, 1):
            k += 1
            eid = f"EQM-{k:03d}"
            last = base + dt.timedelta(days=(k * 37) % 330)
            if inter == 6:
                last = dt.date(2026, 4, 1) + dt.timedelta(days=(k * 11) % 120)
            estado_uso = "Em uso"
            if eid == "EQM-004":             # balança da ISBM-006: fora de tolerância em mai/2026, ajustada e recalibrada (OOT-26-01)
                last, inter = dt.date(2026, 5, 13), 6
            if eid in ("EQM-022", "EQM-031"):  # vencidos (constatação de auditoria)
                last = dt.date(2025, 8, 5) if inter == 12 else dt.date(2025, 12, 1)
            if eid == "EQM-043":
                estado_uso = "Fora de serviço"
            # fecho do ano (31/12/2026): confirmações seguintes realizadas no prazo; EQM-022/031 recalibrados após a CON-Q-26-04
            seguintes = []
            if eid in ("EQM-022", "EQM-031"):
                seguintes.append(dt.date(2026, 9, 24) if eid == "EQM-022" else dt.date(2026, 10, 2))
            nxt = pd.Timestamp(seguintes[-1] if seguintes else last) + pd.DateOffset(months=inter)
            while nxt.date() <= dt.date(2026, 12, 31):
                seguintes.append((nxt - pd.Timedelta(days=3 + k % 6)).date())
                nxt = pd.Timestamp(seguintes[-1]) + pd.DateOffset(months=inter)
            anterior = last
            if seguintes:
                last = seguintes[-1]
            rows.append(dict(ID_Equipamento=eid, Codigo_Interno=f"{pref}-{j:02d}", Equipamento=eq, Tipo_Controlo=tipo, Local=loc, Processo=proc, Caracteristica=carac,
                             Tolerancia_Mais_Menos=tol, Unidade=un, Resolucao=res, EMA=ema, Periodicidade_Meses=inter, Ultima_Calibracao=last,
                             Entidade=lab, Estado_Uso=estado_uso))
            # histórico: 2 confirmações por equipamento
            if eid == "EQM-004":
                hist.append(dict(ID_Calibracao="CAL-004-0", ID_Equipamento=eid, Data=dt.date(2026, 5, 12), Certificado="C-2605-004A", Entidade=lab.split(" (")[0],
                                 Erro_Max_Encontrado=round(ema * 1.6, 6), Incerteza_U=u, EMA=ema))
            for n, dd in enumerate([anterior - dt.timedelta(days=int(inter * 30.4)), anterior] + seguintes[:-1] + ([last] if seguintes else [])):
                erro = round(ema * (0.15 + 0.1 * ((k + n) % 5)), 6) if ema else None
                uu = u
                if eid == "EQM-019" and n == 1:   # decisão com banda de guarda: erro dentro do EMA mas erro + U fora
                    erro = round(ema - uu / 2, 6)
                hist.append(dict(ID_Calibracao=f"CAL-{eid[4:]}-{n + 1}", ID_Equipamento=eid, Data=dd, Certificado=f"{'C' if tipo.startswith('Cal') else 'V'}-{dd:%y%m}-{k:03d}",
                                 Entidade=lab.split(" (")[0], Erro_Max_Encontrado=erro, Incerteza_U=uu, EMA=ema))
    return rows, hist


def build(out):
    b = Book("RG-SGQ-09", "Metrologia: Confirmação Metrológica, Calibração e MSA",
             activities="Manter o inventário de equipamentos de monitorização e medição, planear e registar a calibração/verificação, decidir a conformidade metrológica, avaliar o impacto de equipamento fora de tolerância e demonstrar a adequação do sistema de medição (MSA).",
             clauses="7.1.5.1 a) b) e informação documentada como evidência de adequação; 7.1.5.2 a) calibração/verificação rastreável, b) identificação do estado, c) proteção contra ajustes, e avaliação da validade de resultados anteriores; 8.5.1 b); 9.1.1 b)",
             purpose="Registo do sistema de gestão da medição da Plasticom segundo a ISO 10012:2026: inventário com requisitos metrológicos (tolerância da característica, EMA, relação de incerteza), estado de confirmação calculado, histórico de calibrações com regra de decisão com banda de guarda, avaliações retrospetivas de fora de tolerância e o estudo Gage R&R real do peso das tampas calculado por fórmulas.",
             links=[("RG-SGQ-13 Plano de controlo", "Equipamento de cada característica do plano de controlo."), ("RG-SGA-13", "Equipamentos de medição ambiental (SGI)."),
                    ("dataset fact_gage_rr_study", "Dados brutos do estudo GRR-CAP-WEIGHT-001 (tbl_grr_dados).")],
             guidance=[("ISO 10012:2026 (Academy cap. 59)", "Calibração válida ≠ sistema de medição adequado: requisito metrológico derivado da tolerância, confirmação metrológica, MSA proporcional ao risco e reação a medição não fiável."),
                       ("AIAG MSA 4.ª ed. / Academy cap. 60–61, 163, 175", "Gage R&R pelo método da média e amplitude (K1 = 0,5908; K2 = 0,5231; K3 = 0,3146 para 3 ensaios, 3 avaliadores, 10 peças); critérios %GRR < 10% aceitável, 10–30% condicional; ndc ≥ 5; MSA por atributos (kappa)."),
                       ("ISO 14253-1 (regra de decisão)", "Conforme se |erro| + U ≤ EMA (banda de guarda); 'Indeterminado' se |erro| ≤ EMA < |erro| + U."),
                       ("ISO/TC 176 APG — Resources (monitoring and measuring)", "O auditor segue um instrumento do posto até ao certificado e ao padrão nacional; verifica a avaliação retrospetiva quando está fora de tolerância.")])
    b.add_list("TipoConf", ["Calibração externa", "Verificação interna"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("EstadoUso", ["Em uso", "Fora de serviço", "Abatido"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("EstadoMSA", ["Concluído", "Planeado", "Em curso"])

    inv, hist = inventario()
    cols = [col("ID_Equipamento", 9, key="PK", desc="ID único."), col("Codigo_Interno", 9, desc="Etiqueta no equipamento (identificação do estado, 7.1.5.2 b)."),
            col("Equipamento", 30, desc="Equipamento."), col("Tipo_Controlo", 14, dv="TipoConf", desc="Calibração externa rastreável ou verificação interna."),
            col("Local", 18, desc="Local de uso."), col("Processo", 7, dv="Processo", desc="Processo."), col("Caracteristica", 26, desc="Característica medida (requisito do cliente/plano de controlo)."),
            col("Tolerancia_Mais_Menos", 9, "num3", desc="Meia-tolerância da característica (±), na unidade.", req=False), col("Unidade", 8, desc="Unidade."),
            col("Resolucao", 8, "num3", desc="Resolução do equipamento.", req=False), col("EMA", 8, "num3", desc="Erro máximo admissível (requisito metrológico, ISO 10012)."),
            col("Periodicidade_Meses", 8, "int", desc="Intervalo de confirmação."), col("Ultima_Calibracao", 11, "date", desc="Data da última calibração/verificação."),
            col("Entidade", 30, desc="Laboratório acreditado ou método de verificação (rastreabilidade)."), col("Estado_Uso", 11, dv="EstadoUso", desc="Estado de uso."),
            col("Proxima_Calibracao", 11, "date", f='=IF(@ID_Equipamento@="","",EDATE(@Ultima_Calibracao@,@Periodicidade_Meses@))', desc="Última + intervalo."),
            col("Ultimo_Resultado", 12, f='=IFERROR(INDEX(tbl_calibracoes[Decisao],MATCH(@ID_Equipamento@&"|"&@Ultima_Calibracao@,tbl_calibracoes[Chave],0)),"Sem registo")',
                desc="Decisão da última confirmação (tbl_calibracoes)."),
            col("Estado", 14, f=('=IF(@ID_Equipamento@="","",IF(@Estado_Uso@<>"Em uso",@Estado_Uso@,IF(@Ultimo_Resultado@="Não conforme","Bloqueado — NC",'
                                              'IF(@Proxima_Calibracao@<DataRef,"Vencido",IF(@Proxima_Calibracao@<=DataRef+30,"A vencer (30 d)","Válido")))))'),
                desc="Estado para identificação no posto (7.1.5.2 b)."),
            col("Rel_Tolerancia_EMA", 9, "num1", f='=IF(@Tolerancia_Mais_Menos@="","",IFERROR(@Tolerancia_Mais_Menos@/@EMA@,""))', desc="Tolerância ÷ EMA (recomendado ≥ 4; ideal ≥ 10).")]
    b.table("Inventario_Equipamentos", "tbl_equipamentos", cols, inv,
            "Inventário de equipamentos de monitorização e medição com requisitos metrológicos e estado de confirmação calculado (7.1.5; ISO 10012:2026).",
            title="INVENTÁRIO DE EQUIPAMENTOS DE MEDIÇÃO E CONFIRMAÇÃO METROLÓGICA (7.1.5 · ISO 10012:2026)",
            subtitle="Derivado dos planos de controlo do dataset · EMA = requisito metrológico · Estado calculado à data de referência · Vermelho = não usar",
            cf=[("Estado", {"Vencido": "red", "Bloqueado": "red", "A vencer": "orange", "Válido": "green", "Fora": "gray"}),
                ("Rel_Tolerancia_EMA", "AND(@<>\"\",@<4)", "orange")], row_height=30, freeze_col=2)

    hcols = [col("ID_Calibracao", 12, key="PK", desc="Registo de calibração/verificação."), col("ID_Equipamento", 9, desc="Equipamento.", key="FK → tbl_equipamentos"),
             col("Data", 11, "date", desc="Data."), col("Chave", 16, f='=@ID_Equipamento@&"|"&@Data@', desc="Chave técnica."),
             col("Certificado", 14, desc="N.º do certificado / relatório."), col("Entidade", 26, desc="Laboratório ou verificação interna."),
             col("Erro_Max_Encontrado", 10, "num3", desc="Maior erro encontrado (valor absoluto).", req=False), col("Incerteza_U", 9, "num3", desc="Incerteza expandida U (k = 2)."),
             col("EMA", 8, "num3", desc="Erro máximo admissível."),
             col("Decisao", 13, f='=IF(@Erro_Max_Encontrado@="","Verificado OK",IF(ABS(@Erro_Max_Encontrado@)+@Incerteza_U@<=@EMA@,"Conforme",IF(ABS(@Erro_Max_Encontrado@)<=@EMA@,"Indeterminado","Não conforme")))',
                 desc="Regra de decisão com banda de guarda (ISO 14253-1)."),
             col("Ajustado", 8, dv="SimNao", desc="Houve ajuste? (7.1.5.2 c: proteção contra ajustes não autorizados)", req=False)]
    for h in hist:
        h["Ajustado"] = "Sim" if h["ID_Equipamento"] == "EQM-004" and h["Data"] > dt.date(2026, 1, 1) else "Não"
    b.table("Calibracoes", "tbl_calibracoes", hcols, hist, "Histórico de calibrações e verificações com decisão de conformidade metrológica.",
            cf=[("Decisao", {"Não conforme": "red", "Indeterminado": "orange", "Conforme": "green"})], row_height=16)

    oot = [("OOT-26-01", "EQM-004", "2026-05-12", "Balança 0,01 g da ISBM-006 com erro de 0,08 g (EMA 0,05 g) na calibração anual",
            "2026-01-10 a 2026-05-12", "Recalculadas as decisões de peso dos lotes da ISBM-006 com a correção de −0,08 g: 0 lotes mudam de decisão (folga mínima 0,21 g face ao LSL).",
            "Nenhum lote afetado; cliente não notificado", "Ajuste e recalibração; intervalo reduzido para 6 meses; ligação ao relato REL-26-02", GQ, "Fechada"),
           ("OOT-26-02", "EQM-022", "2026-09-17", "Proveta graduada da linha 2 com verificação vencida (constatação de auditoria)",
            "2025-08-05 a 2026-09-17", "Verificação gravimétrica feita no dia: erro 1,2 ml (EMA 5 ml). Resultados anteriores válidos.", "Nenhum", "Plano de verificação no calendário do laboratório", GQ, "Fechada"),
           ("OOT-26-03", "EQM-031", "2026-09-17", "Equipamento de ensaio de estanquidade da ISBM-009 com verificação semestral vencida",
            "2026-06-01 a 2026-09-17", "Verificação com fuga calibrada: deteta 100% das fugas-padrão. Lotes farma libertados válidos.", "Nenhum; CUST-017 informado por transparência",
            "Alerta automático de vencimento no MES", GQ, "Em curso")]
    ocols = [col("ID_OOT", 9, key="PK", desc="Avaliação de fora de tolerância."), col("ID_Equipamento", 9, desc="Equipamento.", key="FK → tbl_equipamentos"),
             col("Data_Detecao", 11, "date", desc="Data."), col("Descricao", 44, desc="O que foi encontrado."), col("Periodo_Afetado", 20, desc="Período desde a última confirmação conforme."),
             col("Avaliacao_Retrospetiva", 52, desc="Validade dos resultados anteriores (7.1.5.2 último parágrafo)."), col("Produto_Afetado", 26, desc="Produto afetado / ação sobre o produto."),
             col("Acao", 40, desc="Ação tomada."), col("Responsavel", 22, desc="Responsável."), col("Estado", 10, desc="Estado.")]
    b.table("Fora_Tolerancia", "tbl_fora_tolerancia", ocols, rows_from(input_names(ocols), oot, dates=("Data_Detecao",)),
            "Equipamento fora de tolerância ou vencido e avaliação do impacto nos resultados anteriores (7.1.5.2).",
            title="EQUIPAMENTO NÃO APTO — AVALIAÇÃO RETROSPETIVA (7.1.5.2)", row_height=60)

    g = Q.rd("fact_gage_rr_study_processed.csv")
    grows = [dict(ID_Medicao=f"GRR-{i + 1:03d}", Estudo=r.StudyId, Peca=r.PartId, Avaliador=r.Inspector, Ensaio=int(r.Trial), Valor=float(r.MeasuredValue),
                  Data_Hora=str(r.MeasurementDateTime)[:16], LSL=float(r.LSL), USL=float(r.USL)) for i, r in enumerate(g.itertuples())]
    gcols = [col("ID_Medicao", 9, key="PK", desc="Medição."), col("Estudo", 18, desc="Estudo MSA."), col("Peca", 8, desc="Peça (10 peças da produção de OP-INJ-003)."),
             col("Avaliador", 14, desc="Inspetor."), col("Ensaio", 6, "int", desc="Repetição 1–3."), col("Valor", 9, "num3", desc="Peso medido (g)."),
             col("Data_Hora", 16, desc="Data/hora da medição."), col("LSL", 7, "num", desc="Limite inferior."), col("USL", 7, "num", desc="Limite superior.")]
    b.table("GRR_Dados", "tbl_grr_dados", gcols, grows, "Dados brutos do estudo Gage R&R GRR-CAP-WEIGHT-001 (dataset do projeto, 10 peças × 3 avaliadores × 3 ensaios).", row_height=15)

    ws = b.sheet("GRR_Calculo", "Cálculo do Gage R&R por fórmulas (método da média e amplitude, AIAG MSA) sobre tbl_grr_dados.", tab_color="7030A0")
    title(ws, "GAGE R&R — PESO DAS TAMPAS (GRR-CAP-WEIGHT-001) — calculado", "Método da média e amplitude (AIAG MSA 4.ª ed.) · 10 peças × 3 avaliadores × 3 ensaios · Tudo em fórmulas sobre tbl_grr_dados")
    header_row(ws, 4, ["Avaliador", "Peça", "Máximo", "Mínimo", "Amplitude", "Média"], widths=[16, 10, 11, 11, 11, 11])
    aval = sorted(g.Inspector.unique())
    pecas = sorted(g.PartId.unique())
    r = 5
    for a in aval:
        for p in pecas:
            cell(ws, r, 1, a)
            cell(ws, r, 2, p)
            cell(ws, r, 3, f'=_xlfn.MAXIFS(tbl_grr_dados[Valor],tbl_grr_dados[Avaliador],A{r},tbl_grr_dados[Peca],B{r})', fmt="0.0000")
            cell(ws, r, 4, f'=_xlfn.MINIFS(tbl_grr_dados[Valor],tbl_grr_dados[Avaliador],A{r},tbl_grr_dados[Peca],B{r})', fmt="0.0000")
            cell(ws, r, 5, f"=C{r}-D{r}", fmt="0.0000")
            cell(ws, r, 6, f'=AVERAGEIFS(tbl_grr_dados[Valor],tbl_grr_dados[Avaliador],A{r},tbl_grr_dados[Peca],B{r})', fmt="0.0000")
            r += 1
    last = r - 1
    ws.column_dimensions["H"].width = 44
    ws.column_dimensions["I"].width = 13
    ws.column_dimensions["J"].width = 50
    res = [
        ("n peças", len(pecas), "0", "Dado do estudo"), ("r ensaios", 3, "0", "Dado do estudo"), ("k avaliadores", len(aval), "0", "Dado do estudo"),
        ("K1 (3 ensaios)", 0.5908, "0.0000", "Constante AIAG (1/d2*)"), ("K2 (3 avaliadores)", 0.5231, "0.0000", "Constante AIAG"), ("K3 (10 peças)", 0.3146, "0.0000", "Constante AIAG"),
        ("R̄ (amplitude média)", f"=AVERAGE(E5:E{last})", "0.00000", "Média das amplitudes avaliador × peça"),
        ("X̄diff (diferença entre médias dos avaliadores)", "=" + "MAX(" + ",".join(f'AVERAGEIFS(tbl_grr_dados[Valor],tbl_grr_dados[Avaliador],"{a}")' for a in aval) + ")-MIN(" +
         ",".join(f'AVERAGEIFS(tbl_grr_dados[Valor],tbl_grr_dados[Avaliador],"{a}")' for a in aval) + ")", "0.00000", "Máx − mín das médias por avaliador"),
        ("Rp (amplitude das médias das peças)", "=" + "MAX(" + ",".join(f'AVERAGEIFS(tbl_grr_dados[Valor],tbl_grr_dados[Peca],"{p}")' for p in pecas) + ")-MIN(" +
         ",".join(f'AVERAGEIFS(tbl_grr_dados[Valor],tbl_grr_dados[Peca],"{p}")' for p in pecas) + ")", "0.00000", "Máx − mín das médias por peça"),
        ("EV — repetibilidade", "=I10*I7", "0.00000", "R̄ × K1"),
        ("AV — reprodutibilidade", "=SQRT(MAX(0,(I11*I8)^2-I13^2/(I4*I5)))", "0.00000", "√((X̄diff·K2)² − EV²/(n·r))"),
        ("GRR", "=SQRT(I13^2+I14^2)", "0.00000", "√(EV² + AV²)"), ("PV — variação das peças", "=I12*I9", "0.00000", "Rp × K3"),
        ("TV — variação total", "=SQRT(I15^2+I16^2)", "0.00000", "√(GRR² + PV²)"),
        ("%EV (da TV)", "=I13/I17", "0.0%", ""), ("%AV (da TV)", "=I14/I17", "0.0%", ""), ("%GRR (da TV)", "=I15/I17", "0.0%", "< 10% aceitável; 10–30% condicional; > 30% inaceitável"),
        ("%GRR (da tolerância, 6σ)", "=6*I15/(MAX(tbl_grr_dados[USL])-MIN(tbl_grr_dados[LSL]))", "0.0%", "Relevante para decisões de conformidade"),
        ("ndc — n.º de categorias distintas", "=ROUNDDOWN(1.41*I16/I15,0)", "0", "≥ 5 exigido"),
        ("Decisão", '=IF(AND(I20<0.1,I22>=5),"Sistema de medição ACEITÁVEL",IF(AND(I20<=0.3,I22>=5),"CONDICIONAL — melhorar","INACEITÁVEL — não usar para decisões"))', None, "Critérios AIAG"),
    ]
    for k, (lab, v, fmt, note) in enumerate(res):
        rr = 4 + k
        cell(ws, rr, 8, lab, bold=lab in ("GRR", "%GRR (da TV)", "Decisão"))
        c = cell(ws, rr, 9, v, fmt=fmt, bold=lab in ("%GRR (da TV)", "Decisão"))
        cell(ws, rr, 10, note, border=False)
    ws.conditional_formatting.add("I23", FormulaRule(formula=['ISNUMBER(SEARCH("ACEIT",I23))'], fill=PatternFill("solid", fgColor=CF_COLORS["green"][0])))

    mcols = [col("ID_Estudo", 18, key="PK", desc="Estudo MSA."), col("Caracteristica", 22, desc="Característica."), col("Equipamento", 24, desc="Tipo de equipamento."),
             col("Tipo_Estudo", 22, desc="GRR por variáveis / atributos (kappa) / viés e linearidade."), col("Data", 11, "date", desc="Data.", req=False),
             col("Pct_GRR_TV", 9, "pct1", desc="%GRR da variação total.", req=False), col("ndc_ou_Kappa", 9, "num", desc="ndc (variáveis) ou kappa (atributos).", req=False),
             col("Estado", 10, dv="EstadoMSA", desc="Estado."), col("Decisao", 30, desc="Conclusão.", req=False), col("Prioridade_Risco", 30, desc="Porque é necessário (característica crítica/decisão).")]
    msa = [
        ("GRR-CAP-WEIGHT-001", "Peso da tampa", "Balança analítica 0,001 g", "GRR por variáveis (média e amplitude)", dt.date(2026, 8, 3), "=GRR_Calculo!I20", "=GRR_Calculo!I22", "Concluído",
         "=GRR_Calculo!I23", "Característica maior; base do DMAIC IM-002 (dataset)"),
        ("GRR-BOT-THICK-001", "Espessura de parede", "Medidor de espessura por ultrassons", "GRR por variáveis", None, None, None, "Planeado", None, "R1 / R17: espessura com Cpk marginal na ISBM-003"),
        ("GRR-CAP-TORQUE-001", "Binário de abertura", "Torquímetro digital", "GRR destrutivo (ANOVA aninhada)", None, None, None, "Planeado", None, "Característica crítica; reclamações de binário"),
        ("AAA-VIS-001", "Defeitos visuais (pontos negros, manchas)", "Cabine D65 (inspetores)", "Concordância por atributos (kappa de Fleiss)", dt.date(2026, 7, 22), 0.0, 0.71, "Concluído",
         "Kappa 0,71 — aceitável com melhoria (catálogo de defeitos FOR-Q-14)", "Reclamações de contaminação; 5 inspetores"),
        ("AAA-TAMPER-001", "Anel de inviolabilidade (passa/falha)", "Equipamento do anel", "Concordância por atributos", None, None, None, "Em curso", None, "S = 10 na PFMEA; farma"),
    ]
    mrows = [dict(zip(input_names(mcols), m)) for m in msa]
    mrows[3]["Pct_GRR_TV"] = None
    b.table("Estudos_MSA", "tbl_msa", mcols, mrows, "Plano e resultados de análise do sistema de medição (MSA) proporcional ao risco.",
            title="ANÁLISE DO SISTEMA DE MEDIÇÃO (MSA)", subtitle="O estudo GRR-CAP-WEIGHT-001 lê os resultados da folha GRR_Calculo (dados reais) · Os restantes estão planeados por risco",
            cf=[("Estado", {"Planeado": "gray", "Em curso": "yellow", "Concluído": "green"})], row_height=32)

    ws2 = b.sheet("Resumo_Metrologia", "Indicadores calculados (KPI-Q-17) e estado do parque.")
    title(ws2, "RESUMO DA METROLOGIA — calculado")
    header_row(ws2, 3, ["Indicador", "Valor"], widths=[54, 12])
    E = lambda c_: f"tbl_equipamentos[{c_}]"
    ind = [("Equipamentos no inventário", f"=COUNTA({E('ID_Equipamento')})", "0"), ("  em uso", f'=COUNTIF({E("Estado_Uso")},"Em uso")', "0"),
           ("  válidos", f'=COUNTIF({E("Estado")},"Válido")+COUNTIF({E("Estado")},"A vencer (30 d)")', "0"),
           ("  vencidos", f'=COUNTIF({E("Estado")},"Vencido")', "0"), ("  bloqueados por não conformidade", f'=COUNTIF({E("Estado")},"Bloqueado*")', "0"),
           ("KPI-Q-17 — equipamentos em uso com confirmação válida", "=IFERROR(B6/B5,\"\")", "0.0%"),
           ("Equipamentos com tolerância/EMA < 4 (resolução insuficiente)", f'=COUNTIF({E("Rel_Tolerancia_EMA")},"<4")', "0"),
           ("Calibrações 'Indeterminado' (banda de guarda)", '=COUNTIF(tbl_calibracoes[Decisao],"Indeterminado")', "0"),
           ("Avaliações de fora de tolerância em curso", '=COUNTIF(tbl_fora_tolerancia[Estado],"Em curso")', "0")]
    for k, (a, f, fmt) in enumerate(ind):
        cell(ws2, 4 + k, 1, a, bold=not a.startswith("  "))
        cell(ws2, 4 + k, 2, f, fmt=fmt)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
