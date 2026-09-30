"""RG-SGE-14 — Não conformidades e ação corretiva; melhoria contínua do SGE e do desempenho energético.
ISO 50001:2018 10.1 a)–e) (reter a natureza das NC, ações e resultados), 10.2 (demonstrar a melhoria contínua do desempenho energético)."""
import numpy as np
from sgelib import *
from dimse import *
import edata
import build_05_ide_lbe as b05

NC = [
    ("NCE-26-01", "2026-11-18", "Auditoria interna", "CONE-A-26-01", "GES", "Projeto das linhas novas (PRJ-E-01) sem avaliação do desempenho energético nem LCC documentados.",
     "Atas de projeto e propostas sem análise energética", "Não conformidade menor", "ISO 50001 8.2", "Avaliação energética retroativa das 4 máquinas com a campanha PA-01 (kW medidos) — feita em 12/2026",
     "A checklist de alterações do SGI (PR-SGA-06) não tinha secção de energia e o processo de investimento não exigia LCC", "Método", "5 Porquês",
     "Secção de energia obrigatória na checklist (critérios de projeto do PR-SGE-07) e LCC obrigatório acima de € 50 000 (RD-E-26-D05)", "Sim: novo molde PT-013 (PRJ-E-04) foi avaliado — não há outros casos",
     "PR-SGA-06 e PR-SGE-07 revistos", DIND, "2027-02-28", "Em curso", None, "Por avaliar", None),
    ("NCE-26-02", "2026-11-18", "Auditoria interna", "CONE-A-26-02", "CMP", "Contrato de manutenção do chiller sem critérios energéticos nem informação ao fornecedor (8.3).",
     "Contrato AQE-26-04 de 15/06/2026", "Não conformidade menor", "ISO 50001 8.3", "Aditamento ao contrato com relatório de eficiência e verificação do setpoint (AQE-26-09)",
     "Os critérios de aquisição não abrangiam serviços com impacto nos USE", "Método", "Análise direta",
     "Categoria CAQ-06 (serviços com impacto nos USE) nos critérios de aquisição; formação FOR-E-04 às compras", "Sim: revistos os contratos dos compressores (já tinham critérios)",
     "RG-SGE-09 tbl_criterios_aquisicao", CMP_, "2026-12-31", "Fechada", "2026-12-02", "Por avaliar", "2027-06-30"),
    ("NCE-26-03", "2026-08-19", "Ronda de energia", "DSV-26-03", "UTL", "Setpoint do chiller baixado para 6 °C sem justificação durante 9 dias (critério CO-13).",
     "Registo do controlador do chiller", "Não conformidade menor", "ISO 50001 8.1 c)", "Setpoint reposto em 7 °C",
     "Operador resolveu empenos de um molde baixando a água gelada; a causa real era o canal de arrefecimento parcialmente obstruído", "Máquina", "5 Porquês",
     "Limpeza do molde; alarme no BI para alterações de setpoint (SUGE-12); CO-13 na formação dos operadores", "Não", "IT-SGE-03 revista", TUTL, "2026-09-30", "Fechada", "2026-08-28",
     "Eficaz", "2026-12-10"),
    ("NCE-26-04", "2026-09-05", "Desvio significativo", "DSV-26-02", "GES", "Potência tomada de 1 429 kW em ago/2026, acima dos 1 400 kW contratados (risco RE-03 materializado).",
     "Fatura FT-202608", "Não conformidade menor", "Requisito contratual / 8.1", "Nenhuma possível no mês (fatura já emitida)",
     "Arranques simultâneos após a paragem de 15/08 com o chiller no máximo e as 4 máquinas novas; sem monitorização de potência em tempo real", "Método", "5 Porquês",
     "Aumento da potência contratada para 1 550 kW (01/2027); alarme a 90% nos analisadores (12/2026); procedimento de arranque escalonado", "Sim: risco no arranque após o Natal (SUGE-13)",
     "RG-SGE-03 RE-03; IT de arranque", DFIN, "2027-01-31", "Em curso", None, "Por avaliar", None),
]
PORQUES = [
    ("NCE-26-01", 1, "Porque não houve avaliação energética do projeto?", "A checklist de alterações não pedia.", "PR-SGA-06 rev. 00", "Não"),
    ("NCE-26-01", 2, "Porque a checklist não pedia?", "Foi criada pelo SGA com foco em aspetos ambientais e legais.", "RG-SGA-18", "Não"),
    ("NCE-26-01", 3, "Porque não foi integrada a energia quando se criou o SGE?", "O SGE começou em 07/2026, depois de o projeto estar aprovado (03/2026).", "OS-2026-07", "Não"),
    ("NCE-26-01", 4, "Porque o processo de investimento não obrigava a LCC?", "O critério de decisão era só o preço de compra.", "Regras de CAPEX", "Sim"),
    ("NCE-26-04", 1, "Porque se ultrapassou a potência contratada?", "Pico de arranques simultâneos após a paragem de 15/08.", "Diagrama de carga do comercializador", "Não"),
    ("NCE-26-04", 2, "Porque houve arranques simultâneos?", "Não existia regra de arranque escalonado.", "Entrevistas aos chefes de turno", "Não"),
    ("NCE-26-04", 3, "Porque não havia regra?", "A potência nunca tinha sido um problema antes das linhas novas.", "Faturas 2025 (< 80% da contratada)", "Não"),
    ("NCE-26-04", 4, "Porque não se reviu a potência com as linhas novas?", "A alteração ALT-2026-03 não avaliou o efeito na potência elétrica.", "RG-SGA-18", "Sim"),
]


def trimestres():
    bm = edata.base_mensal()
    co, y, e = b05.model_np(bm)
    x1 = ((bm["Unid_INJ"] + bm["Unid_SOP"] - bm["Unid_Maquinas_Novas"]) / 1000).to_numpy()
    x2 = bm["CDD_15"].to_numpy()
    lo1, hi1 = x1[:12].min() * 0.9, x1[:12].max() * 1.1
    hi2 = x2[:12].max() * 1.1
    dom = (x1 >= lo1) & (x1 <= hi1) & (x2 <= hi2)
    meses = list(bm["Mes"])
    out = []
    for lab, ini, fim in (("2026-T2 (abr–jun)", 4, 6), ("2026-T3 (jul–set)", 7, 9), ("2026-T4 (out–dez)", 10, 12)):
        idx = [i for i, m in enumerate(meses) if m.year == 2026 and ini <= m.month <= fim and dom[i]]
        out.append((lab, round(float(1 - y[idx].sum() / e[idx].sum()), 4), len(idx)))
    return out


def build(out):
    b = Book("RG-SGE-14", "Não Conformidades, Ação Corretiva e Melhoria Contínua do SGE",
             activities="Reagir às não conformidades, determinar as causas, implementar e rever a eficácia das ações corretivas; demonstrar a melhoria contínua do SGE e do desempenho energético.",
             clauses="10.1 a) reagir (controlar, corrigir, consequências); b) avaliar a necessidade de ação (rever, causas, NC semelhantes); c) implementar; d) rever a eficácia; e) alterar o SGE; "
                     "reter a natureza das NC, as ações e os resultados; 10.2 melhorar continuamente a adequação, suficiência e eficácia do SGE e demonstrar a melhoria do desempenho energético.",
             purpose="4 NC do SGE (auditoria, ronda e desvio) com o ciclo 10.1 a)–e) completo, análise de causas por 5 Porquês e evidência trimestral da melhoria do desempenho energético "
                     "e da melhoria do sistema.",
             links=[("RG-SGE-12", "Constatações da auditoria."), ("RG-SGE-11", "Desvios significativos."), ("RG-SGA-07 / RG-SGQ-18", "NC do SGA e do SGQ (mesmas colunas).")],
             guidance=[("ISO 50004:2020 §10", "Tratamento de NC e demonstração da melhoria contínua."),
                       ("ISO 50006:2023 §10.3", "Demonstração da melhoria do desempenho energético por comparação com a LBE."),
                       ("M-10 Melhoria (curso Bureau Veritas)", "Interpretação de 10.1 e 10.2 (a ISO 50001 exige demonstrar a melhoria do desempenho, não só do sistema).")],
             legal=[("—", "Sem requisitos legais específicos; NC legais seriam tratadas aqui com prazo imediato.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Eficacia", ["Eficaz", "Não eficaz", "Por avaliar"])
    ncols = [col("ID_NC", 10, key="PK", desc="NC."), col("Data_Detecao", 11, "date", desc="Deteção."), col("Origem", 16, desc="Origem."), col("ID_Origem", 12, desc="Constatação / desvio."),
             col("Processo", 7, desc="Processo."), col("Descricao", 44, desc="Natureza da NC (reter)."), col("Evidencia_Objetiva", 26, desc="Evidência."),
             col("Classificacao", 16, desc="Classificação."), col("Requisito_Violado", 16, desc="Requisito."), col("Correcao_C1", 36, desc="Correção e consequências (10.1 a)."),
             col("Causa_Raiz", 44, desc="Causa (10.1 b 2)."), col("Categoria_6M", 9, desc="6M."), col("Metodo_Analise", 11, desc="Método."),
             col("Acao_Corretiva", 44, desc="Ação corretiva (10.1 c)."), col("NC_Semelhantes", 30, desc="NC semelhantes existem ou podem ocorrer? (10.1 b 3)."),
             col("Alteracao_SGE", 22, desc="Alterações ao SGE (10.1 e)."), col("Responsavel", 22, dv="Funcao", desc="Responsável."), col("Prazo", 11, "date", desc="Prazo."),
             col("Estado", 9, desc="Aberta / em curso / fechada."), col("Data_Fecho", 11, "date", desc="Fecho.", req=False),
             col("Eficacia", 10, dv="Eficacia", desc="Resultado da revisão da eficácia (10.1 d)."), col("Data_Verif_Eficacia", 11, "date", desc="Verificação da eficácia.", req=False),
             col("Dias_Aberta", 8, "int", f='=IF(@ID_NC@="","",IF(@Data_Fecho@="",DataRef-@Data_Detecao@,@Data_Fecho@-@Data_Detecao@))', desc="Dias em aberto."),
             col("No_Prazo", 8, f='=IF(@ID_NC@="","",IF(@Data_Fecho@="",IF(@Prazo@<DataRef,"Atrasada","Em curso"),IF(@Data_Fecho@<=@Prazo@,"Sim","Não")))', desc="Fechada no prazo?")]
    b.table("Nao_Conformidades", "tbl_nc", ncols, rows_from(input_names(ncols), NC, dates=("Data_Detecao", "Prazo", "Data_Fecho", "Data_Verif_Eficacia")),
            "Não conformidades e ações corretivas do SGE (10.1 — reter) — colunas do RG-SGA-07 tbl_nc com 10.1 b3 e e).", title="NÃO CONFORMIDADES E AÇÃO CORRETIVA (10.1)",
            cf=[("No_Prazo", {"Atrasada": "red", "Não": "orange", "Sim": "green"}), ("Eficacia", {"Eficaz": "green", "Não eficaz": "red", "Por avaliar": "gray"})], row_height=60, freeze_col=2)
    pcols = [col("ID_NC", 10, desc="NC.", key="FK → tbl_nc"), col("Nivel", 6, "int", desc="Nível."), col("Chave", 13, f='=IF(@ID_NC@="","",@ID_NC@&"|"&@Nivel@)', desc="Chave.", key="PK"),
             col("Pergunta_Porque", 50, desc="Porquê?"), col("Resposta", 50, desc="Resposta."), col("Evidencia", 30, desc="Evidência."), col("E_Causa_Raiz", 8, desc="Causa-raiz?")]
    b.table("Cinco_Porques", "tbl_5porques", pcols, rows_from(["ID_NC", "Nivel", "Pergunta_Porque", "Resposta", "Evidencia", "E_Causa_Raiz"], PORQUES),
            "Análise de causas (5 Porquês) — mesma estrutura do RG-SGA-07.", title="ANÁLISE DE CAUSAS — 5 PORQUÊS", cf=[("E_Causa_Raiz", {"Sim": "red"})], row_height=30)

    tr = trimestres()
    MEL = [(f"MEL-{i + 1:02d}", "Desempenho energético", "IDE-01 — melhoria normalizada da instalação", lab, v, "%", f"LBE-01; {n} meses dentro do domínio", "RG-SGE-05")
           for i, (lab, v, n) in enumerate(tr)]
    MEL += [("MEL-04", "Desempenho energético", "IDE-08 — potência específica do ar comprimido", "jan/2026 → dez/2026", -0.204, "%", "0,1337 → 0,1064 kWh/Nm³ (VSD + fugas + pressão)", "RG-SGE-11"),
            ("MEL-05", "Desempenho energético", "Fugas de ar comprimido (teste de vazio)", "jun/2026 → dez/2026", -0.44, "%", "25% → 14%", "RG-SGE-11"),
            ("MEL-06", "Desempenho energético", "Poupanças verificadas por ação (MV-02 + MV-03)", "out–dez/2026", 70991, "kWh", "IPMVP A e B", "RG-SGE-11"),
            ("MEL-07", "Desempenho energético", "Consumo específico SGCIE (CEE)", "2021 → 2026", -0.038, "%", "1 989 → 1 914 kgep/t (meta 2026: −3,0%)", "RG-SGE-10"),
            ("MEL-08", "Sistema", "Eletricidade medida por submedição (KPI-E-01)", "set/2026 → dez/2026", 0.954, "fração", "0% → 95% (analisadores M01–M06)", "RG-SGE-06"),
            ("MEL-09", "Sistema", "Critérios operacionais conformes nas rondas (média)", "jul/2026 → dez/2026", None, "—", "CO-01/05/09/13 conformes no fim do ano", "RG-SGE-08"),
            ("MEL-10", "Sistema", "Procedimentos e registos do SGE", "2026", 12, "procedimentos", "PR-SGE-01 a 12, IT-SGE-01 a 03, RG-SGE-00 a 14", "RG-SGE-00")]
    mcols = [col("ID_Melhoria", 8, key="PK", desc="Evidência de melhoria."), col("Tipo", 18, desc="Desempenho energético / sistema."), col("Indicador", 44, desc="Indicador."),
             col("Periodo", 20, desc="Período."), col("Valor", 10, "num3", desc="Valor (melhoria positiva em % para o IDE-01; variação para os restantes).", req=False),
             col("Unidade", 11, desc="Unidade."), col("Nota", 44, desc="Nota."), col("Registo", 12, desc="Registo de origem.")]
    b.table("Melhoria_Continua", "tbl_melhoria", mcols, rows_from(input_names(mcols), MEL), "Evidência da melhoria contínua do desempenho energético e do SGE (10.2).",
            title="MELHORIA CONTÍNUA DO DESEMPENHO ENERGÉTICO E DO SGE (10.2)",
            subtitle="IDE-01 por trimestre calculado com o mesmo modelo do RG-SGE-05 (meses dentro do domínio) · Valores à data de referência 31/12/2026", row_height=30)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
