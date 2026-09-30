"""RG-SGE-08 — Controlo operacional dos USE: critérios de operação e manutenção, comunicação dos critérios e rondas de energia.
ISO 50001:2018 8.1 a)–d) (+ alterações planeadas / não intencionais; USE subcontratados)."""
import numpy as np
from sgelib import *
from dimse import *

CRITERIOS = [
    # (ID, USE, equipamento, parâmetro, critério de operação/manutenção, desvio significativo, método de verificação, frequência, responsável, comunicado a, documento, tipo)
    ("CO-01", "USE-01", "ISBM (todas)", "Standby em paragens > 30 min e pausas", "Fornos de pré-forma a 60%, bomba hidráulica desligada", "Máquina aquecida em vazio > 30 min", "Ronda de energia", "Semanal", CTURNO, "Operadores de sopro", "IT-SGE-01", "Operação"),
    ("CO-02", "USE-01", "ISBM (todas)", "Pressão de sopro", "Pressão mínima validada por SKU (ficha de parâmetros)", "> 2 bar acima da ficha", "Leitura no HMI", "Por arranque", F["FE-17"], "Operadores de sopro", "Ficha de parâmetros", "Operação"),
    ("CO-03", "USE-01", "ISBM hidráulicas", "Manutenção hidráulica", "Filtros e óleo no prazo; sem fugas de óleo", "Plano atrasado > 15 dias", "SAP PM", "Mensal", GMAN, "Manutenção", "Plano de manutenção", "Manutenção"),
    ("CO-04", "USE-01", "ISBM elétricas", "Recuperação de ar", "Sistema de recuperação ativo", "Recuperação desativada", "Ronda de energia", "Semanal", TUTL, "Manutenção", "IT-SGE-02", "Operação"),
    ("CO-05", "USE-02", "Injetoras (todas)", "Standby em paragens > 30 min e pausas", "Resistências a 60%, bomba desligada (hidráulicas)", "Máquina aquecida em vazio > 30 min", "Ronda de energia", "Semanal", CTURNO, "Operadores de injeção", "IT-SGE-01", "Operação"),
    ("CO-06", "USE-02", "Injetoras (todas)", "Temperaturas do canhão", "Dentro de ±5 °C do setpoint da ficha do molde", "> 10 °C acima", "Leitura no HMI", "Por arranque", F["FE-16"], "Operadores de injeção", "Ficha do molde", "Operação"),
    ("CO-07", "USE-02", "Injetoras (todas)", "Isolamento dos canhões", "Mantas instaladas e sem danos", "Manta em falta/danificada", "Ronda de energia", "Mensal", F["FE-20"], "Manutenção", "IT-SGE-01", "Manutenção"),
    ("CO-08", "USE-02", "IM-002, IM-004", "Bomba hidráulica", "Pressão do sistema dentro da ficha; sem sobreaquecimento do óleo", "Óleo > 55 °C", "Leitura no HMI", "Semanal", GMAN, "Manutenção", "Plano de manutenção", "Manutenção"),
    ("CO-09", "USE-03", "Rede de ar", "Pressão de serviço", "6,8–7,2 bar (setpoint 6,8 desde 16/11/2026)", "> 7,2 bar", "Controlador dos compressores", "Diária", TUTL, "Utilidades", "IT-SGE-02", "Operação"),
    ("CO-10", "USE-03", "Rede de ar", "Fugas", "Fugas ≤ 10% no teste de vazio; etiquetas reparadas em ≤ 5 dias", "Fugas > 15% ou etiqueta > 10 dias", "Teste de vazio + ultrassom", "Mensal", TUTL, "Manutenção", "IT-SGE-02", "Manutenção"),
    ("CO-11", "USE-03", "Rede de ar", "Ramais ao fim de semana", "Válvulas das áreas paradas fechadas à sexta às 22 h", "Válvula aberta sem produção", "Ronda de sexta", "Semanal", CTURNO, "Chefes de turno", "IT-SGE-02", "Operação"),
    ("CO-12", "USE-03", "Secadores e filtros", "Perda de carga dos filtros", "ΔP ≤ 0,4 bar", "ΔP > 0,4 bar", "Manómetro diferencial", "Semanal", TUTL, "Utilidades", "Plano de manutenção", "Manutenção"),
    ("CO-13", "USE-04", "Chiller CH-01", "Setpoint da água gelada", "≥ 10 °C (desde 01/12/2026, validado por DOE; 11 °C em ensaio)", "< 9 °C sem justificação", "Controlador", "Diária", TUTL, "Utilidades", "IT-SGE-03", "Operação"),
    ("CO-14", "USE-04", "Circuito de frio", "ΔT ida/retorno", "4–6 °C", "< 3 °C (caudal excessivo)", "Sondas", "Semanal", TUTL, "Utilidades", "IT-SGE-03", "Operação"),
    ("CO-15", "USE-04", "Torre TR-01", "Limpeza dos permutadores", "Limpeza antes do verão e sempre que ΔT cai > 1 °C", "ΔT caiu > 1 °C", "Registo de manutenção", "Anual / condição", F["FE-20"], "Manutenção", "Plano de manutenção", "Manutenção"),
    ("CO-16", "Serviços", "Iluminação e AVAC", "Luzes e AVAC desligados em zonas sem atividade", "Zonas vazias com luzes apagadas; AVAC 21–25 °C", "Zona vazia iluminada", "Ronda de energia", "Semanal", CTURNO, "Todos", "IT-SGE-01", "Operação"),
]
PONTOS_RONDA = ["CO-01", "CO-05", "CO-07", "CO-09", "CO-11", "CO-13", "CO-16"]


def build(out):
    b = Book("RG-SGE-08", "Controlo Operacional dos Usos Significativos de Energia",
             activities="Estabelecer critérios de operação e manutenção dos USE cuja ausência pode levar a desvio significativo do desempenho energético, comunicá-los, controlar os processos "
                        "segundo esses critérios e manter evidência; controlar alterações planeadas e rever as não intencionais.",
             clauses="8.1 a) critérios de operação e manutenção (desvio significativo definido pela organização); b) comunicação dos critérios; c) controlo dos processos; d) informação documentada "
                     "(na medida necessária); controlo de alterações planeadas e consequências das não intencionais; USE subcontratados controlados (8.3).",
             purpose="16 critérios operacionais (CO-xx) por USE com o limite de desvio significativo, método e frequência de verificação; rondas de energia semanais jul–dez/2026 (simuladas) "
                     "com taxa de conformidade por critério calculada.",
             links=[("RG-SGE-04 tbl_use", "USE e pessoas que os influenciam."), ("RG-SGA-10", "Rondas ambientais (RON-10 — máquinas e iluminação em paragens) — mesma ronda integrada no SGI."),
                    ("RG-SGA-18 / PR-SGA-06", "Controlo das alterações planeadas (secção de energia)."), ("RG-SGE-11", "Desvios significativos do desempenho investigados.")],
             guidance=[("ISO 50004:2020 §8.1", "Exemplos de critérios de operação e manutenção para USE."),
                       ("ISO 11011:2013", "Pressão, fugas e secadores da central de ar."),
                       ("Kent/BPF", "Standby, isolamento de canhões, setpoint da água gelada (+1 °C ≈ −3%), filtros com ΔP ≤ 0,4 bar."),
                       ("M-8 Operação (curso Bureau Veritas)", "Interpretação de 8.1–8.3 (critérios, alterações e USE subcontratados).")],
             legal=[("Reg. (UE) 2024/573 (gases fluorados)", "Manutenção e deteção de fugas do chiller CH-01 (R410A) — tratado no RG-SGA-10; aqui só o setpoint e a eficiência.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("ResultadoRonda", ["Conforme", "Não conforme", "N/A"])

    ccols = [col("ID_Criterio", 8, key="PK", desc="Critério operacional."), col("ID_USE", 9, desc="USE (RG-SGE-04).", key="FK → RG-SGE-04 tbl_use"), col("Equipamento", 18, desc="Equipamento."),
             col("Parametro", 28, desc="Parâmetro controlado."), col("Criterio", 40, desc="Critério de operação / manutenção (8.1 a)."), col("Desvio_Significativo", 26, desc="O que é desvio significativo (Nota de 8.1)."),
             col("Metodo_Verificacao", 22, desc="Como se verifica (8.1 c)."), col("Frequencia", 14, desc="Frequência."), col("Responsavel", 22, dv="Funcao", desc="Responsável."),
             col("Comunicado_A", 22, desc="A quem é comunicado (8.1 b)."), col("Documento", 16, desc="Onde está escrito (8.1 d)."), col("Tipo", 11, desc="Operação / manutenção."),
             col("N_Verificacoes", 8, "int", f='=IF(@ID_Criterio@="","",COUNTIFS(tbl_rondas_energia[ID_Criterio],@ID_Criterio@,tbl_rondas_energia[Resultado],"<>N/A"))', desc="Verificações registadas."),
             col("Taxa_Conformidade", 9, "pct", f='=IF(OR(@ID_Criterio@="",@N_Verificacoes@=0),"",COUNTIFS(tbl_rondas_energia[ID_Criterio],@ID_Criterio@,tbl_rondas_energia[Resultado],"Conforme")/@N_Verificacoes@)', desc="Conformes ÷ verificações."),
             col("Alerta", 10, f='=IF(OR(@ID_Criterio@="",@Taxa_Conformidade@=""),"",IF(@Taxa_Conformidade@<0.8,"Rever",IF(@Taxa_Conformidade@<0.95,"Atenção","OK")))', desc="< 80% rever.")]
    b.table("Criterios_Operacionais", "tbl_criterios_operacionais", ccols, rows_from(input_names(ccols), CRITERIOS),
            "Critérios de operação e manutenção dos USE (8.1).", title="CRITÉRIOS OPERACIONAIS DOS USE (8.1)",
            subtitle="Desvio significativo definido por critério · Comunicação aos operadores nas IT-SGE-01 a 03 e no quadro SQDC",
            cf=[("Alerta", {"Rever": "red", "Atenção": "orange", "OK": "green"})], row_height=36, freeze_col=2)

    rng = np.random.default_rng(8108)
    prob_nc = {"CO-01": 0.30, "CO-05": 0.22, "CO-07": 0.10, "CO-09": 0.85, "CO-11": 0.18, "CO-13": 0.95, "CO-16": 0.12}
    melhoria = {"CO-01": 0.35, "CO-05": 0.40, "CO-11": 0.6, "CO-16": 0.8}
    obs = {"CO-01": "ISBM-005 aquecida em vazio na pausa", "CO-05": "IM-004 com resistências a 100% na paragem por falta de molde", "CO-07": "Manta do canhão da IM-006 rasgada",
           "CO-09": "Pressão a 7,4 bar (setpoint ainda não alterado — PA-E-02)", "CO-11": "Ramal da decoração aberto", "CO-13": "Setpoint 7 °C (aguarda validação DOE — PA-E-06)",
           "CO-16": "Luzes da expedição ligadas sem atividade"}
    rows = []
    d0 = dt.date(2026, 7, 3)
    for w in range(26):
        data = d0 + dt.timedelta(days=7 * w)
        for p in PONTOS_RONDA:
            pnc = prob_nc[p] * (1 - melhoria.get(p, 0) * (min(w, 12) / 12))
            if p in ("CO-01", "CO-05") and data >= dt.date(2026, 10, 5):
                pnc = 0.06        # standby obrigatório (PA-E-03) a partir de 05/10/2026
            if p == "CO-09" and data >= dt.date(2026, 11, 16):
                pnc = 0.04        # pressão de 6,8 bar (PA-E-02) desde 16/11/2026
            if p == "CO-13" and data >= dt.date(2026, 12, 1):
                pnc = 0.0         # setpoint 10 °C validado por DOE (PA-E-06)
            nc = rng.random() < pnc
            rows.append(dict(ID_Ronda=f"RE-26-{w + 1:02d}", Data=data, Turno=int(rng.integers(1, 4)), ID_Criterio=p, Resultado="Não conforme" if nc else "Conforme",
                             Observacao=obs[p] if nc else None, Acao_Imediata=("Corrigido no momento" if p not in ("CO-09", "CO-13") else "Aguarda plano de ação") if nc else None,
                             Verificador=TUTL if w % 2 else GE))
    rcols = [col("ID_Ronda", 9, desc="Ronda."), col("Data", 11, "date", desc="Data."), col("Turno", 6, "int", desc="Turno."), col("ID_Criterio", 8, desc="Critério.", key="FK → tbl_criterios_operacionais"),
             col("Resultado", 12, dv="ResultadoRonda", desc="Conforme / não conforme."), col("Observacao", 44, desc="Observação.", req=False), col("Acao_Imediata", 22, desc="Ação imediata.", req=False),
             col("Verificador", 22, dv="Funcao", desc="Quem verificou."), col("Chave", 16, f='=IF(@ID_Ronda@="","",@ID_Ronda@&"|"&@ID_Criterio@)', desc="Chave única (ronda|critério).", key="PK"),
             col("NC_Flag", 6, "int", f='=IF(@ID_Ronda@="","",IF(@Resultado@="Não conforme",1,0))', desc="1 = não conforme (para gráficos e ML).")]
    b.table("Rondas_Energia", "tbl_rondas_energia", rcols, rows, "Rondas de energia semanais (8.1 c–d) jul–dez/2026 — simuladas.",
            title="RONDAS DE ENERGIA SEMANAIS (8.1) — SIMULADAS", subtitle="7 pontos por ronda · CO-01/05 melhoram com a consciencialização (jul) e o standby obrigatório (05/10) · CO-09 conforme desde 16/11 · CO-13 desde 01/12",
            cf=[("Resultado", {"Não conforme": "red", "Conforme": "green"})], row_height=16)
    ws = b.sheet("Alteracoes_Nao_Intencionais", "Revisão das consequências de alterações não intencionais e controlo das planeadas (8.1, último parágrafo).")
    title(ws, "ALTERAÇÕES PLANEADAS E NÃO INTENCIONAIS COM EFEITO NA ENERGIA (8.1)")
    header_row(ws, 3, ["ID", "Data", "Tipo", "Descrição", "Consequência no desempenho energético", "Ação para mitigar", "Registo"], widths=[10, 11, 14, 44, 40, 40, 20])
    ALT = [("ANI-01", "2026-07-01", "Planeada", "Entrada em serviço de IM-007/008 e ISBM-009/010 (ALT-2026-03)", "Potência tomada +25%; LBE-01 ajustada (ALE-01)", "Ajuste não rotineiro; alarme de potência (RE-03)", "RG-SGA-18; RG-SGE-05"),
           ("ANI-02", "2026-08-10", "Não intencional", "Setpoint do chiller baixado para 6 °C por um operador para resolver empenos num molde", "≈ +3% no consumo do frio durante 9 dias", "Reposto 7 °C; causa tratada com a qualidade; CO-13 reforçado", "RG-SGE-14 NCE-26-03"),
           ("ANI-03", "2026-02-01", "Planeada", "Compressores VSD (ALT-2026-01)", "Potência específica −14,8% (RG-SGE-11)", "M&V opção B", "RG-SGE-11")]
    for i, a_ in enumerate(ALT):
        for j, v in enumerate(a_):
            cell(ws, 4 + i, 1 + j, dt.date.fromisoformat(v) if j == 1 else v, fmt="yyyy-mm-dd" if j == 1 else None)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
