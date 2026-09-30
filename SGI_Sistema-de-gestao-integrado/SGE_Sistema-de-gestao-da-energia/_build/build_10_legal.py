"""RG-SGE-10 — Requisitos legais e outros requisitos de energia, obrigações e avaliação da conformidade; trajetória do SGCIE (PREn).
ISO 50001:2018 4.2, 9.1.2 · DL 71/2008 (SGCIE) · Despacho 17313/2008 · Diretiva (UE) 2023/1791.
Fonte única dos requisitos legais do SGI: RG-SGA-04 (tbl_legal). LEG-08 já existe lá; os LEG-E-xx são propostos para inclusão."""
import pandas as pd
from sgelib import *
from dimse import *
import edata

LEGAL = [
    # (ID, tema, diploma, tipo, data publicação, âmbito, entidade, resumo, aplicabilidade, justificação, processos, IDs_USE, disposições internas, evidência, tipo evidência,
    #  data evidência, estado, data avaliação, periodicidade meses, ação, responsável, fonte oficial, natureza, papel, registo dono)
    ("LEG-08", "Energia — SGCIE", "Decreto-Lei n.º 71/2008, de 15 de abril (SGCIE), alterado pela Lei n.º 7/2013 e pelo DL n.º 68-A/2015", "Decreto-Lei", "2008-04-15", "Nacional", "DGEG / ADENE",
     "Instalações com consumo > 500 tep/ano: auditoria energética periódica (8 anos), PREn com metas (≥ 1 000 tep: −6% da intensidade energética e do consumo específico em 8 anos; manter a intensidade carbónica), relatórios bienais de execução (REP).",
     "Aplicável", "≈ 1 700 tep/ano (0,215 kgep/kWh × ≈ 7,9 GWh) → consumidor intensivo ≥ 1 000 tep.", "Todos", "Todos", "PR-SGE-10; RG-SGE-10 tbl_sgcie", "REP 2026 submetido em 28/10/2026 (comprovativo SGCIE)", "Comprovativo de submissão",
     "2026-10-28", "Conforme", "2026-12-10", 12, "—", GE, "https://sgcie.pt", "Obrigação legal", "Operador de instalação CIE", "RG-SGA-04"),
    ("LEG-E-01", "Energia — fatores", "Despacho n.º 17313/2008, de 26 de junho (fatores de conversão para tep e de intensidade carbónica)", "Despacho", "2008-06-26", "Nacional", "DGEG",
     "Fatores de conversão (eletricidade 0,215 kgep/kWh) e de emissão (eletricidade 0,47 kgCO2e/kWh) a usar no SGCIE.", "Aplicável", "Cálculo dos indicadores do PREn.",
     "GES", "—", "RG-SGE-04 tbl_tipos_energia; tbl_sgcie", "Fatores usados no RG-SGE-10 conferidos com o conversor SGCIE", "Registo interno", "2026-10-20", "Conforme", "2026-12-10", 12, "—", GE,
     "https://sgcie.pt/conversor-sgcie/", "Obrigação legal", "Operador CIE", "RG-SGE-10 (propor RG-SGA-04)"),
    ("LEG-E-02", "Energia — auditorias", "Decreto-Lei n.º 68-A/2015, de 30 de abril (eficiência energética; transpõe a Diretiva 2012/27/UE)", "Decreto-Lei", "2015-04-30", "Nacional", "DGEG",
     "Auditoria energética de 4 em 4 anos para grandes empresas; alterou o SGCIE.", "Aplicável (via SGCIE)", "A Plasticom cumpre a obrigação de auditoria através do SGCIE; confirmar anualmente o critério de 'grande empresa' (efetivos/volume de negócios).",
     "GES", "—", "PR-SGE-10", "Parecer interno 2026 (critério de PME confirmado com o Diretor Financeiro)", "Parecer", "2026-02-10", "Conforme", "2026-12-10", 12, "—", DFIN, "https://diariodarepublica.pt",
     "Obrigação legal", "Empresa", "RG-SGE-10 (propor RG-SGA-04)"),
    ("LEG-E-03", "Energia — UE", "Diretiva (UE) 2023/1791 (eficiência energética, reformulação), arts. 8.º e 11.º — transposição nacional em curso", "Diretiva UE", "2023-09-20", "UE / nacional",
     "DGEG / ADENE", "Art. 11.º: > 85 TJ/ano → SGE obrigatório; > 10 TJ/ano sem SGE → auditoria de 4 em 4 anos; SGE certificado dispensa a auditoria.", "Aplicável após transposição",
     "≈ 28 TJ/ano (entre 10 e 85 TJ): auditoria periódica OU SGE ISO 50001 certificado (opção escolhida — OE-02). Consulta pública do DL de transposição terminou em 05/12/2025.",
     "GES", "—", "PR-SGE-10; RG-SGE-03 OE-02", "Acompanhamento semestral do Diário da República e da DGEG", "Registo de vigilância legal", "2026-12-10", "Em avaliação", "2026-12-10", 6,
     "OBRE-04", GE, "https://eur-lex.europa.eu/eli/dir/2023/1791/oj", "Obrigação legal (futura)", "Empresa", "RG-SGE-10 (propor RG-SGA-04)"),
    ("LEG-E-04", "Energia — autoconsumo", "Decreto-Lei n.º 15/2022, de 14 de janeiro (Sistema Elétrico Nacional), alterado pelo DL n.º 130/2026, de 29 de junho", "Decreto-Lei", "2026-06-29", "Nacional",
     "DGEG / E-REDES", "Regras e controlo prévio das unidades de produção para autoconsumo (UPAC); o DL 130/2026 transpõe parcialmente a RED III e a Diretiva (UE) 2023/1791 (em vigor desde 27/08/2026).",
     "Aplicável (UPAC 2027)", "Projeto PRJ-E-02 (UPAC ≈ 1 MWp) — controlo prévio antes da ligação.", "GES; UTL", "—", "PR-SGE-07", "Estudo de viabilidade com enquadramento legal", "Relatório",
     "2026-11-30", "Em avaliação", "2026-12-10", 6, "OBRE-05", DFIN, "https://diariodarepublica.pt/dr/detalhe/decreto-lei/130-2026-1139897687", "Obrigação legal (futura)", "Promotor da UPAC", "RG-SGE-10 (propor RG-SGA-04)"),
    ("LEG-E-05", "Equipamentos — motores", "Regulamento (UE) 2019/1781 (conceção ecológica de motores elétricos e variadores de velocidade)", "Regulamento UE", "2019-10-01", "UE",
     "ASAE", "Classes mínimas IE3/IE4 para motores colocados no mercado; VSD IE2.", "Aplicável (compras)", "Critério CAQ-04 nas aquisições.", "MAN; CMP", "USE-01 a USE-04", "RG-SGE-09 tbl_criterios_aquisicao",
     "Motor MOA-02 IE3 (AQE-26-07)", "Declaração UE", "2026-02-20", "Conforme", "2026-12-10", 12, "—", CMP_, "https://eur-lex.europa.eu/eli/reg/2019/1781/oj", "Obrigação legal", "Comprador/utilizador", "RG-SGE-10 (propor RG-SGA-04)"),
    ("LEG-E-06", "Equipamentos — chillers", "Regulamento (UE) 2016/2281 (conceção ecológica de chillers de processo — SEPR)", "Regulamento UE", "2016-12-20", "UE", "ASAE",
     "Eficiência sazonal mínima (SEPR) de chillers de processo.", "Aplicável (compra do chiller 2027)", "PRJ-E-03 (especificação com SEPR ≥ 6,5).", "UTL", "USE-04", "CE-2027-03", "Caderno de encargos", "Documento",
     "2026-11-15", "Conforme", "2026-12-10", 12, "—", CMP_, "https://eur-lex.europa.eu/eli/reg/2016/2281/oj", "Obrigação legal", "Comprador", "RG-SGE-10 (propor RG-SGA-04)"),
    ("LEG-E-07", "Clima — relato", "Diretiva (UE) 2022/2464 (CSRD) / ESRS E1-5 e norma voluntária VSME (B3) — requisito dos clientes", "Outro requisito", "2022-12-14", "UE", "Clientes",
     "Consumo e mix de energia, intensidade energética, quota renovável.", "Outro requisito (clientes)", "A Plasticom não é obrigada à CSRD, mas os clientes pedem os dados (VSME B3).", "GES", "—",
     "RG-SGA-19 tbl_indicadores_esg; RG-SGE-05 IDE-09/10", "Questionários de clientes respondidos (2026)", "Registo", "2026-09-30", "Conforme", "2026-12-10", 12, "—", GSGA, "https://eur-lex.europa.eu", "Outro requisito", "Fornecedor", "RG-SGA-04"),
    ("LEG-E-08", "Certificação", "ISO 50003:2021 — requisitos para os organismos de certificação (melhoria do desempenho energético demonstrada)", "Outro requisito", "2021-11-01", "Internacional",
     "Organismo de certificação", "Para certificar, a organização tem de demonstrar melhoria do desempenho energético (IDE vs LBE).", "Outro requisito subscrito", "Decisão de certificar em 2027 (OE-02).",
     "GES", "Todos", "RG-SGE-05 LBE_Modelo", "Melhoria demonstrada em out–dez/2026 (5,4%)", "Registo", "2026-12-31", "Conforme", "2026-12-18", 12, "—", GE, "https://www.iso.org/standard/77575.html", "Outro requisito", "Candidata à certificação", "RG-SGE-10"),
    ("LEG-E-09", "Energia — tarifas", "Regulamento Tarifário e Regulamento de Relações Comerciais (ERSE)", "Regulamento", "2024-12-15", "Nacional", "ERSE",
     "Estrutura das faturas de MT (períodos, potência, reativa); regras de potência requisitada.", "Aplicável", "Cliente de média tensão.", "GES", "—", "RG-SGE-09 tbl_faturas",
     "Faturas verificadas mensalmente", "Registo", "2026-12-31", "Conforme", "2026-12-10", 12, "—", DFIN, "https://www.erse.pt", "Obrigação legal", "Cliente MT", "RG-SGE-10"),
    ("LEG-E-10", "Gases fluorados", "Regulamento (UE) 2024/573 (gases fluorados) — chiller CH-01 (R410A)", "Regulamento UE", "2024-02-20", "UE", "APA / IGAMAOT",
     "Deteção de fugas, técnicos certificados, registos.", "Aplicável", "Tratado pelo SGA (RG-SGA-04 e RG-SGA-10) — aqui só por ligação ao USE-04.", "UTL", "USE-04", "RG-SGA-10 tbl_manutencao_ambiental",
     "Ver RG-SGA-04", "Remissão", "2026-09-23", "Conforme", "2026-12-10", 12, "—", GSGA, "https://eur-lex.europa.eu/eli/reg/2024/573/oj", "Obrigação legal", "Operador", "RG-SGA-04"),
]

OBRIG = [
    ("OBR-06", "LEG-08", "Auditoria energética SGCIE (octenal)", "8 anos", "2030-06-30", "2022-06-15", "Relatório de auditoria SGCIE 2022", GE),
    ("OBRE-01", "LEG-08", "Plano de Racionalização do Consumo de Energia (PREn) submetido à ADENE", "Após cada auditoria", "2030-10-31", "2022-10-14", "PREn 2022–2030 aprovado (ARCE)", GE),
    ("OBRE-02", "LEG-08", "Relatório de execução e progresso (REP) 2024", "Bienal", "2024-10-31", "2024-10-25", "Comprovativo SGCIE", GE),
    ("OBRE-03", "LEG-08", "Relatório de execução e progresso (REP) 2026", "Bienal", "2028-10-31", "2026-10-28", "Comprovativo SGCIE (próximo REP em 2028)", GE),
    ("OBRE-04", "LEG-E-03", "Verificar a publicação do DL de transposição do art. 11.º da Diretiva (UE) 2023/1791 e o regime aplicável", "Semestral", "2027-06-30", "2026-12-10", "Registo de vigilância legal", GE),
    ("OBRE-05", "LEG-E-04", "Controlo prévio da UPAC (DGEG/E-REDES) antes da ligação", "Única", "2027-04-30", None, "Por fazer", DFIN),
]


def build(out):
    b = Book("RG-SGE-10", "Requisitos Legais e Outros Requisitos de Energia e Avaliação da Conformidade (SGCIE)",
             activities="Identificar e ter acesso aos requisitos legais e outros requisitos de energia; determinar como se aplicam; avaliar a conformidade em intervalos planeados; "
                        "acompanhar as obrigações e a trajetória das metas do SGCIE (PREn).",
             clauses="4.2 b) c) (requisitos legais e outros — como se aplicam; revistos); 5.2 d); 6.2.2 c); 9.1.2 (avaliar a conformidade em intervalos planeados; reter resultados e ações).",
             purpose="10 requisitos (LEG-08 do SGA + LEG-E-01 a 09 propostos para o RG-SGA-04) com a mesma estrutura do tbl_legal do SGA e estado calculado; 6 obrigações com prazos; "
                     "trajetória dos indicadores do PREn (consumo específico, intensidade energética e carbónica) face às metas de 2030.",
             links=[("RG-SGA-04", "Fonte única dos requisitos legais do SGI — incluir os LEG-E-xx na próxima revisão."),
                    ("RG-SGE-05", "IDE-02 e IDE-09 (base dos indicadores do PREn)."), ("RG-SGE-14", "Não conformidades legais tratadas como NC.")],
             guidance=[("SGCIE — perguntas frequentes (sgcie.pt/faq)", "Limiares 500 / 1 000 tep, indicadores do PREn (intensidade energética, consumo específico, intensidade carbónica) e metas de 6% / 4%."),
                       ("DGEG — página do SGCIE", "Gestão operacional pela ADENE; fiscalização pela DGEG."),
                       ("DNV / Comissão Europeia — Diretiva 2023/1791", "Limiares de 85 TJ (SGE obrigatório) e 10 TJ (auditoria) e prazo de 11/10/2027."),
                       ("ISO 50004:2020 §9.1.2", "Método de avaliação da conformidade (checklist, frequência, evidência).")],
             legal=[(r[2], r[7][:180]) for r in LEGAL[:5]])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("EstadoLegal", ["Conforme", "Não conforme", "Em avaliação", "Não aplicável"])

    LN = ["ID_Legal", "Tema", "Diploma_Documento", "Tipo_Diploma", "Data_Publicacao", "Ambito", "Entidade_Fiscalizadora", "Resumo_Obrigacoes", "Aplicabilidade", "Justificacao_Aplicabilidade",
          "Processos", "IDs_USE", "Disposicoes_Internas", "Avaliacao_Conformidade_Evidencia", "Tipo_Evidencia", "Data_Evidencia", "Estado", "Data_Avaliacao", "Periodicidade_Meses", "ID_Acao",
          "Responsavel", "Fonte_Oficial", "Natureza_Obrigacao", "Papel_Plasticom", "Registo_Dono"]
    lcols = [col("ID_Legal", 9, key="PK", desc="Requisito (LEG = RG-SGA-04; LEG-E = proposto)."), col("Tema", 16, desc="Tema."), col("Diploma_Documento", 44, desc="Diploma / documento."),
             col("Tipo_Diploma", 12, desc="Tipo."), col("Data_Publicacao", 11, "date", desc="Publicação."), col("Ambito", 10, desc="Âmbito."), col("Entidade_Fiscalizadora", 16, desc="Entidade."),
             col("Resumo_Obrigacoes", 50, desc="Obrigações."), col("Aplicabilidade", 16, desc="Aplicabilidade."), col("Justificacao_Aplicabilidade", 40, desc="Como se aplica à Plasticom (4.2 c)."),
             col("Processos", 10, desc="Processos."), col("IDs_USE", 14, desc="USE abrangidos (posição de IDs_Aspetos no SGA)."), col("Disposicoes_Internas", 26, desc="Onde é tratado."),
             col("Avaliacao_Conformidade_Evidencia", 36, desc="Evidência da última avaliação (9.1.2)."), col("Tipo_Evidencia", 14, desc="Tipo."), col("Data_Evidencia", 11, "date", desc="Data da evidência."),
             col("Estado", 11, dv="EstadoLegal", desc="Resultado da avaliação."), col("Data_Avaliacao", 11, "date", desc="Data da avaliação."), col("Periodicidade_Meses", 8, "int", desc="Intervalo planeado."),
             col("Proxima_Avaliacao", 11, "date", f='=IF(@ID_Legal@="","",EDATE(@Data_Avaliacao@,@Periodicidade_Meses@))', desc="Próxima avaliação."),
             col("Idade_Evidencia_Dias", 8, "int", f='=IF(@ID_Legal@="","",DataRef-@Data_Evidencia@)', desc="Idade da evidência."),
             col("Alerta", 10, f='=IF(@ID_Legal@="","",IF(@Estado@="Não conforme","NC",IF(@Proxima_Avaliacao@<DataRef,"Vencida",IF(@Estado@="Em avaliação","Acompanhar","OK"))))', desc="Alerta."),
             col("ID_Acao", 9, desc="Ação / obrigação (posição de ID_PAM no SGA).", req=False), col("Responsavel", 22, dv="Funcao", desc="Responsável."), col("Fonte_Oficial", 30, desc="URL oficial."),
             col("Natureza_Obrigacao", 14, desc="Legal / outro requisito."), col("Papel_Plasticom", 16, desc="Papel da Plasticom."), col("Registo_Dono", 18, desc="[Só SGE] Registo dono (fonte única).")]
    b.table("Requisitos_Legais", "tbl_legal", lcols, rows_from(LN, LEGAL, dates=("Data_Publicacao", "Data_Evidencia", "Data_Avaliacao")),
            "Requisitos legais e outros requisitos de energia (4.2, 9.1.2) — mesma estrutura do RG-SGA-04 tbl_legal.", title="REQUISITOS LEGAIS E OUTROS REQUISITOS DE ENERGIA (4.2; 9.1.2)",
            subtitle="Avaliação da conformidade de 10/12/2026 · LEG-E-xx a incluir no RG-SGA-04 (fonte única do SGI)",
            cf=[("Alerta", {"NC": "red", "Vencida": "red", "Acompanhar": "orange", "OK": "green"}), ("Estado", {"Conforme": "green", "Em avaliação": "orange", "Não conforme": "red"})], row_height=60, freeze_col=2)
    ocols = [col("ID_Obrigacao", 9, key="PK", desc="Obrigação."), col("ID_Legal", 9, desc="Requisito.", key="FK → tbl_legal"), col("Obrigacao", 50, desc="Obrigação."),
             col("Frequencia", 14, desc="Frequência."), col("Prazo_Proximo", 11, "date", desc="Próximo prazo."), col("Ultimo_Cumprimento", 11, "date", desc="Último cumprimento.", req=False),
             col("Evidencia", 34, desc="Evidência."), col("Responsavel", 22, dv="Funcao", desc="Responsável."),
             col("Dias_ate_Prazo", 8, "int", f='=IF(@ID_Obrigacao@="","",@Prazo_Proximo@-DataRef)', desc="Dias até ao prazo."),
             col("Estado", 11, f='=IF(@ID_Obrigacao@="","",IF(AND(@Ultimo_Cumprimento@<>"",@Ultimo_Cumprimento@<=@Prazo_Proximo@,@Dias_ate_Prazo@<0),"Cumprida",IF(@Dias_ate_Prazo@<0,"Atrasada",IF(@Dias_ate_Prazo@<=120,"A vencer","Em dia"))))', desc="Estado (Cumprida = obrigação pontual já cumprida no prazo).")]
    b.table("Obrigacoes", "tbl_obrigacoes", ocols, rows_from(input_names(ocols), OBRIG, dates=("Prazo_Proximo", "Ultimo_Cumprimento")),
            "Obrigações com prazo (mesma estrutura do RG-SGA-04 tbl_obrigacoes).", title="OBRIGAÇÕES DE ENERGIA COM PRAZO",
            cf=[("Estado", {"Atrasada": "red", "A vencer": "orange", "Em dia": "green", "Cumprida": "green"})], row_height=30)

    # trajetória SGCIE
    bm = edata.base_mensal()
    bm["Ano"] = [m.year for m in bm["Mes"]]
    massa = lambda df: (df["Unid_SOP"] * 22 + df["Unid_INJ"] * 6) / 1e6
    a25, a26 = bm[bm["Ano"] == 2025], bm[bm["Ano"] == 2026]
    k25 = a25["kWh_Total"].sum() * 12 / len(a25)
    t25 = massa(a25).sum() * 12 / len(a25)
    L25 = (a25["L_Gasoleo_Frota"] + a25["L_Gasoleo_Gerador"]).sum() * 12 / len(a25)
    SG = [(2021, "Auditoria SGCIE 2022 (ano de referência do PREn)", 6_880_000, 3150, 745.0, 10_900_000),
          (2023, "REP 2024 (simulado)", 7_020_000, 3300, 770.0, 11_600_000),
          (2025, "Ano de 2025: 10 meses medidos (mar–dez) extrapolados a 12", round(k25), round(L25), round(float(t25), 1), 12_700_000),
          (2026, "Ano de 2026 (fecho anual; RG-SGA-13 jan–dez)", int(a26["kWh_Total"].sum()), round(float((a26["L_Gasoleo_Frota"] + a26["L_Gasoleo_Gerador"]).sum())), round(float(massa(a26).sum()), 1), 14_300_000)]
    scols = [col("Ano", 6, "int", key="PK", desc="Ano."), col("Fonte", 40, desc="Origem dos dados."), col("kWh_Eletricidade", 12, "kwh", desc="Eletricidade (kWh)."),
             col("L_Gasoleo", 9, "num0", desc="Gasóleo (L)."), col("Producao_t", 9, "num1", desc="Produção (t) — frascos 22 g, tampas/potes 6 g (parâmetros do RG-SGA-13)."),
             col("VAB_EUR", 12, "eur", desc="Valor acrescentado bruto (simulado)."),
             col("tep", 9, "num1", f='=IF(@Ano@="","",(@kWh_Eletricidade@*0.215+@L_Gasoleo@*0.864)/1000)', desc="Energia primária (Despacho 17313/2008)."),
             col("CEE_kgep_t", 10, "num1", f='=IF(@Ano@="","",@tep@*1000/@Producao_t@)', desc="Consumo específico de energia (kgep/t)."),
             col("IE_kgep_kEUR", 10, "num3", f='=IF(@Ano@="","",@tep@*1000/(@VAB_EUR@/1000))', desc="Intensidade energética (kgep por mil € de VAB)."),
             col("IC_kgCO2e_kgep", 9, "num3", f='=IF(@Ano@="","",(@kWh_Eletricidade@*0.47+@L_Gasoleo@*2.68)/(@tep@*1000))', desc="Intensidade carbónica (kgCO2e/kgep)."),
             col("Meta_CEE", 10, "num1", f='=IF(@Ano@="","",INDEX(#CEE_kgep_t#,1)*(1-0.06*MAX(0,MIN(8,@Ano@-2022))/8))', desc="Trajetória linear: −6% em 8 anos (2022–2030) face a 2021."),
             col("Meta_IE", 10, "num3", f='=IF(@Ano@="","",INDEX(#IE_kgep_kEUR#,1)*(1-0.06*MAX(0,MIN(8,@Ano@-2022))/8))', desc="Idem para a intensidade energética."),
             col("Estado_CEE", 11, f='=IF(@Ano@="","",IF(@Ano@=2021,"Referência",IF(@CEE_kgep_t@<=@Meta_CEE@,"Na trajetória","Acima da meta")))', desc="CEE face à trajetória."),
             col("Estado_IE", 11, f='=IF(@Ano@="","",IF(@Ano@=2021,"Referência",IF(@IE_kgep_kEUR@<=@Meta_IE@,"Na trajetória","Acima da meta")))', desc="IE face à trajetória."),
             col("Estado_IC", 11, f='=IF(@Ano@="","",IF(@Ano@=2021,"Referência",IF(@IC_kgCO2e_kgep@<=INDEX(#IC_kgCO2e_kgep#,1)+0.0005,"Mantida","Aumentou")))', desc="Intensidade carbónica mantida?")]
    b.table("Trajetoria_SGCIE", "tbl_sgcie", scols, [dict(zip(["Ano", "Fonte", "kWh_Eletricidade", "L_Gasoleo", "Producao_t", "VAB_EUR"], s_)) for s_ in SG],
            "Indicadores do PREn e trajetória das metas SGCIE (2022–2030).", title="TRAJETÓRIA DOS INDICADORES DO PREn (SGCIE)",
            subtitle="Fatores do Despacho 17313/2008: 0,215 kgep/kWh; 0,864 kgep/L; 0,47 kgCO2e/kWh; 2,68 kgCO2e/L · 2021 e 2023 simulados (relatórios SGCIE) · VAB simulado",
            cf=[("Estado_CEE", {"Acima": "red", "Na trajetória": "green"}), ("Estado_IE", {"Acima": "red", "Na trajetória": "green"}), ("Estado_IC", {"Aumentou": "red", "Mantida": "green"})], row_height=30)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
