"""RG-SGQ-18 — Não conformidade e ação corretiva (ISO 9001:2026 10.2.1 a)–f), 10.2.2 a)–b)).
tbl_capa: CAPA operacionais do dataset (fact_capa) com estado à data de referência; tbl_capa_sgq: ações corretivas de sistema
(auditorias, reclamações críticas, gemba) com todos os campos de 10.2.1; tbl_8d: relatórios 8D; tbl_5porques: análise de causa."""
import datetime as dt
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

CAPA_Q4 = [
    ("CAPA-Q-26-14", "2026-10-20", "Auditoria interna", "CON-Q-26-13", "RD", "Validação da estanquidade do pote farmacêutico PT-015 sem registo da validação nem dos critérios",
     "Registar retroativamente a validação com o cliente e os resultados dos ensaios", "Sem impacto no produto (ensaios existiam)", "O modelo de stage-gate não tinha campo obrigatório para a validação com o cliente",
     "Método", "5 Porquês", "Sim — verificar os 6 projetos DD-26 (validações registadas)", "Campo obrigatório de validação no stage-gate (RG-SGQ-11)", RD_, "2026-12-15", "Fechada", "2026-12-10",
     "Todos os projetos novos com validação registada na gate 4", "2027-03-31", "Por avaliar", "R12", "PR-SGQ-10 rev. 04"),
]

CAPA_SGQ = [
    # ID, data, origem, ID origem, processo, NC (natureza), a1 controlar/corrigir, a2 consequências, b2 causa raiz, 6M, método, b3 NC semelhantes, c ação corretiva, responsável, prazo,
    # estado, data fecho, d método eficácia, data verif, resultado, e) riscos atualizados, f) alteração ao SGQ
    ("CAPA-Q-26-02", "2025-08-25", "Reclamação", "CC-20114; 8D-26-02", "EXP", "Produto errado expedido (29 reclamações no período)", "Troca do produto ao cliente; inventário das paletes no cais",
     "Crédito ao cliente; transporte extra", "Carga validada só visualmente por etiqueta; referências semelhantes (TR-002 PP/PETG/PCR) com etiquetas quase iguais", "Método", "8D",
     "Sim — mesmo risco em potes e tampas novas", "Leitura obrigatória de código de barras na carga (MOC-Q-26-10); etiqueta com cor por material", LOG, "2026-12-31", "Em implementação", None,
     "Zero reclamações de produto trocado durante 3 meses após implementação", "2027-03-31", "Por avaliar", "R21 atualizado", "IT-EXP-02 rev. 02"),
    ("CAPA-Q-26-03", "2026-02-20", "Risco / NC recorrente", "R6", "SER", "Falhas de aderência da serigrafia em FR-007-PP-350", "Segregação e ensaio 100% dos lotes afetados", "Rejeição de 43 lotes (dataset)",
     "Ensaio de aderência só no fim do lote; lote de PP marginal não detetado na receção", "Método", "5 Porquês", "Sim — hot foil (aderência do foil)", "Ensaio no arranque e a meio do lote (MES); tratamento de superfície verificado", GPROD,
     "2026-08-31", "Implementada", "2026-08-05", "Zero lotes com aderência NC durante 3 meses", "2026-11-05", "Por avaliar", "R6", "PC-DEC-01 rev. 03"),
    ("CAPA-Q-26-04", "2026-03-15", "Dados (raio-X)", "R1", "SOP", "Espessura fora de especificação na ISBM-003 (rejeição 3,9%)", "Aumento temporário da frequência de medição", "Rejeição e refações",
     "Perfil de aquecimento sem compensação de temperatura ambiente; zona 3 do forno degradada", "Máquina", "Ishikawa + dados", "Sim — ISBM-002 e ISBM-008 (mesma geração)", "Reparação da zona 3; SPC de espessura por cavidade", GMAN,
     "2026-10-31", "Em implementação", None, "Rejeição ISBM-003 ≤ 2,5% em 3 meses", "2027-01-31", "Por avaliar", "R1", "PC-SOP-01 rev. 04"),
    ("CAPA-Q-26-05", "2026-03-12", "Auditoria interna", "CON-Q-26-01", "CMP", "SUP-005 classe D sem plano de ação", "Quarentena de todos os lotes SUP-005 até ensaio completo", "Stock bloqueado",
     "Critério de reavaliação sem consequência definida para classes C/D", "Método", "5 Porquês", "Sim — SUP-004 e SUP-006 em classe C", "Regra de decisão no scorecard (manter / plano / condicional / suspender)", CMP_,
     "2026-06-30", "Fechada", "2026-06-20", "Decisão registada para todos os fornecedores C/D", "2026-09-20", "Eficaz", "R13", "PR-SGQ-12 rev. 03"),
    ("CAPA-Q-26-06", "2026-05-14", "Auditoria interna", "CON-Q-26-02", "INJ", "Operador temporário sem validação a trabalhar sozinho", "Tutor designado de imediato", "Nenhum lote NC identificado",
     "Integração de temporários sem regra de validação antes de trabalhar sozinho", "Mão de obra", "5 Porquês", "Sim — sopro (OP-SOP-005/006)", "Coluna 'Pode trabalhar sozinho' na matriz; bloqueio no MES sem validação", RH_,
     "2026-07-31", "Fechada", "2026-07-25", "Auditoria de seguimento a 5 postos", "2026-09-16", "Eficaz", "R23", "PR-SGQ-17 rev. 02"),
    ("CAPA-Q-26-08", "2026-09-18", "Auditoria interna", "CON-Q-26-03; REL-26-03", "LAB", "Concessões libertadas sem aprovação do cliente (9 casos)", "Clientes informados; aprovações obtidas a posteriori quando possível",
     "Risco de reclamação e de perda de confiança", "Sistema permite imprimir etiqueta de concessão sem registo da aprovação do cliente; pressão de prazos no pico", "Método", "5 Porquês",
     "Sim — derrogações de MP também sem registo sistemático", "Bloqueio no ERP: concessão só é expedida com aprovação anexada (RPG-2026-01-D02)", GQ, "2026-10-31", "Em implementação", None,
     "Zero concessões sem aprovação em 3 meses", "2027-01-31", "Por avaliar", "R16", "PR-SGQ-14 rev. 03"),
    ("CAPA-Q-26-09", "2026-09-18", "Auditoria interna", "CON-Q-26-04", "MET", "Equipamentos com confirmação vencida em uso", "Verificação imediata; avaliação retrospetiva (OOT-26-02/03)", "Nenhum produto afetado",
     "Plano de calibração sem alertas automáticos; equipamentos de linha fora da lista do laboratório", "Medição", "5 Porquês", "Sim — termo-higrómetros", "Alertas de vencimento no MES; inventário único", GQ,
     "2026-10-15", "Em implementação", None, "100% dos equipamentos válidos durante 6 meses", "2027-04-15", "Por avaliar", "R17", "PR-SGQ-16 rev. 03"),
    ("CAPA-Q-26-10", "2026-09-18", "Auditoria interna", "CON-Q-26-05", "MAN", "Alteração de equipamento sem planeamento (compressores)", "MOC retroativo e análise do ar de sopro", "Nenhum lote NC identificado",
     "Investimentos em utilidades não passavam pelo processo de alterações", "Método", "5 Porquês", "Sim — mesma falha no SGA (NC-SGA-26-06)", "Campo obrigatório 'MOC' no pedido de investimento", DIND,
     "2026-11-30", "Em implementação", None, "100% dos investimentos com MOC", "2027-03-31", "Por avaliar", "R22", "PR-SGQ-03"),
    ("CAPA-Q-26-11", "2026-09-28", "Auditoria interna", "CON-Q-26-06; DC-26-01", "LAB", "Característica 'rosca' aplicada à tampa de encaixe TP-013", "Retirar a característica; reavaliar os 7 lotes rejeitados",
     "Lotes possivelmente conformes rejeitados (custo)", "Plano de inspeção dos SKU novos clonado de tampas de rosca sem revisão característica a característica", "Método", "5 Porquês",
     "Sim — verificar os 17 SKU novos (auditoria da configuração)", "Revisão das características na saída do design (8.3.5) com checklist", RD_, "2026-10-31", "Em implementação", None,
     "Auditoria da configuração dos 17 SKU sem desvios", "2026-12-15", "Por avaliar", "R12", "PR-SGQ-10 rev. 03"),
    ("CAPA-Q-26-12", "2026-09-18", "Auditoria interna", "CON-Q-26-07", "QUA", "Ação corretiva não sistemática (272 NC maiores sem CAPA; eficácia 56%)", "Triagem das 272 NC: agrupar por causa e abrir CAPA por família",
     "Recorrência de NC; custo da não qualidade", "Critério de abertura de CAPA não definido; donos de CAPA sem tempo nem formação em análise de causa", "Método", "5 Porquês",
     "Sim — o mesmo padrão no SGA", "Regra: NC maior/crítica → CAPA; comité semanal; 8D; verificação de eficácia aos 90 dias", DIND, "2026-12-31", "Em implementação", None,
     "CAPA no prazo ≥ 85% e eficácia ≥ 80% (OBJ-Q-05)", "2027-03-31", "Por avaliar", "R20", "PR-SGQ-06 rev. 04"),
    ("CAPA-Q-26-13", "2026-09-18", "Auditoria interna", "CON-Q-26-12", "COM", "Encomendas aceites com revisão incompleta ou tardia", "Revisão das 3 encomendas; confirmação dos requisitos legais", "Nenhuma entrega NC",
     "Confirmação automática do ERP antes da revisão técnica em encomendas urgentes", "Método", "5 Porquês", "Não", "Bloqueio da confirmação sem checklist 8.2.3 completa", DCOM, "2026-11-15",
     "Em implementação", None, "100% das encomendas com revisão antes do compromisso", "2027-02-15", "Por avaliar", "R21", "PR-SGQ-08 rev. 03"),
]

OITO_D = {
    "8D-26-01": ("CC-20000", "CUST-012", "Material estranho / contaminação em FR-007-PVC-350 (reclamação crítica)", [
        ("D1", "Equipa", "Gerente da Qualidade (líder), Gerente de Produção, Responsável de Compras, Técnico(a) de Laboratório (Elena Santos), Key Account"),
        ("D2", "Descrição do problema", "15/12/2025 — CUST-012 encontrou partículas negras em 51 frascos do lote da WO-1228 (ISBM, PVC). Quê: pontos negros; onde: parede; quanto: 51 un."),
        ("D3", "Contenção", "Bloqueio do stock do lote e de 2 lotes adjacentes; triagem 100% no cliente; lotes de masterbatch COR-001 em quarentena."),
        ("D4", "Causa raiz", "Degradação térmica do PVC no cilindro após paragem longa sem purga (ocorrência) + inspeção visual por amostragem com AQL 1,5 para pontos negros (não deteção)."),
        ("D5", "Ações corretivas", "Purga obrigatória após paragem > 30 min; reclassificar 'pontos negros' em PVC como maior (AQL 0,65)."),
        ("D6", "Implementação e validação", "Em curso — aguarda dados de 3 meses (reclamação ainda aberta à data de referência)."),
        ("D7", "Prevenção da recorrência", "PFMEA (PFMEA pontos negros) e IT-SOP-01 a atualizar; replicar a regra de purga à injeção."),
        ("D8", "Fecho", "Pendente — verificação de eficácia em dez/2026.")]),
    "8D-26-02": ("CC-20114", "CUST-002", "Produto errado expedido (TR-002-PETG em vez de TR-002-PP)", [
        ("D1", "Equipa", "Responsável de Armazém e Logística (líder), Key Account, Gerente da Qualidade"),
        ("D2", "Descrição do problema", "20/08/2025 — 136 tampas TR-002-PETG enviadas em vez de TR-002-PP; etiquetas de palete quase idênticas."),
        ("D3", "Contenção", "Troca no cliente em 48 h; inventário das paletes do cais."),
        ("D4", "Causa raiz", "Carga validada só visualmente; 3 variantes de material da mesma tampa com etiquetas iguais exceto o sufixo."),
        ("D5", "Ações corretivas", "Leitura obrigatória de código de barras (EH-01, MOC-Q-26-10); cor da etiqueta por material."),
        ("D6", "Implementação e validação", "Em implementação (teste de 2 semanas em out/2026)."),
        ("D7", "Prevenção da recorrência", "IT-EXP-02 rev. 02; risco R21 reavaliado."),
        ("D8", "Fecho", "Pendente — CAPA-Q-26-02.")]),
    "8D-26-03": ("CC-20071", "CUST-010", "Frascos FR-018-MDPE-600 com fuga (110 un)", [
        ("D1", "Equipa", "Gerente da Qualidade, Engenheiro(a) de Processo, Técnico(a) de Manutenção (Vitor Sousa)"),
        ("D2", "Descrição do problema", "25/01/2026 — 110 frascos com fuga pelo gargalo detetados na linha de enchimento do cliente."),
        ("D3", "Contenção", "Ensaio de fuga 100% do stock (4 lotes); nenhum outro lote afetado."),
        ("D4", "Causa raiz", "Rebarba no gargalo por desgaste do molde; ensaio de fuga por amostragem (AQL 0,1, n = 125) com baixa probabilidade de deteção."),
        ("D5", "Ações corretivas", "Reforma do molde; leak tester em linha nas ISBM mais antigas (RPG-2026-01-D04)."),
        ("D6", "Implementação e validação", "Reforma concluída; zero reclamações de fuga do cliente desde fev/2026."),
        ("D7", "Prevenção da recorrência", "Manutenção de moldes por contador de ciclos (O2); PFMEA fuga D = 3 com leak tester."),
        ("D8", "Fecho", "Fechado em 29/01/2026 (resposta); eficácia verificada em 30/04/2026.")]),
    "8D-26-04": ("CC-20113", "CUST-002", "Tampas TR-002-HDPE desapertam após fecho (retenção de binário) — 179 un", [
        ("D1", "Equipa", "Engenheiro(a) de Processo (líder), Gerente da Qualidade, Técnico(a) de Laboratório"),
        ("D2", "Descrição do problema", "15/08/2025 — back-off de tampas 24/410 HDPE após 48 h em armazém do cliente."),
        ("D3", "Contenção", "Ensaio de retenção de binário a 48 h nos lotes em stock."),
        ("D4", "Causa raiz", "Relaxação do HDPE com arrefecimento curto; binário só medido a quente (logo após a moldação)."),
        ("D5", "Ações corretivas", "Tempo de arrefecimento +2 s; ensaio de binário a 24 h por lote."),
        ("D6", "Implementação e validação", "Zero reclamações de back-off em 12 meses."),
        ("D7", "Prevenção da recorrência", "Plano de controlo PC-INJ-01 (binário a 24 h); lição aprendida para TA-014."),
        ("D8", "Fecho", "Fechado em 18/09/2025; eficácia verificada em 18/12/2025.")]),
    "8D-26-05": ("CC-20090", "CUST-012", "Frascos FR-015-HDPE-PCR deformados/colapsados (62 un)", [
        ("D1", "Equipa", "Gerente da Qualidade, Responsável de Compras, Engenheiro(a) de Processo"),
        ("D2", "Descrição do problema", "06/06/2026 — 62 frascos colapsados no enchimento a quente do cliente."),
        ("D3", "Contenção", "Bloqueio dos lotes com o mesmo lote de HDPE-PCR (SUP-004)."),
        ("D4", "Causa raiz", "Em investigação: variação do MFI do HDPE-PCR (SUP-004 classe C) com espessura mínima na base."),
        ("D5", "Ações corretivas", "Propostas: especificação de MFI mais apertada para PCR; espessura mínima na base +0,1 mm."),
        ("D6", "Implementação e validação", "Pendente."),
        ("D7", "Prevenção da recorrência", "Pendente."),
        ("D8", "Fecho", "Aberto — reclamação atrasada à data de referência.")]),
}

WHY = {
    "CAPA-Q-26-08": [("Porque foram expedidos lotes por concessão sem aprovação do cliente?", "Porque a etiqueta de concessão foi impressa e a palete expedida antes da resposta do cliente.", "9 concessões sem data de aprovação (tbl_concessoes)"),
                     ("Porque foi possível imprimir a etiqueta?", "Porque o ERP não exige anexo de aprovação para imprimir a etiqueta de concessão.", "Teste no ERP em 18/09/2026"),
                     ("Porque se avançou sem resposta?", "Porque no pico havia pressão para cumprir a data de entrega e a regra não era clara para os chefes de turno.", "REL-26-03; entrevistas"),
                     ("Porque a regra não era clara?", "Porque o PR-SGQ-14 rev. 02 não definia quem pede, quem aprova e o bloqueio da expedição.", "PR-SGQ-14 rev. 02")],
    "CAPA-Q-26-12": [("Porque há 272 NC maiores sem CAPA?", "Porque a abertura de CAPA é decidida caso a caso pelo inspetor.", "tbl_snc (RG-SGQ-14)"),
                     ("Porque é decidida caso a caso?", "Porque o PR-SGQ-06 não define critério de abertura.", "PR-SGQ-06 rev. 03"),
                     ("Porque 44% das CAPA avaliadas não são eficazes?", "Porque a causa raiz fica ao nível do sintoma (ex.: 'operador') e a verificação é feita logo após a implementação.", "Amostra de 20 CAPA não eficazes"),
                     ("Porque a análise fica no sintoma?", "Porque os donos de CAPA (inspetores e técnicos) não têm tempo reservado nem formação em análise de causa (só 6 formados em 8D).", "FOR-Q-10; carga de trabalho"),
                     ("Porque não há tempo reservado?", "Porque a gestão não tinha a eficácia das CAPA como objetivo nem revisão periódica.", "Objetivos 2025")],
}


def capa_rows():
    c = Q.capa()
    rows = []
    for r in c.sort_values("OpenDate").itertuples():
        close = r.Close.date() if pd.notna(r.Close) else None
        efic = Q.T_EFIC.get(r.EffectivenessCheck, "Por avaliar") if close else "Por avaliar"
        rows.append(dict(ID_CAPA=r.CAPAId, Data_Abertura=dt.date.fromisoformat(r.OpenDate), Mes=r.OpenDate[:7], Tipo=Q.T_TIPO_CAPA[r.CAPAType], ID_NC=r.RelatedNCId,
                         Local=Q.T_AREA.get(r.Area, r.Area), Processo=Q.T_PROC.get(r.Process, r.Process), Severidade=Q.T_SEV[r.Severity],
                         Categoria_6M=Q.T_CAUSA.get(r.RootCauseCategory, r.RootCauseCategory), Responsavel=r.Owner, Prazo=r.Due.date(), Data_Fecho=close, Eficacia=efic))
    return rows


def build(out):
    b = Book("RG-SGQ-18", "Não Conformidades e Ações Corretivas (CAPA, 8D)",
             activities="Reagir às não conformidades, avaliar a necessidade de eliminar as causas, determinar causas e NC semelhantes, implementar ações, rever a eficácia, atualizar riscos e alterar o SGQ quando necessário.",
             clauses="10.2.1 a) 1–2, b) 1–3 (incl. NC semelhantes ou que possam ocorrer), c), d) eficácia, e) atualizar riscos e oportunidades, f) alterar o SGQ; 10.2.2 a) b); Nota: reclamações como fonte de NC",
             purpose=f"CAPA operacionais do dataset abertas entre {PER_INI} e {PER_FIM} (estado, prazo e eficácia à data de referência), ações corretivas de sistema com todos os campos de 10.2.1, 5 relatórios 8D de reclamações críticas e análises 5 Porquês; indicadores de prazo, eficácia e causas (6M).",
             links=[("RG-SGQ-14 tbl_snc", "NC que originam CAPA (ID_NC)."), ("RG-SGQ-16 tbl_constatacoes", "CAPA de constatações de auditoria."),
                    ("RG-SGQ-15 tbl_reclamacoes", "8D de reclamações críticas (ID_8D)."), ("RG-SGA-07", "NC e ações corretivas do SGA (mesma estrutura).")],
             guidance=[("Academy — cap. 160 (5 Porquês, 8D e CAPA)", "Correção ≠ ação corretiva ≠ ação preventiva; D0–D8; causa de ocorrência e causa de não deteção."),
                       ("ISO 10009:2024 (pasta de interpretação)", "Ferramentas da qualidade para análise de causa (Ishikawa, 5 Porquês, Pareto)."),
                       ("ISO/TC 176 APG — Nonconformity review and closing", "Fechar só com evidência de implementação e eficácia, proporcional ao risco."),
                       ("Nota sobre 'ação preventiva'", "A ISO 9001 já não tem requisito de ação preventiva (substituído pelo pensamento baseado em risco, 6.1); as CAPA 'preventivas' do dataset devem ligar a riscos do RG-SGQ-04.")])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Cat6M", ["Material", "Máquina", "Método", "Mão de obra", "Molde / ferramenta", "Medição", "Meio ambiente", "Requisito do cliente"])
    b.add_list("Eficacia", ["Eficaz", "Não eficaz", "Por avaliar"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("EstadoCAPA", ["Aberta", "Em implementação", "Implementada", "Fechada"])

    # nomes de coluna comuns ao RG-SGA-07 tbl_nc / RG-SGA-06 tbl_pam: Local, Categoria_6M, Responsavel, Dias_Aberta, Eficacia, Correcao_C1, Causa_Raiz
    cols = [col("ID_CAPA", 10, key="PK", desc="CAPA (dataset)."), col("Data_Abertura", 11, "date", desc="Abertura."), col("Mes", 8, desc="aaaa-mm."),
            col("Tipo", 10, desc="Corretiva / preventiva (ver nota no LEIA-ME)."), col("ID_NC", 9, desc="NC de origem.", key="FK → RG-SGQ-14"), col("Local", 14, desc="Área / local."),
            col("Processo", 7, dv="Processo", desc="Processo."), col("Severidade", 8, desc="Severidade."), col("Categoria_6M", 14, dv="Cat6M", desc="Categoria da causa raiz (6M)."),
            col("Responsavel", 14, desc="Dono da CAPA (dataset)."), col("Prazo", 11, "date", desc="Prazo."), col("Data_Fecho", 11, "date", desc="Fecho (vazio se posterior à data de referência).", req=False),
            col("Eficacia", 10, dv="Eficacia", desc="Verificação de eficácia (10.2.1 d)."),
            col("Dias_Aberta", 6, "int", f='=IF(@ID_CAPA@="","",IF(@Data_Fecho@="",DataRef-@Data_Abertura@,@Data_Fecho@-@Data_Abertura@))', desc="Dias até ao fecho (ou até hoje)."),
            col("Estado", 10, f='=IF(@ID_CAPA@="","",IF(@Data_Fecho@<>"","Fechada",IF(@Prazo@<DataRef,"Atrasada","Aberta")))', desc="Estado à data de referência."),
            col("No_Prazo", 8, f='=IF(@Data_Fecho@="",IF(@Prazo@<DataRef,"Não","Em curso"),IF(@Data_Fecho@<=@Prazo@,"Sim","Não"))', desc="Fechada no prazo?")]
    rows = capa_rows()
    for c_ in cols:
        if c_["f"]:
            c_["f"] = c_["f"].replace("[Processo]", "tbl_capa[Processo]").replace("[Categoria_6M]", "tbl_capa[Categoria_6M]").replace("[Data_Abertura]", "tbl_capa[Data_Abertura]").replace("[Eficacia]", "tbl_capa[Eficacia]")
    b.table("CAPA_Operacionais", "tbl_capa", cols, rows, "CAPA operacionais do dataset com estado, prazo e eficácia à data de referência.",
            title="AÇÕES CORRETIVAS OPERACIONAIS (dataset) — ESTADO À DATA DE REFERÊNCIA", subtitle=f"{len(rows)} CAPA abertas entre {PER_INI} e {PER_FIM} · Fechos posteriores a 31/12/2026 contam como abertos",
            cf=[("Estado", {"Atrasada": "red", "Aberta": "orange", "Fechada": "green"}), ("Eficacia", {"Não eficaz": "red", "Eficaz": "green"})],
            row_height=14, freeze_col=1)

    scols = [col("ID_CAPA", 11, key="PK", desc="Ação corretiva de sistema."), col("Data_Detecao", 11, "date", desc="Abertura (deteção da NC)."), col("Origem", 16, desc="Origem."), col("ID_Origem", 18, desc="Constatação, reclamação, risco."),
             col("Processo", 7, dv="Processo", desc="Processo."), col("Descricao", 40, desc="Natureza da NC (10.2.2 a)."), col("Correcao_C1", 36, desc="10.2.1 a1) — reagir: controlar e corrigir."),
             col("a2_Consequencias", 26, desc="10.2.1 a2)."), col("Causa_Raiz", 46, desc="10.2.1 b2) — causa raiz."), col("Categoria_6M", 11, dv="Cat6M", desc="6M."), col("Metodo_Analise", 12, desc="Método."),
             col("b3_NC_Semelhantes", 34, desc="10.2.1 b3) — existem ou podem ocorrer noutro local?"), col("c_Acao_Corretiva", 46, desc="10.2.1 c)."), col("Responsavel", 22, desc="Responsável."),
             col("Prazo", 11, "date", desc="Prazo."), col("Estado", 13, dv="EstadoCAPA", desc="Estado."), col("Data_Fecho", 11, "date", desc="Fecho.", req=False),
             col("d_Metodo_Eficacia", 34, desc="10.2.1 d) — como e quando se revê a eficácia."), col("Data_Verif_Eficacia", 11, "date", desc="Data prevista/real."),
             col("Eficacia", 10, dv="Eficacia", desc="Resultado da verificação da eficácia (10.2.2 b)."), col("e_Riscos_Atualizados", 14, desc="10.2.1 e) riscos atualizados (IDs)."),
             col("f_Alteracao_SGQ", 18, desc="10.2.1 f) alteração ao SGQ (documento/MOC)."),
             col("Controlo_Qualidade", 20, f=('=IF(@ID_CAPA@="","",IF(@Causa_Raiz@="","FALTA causa raiz",IF(AND(@Estado@="Fechada",@Eficacia@="Por avaliar",@Data_Verif_Eficacia@<DataRef),"FALTA verificar eficácia",'
                                    'IF(AND(@Estado@<>"Fechada",@Prazo@<DataRef),"Atrasada","OK"))))'), desc="Regras de 10.2.")]
    # fecho do ano (31/12/2026): estado, fecho e eficácia; + CAPA-Q-26-14 (auditoria AUD-Q-26-04)
    FECHO_CAPA = {"CAPA-Q-26-02": ("Implementada", "2026-12-18", None, None), "CAPA-Q-26-03": ("Fechada", "2026-08-05", "Eficaz", "2026-11-05"),
                  "CAPA-Q-26-04": ("Fechada", "2026-10-28", None, None), "CAPA-Q-26-08": ("Fechada", "2026-10-30", None, None),
                  "CAPA-Q-26-09": ("Fechada", "2026-10-14", None, None), "CAPA-Q-26-10": ("Fechada", "2026-11-25", None, None),
                  "CAPA-Q-26-11": ("Fechada", "2026-10-29", "Eficaz", "2026-12-15"), "CAPA-Q-26-13": ("Fechada", "2026-11-12", None, None)}
    capa_f = []
    for t in CAPA_SGQ + CAPA_Q4:
        if t[0] in FECHO_CAPA:
            e, fe, ef, dv = FECHO_CAPA[t[0]]
            t = t[:15] + (e, fe, t[17], dv or t[18], ef or t[19]) + t[20:]
        capa_f.append(t)
    b.table("CAPA_Sistema", "tbl_capa_sgq", scols, rows_from(input_names(scols), capa_f, dates=("Data_Detecao", "Prazo", "Data_Fecho", "Data_Verif_Eficacia")),
            "Ações corretivas de sistema com todos os elementos de 10.2.1 a)–f).", title="AÇÕES CORRETIVAS DE SISTEMA (10.2.1 a–f)",
            subtitle="Origem: constatações de auditoria, reclamações críticas, riscos e gemba walks · Inclui NC semelhantes (b3), atualização de riscos (e) e alterações ao SGQ (f)",
            cf=[("Estado", {"Fechada": "green", "implementação": "yellow"}), ("Eficacia", {"Não eficaz": "red", "Eficaz": "green"}), ("Controlo_Qualidade", {"FALTA": "red", "Atrasada": "red", "OK": "green"})],
            row_height=60, freeze_col=1, extra_rows=5)

    drows = []
    for did, (cc, cli, prob, steps) in OITO_D.items():
        for d, tit, txt in steps:
            drows.append(dict(ID_8D=did, ID_Reclamacao=cc, ID_Cliente=cli, Problema=prob, Disciplina=d, Titulo=tit, Conteudo=txt))
    dcols = [col("ID_8D", 9, desc="Relatório 8D.", key="FK"), col("ID_Reclamacao", 10, desc="Reclamação (dataset).", key="FK → RG-SGQ-15"), col("ID_Cliente", 9, desc="Cliente."),
             col("Problema", 40, desc="Problema."), col("Disciplina", 6, desc="D1–D8."), col("Titulo", 22, desc="Disciplina."), col("Conteudo", 90, desc="Conteúdo."),
             col("Chave", 14, f='=@ID_8D@&"|"&@Disciplina@', desc="Chave técnica.")]
    b.table("Relatorios_8D", "tbl_8d", dcols, drows, "Relatórios 8D das reclamações críticas (formato longo: uma linha por disciplina).",
            title="RELATÓRIOS 8D — RECLAMAÇÕES CRÍTICAS", row_height=40)

    wrows = []
    for cid, lv in WHY.items():
        for k, (q, a, e) in enumerate(lv, 1):
            wrows.append(dict(ID_CAPA=cid, Nivel=k, Pergunta_Porque=q, Resposta=a, Evidencia=e, E_Causa_Raiz="Sim" if k == len(lv) else "Não"))
    wcols = [col("ID_CAPA", 11, desc="CAPA.", key="FK → tbl_capa_sgq"), col("Nivel", 5, "int", desc="Nível."), col("Pergunta_Porque", 44, desc="Porquê?"), col("Resposta", 60, desc="Resposta."),
             col("Evidencia", 34, desc="Evidência."), col("E_Causa_Raiz", 8, dv="SimNao", desc="Nível da causa raiz.")]
    b.table("Cinco_Porques", "tbl_5porques", wcols, wrows, "Análises 5 Porquês das CAPA de sistema (mesma estrutura do RG-SGA-07 tbl_5porques).", cf=[("E_Causa_Raiz", {"Sim": "red"})], row_height=40)

    ws = b.sheet("Indicadores_CAPA", "Indicadores calculados: estado, prazo, eficácia e causas 6M.", tab_color="C00000")
    title(ws, "INDICADORES DE AÇÃO CORRETIVA — calculado", "CAPA operacionais do dataset · Eficácia = eficazes ÷ (eficazes + não eficazes)")
    header_row(ws, 4, ["Categoria de causa (6M)", "CAPA", "Abertas/atrasadas", "Eficazes", "Não eficazes", "Eficácia"], widths=[24, 8, 16, 9, 11, 9])
    T = lambda c_: f"tbl_capa[{c_}]"
    cats = ["Material", "Máquina", "Método", "Mão de obra", "Molde / ferramenta", "Requisito do cliente"]
    for k, cat in enumerate(cats):
        r = 5 + k
        cell(ws, r, 1, cat)
        cell(ws, r, 2, f'=COUNTIF({T("Categoria_6M")},A{r})', fmt="0")
        cell(ws, r, 3, f'=COUNTIFS({T("Categoria_6M")},A{r},{T("Estado")},"<>Fechada")', fmt="0")
        cell(ws, r, 4, f'=COUNTIFS({T("Categoria_6M")},A{r},{T("Eficacia")},"Eficaz")', fmt="0")
        cell(ws, r, 5, f'=COUNTIFS({T("Categoria_6M")},A{r},{T("Eficacia")},"Não eficaz")', fmt="0")
        cell(ws, r, 6, f'=IFERROR(D{r}/(D{r}+E{r}),"")', fmt="0%")
    r = 5 + len(cats)
    cell(ws, r, 1, "Total", bold=True)
    for c_ in range(2, 6):
        L = get_column_letter(c_)
        cell(ws, r, c_, f"=SUM({L}5:{L}{r - 1})", fmt="0", bold=True)
    cell(ws, r, 6, f'=IFERROR(D{r}/(D{r}+E{r}),"")', fmt="0%", bold=True)
    header_row(ws, r + 2, ["Indicador", "Valor"])
    ind = [("CAPA fechadas no prazo (das fechadas)", f'=IFERROR(COUNTIF({T("No_Prazo")},"Sim")/COUNTIF({T("Estado")},"Fechada"),"")', "0%"),
           ("CAPA atrasadas à data de referência", f'=COUNTIF({T("Estado")},"Atrasada")', "0"), ("Tempo médio até ao fecho (dias)", f'=AVERAGEIFS({T("Dias_Aberta")},{T("Estado")},"Fechada")', "0"),
           ("CAPA 'preventivas' (ligar a riscos — 6.1)", f'=COUNTIF({T("Tipo")},"Preventiva")', "0"),
           ("CAPA de sistema abertas", '=COUNTIFS(tbl_capa_sgq[Estado],"<>Fechada",tbl_capa_sgq[ID_CAPA],"<>")', "0")]
    for k, (a, f, fmt) in enumerate(ind):
        cell(ws, r + 3 + k, 1, a)
        cell(ws, r + 3 + k, 2, f, fmt=fmt)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
