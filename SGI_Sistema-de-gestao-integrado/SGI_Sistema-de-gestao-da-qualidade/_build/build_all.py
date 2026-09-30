"""Reconstrói os registos do SGQ, recalcula-os no Excel e gera o índice com a verificação de integridade.
Uso: python build_all.py            (todos)
     python build_all.py 05 09      (só os registos indicados, sem índice)"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "Registos_SGQ_Plasticom"))
sys.path.insert(0, HERE)
import sgqlib  # noqa: E402,F401  (acrescenta o _build do SGA ao sys.path)
import recalc  # noqa: E402  (recalc.py do SGA: Excel via COM)

JOBS = [
    ("build_01_contexto", "SGQ-01_Contexto_SWOT_PESTEL.xlsx"),
    ("build_02_processos", "SGQ-02_Processos_Infraestrutura_Ambiente.xlsx"),
    ("build_03_lideranca", "SGQ-03_Lideranca_Politica_Cultura.xlsx"),
    ("build_04_riscos", "SGQ-04_Gestao_Riscos_Oportunidades.xlsx"),
    ("build_05_objetivos", "SGQ-05_Objetivos_Metas_KPI.xlsx"),
    ("build_06_alteracoes", "SGQ-06_Planeamento_Alteracoes.xlsx"),
    ("build_07_competencias", "SGQ-07_Competencias_Consciencializacao.xlsx"),
    ("build_08_documentacao", "SGQ-08_Comunicacao_Controlo_Documental.xlsx"),
    ("build_09_metrologia", "SGQ-09_Metrologia_Calibracao_MSA.xlsx"),
    ("build_10_clientes", "SGQ-10_Requisitos_Cliente_Encomendas.xlsx"),
    ("build_11_design", "SGQ-11_Design_Desenvolvimento.xlsx"),
    ("build_12_fornecedores", "SGQ-12_Fornecedores_Avaliacao.xlsx"),
    ("build_13_producao", "SGQ-13_Producao_Rastreabilidade_Libertacao.xlsx"),
    ("build_14_snc", "SGQ-14_Saidas_Nao_Conformes.xlsx"),
    ("build_15_satisfacao", "SGQ-15_Reclamacoes_Satisfacao_Cliente.xlsx"),
    ("build_16_auditoria", "SGQ-16_Auditoria_Interna.xlsx"),
    ("build_17_revisao", "SGQ-17_Revisao_pela_Gestao.xlsx"),
    ("build_18_capa", "SGQ-18_Nao_Conformidades_CAPA.xlsx"),
    ("build_19_melhoria", "SGQ-19_Melhoria_Continua_Custo_Qualidade.xlsx"),
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
        idx = os.path.join(OUT, "SGQ-00_Indice_Modelo_Dados.xlsx")
        importlib.import_module("build_00_indice").build(idx, OUT)
        recalc.recalc([idx])
        n, e = recalc.check(idx)
        total += len(e)
        print(f"SGQ-00_Indice_Modelo_Dados.xlsx: {n} fórmulas, {len(e)} erros")
    print("TOTAL DE ERROS:", total)
