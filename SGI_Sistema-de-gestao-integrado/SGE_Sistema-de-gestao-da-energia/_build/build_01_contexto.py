"""RG-SGE-01 — Contexto (lente da energia), partes interessadas, alterações climáticas, âmbito e fronteiras do SGE.
ISO 50001:2018 + Amd 1:2024: 4.1, 4.2, 4.3. Fonte única do contexto do SGI: RG-SGA-01 (PESTEL/SWOT) — aqui só se acrescentam
as questões específicas de energia e se ligam as do SGA por ID (ID_Contexto_SGI)."""
from sgelib import *
from dimse import *

# questões externas e internas pertinentes ao SGE (4.1): (ID, interna/externa, dimensão, questão, efeito no SGE, direção, fonte de monitorização, ID SGI, resposta, dono)
CONTEXTO = [
    ("CTX-E-01", "Externa", "Político / legal", "Pacto Ecológico, PNEC 2030 e Diretiva (UE) 2023/1791 (eficiência energética): SGE obrigatório > 85 TJ e auditoria > 10 TJ; transposição nacional em curso.",
     "Plasticom (≈ 26 TJ/ano) terá auditoria de 4 em 4 anos ou SGE ISO 50001 certificado (isenção).", "Oportunidade", "DGEG / ADENE / Diário da República", "PES-01", "Certificar a ISO 50001 até 2027 (RE-01, OE-02).", GE),
    ("CTX-E-02", "Externa", "Económico", "Volatilidade do preço da eletricidade (MIBEL) e das tarifas de acesso às redes; 1.º custo ambiental (≈ € 1,05 M em 2026).",
     "Cada +0,03 €/kWh custa ≈ € 235 000/ano; aumenta o valor das medidas de eficiência.", "Ameaça", "Faturas (RG-SGE-09), OMIE, ERSE", "PES-02", "Contratos a prazo; medidas de eficiência e UPAC (R25).", DFIN),
    ("CTX-E-03", "Externa", "Ambiental / clima", "Ondas de calor mais frequentes (verão de 2026 +2 °C): mais consumo do chiller e do AVAC.",
     "Aumenta o consumo do USE-04; em ago/2026 a potência tomada (1 429 kW) ultrapassou a contratada (1 400 kW).", "Ameaça", "IPMA; graus-dia (RG-SGE-05)", "PES-08", "Free-cooling e setpoint mais alto (OBJ-E-04); gestão da potência (OPE-16).", TUTL),
    ("CTX-E-04", "Externa", "Tecnológico", "Máquinas totalmente elétricas, servo-bombas, VSD, IoT e analytics de energia a baixo custo.",
     "Novas máquinas consomem 30–40% menos (campanha PA-01); a submedição permite IDE por USE.", "Oportunidade", "Fornecedores; feiras (K, Fakuma)", "PES-06", "Critérios energéticos nas compras (8.3) e LCC (RG-SGE-09).", GE),
    ("CTX-E-05", "Externa", "Mercado / clientes", "Clientes de cosmética e alimentar pedem dados de carbono do produto (PCF) e eletricidade renovável (CDP, EcoVadis).",
     "Requisito de dados de energia por SKU/máquina; eletricidade renovável como critério de compra.", "Oportunidade", "Questionários de clientes (RG-SGQ-10)", "SWT-O03", "IDE por máquina e UPAC (OBJ-E-05).", GE),
    ("CTX-E-06", "Externa", "Financeiro", "Financiamento para eficiência energética e renováveis (Portugal 2030, Fundo Ambiental, PRR).",
     "Reduz o retorno das medidas de investimento.", "Oportunidade", "ADENE; COMPETE 2030", "TOWS-03", "Candidatura da submedição e da UPAC (RG-26-D03).", DFIN),
    ("CTX-E-07", "Interna", "Infraestrutura", "Parque de máquinas misto: 7 máquinas hidráulicas de 2011–2015 com consumo 40–60% acima das elétricas.",
     "Principal fonte de ineficiência e de carga em espera.", "Fraqueza", "Campanha PA-01 (RG-SGE-04)", "SWT-W01", "OPE-06, OPE-14 no plano de investimentos.", GMAN),
    ("CTX-E-08", "Interna", "Dados", "Sem submedição: consumos por uso estimados (rateio por horas × kW).",
     "Impede IDE por USE e a demonstração da melhoria exigida para certificar (ISO 50003).", "Fraqueza", "RG-SGA-02 R35", "SWT-W01", "PA-E-01: 6 analisadores em serviço desde 15/12/2026.", TI_),
    ("CTX-E-09", "Interna", "Cultura / pessoas", "Cultura de dados industriais (OEE, SPC) e sugestões de energia do chão de fábrica (KZ-01, KZ-04).",
     "Facilita IDE, rondas e controlo operacional.", "Força", "RG-SGA-16", "SWT-F01", "Ligar a energia ao quadro SQDC dos turnos.", GPROD),
    ("CTX-E-10", "Interna", "Processo", "Processo 100% elétrico (sem combustão): descarbonização depende da eletricidade.",
     "Âmbito 1 muito baixo; a UPAC e as garantias de origem descarbonizam quase tudo.", "Força", "Inventário GEE (RG-SGA-19)", "SWT-F02", "OBJ-E-05.", DFIN),
    ("CTX-E-11", "Interna", "Operação", "Expansão das linhas alimentar e farmacêutica (+4 máquinas em 07/2026).",
     "Alteração de fatores estáticos: a LBE-01 teve de ser ajustada (ALE-01) e a potência tomada subiu ≈ 30% (ultrapassagem em ago/2026).", "Ameaça", "RG-SGA-18 ALT-2026-03", "—", "Ajuste não rotineiro; nova LBE em 07/2027.", GE),
]

# partes interessadas (4.2) — mesmas colunas do RG-SGA-01 / RG-SGQ-01 tbl_partes_interessadas (Tratado_pelo_SGE na posição de Torna_se_Obrigacao)
PI = [
    ("PIE-01", "Gestão de topo / acionistas", "Interna", "Gestão de topo", "Custos de energia controlados, retorno das medidas, reputação, certificação.", "Clima", "Sim", "Sim", "Requisito interno",
     "—", "Revisão pela gestão; quadro de IDE", "Mensal", "Alta", "Alta", "Gerir de perto", "RE-01", DG, "PI-03", "Mesma PI do SGA (PI-03)", "RG-SGE-13"),
    ("PIE-02", "DGEG / ADENE (SGCIE)", "Externa", "Regulador", "Auditoria energética, PREn e relatórios de execução (REP) com metas de −6% em 8 anos.", "Clima", "Sim", "Sim", "Obrigação legal",
     "LEG-08; LEG-E-01", "Plataforma SGCIE", "Bienal (REP); octenal (auditoria)", "Alta", "Média", "Gerir de perto", "RE-02", GE, "—", "DL 71/2008", "RG-SGE-10"),
    ("PIE-03", "Comercializador de eletricidade (ENE-01)", "Externa", "Fornecedor", "Contrato de fornecimento, potência contratada, garantias de origem.", "Clima", "Sim", "Sim", "Contrato",
     "—", "Faturas mensais; reunião anual", "Mensal", "Média", "Média", "Manter satisfeito", "RE-03", DFIN, "—", "Contrato MT 2025–2027", "RG-SGE-09"),
    ("PIE-04", "Operador da rede de distribuição (E-REDES)", "Externa", "Regulador técnico", "Contagem, qualidade de serviço, potência requisitada, ligação da UPAC.", "—", "Sim", "Sim", "Obrigação legal",
     "LEG-E-04", "Portal do operador", "Anual", "Média", "Baixa", "Manter informado", "—", GMAN, "—", "RRC / DL 15/2022", "RG-SGE-09"),
    ("PIE-05", "Clientes de cosmética, alimentar e farmacêutica", "Externa", "Cliente", "Dados de energia/carbono por produto, eletricidade renovável, questionários CDP/EcoVadis.", "Clima", "Sim", "Sim", "Requisito do cliente",
     "—", "Questionários; auditorias de clientes", "Anual", "Alta", "Média", "Gerir de perto", "OE-03", GE, "PI-01", "Requisitos de sustentabilidade dos contratos", "RG-SGE-05 IDE-10"),
    ("PIE-06", "Organismo de certificação (ISO 50001)", "Externa", "Certificação", "Demonstração da melhoria do desempenho energético (ISO 50003:2021).", "—", "Sim", "Sim", "Outro requisito subscrito",
     "—", "Auditorias de certificação", "Anual", "Alta", "Média", "Gerir de perto", "RE-01", GE, "—", "ISO 50003:2021", "RG-SGE-05 LBE_Modelo"),
    ("PIE-07", "Trabalhadores e chefes de turno", "Interna", "Colaboradores", "Condições térmicas adequadas (AVAC), formação, reconhecimento das sugestões.", "Clima", "Sim", "Não", "—",
     "—", "Caixa de sugestões; reuniões de turno", "Contínua", "Média", "Média", "Envolver", "—", RH_, "PI-05", "—", "RG-SGE-07 tbl_sugestoes"),
    ("PIE-08", "Bancos e seguradoras", "Externa", "Financeiro", "Exposição a custos de energia e risco climático; taxonomia da UE.", "Clima", "Sim", "Não", "—",
     "—", "Relatório anual", "Anual", "Média", "Baixa", "Manter informado", "RE-03", DFIN, "—", "—", "RG-SGA-17"),
    ("PIE-09", "Entidades de financiamento (Portugal 2030, Fundo Ambiental)", "Externa", "Financeiro", "Auditoria prévia e M&V das poupanças financiadas.", "Clima", "Sim", "Sim", "Obrigação contratual",
     "—", "Avisos; relatórios de execução", "Por candidatura", "Média", "Média", "Manter satisfeito", "OE-01", DFIN, "—", "Regulamento do aviso", "RG-SGE-11"),
    ("PIE-10", "Comunidade / vizinhança", "Externa", "Comunidade", "Ruído dos compressores e da torre; UPAC visível.", "—", "Sim", "Não", "—",
     "LEG-05", "Canal de reclamações", "Contínua", "Baixa", "Média", "Manter informado", "—", GSGA, "PI-08", "Tratado pelo SGA", "RG-SGA-09"),
]

AMBITO = [
    ("Âmbito do SGE (4.3)", "Uso e consumo de energia na conceção, produção e decoração de embalagens plásticas (frascos, tampas e potes) por injeção, injeção-sopro, serigrafia e hot foil, "
                            "incluindo utilidades, armazenagem, expedição, serviços de apoio e frota de serviço da Unidade 1 da Plasticom, Marinha Grande."),
    ("Fronteiras físicas", "Terreno de 45 000 m² da Unidade 1: naves de produção, central de ar comprimido, chiller e torre, armazéns, escritórios, laboratório, parque de resíduos e parque de viaturas; "
                           "contador geral de média tensão (PT privativo) como fronteira de medida da eletricidade."),
    ("Fronteiras organizacionais", "Todas as funções da Unidade 1; exclui a sede comercial e os armazéns de clientes (não há autoridade sobre o seu consumo)."),
    ("Tipos de energia incluídos", "Eletricidade da rede, gasóleo da frota e do gerador; ar comprimido como vetor interno; eletricidade solar da UPAC (a partir de 2027). "
                                   "Nenhum tipo de energia dentro das fronteiras é excluído (4.3)."),
    ("Autoridade para controlar (4.3)", "A Plasticom controla a eficiência energética, o uso e o consumo de todos os equipamentos dentro das fronteiras (instalações próprias; frota própria)."),
    ("Questões de 4.1 e requisitos de 4.2 considerados", "tbl_contexto_energia (11 questões) e tbl_partes_interessadas (10 partes) deste registo; contexto geral do SGI no RG-SGA-01."),
    ("Integração no SGI", "O SGE partilha com o SGA e o SGQ: contexto (RG-SGA-01), riscos (RG-SGA-02), requisitos legais (RG-SGA-04), controlo documental (PR-SGA-08), "
                          "planeamento de alterações (PR-SGA-06/RG-SGA-18) e auditorias/revisões integradas."),
    ("Disponibilidade", "Âmbito e fronteiras mantidos como informação documentada (4.3) neste registo e no MAN-SGE-01."),
]

FRONTEIRAS = [
    ("FRT-01", "Nave de sopro (ISBM-001 a ISBM-010)", "Dentro", "Eletricidade; ar comprimido", "QGBT-SOP", "SOP", "Sim"),
    ("FRT-02", "Nave de injeção (IM-001 a IM-009)", "Dentro", "Eletricidade; ar comprimido", "QGBT-INJ", "INJ", "Sim"),
    ("FRT-03", "Decoração (SS-001/002, HF-001/002)", "Dentro", "Eletricidade; ar comprimido", "QGBT-DEC", "SER; HFS", "Sim"),
    ("FRT-04", "Central de ar comprimido (CMP-01/02, secadores)", "Dentro", "Eletricidade", "Q-AR", "UTL-AR", "Sim"),
    ("FRT-05", "Arrefecimento (chiller CH-01, torre TR-01, bombas)", "Dentro", "Eletricidade", "Q-FRIO", "UTL-FRIO", "Sim"),
    ("FRT-06", "Escritórios, laboratório, armazéns, iluminação exterior, AVAC", "Dentro", "Eletricidade", "Q-SERV", "GER", "Sim"),
    ("FRT-07", "Frota de serviço (2 viaturas + 1 carrinha)", "Dentro", "Gasóleo", "Cartão de frota", "FRO", "Sim"),
    ("FRT-08", "Gerador de emergência GE-01", "Dentro", "Gasóleo", "Registo de testes", "GER-EMG", "Sim"),
    ("FRT-09", "Cobertura (futura UPAC ≈ 1 MWp)", "Dentro (2027)", "Solar fotovoltaica", "Contador da UPAC", "—", "Sim"),
    ("FRT-10", "Transporte de clientes e fornecedores (subcontratado)", "Fora", "Gasóleo", "—", "—", "Não (influência: âmbito 3 no RG-SGA-19)"),
    ("FRT-11", "Sede comercial (Lisboa)", "Fora", "Eletricidade", "—", "—", "Não (outra organização)"),
]

CLIMA = [
    ("CLE-01", "As alterações climáticas são uma questão pertinente para o SGE? (4.1, Amd 1:2024)", "Sim",
     "O consumo de frio e AVAC depende da temperatura (b2 = 56 kWh por grau-dia na LBE-01); o preço e a origem da eletricidade dependem da transição energética; "
     "clientes exigem energia renovável.", "CTX-E-03; CTX-E-05; R34; RG-SGA-01 PES-08"),
    ("CLE-02", "As partes interessadas têm requisitos relacionados com as alterações climáticas? (4.2 Nota, Amd 1:2024)", "Sim",
     "Clientes (eletricidade renovável, PCF), bancos (taxonomia), SGCIE (intensidade carbónica), CSRD/ESRS E1 via clientes.", "PIE-02; PIE-05; PIE-08"),
    ("CLE-03", "Como o SGE responde", "—", "IDE-10 (renovável), OBJ-E-05, UPAC (PA-E-07), normalização por graus-dia, plano de transição PL-SGA-01.", "RG-SGE-05; PL-SGA-01"),
]


def build(out):
    b = Book("RG-SGE-01", "Contexto, Partes Interessadas, Âmbito e Fronteiras do SGE",
             activities="Determinar as questões externas e internas que afetam a capacidade de atingir os resultados pretendidos do SGE e de melhorar o desempenho energético; "
                        "partes interessadas e requisitos aplicáveis; alterações climáticas; âmbito e fronteiras.",
             clauses="4.1 (questões externas e internas; alterações climáticas — Amd 1:2024); 4.2 a)–c) (partes interessadas, requisitos pertinentes, requisitos legais e outros — acesso; Nota climática); "
                     "4.3 (fronteiras e aplicabilidade; autoridade para controlar; nenhum tipo de energia excluído; âmbito e fronteiras mantidos como informação documentada); 4.4.",
             purpose="Vista do contexto do SGI com a lente da energia (11 questões ligadas ao PESTEL/SWOT do RG-SGA-01), 10 partes interessadas com o mesmo formato do SGA/SGQ, "
                     "determinação sobre alterações climáticas, declaração do âmbito e mapa de fronteiras com tipos de energia e pontos de medida.",
             links=[("RG-SGA-01", "Fonte única do contexto do SGI (PES-xx, SWT-xx, TOWS-xx) — ligado por ID_Contexto_SGI."),
                    ("RG-SGA-04 / RG-SGE-10", "Requisitos legais de energia (IDs_Legal)."), ("RG-SGE-03", "Riscos e oportunidades (ID_RO)."),
                    ("RG-SGE-06", "Pontos de medida das fronteiras (tbl_contadores).")],
             guidance=[("ISO 50004:2020 §4", "Exemplos de questões internas/externas de energia e determinação das fronteiras."),
                       ("ISO 50001:2018/Amd 1:2024", "Determinar se as alterações climáticas são pertinentes (4.1) e nota sobre requisitos climáticos das partes interessadas (4.2)."),
                       ("M-4 Contexto (curso Bureau Veritas, pasta de interpretação)", "Interpretação de 4.1–4.3 (autoridade para controlar e não exclusão de tipos de energia)."),
                       ("ISO 50006:2023 §5.3", "Fronteiras de medida coerentes com os IDE.")],
             legal=[("DL 71/2008 (SGCIE)", "Instalação consumidora intensiva: parte interessada DGEG/ADENE."),
                    ("Diretiva (UE) 2023/1791, art. 11.º", "Questão CTX-E-01.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("SimNao", SIMNAO)
    b.add_list("Direcao", ["Oportunidade", "Ameaça", "Força", "Fraqueza"])

    ccols = [col("ID_Contexto", 9, key="PK", desc="Questão de energia."), col("Interna_Externa", 9, desc="Interna / externa."), col("Dimensao", 14, desc="Dimensão (PESTEL / interna)."),
             col("Questao", 50, desc="Questão pertinente (4.1)."), col("Efeito_no_SGE", 44, desc="Efeito na capacidade de atingir os resultados do SGE e melhorar o desempenho energético."),
             col("Direcao", 11, dv="Direcao", desc="Oportunidade / ameaça / força / fraqueza."), col("Fonte_Monitorizacao", 28, desc="Como é monitorizada."),
             col("ID_Contexto_SGI", 11, desc="Fator equivalente no RG-SGA-01 (fonte única do SGI).", key="FK → RG-SGA-01 tbl_pestel / tbl_swot / tbl_tows", req=False),
             col("Resposta", 40, desc="Resposta / ação."), col("Dono", 22, dv="Funcao", desc="Dono."),
             col("Data_Revisao", 11, "date", desc="Última revisão.")]
    rows = rows_from(input_names(ccols), [c + ("2026-12-10",) for c in CONTEXTO], dates=("Data_Revisao",))
    b.table("Contexto_Energia", "tbl_contexto_energia", ccols, rows, "Questões externas e internas pertinentes ao SGE (4.1), ligadas ao contexto do SGI.",
            title="CONTEXTO DO SGE — QUESTÕES EXTERNAS E INTERNAS (4.1)", subtitle="Vista de energia do contexto do SGI · Fonte única: RG-SGA-01 (PESTEL/SWOT/TOWS) — novas questões de energia com prefixo CTX-E",
            cf=[("Direcao", {"Ameaça": "red", "Fraqueza": "orange", "Oportunidade": "green", "Força": "blue"})], row_height=48, freeze_col=2)

    pcols = [col("ID_PI", 8, key="PK", desc="Parte interessada."), col("Parte_Interessada", 30, desc="Parte interessada."), col("Tipo", 9, desc="Interna / externa."),
             col("Categoria", 14, desc="Categoria."), col("Necessidades_Expectativas", 44, desc="Necessidades e expectativas (4.2 a–b)."), col("Condicao_Ambiental", 10, desc="Ligação ao clima (Amd 1:2024)."),
             col("Relevante", 8, dv="SimNao", desc="Relevante para o SGE?"),
             col("Tratado_pelo_SGE", 9, dv="SimNao", desc="O SGE trata este requisito? (posição equivalente a Torna_se_Obrigacao do SGA)."),
             col("Tipo_Obrigacao", 16, desc="Obrigação legal / contrato / outro requisito."), col("IDs_Legal", 14, desc="Requisitos legais.", key="FK → RG-SGA-04 / RG-SGE-10", req=False),
             col("Como_Monitorizar", 26, desc="Como se monitoriza."), col("Frequencia", 14, desc="Frequência."), col("Influencia", 8, desc="Influência."), col("Interesse", 8, desc="Interesse."),
             col("Estrategia", 14, desc="Estratégia (matriz influência × interesse)."), col("ID_RO", 8, desc="Risco/oportunidade.", key="FK → RG-SGE-03", req=False),
             col("Dono", 22, dv="Funcao", desc="Dono da relação."), col("ID_PI_SGI", 8, desc="Mesma parte no RG-SGA-01.", req=False),
             col("Fonte_Requisito", 26, desc="[Só SGE] Origem do requisito."), col("Registo_Evidencia", 20, desc="[Só SGE] Onde está a evidência.")]
    b.table("Partes_Interessadas", "tbl_partes_interessadas", pcols, rows_from(input_names(pcols), PI),
            "Partes interessadas do SGE e requisitos (4.2) — mesmas colunas do SGA/SGQ.", title="PARTES INTERESSADAS E REQUISITOS (4.2)", row_height=40, freeze_col=2)

    b.table("Clima", "tbl_clima", [col("ID_Clima", 8, key="PK"), col("Pergunta", 44), col("Resposta", 8), col("Justificacao", 70), col("Ligacoes", 30)],
            [dict(zip(["ID_Clima", "Pergunta", "Resposta", "Justificacao", "Ligacoes"], c)) for c in CLIMA],
            "Determinação sobre as alterações climáticas (ISO 50001:2018/Amd 1:2024) — mesma estrutura do RG-SGQ-01.", title="ALTERAÇÕES CLIMÁTICAS (4.1 e 4.2 — Amd 1:2024)", row_height=48)
    b.table("Ambito", "tbl_ambito", [col("Elemento", 30, key="PK"), col("Conteudo", 110)], [dict(Elemento=a, Conteudo=c) for a, c in AMBITO],
            "Âmbito e fronteiras do SGE (4.3 — mantidos como informação documentada).", title="ÂMBITO E FRONTEIRAS DO SGE (4.3)", row_height=45)
    fcols = [col("ID_Fronteira", 8, key="PK", desc="Área / sistema."), col("Area_Sistema", 44, desc="Área ou sistema."), col("Dentro_Fora", 11, desc="Dentro / fora das fronteiras."),
             col("Tipos_Energia", 24, desc="Tipos de energia."), col("Ponto_Medida", 16, desc="Contador / quadro (RG-SGE-06).", key="FK → RG-SGE-06 tbl_contadores", req=False),
             col("ID_Uso", 10, desc="Uso de energia (RG-SGE-04).", req=False), col("Autoridade_Controlo", 30, desc="A Plasticom tem autoridade para controlar? (4.3)")]
    b.table("Mapa_Fronteiras", "tbl_fronteiras", fcols, rows_from(input_names(fcols), FRONTEIRAS), "Mapa das fronteiras com tipos de energia e pontos de medida (4.3).",
            title="MAPA DAS FRONTEIRAS DO SGE (4.3)", cf=[("Dentro_Fora", {"Fora": "gray", "Dentro": "green"})], row_height=20)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
