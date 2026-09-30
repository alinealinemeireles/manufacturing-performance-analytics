"""Reconstrói todos os registos do SGA, recalcula-os no Excel e gera o índice com a verificação de integridade.
Uso: python build_all.py"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "Registos_SGA_Plasticom"))
sys.path.insert(0, HERE)

JOBS = [
    ("build_01_contexto", "SGA-01_Contexto_SWOT_PESTEL.xlsx"),
    ("build_02_riscos", "SGA-02_Gestao_Riscos_Oportunidades.xlsx"),
    ("build_03_aspetos", "SGA-03_Aspetos_Impactes_Ambientais.xlsx"),
    ("build_04_legal", "SGA-04_Requisitos_Legais_Conformidade.xlsx"),
    ("build_05_objetivos", "SGA-05_Objetivos_Metas_KPI.xlsx"),
    ("build_06_pam", "SGA-06_Plano_Acoes_Melhoria_PAM.xlsx"),
    ("build_07_nc", "SGA-07_Nao_Conformidades_RNC.xlsx"),
    ("build_08_competencias", "SGA-08_Competencias_Consciencializacao.xlsx"),
    ("build_09_comunicacao", "SGA-09_Comunicacao_Controlo_Documental.xlsx"),
    ("build_10_rondas", "SGA-10_Controlo_Operacional_Rondas.xlsx"),
    ("build_11_fornecedores", "SGA-11_Fornecedores_Ciclo_Vida.xlsx"),
    ("build_12_emergencias", "SGA-12_Emergencias_Ambientais.xlsx"),
    ("build_13_monitorizacao", "SGA-13_Monitorizacao_Medicao_Desempenho.xlsx"),
    ("build_14_auditoria", "SGA-14_Auditoria_Interna.xlsx"),
    ("build_15_revisao", "SGA-15_Revisao_pela_Gestao.xlsx"),
    ("build_16_melhoria_emas", "SGA-16_Melhoria_Kaizen_EMAS.xlsx"),
    ("build_17_dupla_materialidade", "SGA-17_Dupla_Materialidade.xlsx"),
    ("build_18_alteracoes", "SGA-18_Planeamento_Alteracoes.xlsx"),
    ("build_19_esg_ambiental", "SGA-19_ESG_Ambiental_GEE.xlsx"),
    ("build_20_reciclabilidade", "SGA-20_Reciclabilidade_Embalagens.xlsx"),
    ("build_21_quimicos", "SGA-21_Gestao_Produtos_Quimicos.xlsx"),
]

# Registos mantidos manualmente: não são regerados (só recalculados e verificados).
# SGA-02 passou a ser o registo corporativo de riscos e oportunidades, editado à mão (24/09/2026);
# build_02_riscos.py fica como referência da matriz do SGA, mas não sobrescreve o ficheiro.
MANUAL = {"SGA-02_Gestao_Riscos_Oportunidades.xlsx"}

if __name__ == "__main__":
    import recalc
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for mod, fn in JOBS:
        p = os.path.join(OUT, fn)
        if fn in MANUAL:
            print("mantido (manual)", fn, flush=True)
        else:
            importlib.import_module(mod).build(p)
            print("gerado", fn, flush=True)
        paths.append(p)
    recalc.recalc(paths)
    for (mod, fn), p in zip(JOBS, paths):  # pós-processamento no Excel (tabelas dinâmicas, segmentações, rótulos)
        m = importlib.import_module(mod)
        if fn not in MANUAL and hasattr(m, "postprocess"):
            m.postprocess(p)
    total = 0
    for p in paths:
        n, e = recalc.check(p)
        total += len(e)
        print(f"{os.path.basename(p)}: {n} fórmulas, {len(e)} erros", flush=True)
        for x in e[:10]:
            print("   ", x)
    print("documentos:", len(importlib.import_module("build_docs").build()), flush=True)
    idx = os.path.join(OUT, "SGA-00_Indice_Modelo_Dados.xlsx")
    importlib.import_module("build_00_indice").build(idx, OUT)
    recalc.recalc([idx])
    n, e = recalc.check(idx)
    print(f"SGA-00_Indice_Modelo_Dados.xlsx: {n} fórmulas, {len(e)} erros")
    print("TOTAL DE ERROS:", total + len(e))
