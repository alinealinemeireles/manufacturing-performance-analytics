"""Reconstrói os registos do SGE, recalcula-os no Excel e gera o índice com a verificação de integridade.
Uso: python build_all.py            (todos)
     python build_all.py 05 09      (só os registos indicados, sem índice)"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "Registos_SGE_Plasticom"))
sys.path.insert(0, HERE)
import sgelib  # noqa: E402,F401  (acrescenta os _build do SGQ e do SGA ao sys.path)
import recalc  # noqa: E402  (recalc.py do SGA: Excel via COM)

JOBS = [
    ("build_01_contexto", "SGE-01_Contexto_Ambito_Fronteiras.xlsx"),
    ("build_02_lideranca", "SGE-02_Lideranca_Politica_Equipa.xlsx"),
    ("build_03_riscos", "SGE-03_Riscos_Oportunidades.xlsx"),
    ("build_04_revisao", "SGE-04_Revisao_Energetica_USE.xlsx"),
    ("build_05_ide_lbe", "SGE-05_IDE_LBE_Objetivos_Metas.xlsx"),
    ("build_06_dados", "SGE-06_Recolha_Dados_Medicao.xlsx"),
    ("build_07_competencias", "SGE-07_Competencias_Comunicacao.xlsx"),
    ("build_08_operacional", "SGE-08_Controlo_Operacional_USE.xlsx"),
    ("build_09_aquisicoes", "SGE-09_Projeto_Aquisicoes_Compra_Energia.xlsx"),
    ("build_10_legal", "SGE-10_Conformidade_Legal_SGCIE.xlsx"),
    ("build_11_desvios_mv", "SGE-11_Desvios_MV_Poupancas.xlsx"),
    ("build_12_auditoria", "SGE-12_Auditoria_Interna.xlsx"),
    ("build_13_revisao", "SGE-13_Revisao_pela_Gestao.xlsx"),
    ("build_14_melhoria", "SGE-14_NC_Acao_Corretiva_Melhoria.xlsx"),
]

if __name__ == "__main__":
    only = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    jobs = [j for j in JOBS if not only or j[1][4:6] in only]
    paths = []
    for mod, fn in jobs:
        p = os.path.join(OUT, fn)
        importlib.import_module(mod).build(p)
        print("gerado", fn, flush=True)
        paths.append(p)
    recalc.recalc(paths)
    total = 0
    for p in paths:
        n, e = recalc.check(p)
        total += len(e)
        print(f"{os.path.basename(p)}: {n} fórmulas, {len(e)} erros", flush=True)
        for x in e[:10]:
            print("   ", x)
    if not only:
        idx = os.path.join(OUT, "SGE-00_Indice_Modelo_Dados.xlsx")
        importlib.import_module("build_00_indice").build(idx, OUT)
        recalc.recalc([idx])
        n, e = recalc.check(idx)
        total += len(e)
        print(f"SGE-00_Indice_Modelo_Dados.xlsx: {n} fórmulas, {len(e)} erros")
    print("TOTAL DE ERROS:", total)
