"""RG-SGA-20 — Reciclabilidade e conformidade de embalagens (RecyClass / PPWR / legislação de produto).

Uma linha por SKU (frascos e potes do dataset) com os campos pedidos pela ferramenta online RecyClass
(categoria, corpo, cor, densidade, barreira, tampa, vedante, rótulo, adesivo, cobertura, decoração) e o cálculo
feito por fórmulas: classe de cada característica pelas regras de design para reciclagem (tbl_regras_dfr),
classe RecyClass (pior característica), taxa de reciclabilidade em massa, grau PPWR indicativo (art. 6.º),
conteúdo reciclado face às metas do art. 7.º, requisitos legais por produto, vendas por país e evidências.

A lógica em Python (avaliar()) replica as fórmulas para que outros registos (RG-SGA-05, 17, 19) usem os mesmos
resultados; recalc + check garantem que o Excel dá o mesmo resultado.
"""
import datetime as dt
import os
import re
import pandas as pd
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from sgalib import *
from dims import *
import envdata

D = dt.date.fromisoformat
SIL = os.path.join(envdata.ROOT, "datasets", "silver")
DIMD = os.path.join(envdata.ROOT, "datasets", "dim")
P12 = ("2026-01-01", "2026-12-31")   # vendas do ano civil de 2026
DAV = dt.date(2026, 9, 22)          # data da autoavaliação
CLS = ["A", "B", "C", "D", "E", "F"]
PE, PP, PET = "PE rígido", "PP rígido", "PET frascos e garrafas"
SF_PETG, SF_PVC = "Sem fluxo (PETG)", "Sem fluxo (PVC)"
PAIS = {"Portugal": ("PT", "Portugal"), "Spain": ("ES", "Espanha"), "France": ("FR", "França"), "Italy": ("IT", "Itália"),
        "Germany": ("DE", "Alemanha"), "Poland": ("PL", "Polónia")}
F_RD, F_QUA, F_SGA, F_CMP = "Responsável de R&D", "Gerente da Qualidade", "Gestor do SGA / EHS (Responsável Ambiental)", "Responsável de Compras"
F_DG, F_FIN, F_LOG = "Diretor Geral (Gestão de Topo)", "Diretor Financeiro", "Responsável de Armazém e Logística"

# ------------------------------------------------------------------ materiais
# Material, polímero base, fluxo de reciclagem, densidade (g/cm³), grau, % PCR, código de identificação, fornecedor
MATERIAIS = [
    ("HDPE", "PE", PE, 0.955, "Virgem", 0.0, ">PE-HD< (2)", "SUP-001"),
    ("HDPE-PCR", "PE", PE, 0.960, "Reciclado pós-consumo", 0.30, ">PE-HD< (2)", "SUP-004"),
    ("MDPE", "PE", PE, 0.935, "Virgem", 0.0, ">PE-MD< (4)", "SUP-001"),
    ("LDPE", "PE", PE, 0.920, "Virgem", 0.0, ">PE-LD< (4)", "SUP-007"),
    ("HDPE-FG", "PE", PE, 0.955, "Grau alimentar (FCM)", 0.0, ">PE-HD< (2)", "SUP-010"),
    ("PP", "PP", PP, 0.905, "Virgem", 0.0, ">PP< (5)", "SUP-002"),
    ("PP-PCR", "PP", PP, 0.910, "Reciclado pós-consumo", 0.30, ">PP< (5)", "SUP-002"),
    ("PP-FG", "PP", PP, 0.905, "Grau alimentar (FCM)", 0.0, ">PP< (5)", "SUP-010"),
    ("PP-PG", "PP", PP, 0.905, "Grau farmacêutico", 0.0, ">PP< (5)", "SUP-009"),
    ("PET", "PET", PET, 1.380, "Virgem", 0.0, ">PET< (1)", "SUP-003"),
    ("rPET", "PET", PET, 1.380, "Reciclado pós-consumo", 0.50, ">PET< (1)", "SUP-004"),
    ("PET-PG", "PET", PET, 1.380, "Grau farmacêutico", 0.0, ">PET< (1)", "SUP-009"),
    ("PETG", "PETG", SF_PETG, 1.270, "Virgem", 0.0, ">PETG< (7)", "SUP-003"),
    ("PVC", "PVC", SF_PVC, 1.350, "Virgem", 0.0, ">PVC< (3)", "SUP-005"),
]
MAT = {m[0]: m for m in MATERIAIS}

COR = {"Natural (Uncolored)": "Natural / incolor", "Opaque White": "Branco (TiO2)", "Pharma White": "Branco (TiO2)",
       "Cardinal Red": "Colorido (claro ou transparente)", "Cobalt Blue": "Colorido (claro ou transparente)",
       "Emerald Green": "Colorido (claro ou transparente)", "Translucent Amber": "Colorido (claro ou transparente)",
       "Graphite Gray": "Colorido escuro / opaco", "Matte Black": "Preto (negro de carbono)"}
CORES = ["Natural / incolor", "Branco (TiO2)", "Colorido (claro ou transparente)", "Colorido escuro / opaco",
         "Preto (negro de carbono)", "Preto detetável por NIR"]

# ------------------------------------------------------------------ regras de design para reciclagem
# (fluxo, característica, valor, classe, fração reciclável, fundamentação, recomendação)
R_ = []


def rule(fl, car, val, c, fr, fund, rec="Sem ação — manter."):
    R_.append((fl, car, val, c, fr, fund, rec))


for fl in (PE, PP, PET):
    rule(fl, "Fluxo de reciclagem", fl, "A", 1, "Fluxo de triagem e reciclagem mecânica estabelecido na Europa.")
rule(SF_PETG, "Fluxo de reciclagem", SF_PETG, "F", 0, "PETG não tem fluxo de reciclagem dedicado; é triado com o PET e perturba o processo (amolece a temperaturas de secagem do PET).",
     "Mudar o corpo para PET (ou PP/PE) — PETG não passa a grau C em 2030.")
rule(SF_PVC, "Fluxo de reciclagem", SF_PVC, "F", 0, "Sem fluxo de reciclagem de embalagens domésticas de PVC; contamina o PET (HCl na extrusão).",
     "Eliminar o PVC do portfólio (substituir por PET ou PP).")
for fl in (PE, PP):
    n = "PE" if fl == PE else "PP"
    rule(fl, "Cor do corpo", "Natural / incolor", "A", 1, "Reciclado incolor de maior valor.")
    rule(fl, "Cor do corpo", "Branco (TiO2)", "A", 1, "Cores claras/brancas totalmente compatíveis.")
    rule(fl, "Cor do corpo", "Colorido (claro ou transparente)", "B", 1, f"Reciclado de {n} colorido — valor e aplicações mais limitados.", "Preferir natural, branco ou cores claras.")
    rule(fl, "Cor do corpo", "Colorido escuro / opaco", "B", 1, f"Reciclado de {n} escuro — só aplicações escuras.", "Preferir cores claras.")
    rule(fl, "Cor do corpo", "Preto (negro de carbono)", "F", 0, "Negro de carbono absorve o infravermelho próximo: a embalagem não é identificada na triagem NIR e vai para refugo.",
         "Substituir o masterbatch por preto detetável por NIR (pigmentos sem negro de carbono).")
    rule(fl, "Cor do corpo", "Preto detetável por NIR", "B", 1, "Detetável na triagem; reciclado escuro.", "Manter pigmento detetável por NIR e validar com teste de triagem.")
    rule(fl, "Densidade do corpo", "< 1,0 g/cm³", "A", 1, "Flutua em água: separado corretamente das impurezas no tanque de afunda-flutua.")
    rule(fl, "Densidade do corpo", "≥ 1,0 g/cm³", "D", 1, "Afunda com as impurezas (cargas/minerais) e perde-se no afunda-flutua.", "Reduzir cargas minerais / masterbatch para densidade < 1,0 g/cm³.")
    rule(fl, "Barreira / revestimento", "Nenhuma", "A", 1, "Estrutura monocamada.")
    rule(fl, "Barreira / revestimento", "EVOH ≤ 6% com compatibilizante", "B", 1, "Tolerado em baixa percentagem.", "Limitar a barreira ao mínimo necessário.")
    rule(fl, "Barreira / revestimento", "Camada de outro polímero (PA, PET)", "D", 1, "Multimaterial não separável — degrada o reciclado.", "Substituir por barreira compatível ou monomaterial.")
    rule(fl, "Material da tampa", "Sem tampa", "A", 1, "Sem componente.")
    rule(fl, "Material da tampa", "PE", "A", 1, "Poliolefina: reciclada com o corpo ou no fluxo de poliolefinas.")
    rule(fl, "Material da tampa", "PP", "A", 1, "Poliolefina: flutua e é reciclada no fluxo de poliolefinas.")
    rule(fl, "Material da tampa", "PETG", "B", 0, "Afunda e é separada no afunda-flutua; massa perdida.", "Usar tampa de PP ou PE.")
    rule(fl, "Material da tampa", "PET", "B", 0, "Afunda e é separada; massa perdida.", "Usar tampa de PP ou PE.")
    rule(fl, "Vedante / liner", "Sem vedante", "A", 1, "Sem componente.")
    rule(fl, "Vedante / liner", "Vedante PE/EVA", "A", 1, "Poliolefina compatível.")
    rule(fl, "Vedante / liner", "Válvula de silicone", "C", 1, "Silicone contamina o reciclado de poliolefinas.", "Usar válvula de poliolefina (TPE-PO).")
    rule(fl, "Tipo de rótulo", "Sem rótulo", "A", 1, "Sem componente.")
    rule(fl, "Tipo de rótulo", "Autoadesivo PE/PP", "A", 1, "Mesmo fluxo (poliolefinas).")
    rule(fl, "Tipo de rótulo", "In-mould PE/PP", "A", 1, "Mesmo polímero, monomaterial.")
    rule(fl, "Tipo de rótulo", "Autoadesivo PET", "B", 0, "Afunda e é separado; massa perdida.", "Usar rótulo de PE/PP.")
    rule(fl, "Tipo de rótulo", "Autoadesivo papel", "C", 0, "Fibras de papel passam para o reciclado de poliolefina (defeitos e odor).", "Usar rótulo de PE/PP.")
    rule(fl, "Tipo de rótulo", "Manga termorretrátil PETG", "C", 0, "Pode impedir a identificação NIR do corpo; PETG separado.", "Manga de PE/PP com picotado ou rótulo parcial.")
    for adh in ("Sem adesivo", "Acrílico permanente", "Lavável a 80 °C (alcalino)", "Hot-melt"):
        rule(fl, "Adesivo do rótulo", adh, "A", 1, "Na reciclagem de poliolefinas o rótulo compatível é reciclado com o corpo; adesivo em quantidade vestigial.")
    for cov in ("≤ 70% da superfície", "> 70% da superfície"):
        rule(fl, "Cobertura do rótulo", cov, "A", 1, "Sem impacto relevante na triagem de poliolefinas com rótulo compatível.")
    rule(fl, "Decoração direta", "Nenhuma", "A", 1, "Sem decoração.")
    rule(fl, "Decoração direta", "Impressão de lote/data", "A", 1, "Codificação mínima tolerada.")
    rule(fl, "Decoração direta", "Serigrafia 1–2 cores", "B", 0, "Tintas diretas colorem o reciclado (baixa cobertura).", "Tintas sem metais pesados e que não sangrem; reduzir área impressa.")
    rule(fl, "Decoração direta", "Serigrafia ≥ 3 cores", "C", 0, "Cobertura de tinta elevada colore e contamina o reciclado.", "Reduzir cores/área ou passar a rótulo de PE/PP.")
    rule(fl, "Decoração direta", "Hot foil metalizado", "C", 0, "Camada metalizada e verniz não removíveis contaminam o reciclado.", "Reduzir a área de hot foil ou usar rótulo metalizado destacável.")
# PET
rule(PET, "Cor do corpo", "Natural / incolor", "A", 1, "PET transparente incolor — reciclado de maior valor (garrafa a garrafa).")
rule(PET, "Cor do corpo", "Colorido (claro ou transparente)", "B", 1, "Vai para o fluxo de PET colorido, de menor valor.", "Preferir PET incolor ou azul-claro.")
rule(PET, "Cor do corpo", "Colorido escuro / opaco", "D", 1, "PET opaco perturba o fluxo de PET transparente.", "Usar PET transparente (cor por rótulo).")
rule(PET, "Cor do corpo", "Branco (TiO2)", "D", 1, "PET branco opaco (TiO2) — não compatível com o reciclado transparente.", "Usar PET transparente com rótulo branco ou mudar para PP/HDPE branco.")
rule(PET, "Cor do corpo", "Preto (negro de carbono)", "F", 0, "Não identificado por NIR.", "Preto detetável por NIR ou PET transparente.")
rule(PET, "Cor do corpo", "Preto detetável por NIR", "D", 1, "PET opaco escuro.", "Usar PET transparente.")
rule(PET, "Densidade do corpo", "≥ 1,0 g/cm³", "A", 1, "O PET afunda e é separado das poliolefinas (normal).")
rule(PET, "Densidade do corpo", "< 1,0 g/cm³", "D", 1, "PET expandido/espumado flutua e perde-se.", "Evitar PET expandido.")
rule(PET, "Barreira / revestimento", "Nenhuma", "A", 1, "Monocamada.")
rule(PET, "Barreira / revestimento", "Revestimento SiOx (plasma)", "A", 1, "Camada vestigial compatível.")
rule(PET, "Barreira / revestimento", "Camada de outro polímero (PA, PET)", "C", 1, "Multicamada com PA amarelece o reciclado.", "Usar barreira compatível.")
rule(PET, "Material da tampa", "Sem tampa", "A", 1, "Sem componente.")
rule(PET, "Material da tampa", "PE", "A", 1, "Flutua e é separada; reciclada no fluxo de poliolefinas.")
rule(PET, "Material da tampa", "PP", "A", 1, "Flutua e é separada; reciclada no fluxo de poliolefinas.")
rule(PET, "Material da tampa", "PETG", "D", 0, "Afunda com os flocos de PET e contamina-os (aglomera na secagem).", "Usar tampa de PP ou PE.")
rule(PET, "Material da tampa", "PET", "B", 1, "Mesmo polímero mas grau diferente.", "Preferir tampa de PP/PE.")
rule(PET, "Vedante / liner", "Sem vedante", "A", 1, "Sem componente.")
rule(PET, "Vedante / liner", "Vedante PE/EVA", "A", 1, "Flutua com a tampa.")
rule(PET, "Vedante / liner", "Válvula de silicone", "D", 1, "Silicone (densidade > 1) afunda com os flocos de PET.", "Válvula de poliolefina.")
rule(PET, "Tipo de rótulo", "Sem rótulo", "A", 1, "Sem componente.")
rule(PET, "Tipo de rótulo", "Autoadesivo PE/PP", "A", 1, "Flutua e é separado; reciclado no fluxo de poliolefinas.")
rule(PET, "Tipo de rótulo", "In-mould PE/PP", "B", 1, "Não removível do corpo (raro em PET).", "Usar rótulo autoadesivo de PE/PP.")
rule(PET, "Tipo de rótulo", "Autoadesivo PET", "C", 0, "Afunda com os flocos; adesivo e tinta contaminam.", "Usar rótulo de PE/PP.")
rule(PET, "Tipo de rótulo", "Autoadesivo papel", "C", 0, "Fibras e colas contaminam a água de lavagem e os flocos.", "Usar rótulo de PE/PP com adesivo lavável.")
rule(PET, "Tipo de rótulo", "Manga termorretrátil PETG", "D", 0, "PETG afunda com o PET e cobre o corpo (triagem NIR errada).", "Manga de PE/PP flutuante com picotado.")
rule(PET, "Adesivo do rótulo", "Sem adesivo", "A", 1, "Sem adesivo.")
rule(PET, "Adesivo do rótulo", "Lavável a 80 °C (alcalino)", "A", 1, "Removido na lavagem cáustica a quente.")
rule(PET, "Adesivo do rótulo", "Acrílico permanente", "C", 1, "Adesivo não lavável fica nos flocos (amarelecimento, pontos negros).", "Exigir ao cliente adesivo lavável a 80 °C (teste de lavabilidade).")
rule(PET, "Adesivo do rótulo", "Hot-melt", "D", 1, "Resíduos de hot-melt contaminam o reciclado.", "Adesivo lavável a 80 °C.")
rule(PET, "Cobertura do rótulo", "≤ 70% da superfície", "A", 1, "Corpo visível para a triagem NIR.")
rule(PET, "Cobertura do rótulo", "> 70% da superfície", "C", 1, "Rótulo pode mascarar o corpo na triagem NIR.", "Reduzir a cobertura para ≤ 70%.")
rule(PET, "Decoração direta", "Nenhuma", "A", 1, "Sem decoração.")
rule(PET, "Decoração direta", "Impressão de lote/data", "A", 1, "Codificação mínima tolerada.")
rule(PET, "Decoração direta", "Serigrafia 1–2 cores", "D", 0, "Tinta direta não removida na lavagem contamina os flocos de PET.", "Rótulo de PE/PP ou tinta destintável em lavagem alcalina (validar).")
rule(PET, "Decoração direta", "Serigrafia ≥ 3 cores", "D", 0, "Tinta direta não removida na lavagem contamina os flocos de PET.", "Rótulo de PE/PP ou tinta destintável em lavagem alcalina (validar).")
rule(PET, "Decoração direta", "Hot foil metalizado", "D", 0, "Metalização e verniz não removíveis contaminam os flocos.", "Rótulo metalizado de PE/PP destacável.")
RULES = {f"{r[0]}|{r[1]}|{r[2]}": r for r in R_}
LISTA = {car: sorted({r[2] for r in R_ if r[1] == car}) for car in {r[1] for r in R_}}
FEAT = [  # coluna Classe_*, característica, expressão Excel do valor, chave python
    ("Classe_Fluxo", "Fluxo de reciclagem", "@Fluxo_Reciclagem@", "fluxo"),
    ("Classe_Cor", "Cor do corpo", "@Cor_Corpo@", "cor"),
    ("Classe_Densidade", "Densidade do corpo", 'IF(@Densidade_Corpo_g_cm3@<1,"< 1,0 g/cm³","≥ 1,0 g/cm³")', "dens"),
    ("Classe_Barreira", "Barreira / revestimento", "@Barreira_Revestimento@", "barr"),
    ("Classe_Tampa", "Material da tampa", "@Polimero_Tampa@", "tampa"),
    ("Classe_Vedante", "Vedante / liner", "@Vedante_Tampa@", "ved"),
    ("Classe_Rotulo", "Tipo de rótulo", "@Rotulo_Tipo@", "rot"),
    ("Classe_Adesivo", "Adesivo do rótulo", "@Rotulo_Adesivo@", "ades"),
    ("Classe_Cobertura", "Cobertura do rótulo", 'IF(@Rotulo_Cobertura_Pct@>0.7,"> 70% da superfície","≤ 70% da superfície")', "cob"),
    ("Classe_Decoracao", "Decoração direta", "@Decoracao_Valor@", "deco"),
]

# ------------------------------------------------------------------ parâmetros e metas do art. 7.º
PARAM = [
    ("P-01", "Imposto espanhol sobre embalagens de plástico não reutilizáveis (Lei 7/2022)", 0.45, "€/kg de plástico não reciclado", "BOE — Ley 7/2022, art. 81.º (confirmar taxa em vigor)"),
    ("P-02", "Gramagem de rótulo de filme PE/PP/PET", 55, "g/m²", "Estimativa técnica (filme 60 µm + adesivo)"),
    ("P-03", "Gramagem de rótulo de papel", 75, "g/m²", "Estimativa técnica"),
    ("P-04", "Tinta de serigrafia depositada por cor", 0.08, "g/un", "RG-SGA-13 (0,24 kg/1.000 peças para ≈ 3 cores)"),
    ("P-05", "Metalização de hot foil transferida para a peça", 0.03, "g/un", "Estimativa (foil consumido 1,9 kg/1.000; filme de suporte vai para resíduo)"),
    ("P-06", "Limiar do grau PPWR A (taxa de reciclabilidade em massa)", 0.95, "fração", "Reg. (UE) 2025/40, anexo II, quadro 3"),
    ("P-07", "Limiar do grau PPWR B", 0.80, "fração", "Reg. (UE) 2025/40, anexo II, quadro 3"),
    ("P-08", "Limiar do grau PPWR C", 0.70, "fração", "Reg. (UE) 2025/40, anexo II, quadro 3"),
    ("P-09", "Cartão por caixa de expedição", 0.45, "kg/caixa", "Especificação logística Plasticom"),
    ("P-10", "Frascos por caixa", 250, "un/caixa", "Especificação logística (média)"),
    ("P-11", "Tampas por caixa", 1000, "un/caixa", "Especificação logística (média)"),
    ("P-12", "Caixas por palete", 40, "caixas/palete", "Especificação logística"),
    ("P-13", "Massa de uma palete de madeira (sem retorno)", 22, "kg/palete", "Especificação logística"),
    ("P-14", "Filme estirável por palete", 0.30, "kg/palete", "Especificação logística"),
    ("P-15", "Prestação financeira — cartão (embalagens não urbanas, PT)", 0.03, "€/kg", "Valor INDICATIVO — substituir pela tabela da entidade gestora em vigor"),
    ("P-16", "Prestação financeira — plástico (embalagens não urbanas, PT)", 0.10, "€/kg", "Valor INDICATIVO — substituir pela tabela da entidade gestora em vigor"),
    ("P-17", "Prestação financeira — madeira (embalagens não urbanas, PT)", 0.01, "€/kg", "Valor INDICATIVO — substituir pela tabela da entidade gestora em vigor"),
]
PV = {p[0]: p[2] for p in PARAM}
METAS7 = [
    ("Sensível ao contacto — PET", 0.30, 0.50, "Art. 7.º, n.º 1, al. a) e n.º 2, al. a)", "Inclui embalagens alimentares de PET (exceto garrafas de bebidas)."),
    ("Sensível ao contacto — outros plásticos", 0.10, 0.25, "Art. 7.º, n.º 1, al. b) e n.º 2, al. b)", "Embalagens alimentares de PE/PP: o reciclado tem de cumprir o Reg. (UE) 2022/1616."),
    ("Garrafas de bebidas de utilização única", 0.30, 0.65, "Art. 7.º, n.º 1, al. c) e n.º 2, al. c)", "Sem SKUs atuais (confirmar uso de FA-030/031)."),
    ("Outras embalagens de plástico", 0.35, 0.65, "Art. 7.º, n.º 1, al. d) e n.º 2, al. d)", "Cosmética e higiene: pressupõe-se que NÃO é 'sensível ao contacto' (confirmar a definição do art. 3.º) — cenário conservador."),
    ("Isenta — medicamentos (art. 7.º)", None, None, "Art. 7.º (isenções)", "Embalagem sensível ao contacto de medicamentos para uso humano e veterinário."),
]
M7 = {m[0]: m for m in METAS7}


def _p(k):
    return f'INDEX(tbl_param_emb[Valor],MATCH("{k}",tbl_param_emb[ID_Parametro],0))'


# ------------------------------------------------------------------ dados de produto
def _dados():
    bt = pd.read_csv(os.path.join(SIL, "dim_bottle.csv"))
    cp = pd.read_csv(os.path.join(SIL, "dim_cap.csv"))
    ink = pd.read_csv(os.path.join(SIL, "dim_ink.csv"))
    pr = pd.read_csv(os.path.join(SIL, "fact_production_processed.csv"), usecols=["Date", "Process", "ProductId", "ProducedQty"], low_memory=False)
    sa = pd.read_csv(os.path.join(SIL, "fact_sales_processed.csv"), low_memory=False)
    cu = pd.read_csv(os.path.join(DIMD, "dim_customer.csv"))
    hfs = set(pr[pr.Process == "Hot Foil Stamping"].ProductId)
    ser = set(pr[pr.Process == "Screen Printing"].ProductId)
    cores = ink[~ink.PrintToolId.str.startswith("RS-")].set_index("ProductId").ColorCount.to_dict()
    sa = sa.merge(cu[["CustomerId", "Country", "Segment"]], on="CustomerId", how="left")
    s12 = sa[(sa.Date >= P12[0]) & (sa.Date <= P12[1])]
    return bt, cp, hfs, ser, cores, s12, sa


def _segmento(pid, mat):
    pre = pid.split("-")[0]
    if pre == "FA":
        return "Alimentar"
    if pre == "FP" or (pre == "PT" and mat == "PP-PG"):
        return "Farmacêutico"
    return "Cosmética e higiene pessoal"


def _familia(tipo, mat):
    if tipo == "Pote":
        return "FAM-15"
    if tipo == "Tampa":
        return {"PP": "FAM-16", "PP-PCR": "FAM-17", "HDPE": "FAM-18", "PETG": "FAM-19", "PP-PG": "FAM-20", "HDPE-FG": "FAM-21", "PP-FG": "FAM-22"}[mat]
    return f"FAM-{[m[0] for m in MATERIAIS].index(mat) + 1:02d}"


FAMILIAS = [(f"FAM-{i + 1:02d}", f"Frascos {m[0]}", "Frasco", m[0]) for i, m in enumerate(MATERIAIS)] + [
    ("FAM-15", "Potes PP (inclui PP-PG)", "Pote", "PP"), ("FAM-16", "Tampas PP", "Tampa", "PP"), ("FAM-17", "Tampas PP-PCR", "Tampa", "PP-PCR"),
    ("FAM-18", "Tampas HDPE", "Tampa", "HDPE"), ("FAM-19", "Tampas PETG", "Tampa", "PETG"), ("FAM-20", "Tampas PP-PG (farmacêuticas)", "Tampa", "PP-PG"),
    ("FAM-21", "Tampas HDPE-FG (alimentares)", "Tampa", "HDPE-FG"), ("FAM-22", "Tampas PP-FG (alimentares)", "Tampa", "PP-FG")]
DOC_OK = {"FAM-01", "FAM-02", "FAM-03", "FAM-04", "FAM-05", "FAM-06", "FAM-16", "FAM-18", "FAM-21"}   # 9 de 22 em 10/09/2026
# fecho do ano: +8 famílias com documentação técnica e declaração UE no 4.º trimestre (PAM-26-10) → 17 de 22 (KPI-12)
DOC_Q4 = {"FAM-07": "2026-10-20", "FAM-08": "2026-10-20", "FAM-10": "2026-11-06", "FAM-11": "2026-11-27", "FAM-15": "2026-11-13",
          "FAM-17": "2026-10-20", "FAM-20": "2026-12-22", "FAM-22": "2026-12-04"}
DOC_OK = DOC_OK | set(DOC_Q4)
METAIS_LAB = {"FAM-01", "FAM-02", "FAM-03", "FAM-05", "FAM-18", "FAM-21"}                             # RM-2026-07 (famílias HDPE/PE)
METAIS_DECL = {"FAM-04", "FAM-06", "FAM-07", "FAM-10", "FAM-16", "FAM-17", "FAM-08", "FAM-22"}


def _tampa_para(pid, mat, vol):
    """Tampa de referência do sistema de embalagem (a comercial com o cliente pode ser outra)."""
    pre, num = pid.split("-")[0], int(pid.split("-")[1])
    if pre == "PT":
        return "TP-013-PP-PG-070" if mat == "PP-PG" else "TP-013-PP-070"
    if pre == "FP":
        return "TE-012-PP-PG-24410"
    if pre == "FA":
        return "TA-014-HDPE-FG-28410" if mat == "HDPE-FG" else "TA-014-PP-FG-28410"
    capmat = {"HDPE": "HDPE", "MDPE": "HDPE", "LDPE": "HDPE", "HDPE-PCR": "PP-PCR", "PP": "PP", "PP-PCR": "PP-PCR",
              "PET": "PP", "rPET": "PP", "PETG": "PETG", "PVC": "PP"}[mat]
    small = vol <= 350
    flip = num % 2 == 0 and capmat != "PETG"
    if flip:
        return f"TF-005-{capmat}-24410" if small else f"TF-007-{capmat}-28410"
    return f"TR-001-{capmat}-24410" if small else f"TR-004-{capmat}-28410"


def _geom(vol, pote):
    """Área lateral (cm²) estimada: frasco cilíndrico H = 2D; pote H = 0,8D."""
    import math
    k = 0.8 if pote else 2.0
    d = (vol / (math.pi / 4 * k)) ** (1 / 3)
    return math.pi * d * d * k, d * 10, d * k * 10


def produtos():
    bt, cp, hfs, ser, cores, s12, _sa = _dados()
    caps = {}
    for x in cp.itertuples():
        caps[x.CapId] = dict(CapId=x.CapId, Descricao=x.ItemDescription, Tipo_Abertura=x.OpeningType, Material=x.Material,
                             Massa_g=round((x.MinWeightG + x.MaxWeightG) / 2, 1), Rosca=x.ThreadFinish if isinstance(x.ThreadFinish, str) else f"{x.ThreadDiameterMm} mm",
                             Vedante="Sem vedante", Familia_PPWR=_familia("Tampa", x.Material))
    rows = []
    for k, x in enumerate(bt.itertuples(), start=1):
        mat, vol, pid = x.BaseMaterial, x.VolumeMl, x.ProductId
        pote = pid.startswith("PT-")
        seg = _segmento(pid, mat)
        m_corpo = round(envdata.P["G_FRASCO"] * (vol / 300) ** (2 / 3), 1)
        area, dmm, hmm = _geom(vol, pote)
        # decoração (dataset) e rótulo (cenário típico do cliente)
        if pid in hfs:
            deco, ncor = "Hot foil metalizado", 1
        elif pid in ser:
            deco, ncor = "Serigrafia", int(cores.get(pid, 1))
        else:
            deco, ncor = "Nenhuma", 0
        num = int(pid.split("-")[1])
        if deco != "Nenhuma":
            rot, ades, cob = "Sem rótulo", "Sem adesivo", 0.0
        elif seg == "Farmacêutico":
            rot, ades, cob = "Autoadesivo papel", "Acrílico permanente", 0.35
        elif MAT[mat][1] in ("PET", "PETG", "PVC"):
            rot, ades, cob = "Autoadesivo PE/PP", ("Acrílico permanente" if (mat == "PET" and num % 2 == 1) else "Lavável a 80 °C (alcalino)"), 0.40
        else:
            rot, ades, cob = "Autoadesivo PE/PP", "Acrílico permanente", 0.40
        gsm = PV["P-03"] if "papel" in rot else PV["P-02"]
        m_rot = round(area * cob * gsm / 10000, 2)
        m_deco = round(ncor * PV["P-04"], 2) if deco == "Serigrafia" else (PV["P-05"] if deco.startswith("Hot") else 0.0)
        cap = _tampa_para(pid, mat, vol)
        assert cap in caps, cap
        ved = "Vedante PE/EVA" if pid.startswith("FA") else "Sem vedante"
        g = s12[s12.ProductId == pid]
        paises = sorted({PAIS[c][0] for c in g.Country.dropna()})
        rows.append(dict(ID_Avaliacao=f"RCA-{k:03d}", ProductId=pid, Formato="Pote" if pote else "Frasco", Segmento=seg,
                         Contacto="Contacto direto com " + {"Alimentar": "alimento", "Farmacêutico": "medicamento"}.get(seg, "cosmético/higiene"),
                         Processo_Fabrico="Injeção" if pote else "Injeção-sopro (ISBM)", Familia_PPWR=_familia("Pote" if pote else "Frasco", mat),
                         Volume_ml=vol, Dimensao_Max_mm=round(max(dmm, hmm)), Material_Corpo=mat, Cor_Dataset=x.ColorName, Cor_Corpo=COR[x.ColorName],
                         Masterbatch_Tipo=x.MasterbatchType, Masterbatch_Pct=x.StandardDosagePctMass, Barreira_Revestimento="Nenhuma",
                         Massa_Corpo_g=m_corpo, Origem_Massa="Estimada (22 g a 300 ml, escala ^2/3)", ID_Tampa=cap, Vedante_Tampa=ved,
                         Rotulo_Tipo=rot, Rotulo_Adesivo=ades, Rotulo_Cobertura_Pct=cob, Massa_Rotulo_g=m_rot,
                         Origem_Rotulo="Sem rótulo (decoração direta Plasticom)" if deco != "Nenhuma" else "Cenário típico do cliente — confirmar especificação",
                         Decoracao_Tipo=deco, Decoracao_N_Cores=ncor, Massa_Decoracao_g=m_deco,
                         Unid_Vendidas_P12=int(g.ShippedQty.sum()), N_Clientes_P12=int(g.CustomerId.nunique()), Paises_Venda="; ".join(paises),
                         Data_Avaliacao=DAV, Avaliador=F_RD, Estado_Avaliacao="Autoavaliação (não certificada)",
                         Metodo="Regras simplificadas SGA-20 v1 (diretrizes DfR RecyClass) — confirmar na ferramenta online"))
    for cid, c in caps.items():
        g = s12[s12.ProductId == cid]
        c["Unid_Vendidas_P12"] = int(g.ShippedQty.sum())
        c["Paises_Venda"] = "; ".join(sorted({PAIS[p][0] for p in g.Country.dropna()}))
    return rows, list(caps.values()), s12


# ------------------------------------------------------------------ avaliação em Python (espelho das fórmulas)
def _grade_rate(t):
    return 1 if t >= PV["P-06"] else 2 if t >= PV["P-07"] else 3 if t >= PV["P-08"] else 4


def avaliar(rows=None, caps=None):
    if rows is None:
        rows, caps, _ = produtos()
    cmap = {c["CapId"]: c for c in caps}
    out = []
    for r in rows:
        m = MAT[r["Material_Corpo"]]
        fl = m[2]
        cap = cmap[r["ID_Tampa"]]
        cpol = MAT[cap["Material"]][1]
        dens = m[3] + r["Masterbatch_Pct"] * 1.2
        dv = r["Decoracao_Tipo"] if r["Decoracao_Tipo"] != "Serigrafia" else ("Serigrafia ≥ 3 cores" if r["Decoracao_N_Cores"] >= 3 else "Serigrafia 1–2 cores")
        vals = dict(fluxo=fl, cor=r["Cor_Corpo"], dens="< 1,0 g/cm³" if dens < 1 else "≥ 1,0 g/cm³", barr=r["Barreira_Revestimento"],
                    tampa=cpol, ved=r["Vedante_Tampa"], rot=r["Rotulo_Tipo"], ades=r["Rotulo_Adesivo"],
                    cob="> 70% da superfície" if r["Rotulo_Cobertura_Pct"] > 0.7 else "≤ 70% da superfície", deco=dv)
        cls, fr = {}, {}
        for colname, car, _e, key in FEAT:
            if fl.startswith("Sem fluxo") and key != "fluxo":
                cls[colname] = "—"
                continue
            rr = RULES[f"{fl}|{car}|{vals[key]}"]
            cls[colname], fr[key] = rr[3], rr[4]
        nmax = max(CLS.index(c) + 1 for c in cls.values() if c in CLS)
        classe = CLS[nmax - 1]
        fb = min(fr.get("fluxo", 0), fr.get("cor", 0))
        mt = cap["Massa_g"]
        tot = r["Massa_Corpo_g"] + mt + r["Massa_Rotulo_g"] + r["Massa_Decoracao_g"]
        rec = fb * (r["Massa_Corpo_g"] + mt * fr.get("tampa", 0) + r["Massa_Rotulo_g"] * fr.get("rot", 0))
        taxa = rec / tot
        if classe == "F":
            grau = "Não reciclável (F)"
        else:
            grau = ["A", "B", "C", "Abaixo de C"][max(min(nmax, 4), _grade_rate(taxa)) - 1]
        farm = r["Segmento"] == "Farmacêutico"
        c30 = "Isento até 2035" if farm else ("Sim" if grau in ("A", "B", "C") else "Não")
        pcr_c, pcr_t = m[5], MAT[cap["Material"]][5]
        pcr = (r["Massa_Corpo_g"] * pcr_c + mt * pcr_t) / (r["Massa_Corpo_g"] + mt)
        if farm:
            cat = "Isenta — medicamentos (art. 7.º)"
        elif r["Segmento"] == "Alimentar":
            cat = "Sensível ao contacto — PET" if m[1] == "PET" else "Sensível ao contacto — outros plásticos"
        else:
            cat = "Outras embalagens de plástico"
        meta = M7[cat][1]
        c7 = "Isento" if meta is None else ("Sim" if pcr >= meta else "Não")
        out.append(dict(ProductId=r["ProductId"], Segmento=r["Segmento"], Material=r["Material_Corpo"], Fluxo=fl, Classe=classe, Taxa=taxa,
                        Grau=grau, Conforme_2030=c30, PCR=pcr, Categoria_Art7=cat, Conforme_Art7=c7, Massa_Corpo=r["Massa_Corpo_g"],
                        Unid=r["Unid_Vendidas_P12"], Massa_Vendida_kg=r["Unid_Vendidas_P12"] * r["Massa_Corpo_g"] / 1000, Familia=r["Familia_PPWR"], **cls))
    return pd.DataFrame(out)


def resumo():
    """Indicadores usados por RG-SGA-05 (KPI), RG-SGA-17 (evidências) e RG-SGA-19 (ESG-E29)."""
    rows, caps, s12 = produtos()
    a = avaliar(rows, caps)
    nao_isentos = a[a.Segmento != "Farmacêutico"]
    ok = nao_isentos.Grau.isin(["A", "B", "C"])
    mv = a.Massa_Vendida_kg
    return dict(n_skus=len(a), n_avaliados=len(a), pct_ac_skus=ok.mean(), n_ac=int(ok.sum()), n_nao_isentos=len(nao_isentos),
                pct_ac_massa=mv[a.Grau.isin(["A", "B", "C"]) & (a.Segmento != "Farmacêutico")].sum() / mv[a.Segmento != "Farmacêutico"].sum(),
                n_F=int((a.Classe == "F").sum()), classes=a.Classe.value_counts().to_dict(), pcr_massa=(a.PCR * mv).sum() / mv.sum(),
                cert_validos=2, cert_necessarios=3, doc_ok=len(DOC_OK), familias=len(FAMILIAS))


# ------------------------------------------------------------------ requisitos (matriz integrada verificada)
# (ID, grupo, fonte, artigo, tema, requisito, natureza, papel, nível, âmbito, data aplic., aplicabilidade, evidência SGA, método, frequência,
#  estado, risco, ID_Legal, ID_PAM, responsável, prazo, verificação, nota, fonte oficial)
PPWR_URL = "https://eur-lex.europa.eu/eli/reg/2025/40/oj"
REQ = [
    ("EU-ENV-001", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Arts. 1.º–4.º; aplicação geral (art. 71.º)", "Âmbito PPWR",
     "Todas as embalagens colocadas no mercado da UE têm de cumprir os requisitos de sustentabilidade, rotulagem e informação do PPWR, aplicável desde 12/08/2026 (aplicação faseada).",
     "Obrigação legal", "Fabricante de embalagens e fornecedor a fabricantes de produtos embalados", "Empresa", "Todos", "2026-08-12", "Sim",
     "RG-SGA-04 LEG-09; RG-SGA-20 tbl_recyclass, tbl_familias_ppwr", "Análise documental", "Semestral", "Parcial", "Alto", "LEG-09", "PAM-26-10", F_RD, "2026-12-31",
     "Confirmado", "Data de início de aplicação confirmada (12/08/2026). Papel da Plasticom precisado: fabricante das embalagens vazias que vende em nome próprio.", PPWR_URL),
    ("EU-ENV-002", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 6.º e anexo II (graus de desempenho)", "Conceção para reciclagem",
     "A partir de 01/01/2030 só embalagens recicláveis com grau A, B ou C; a partir de 01/01/2038 só A ou B. Critérios de DfR por atos delegados (até 01/01/2028). Isenção até 2035 para embalagem imediata de medicamentos e dispositivos médicos.",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Todos", "2030-01-01", "Futuro",
     "RG-SGA-20 tbl_recyclass (Classe_RecyClass, Grau_PPWR_Indicativo), tbl_regras_dfr", "Avaliação técnica por SKU (autoavaliação RecyClass)", "Anual e em cada alteração de design", "Parcial", "Alto", "LEG-09", "PAM-26-22", F_RD, "2028-12-31",
     "Complementado", "Correto quanto a 2030 (A–C) e 2038 (A–B). Acrescentado: atos delegados de DfR ainda por publicar (grau atual é indicativo), isenção farmacêutica até 2035 e 'reciclado à escala' (EU-ENV-010).", PPWR_URL),
    ("EU-ENV-003", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 7.º (teor mínimo de reciclado)", "Conteúdo reciclado",
     "A partir de 01/01/2030, teor mínimo de plástico reciclado pós-consumo por unidade de embalagem (média por instalação de fabrico e por ano): 30% PET sensível ao contacto; 10% outros plásticos sensíveis ao contacto; 30% garrafas de bebidas; 35% outras. Em 2040: 50% / 25% / 65% / 65%.",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Todos", "2030-01-01", "Futuro",
     "RG-SGA-20 tbl_recyclass (Conteudo_Reciclado_Pct, Gap_2030), tbl_metas_art7, tbl_certificados_pcr; RG-SGA-13 PCR_KG", "Balanço de massa anual + certificados EN 15343", "Anual", "Parcial", "Alto", "LEG-09", "PAM-26-25", F_CMP, "2029-12-31",
     "Complementado", "Acrescentadas as metas numéricas 2030/2040, a regra de cálculo por instalação/ano e as isenções (medicamentos, dispositivos médicos, componentes < 5% da massa). Método de cálculo por ato de execução — confirmar publicação.", PPWR_URL),
    ("EU-ENV-004", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 10.º (minimização)", "Minimização",
     "A partir de 2030, peso e volume reduzidos ao mínimo necessário para a função; a documentação técnica deve demonstrar a minimização.",
     "Obrigação legal", "Fabricante de embalagens (e produtor do produto embalado)", "Produto", "Todos", "2030-01-01", "Futuro",
     "RG-SGA-20 tbl_recyclass (Massa_Corpo_g); RG-SGA-19 tbl_pegada_produto", "Análise documental da documentação técnica", "Anual", "Parcial", "Médio", "LEG-09", "PAM-26-10", F_RD, "2029-12-31",
     "Confirmado", "Massas dos frascos ainda estimadas (escala de volume) — substituir por massas medidas por molde.", PPWR_URL),
    ("EU-ENV-005", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 12.º (rotulagem harmonizada)", "Rotulagem",
     "Rótulo harmonizado de composição material a partir de 12/08/2028 (ou 24 meses após o ato de execução); rótulo de conteúdo reciclado facultativo com regras próprias.",
     "Obrigação legal", "Produtor do produto embalado (cliente); a Plasticom fornece a informação de material e pode marcar o código no molde (ISO 11469)", "Produto", "Todos", "2028-08-12", "Futuro",
     "RG-SGA-20 tbl_materiais (Codigo_Identificacao); fichas técnicas", "Verificação de amostras e fichas técnicas", "Anual", "Futuro", "Médio", "LEG-09", "", F_RD, "2028-08-12",
     "Complementado", "Distinguido o responsável (cliente) do contributo da Plasticom (informação e marcação no molde).", PPWR_URL),
    ("EU-ENV-006", "UE — resíduos", "Diretiva 2008/98/CE (quadro dos resíduos), transposta pelo DL 102-D/2020", "Arts. 4.º (hierarquia), 15.º", "Resíduos internos",
     "Aplicar a hierarquia dos resíduos, separar, encaminhar para operadores licenciados e registar (MIRR, e-GAR).",
     "Obrigação legal", "Produtor de resíduos", "Empresa", "Empresa", "2020-12-10", "Sim",
     "RG-SGA-04 LEG-01, LEG-13; RG-SGA-13 tbl_residuos; RG-SGA-05 KPI-05", "Auditoria / análise documental", "Anual", "Conforme", "Médio", "LEG-01", "", F_SGA, "",
     "Confirmado", "Já coberto no SGA (LEG-01, LEG-13).", "https://eur-lex.europa.eu/eli/dir/2008/98/oj"),
    ("EU-ENV-007", "UE — embalagens", "Diretiva (UE) 2019/904 (SUP), transposta pelo DL 78/2021", "Arts. 5.º–7.º e anexo (tampas presas, recipientes para alimentos)", "Plásticos de utilização única",
     "Recipientes para bebidas até 3 L com tampas de plástico têm de ter tampas presas; recipientes para alimentos de consumo imediato sujeitos a redução de consumo e RAP.",
     "Necessita verificação", "Fabricante de embalagens (tampas) — obrigação de colocação no mercado do produtor do produto", "Produto", "Alimentar", "2024-07-03", "Condicional",
     "RG-SGA-20 tbl_aplicabilidade (FA-030/031); confirmação de uso pelos clientes CUST-015/016", "Declaração de utilização do cliente", "Por ocorrência", "Conforme", "Médio", "LEG-19", "PAM-26-26", F_RD, "2026-11-30",
     "Complementado", "Condicional confirmado. Ponto crítico novo: se os frascos alimentares FA-030/031 forem usados para bebidas, as tampas TA-014 têm de ser presas (tethered).", "https://eur-lex.europa.eu/eli/dir/2019/904/oj"),
    ("EU-ENV-008", "UE — químicos", "Reg. (CE) 1907/2006 (REACH)", "Art. 33.º (SVHC em artigos > 0,1%); anexo XVII", "Substâncias na cadeia",
     "Comunicar aos clientes SVHC > 0,1% (m/m) nos artigos (art. 33.º); notificar a SCIP e, se > 1 t/ano, a ECHA (art. 7.º, n.º 2); cumprir as restrições do anexo XVII aplicáveis aos artigos.",
     "Obrigação legal", "Utilizador a jusante (misturas) e fornecedor de artigos (embalagens)", "Empresa", "Todos", "2007-06-01", "Sim",
     "RG-SGA-20 tbl_familias_ppwr (SVHC_Artigo); RG-SGA-21 tbl_declaracoes", "Declarações de fornecedores e cálculo por artigo", "Semestral", "Parcial", "Médio", "LEG-06", "PAM-26-34", F_CMP, "2026-12-31",
     "Confirmado", "Por confirmar: PVC (FAM-14) e tampas PP com aditivo antiestático (FAM-16/17).", "https://eur-lex.europa.eu/eli/reg/2006/1907/oj"),
    ("EU-ENV-009", "UE — químicos", "Reg. (CE) 1272/2008 (CLP)", "Arts. 17.º e 31.º", "Classificação e rotulagem de misturas",
     "Aplica-se às misturas usadas (tintas, solventes, óleos), não às embalagens vendidas.",
     "Obrigação legal", "Utilizador a jusante", "Empresa", "Empresa", "2009-01-20", "Sim",
     "RG-SGA-04 LEG-06 (FDS e rotulagem CLP)", "Inspeção de rótulos e FDS", "Anual", "Conforme", "Baixo", "LEG-06", "", F_LOG, "",
     "Confirmado", "Correto: o CLP não equivale à rotulagem das embalagens de consumo.", "https://eur-lex.europa.eu/eli/reg/2008/1272/oj"),
    ("EU-ENV-010", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 6.º (reciclado à escala)", "Reciclado à escala",
     "A partir de 2035 as embalagens têm também de ser 'recicladas à escala' (recolha, triagem e reciclagem com capacidade na UE, metodologia por ato de execução).",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Todos", "2035-01-01", "Futuro",
     "RG-SGA-20 tbl_recyclass (Fluxo_Reciclagem)", "Avaliação técnica", "Anual", "Futuro", "Médio", "LEG-09", "", F_RD, "2034-12-31",
     "Adicionado", "Não referido explicitamente na matriz do ChatGPT (apenas 'reciclagem em escala' como evidência).", PPWR_URL),
    ("EU-ENV-011", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 5.º (metais pesados)", "Metais pesados",
     "Soma de chumbo, cádmio, mercúrio e crómio hexavalente ≤ 100 mg/kg na embalagem ou nos seus componentes.",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Todos", "2026-08-12", "Sim",
     "RG-SGA-20 tbl_familias_ppwr (Metais_Pesados_Evidencia); relatório RM-2026-07", "Ensaio laboratorial por família / declaração do fornecedor", "Anual", "Parcial", "Alto", "LEG-09", "PAM-26-10", F_QUA, "2026-12-31",
     "Adicionado", "A matriz do ChatGPT só fala em 'restrições de substâncias' em geral.", PPWR_URL),
    ("EU-ENV-012", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 5.º, n.º 5 (PFAS em contacto alimentar)", "PFAS",
     "Desde 12/08/2026 as embalagens em contacto com alimentos não podem conter PFAS acima de 25 ppb (cada PFAS), 250 ppb (soma) ou 50 ppm (flúor total).",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Alimentar", "2026-08-12", "Sim",
     "Declaração PFAS SUP-010 (07/2026); RG-SGA-21 tbl_declaracoes; RG-SGA-20 tbl_alegacoes ALG-10", "Declaração do fornecedor + ensaio de flúor total", "Anual", "Conforme", "Alto", "LEG-17", "", F_QUA, "",
     "Adicionado", "Requisito com aplicação imediata não identificado na matriz do ChatGPT.", PPWR_URL),
    ("EU-ENV-013", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Arts. 15.º e 38.º–39.º, anexo VII (confirmar numeração na versão consolidada)", "Documentação técnica e declaração UE",
     "Avaliação da conformidade (controlo interno da produção), documentação técnica e declaração UE de conformidade antes da colocação no mercado; conservar 5 anos (10 se reutilizável).",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Todos", "2026-08-12", "Sim",
     "RG-SGA-20 tbl_familias_ppwr (17/22 em 22/12/2026); RG-SGA-05 KPI-12; RG-SGA-04 OBR-12", "Análise documental do dossier", "Semestral", "Parcial", "Alto", "LEG-09", "PAM-26-10", F_RD, "2026-12-31",
     "Complementado", "O ChatGPT refere 'documentação técnica'; faltava a declaração UE e o prazo de conservação.", PPWR_URL),
    ("EU-ENV-014", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Obrigações de informação na cadeia (fornecedor → fabricante do produto embalado)", "Informação ao cliente",
     "Fornecer ao fabricante do produto embalado a informação e documentos necessários para demonstrar a conformidade (material, reciclabilidade, reciclado, substâncias).",
     "Obrigação legal", "Fornecedor de embalagens a fabricantes de produtos embalados", "Empresa", "Todos", "2026-08-12", "Sim",
     "RG-SGA-20 Formulario_RecyClass e tbl_recyclass (ficha por SKU)", "Amostragem de fichas enviadas aos clientes", "Anual", "Parcial", "Médio", "LEG-09", "PAM-26-10", F_RD, "2026-12-31",
     "Adicionado", "Os clientes (7 de 9 grandes) já pedem classe de reciclabilidade — DM-11 do RG-SGA-17.", PPWR_URL),
    ("EU-ENV-015", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Art. 29.º (embalagens de transporte reutilizáveis)", "Reutilização — expedição",
     "A partir de 2030, paletes, grades e caixas de plástico usadas no transporte entre instalações próprias ou para parceiros no mesmo Estado-Membro têm de ser reutilizáveis (caixas de cartão excluídas).",
     "Necessita verificação", "Utilizador de embalagens de transporte (expedição)", "Empresa", "Expedição", "2030-01-01", "Futuro",
     "RG-SGA-20 tbl_emb_expedicao (paletes sem retorno)", "Análise documental", "Anual", "Lacuna", "Médio", "LEG-09", "PAM-26-26", F_LOG, "2029-06-30",
     "Adicionado", "Paletes de madeira sem retorno nas entregas em Portugal — estudar pool/retorno.", PPWR_URL),
    ("EU-ENV-016", "UE — embalagens", "Reg. (UE) 2025/40 (PPWR)", "Arts. 44.º–45.º (RAP e modulação das prestações)", "RAP e ecomodulação",
     "Os produtores (clientes) pagam prestações moduladas pelo grau de reciclabilidade; grau mais baixo = custo maior.",
     "Obrigação legal", "Produtor do produto embalado (cliente) — impacto comercial para a Plasticom", "Empresa", "Todos", "2028-08-12", "Futuro",
     "RG-SGA-20 tbl_recyclass (grau por SKU) e tbl_requisitos_pais", "Análise documental", "Anual", "Futuro", "Médio", "LEG-16", "", F_FIN, "",
     "Adicionado", "Datas da modulação por grau a confirmar nos atos de execução.", PPWR_URL),
    ("EU-ENV-017", "UE — embalagens", "Diretiva 94/62/CE (embalagens e resíduos de embalagens)", "Revogada pelo PPWR (com disposições transitórias)", "Regime anterior",
     "Base histórica dos requisitos essenciais e das normas EN 13427–13432; mantém efeitos só nas disposições transitórias.",
     "Necessita verificação", "—", "Empresa", "Nenhum", "1994-12-31", "Não",
     "RG-SGA-04 (histórico)", "Análise documental", "Por ocorrência", "Não aplicável", "Baixo", "", "", F_SGA, "",
     "Corrigido", "O ChatGPT lista-a como referência; foi substituída pelo PPWR a partir de 12/08/2026 — manter apenas para rastrear disposições transitórias.", "https://eur-lex.europa.eu/eli/dir/1994/62/oj"),
    ("EU-ENV-018", "UE — consumidores", "Diretiva (UE) 2024/825 (capacitação dos consumidores para a transição ecológica)", "Alterações à Diretiva 2005/29/CE (anexo I)", "Alegações ambientais",
     "A partir de 27/09/2026 são proibidas alegações ambientais genéricas sem desempenho reconhecido e alegações baseadas em compensações; as alegações têm de ser específicas e comprovadas.",
     "Obrigação legal", "Autor de comunicações comerciais (site, catálogos, fichas)", "Empresa", "Todos", "2026-09-27", "Sim",
     "PR-SGA-14; RG-SGA-20 tbl_alegacoes", "Revisão das comunicações", "Semestral", "Conforme", "Alto", "LEG-18", "PAM-26-27", F_DG, "2026-09-27",
     "Adicionado", "Na matriz do ChatGPT aparece só como COS-005; tem aplicação transversal e prazo imediato.", "https://eur-lex.europa.eu/eli/dir/2024/825/oj"),
    ("FCM-001", "UE — contacto alimentar", "Reg. (CE) 1935/2004", "Arts. 3.º, 16.º, 17.º", "Materiais em contacto com alimentos",
     "Materiais inertes nas condições de uso, rastreabilidade e declaração de conformidade.",
     "Obrigação legal", "Fabricante de materiais em contacto com alimentos", "Produto", "Alimentar", "2004-12-03", "Sim",
     "RG-SGA-04 LEG-17; dossier FCM dos SKUs FA", "Análise documental", "Anual", "Conforme", "Alto", "LEG-17", "", F_QUA, "",
     "Confirmado", "", "https://eur-lex.europa.eu/eli/reg/2004/1935/oj"),
    ("FCM-002", "UE — contacto alimentar", "Reg. (CE) 2023/2006 (BPF)", "Arts. 5.º–7.º", "Boas práticas de fabrico FCM",
     "Sistema de garantia e controlo da qualidade e documentação das BPF.",
     "Obrigação legal", "Fabricante de materiais em contacto com alimentos", "Produto", "Alimentar", "2008-08-01", "Sim",
     "Procedimentos de qualidade da linha alimentar", "Auditoria interna BPF", "Anual", "Parcial", "Médio", "LEG-17", "", F_QUA, "2027-03-31",
     "Confirmado", "Falta auditoria interna específica de BPF (2023/2006).", "https://eur-lex.europa.eu/eli/reg/2006/2023/oj"),
    ("FCM-006", "UE — contacto alimentar", "Reg. (UE) 2024/3190", "Arts. 3.º–5.º", "Bisfenol A e bisfenóis perigosos",
     "Proibição de BPA e de outros bisfenóis perigosos em materiais e objetos em contacto com alimentos (incl. vernizes e tintas), com períodos de transição.",
     "Obrigação legal", "Fabricante de materiais plásticos em contacto com alimentos", "Produto", "Alimentar", "2025-01-20", "Sim",
     "RG-SGA-21 tbl_declaracoes (BPA = Não em todos os polímeros FCM)", "Declaração do fornecedor", "Anual", "Conforme", "Médio", "LEG-17", "", F_QUA, "",
     "Adicionado", "Antes estava só na matriz de químicos (RG-SGA-21); é requisito de produto.", "https://eur-lex.europa.eu/eli/reg/2024/3190/oj"),
    ("FCM-003", "UE — contacto alimentar", "Reg. (UE) 10/2011", "Arts. 11.º–12.º, 15.º, anexo IV", "Plásticos em contacto com alimentos",
     "Lista da União de substâncias, limites de migração global e específica e declaração de conformidade (anexo IV).",
     "Obrigação legal", "Fabricante de materiais plásticos em contacto com alimentos", "Produto", "Alimentar", "2011-05-01", "Sim",
     "Ensaios de migração 2026-03 (HDPE-FG, PP-FG); DoC anexo IV", "Ensaio + análise documental", "Por ocorrência (alteração de material)", "Conforme", "Alto", "LEG-17", "", F_QUA, "",
     "Confirmado", "", "https://eur-lex.europa.eu/eli/reg/2011/10/oj"),
    ("FCM-004", "UE — contacto alimentar", "Reg. (UE) 2022/1616 (plásticos reciclados em contacto com alimentos)", "Arts. 4.º–6.º", "Reciclado em contacto alimentar",
     "Plástico reciclado só de processos com tecnologia adequada/autorizada. Hoje sem reciclado nos SKUs alimentares; condiciona a meta de 10% do PPWR para PE/PP alimentar.",
     "Obrigação legal", "Fabricante de materiais em contacto com alimentos", "Material", "Alimentar", "2022-10-10", "Condicional",
     "RG-SGA-20 tbl_certificados_pcr (CERT-04, reciclado químico em avaliação)", "Análise documental", "Por ocorrência", "Não aplicável", "Médio", "LEG-17", "PAM-26-25", F_QUA, "2029-12-31",
     "Complementado", "Acrescentada a ligação à meta de 10% (art. 7.º do PPWR) para PE/PP alimentar.", "https://eur-lex.europa.eu/eli/reg/2022/1616/oj"),
    ("FCM-005", "UE — contacto alimentar", "Reg. (UE) 2025/40 (PPWR) × segurança alimentar", "Arts. 5.º e 7.º", "Interação segurança × ambiente",
     "Avaliar em conjunto PFAS, reciclado e reciclabilidade nas embalagens alimentares.",
     "Obrigação legal", "Fabricante de embalagens", "Empresa", "Alimentar", "2026-08-12", "Sim",
     "EU-ENV-012 e FCM-004", "Análise documental", "Anual", "Conforme", "Médio", "LEG-17", "", F_QUA, "",
     "Confirmado", "Operacionalizado em EU-ENV-012 (PFAS) e FCM-004.", PPWR_URL),
    ("COS-001", "UE — cosméticos", "Reg. (CE) 1223/2009", "Art. 3.º; anexo I (relatório de segurança)", "Segurança do produto cosmético",
     "A pessoa responsável (cliente) avalia a segurança incluindo o material de embalagem; a Plasticom fornece especificações e composição.",
     "Requisito contratual", "Fornecedor de embalagem primária", "Produto", "Cosmética", "2013-07-11", "Sim",
     "Especificações aprovadas e acordos de qualidade com clientes", "Análise documental", "Anual", "Conforme", "Médio", "LEG-20", "", F_QUA, "",
     "Confirmado", "", "https://eur-lex.europa.eu/eli/reg/2009/1223/oj"),
    ("COS-002", "UE — cosméticos", "Reg. (CE) 1223/2009", "Anexo I, parte A, ponto 4 (material de embalagem)", "Materiais e impurezas",
     "Informação sobre o material de embalagem e possíveis migrações/impurezas para o relatório de segurança do cliente.",
     "Requisito contratual", "Fornecedor de embalagem primária", "Produto", "Cosmética", "2013-07-11", "Sim",
     "Declarações de composição por SKU (ficha RecyClass)", "Análise documental", "Anual", "Parcial", "Médio", "LEG-20", "", F_QUA, "2026-12-31",
     "Confirmado", "Declarações de composição ainda não enviadas a todos os clientes.", "https://eur-lex.europa.eu/eli/reg/2009/1223/oj"),
    ("COS-003", "UE — cosméticos", "EN ISO 22716:2007 (BPF de cosméticos)", "Norma harmonizada", "Boas práticas de fabrico",
     "Aplica-se ao fabrico do cosmético; para a Plasticom só por exigência contratual.",
     "Norma técnica de suporte", "Fornecedor (só se contratado)", "Empresa", "Cosmética", "2007-11-15", "Condicional",
     "Acordos de qualidade", "Auditoria de cliente", "Por ocorrência", "Conforme", "Baixo", "LEG-20", "", F_QUA, "",
     "Confirmado", "", "https://single-market-economy.ec.europa.eu/sectors/cosmetics_en"),
    ("COS-004", "UE — cosméticos", "Reg. (CE) 1223/2009 / requisitos do cliente", "—", "Compatibilidade embalagem–produto",
     "Ensaios de compatibilidade e estabilidade feitos pelo cliente com especificação da Plasticom.",
     "Requisito contratual", "Fornecedor de embalagem primária", "Produto", "Cosmética", "2013-07-11", "Sim",
     "Fichas técnicas e amostras aprovadas", "Análise documental", "Por ocorrência", "Conforme", "Médio", "LEG-20", "", F_QUA, "",
     "Confirmado", "", ""),
    ("COS-005", "UE — cosméticos", "Diretiva (UE) 2024/825 / ISO 14021", "—", "Alegações ambientais das embalagens",
     "Ver EU-ENV-018 (tratado de forma transversal).", "Obrigação legal", "Autor da comunicação", "Empresa", "Cosmética", "2026-09-27", "Sim",
     "RG-SGA-20 tbl_alegacoes", "Revisão das comunicações", "Semestral", "Conforme", "Alto", "LEG-18", "PAM-26-27", F_DG, "2026-09-27",
     "Confirmado", "Consolidado em EU-ENV-018.", ""),
    ("PHAR-001", "UE — farmacêutico", "Diretiva 2001/83/CE", "Art. 8.º, anexo I (dossier AIM)", "Medicamentos de uso humano",
     "O titular da AIM declara o acondicionamento primário; alterações de material exigem notificação — obriga a controlo de alterações contratual.",
     "Requisito contratual", "Fornecedor de acondicionamento primário", "Produto", "Farmacêutico", "2001-12-18", "Sim",
     "Acordos de qualidade CUST-017/018; RG-SGA-18 (alterações)", "Auditoria de cliente", "Anual", "Conforme", "Alto", "LEG-20", "", F_QUA, "",
     "Confirmado", "", "https://eur-lex.europa.eu/eli/dir/2001/83/oj"),
    ("PHAR-002", "UE — farmacêutico", "Reg. (UE) 2019/6", "—", "Medicamentos veterinários",
     "Sem clientes de medicamentos veterinários.", "Requisito contratual", "—", "Empresa", "Nenhum", "2022-01-28", "Não",
     "dim_customer (sem segmento veterinário)", "Análise documental", "Anual", "Não aplicável", "Baixo", "", "", F_QUA, "",
     "Confirmado", "Condicional → não aplicável na carteira atual.", "https://eur-lex.europa.eu/eli/reg/2019/6/oj"),
    ("PHAR-003", "UE — farmacêutico", "Reg. Delegado (UE) 2016/161", "Arts. 3.º, 16.º (dispositivo de prevenção de adulterações)", "Dispositivos de segurança",
     "Obrigação do titular da AIM; a tampa com selo TE-012 pode ser o dispositivo de prevenção de adulterações — especificação contratual.",
     "Requisito contratual", "Fornecedor de tampas com selo de garantia", "Produto", "Farmacêutico", "2019-02-09", "Condicional",
     "Especificação TE-012 aprovada pelo cliente", "Análise documental", "Por ocorrência", "Conforme", "Médio", "LEG-20", "", F_QUA, "",
     "Confirmado", "", "https://eur-lex.europa.eu/eli/reg_del/2016/161/oj"),
    ("PHAR-004", "UE — farmacêutico", "EudraLex vol. 4 (BPF de medicamentos)", "Parte I, cap. 5 (materiais de acondicionamento)", "BPF de medicamentos",
     "Os fabricantes de medicamentos qualificam e auditam os fornecedores de acondicionamento.", "Requisito contratual", "Fornecedor qualificado", "Empresa", "Farmacêutico", "2013-03-01", "Sim",
     "Auditoria de cliente CUST-017 (05/2026, sem NC maiores)", "Auditoria de cliente", "Bienal", "Conforme", "Médio", "LEG-20", "", F_QUA, "",
     "Confirmado", "", "https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en"),
    ("PHAR-005", "UE — farmacêutico", "EMA — Guideline on plastic immediate packaging materials", "CPMP/QWP/4359/03", "Materiais plásticos de acondicionamento primário",
     "Dados de composição, extraíveis e conformidade com a Farmacopeia Europeia (3.1/3.2) para PP-PG e PET-PG.",
     "Norma técnica de suporte", "Fornecedor de acondicionamento primário", "Produto", "Farmacêutico", "2005-12-01", "Sim",
     "Declarações Ph. Eur. do fornecedor SUP-009", "Análise documental", "Anual", "Parcial", "Alto", "LEG-20", "", F_QUA, "2026-12-31",
     "Confirmado", "SUP-009 é fornecedor spot com 1 ano: falta carta de acesso ao DMF do PET-PG.", "https://www.ema.europa.eu/en/plastic-immediate-packaging-materials-scientific-guideline"),
    ("PHAR-006", "UE — farmacêutico", "Reg. (UE) 2025/40 (PPWR) — isenções", "Arts. 6.º e 7.º (isenções para medicamentos)", "Isenções PPWR",
     "Embalagem imediata de medicamentos isenta da reciclabilidade até 2035 e do teor de reciclado; a isenção tem de ser documentada por SKU e função.",
     "Obrigação legal", "Fabricante de embalagens", "Produto", "Farmacêutico", "2026-08-12", "Sim",
     "RG-SGA-20 tbl_recyclass (Conforme_PPWR_2030 = Isento), tbl_aplicabilidade", "Análise documental", "Anual", "Parcial", "Médio", "LEG-09", "PAM-26-10", F_RD, "2026-12-31",
     "Confirmado", "Correto: a isenção depende da função (acondicionamento imediato), não do setor. Documentar na declaração UE.", PPWR_URL),
    ("ISO-001", "ISO/EN", "ISO 14001:2026", "Sistema de gestão ambiental", "SGA",
     "Base do SGA (aspetos, obrigações, riscos, objetivos, auditoria).", "Norma voluntária", "Organização certificável", "Empresa", "Empresa", "2026-01-01", "Sim",
     "Todo o sistema RG-SGA-00 a 20", "Auditoria", "Anual", "Conforme", "Baixo", "LEG-21", "", F_SGA, "",
     "Corrigido", "O ChatGPT indica a edição de 2015; o SGA já segue a ISO 14001:2026.", "https://www.iso.org/standard/14001"),
    ("ISO-002", "ISO/EN", "ISO 14040:2006 + Amd 1:2020", "—", "ACV — princípios", "Estrutura para ACV de embalagens.", "Norma técnica de suporte", "—", "Empresa", "Todos", "2006-07-01", "Condicional",
     "RG-SGA-19 tbl_pegada_produto (berço-portão simplificado)", "Revisão crítica", "Por ocorrência", "Parcial", "Baixo", "LEG-21", "", F_RD, "",
     "Complementado", "Acrescentada a emenda de 2020.", ""),
    ("ISO-003", "ISO/EN", "ISO 14044:2006 + Amd 1:2017 + Amd 2:2020", "—", "ACV — requisitos", "Requisitos para inventário, avaliação e interpretação.", "Norma técnica de suporte", "—", "Empresa", "Todos", "2006-07-01", "Condicional",
     "RG-SGA-19 tbl_pegada_produto", "Revisão crítica", "Por ocorrência", "Parcial", "Baixo", "LEG-21", "", F_RD, "",
     "Complementado", "Acrescentadas as emendas.", ""),
    ("ISO-004", "ISO/EN", "ISO 14021:2016 + Amd 1:2021", "§ 7.7 (reciclável) e § 7.8 (conteúdo reciclado)", "Autodeclarações ambientais",
     "Regras para alegações 'reciclável' e 'conteúdo reciclado' (qualificação, cálculo, evidência).", "Norma técnica de suporte", "Autor da alegação", "Empresa", "Todos", "2016-03-15", "Sim",
     "PR-SGA-14; RG-SGA-20 tbl_alegacoes", "Revisão das alegações", "Semestral", "Parcial", "Médio", "LEG-21", "PAM-26-27", F_RD, "",
     "Complementado", "Acrescentada a emenda de 2021 e as secções aplicáveis.", ""),
    ("ISO-005", "ISO/EN", "ISO 14024:2018", "—", "Rotulagem tipo I", "Programas de rótulo ecológico de terceira parte.", "Norma voluntária", "—", "Empresa", "Nenhum", "2018-07-01", "Não",
     "—", "—", "Por ocorrência", "Não aplicável", "Baixo", "", "", F_RD, "", "Confirmado", "Sem rótulo tipo I aplicável a embalagens vazias.", ""),
    ("ISO-006", "ISO/EN", "ISO 14025:2006", "—", "Declarações tipo III (EPD)", "Declarações ambientais de produto baseadas em ACV.", "Norma voluntária", "—", "Empresa", "Todos", "2006-07-01", "Condicional",
     "—", "—", "Por ocorrência", "Não aplicável", "Baixo", "", "", F_RD, "", "Confirmado", "Oportunidade futura (clientes pedem EPD).", ""),
    ("ISO-007", "ISO/EN", "ISO 14067:2018", "—", "Pegada de carbono de produto", "PCF de embalagem com regras de alegação.", "Norma técnica de suporte", "—", "Empresa", "Todos", "2018-08-01", "Sim",
     "RG-SGA-19 tbl_pegada_produto", "Verificação por terceira parte", "Anual", "Parcial", "Médio", "LEG-21", "", F_SGA, "",
     "Confirmado", "Pegada simplificada, não verificada — não usar em alegações (ALG-07).", ""),
    ("ISO-008", "ISO/EN", "ISO 15270:2008", "—", "Recuperação e reciclagem de resíduos plásticos", "Orientações para reciclagem mecânica do scrap.", "Norma técnica de suporte", "Produtor de resíduos plásticos", "Empresa", "Empresa", "2008-06-01", "Sim",
     "RG-SGA-13 REGRIND_KG, tbl_residuos (07 02 13 → R3)", "Análise documental", "Anual", "Conforme", "Baixo", "LEG-21", "PAM-26-12", F_SGA, "", "Confirmado", "", ""),
    ("ISO-009", "ISO/EN", "ISO 11469:2016 (+ ISO 1043-1)", "—", "Identificação de plásticos", "Marcação do polímero (>PP<, >PE-HD<) nas peças.", "Norma técnica de suporte", "Fabricante", "Produto", "Todos", "2016-03-01", "Sim",
     "RG-SGA-20 tbl_materiais (Codigo_Identificacao)", "Inspeção de moldes", "Por ocorrência", "Parcial", "Baixo", "LEG-21", "", F_RD, "",
     "Complementado", "Acrescentada a ISO 1043-1 (símbolos).", ""),
    ("ISO-010", "ISO/EN", "ISO 18601–18606:2013 / EN 13427–13432:2004", "—", "Embalagens e ambiente", "Otimização, reutilização, reciclagem e recuperação de embalagens (as EN são as harmonizadas da Diretiva 94/62).",
     "Norma técnica de suporte", "Fabricante de embalagens", "Empresa", "Todos", "2013-01-01", "Sim",
     "RG-SGA-20 tbl_regras_dfr, tbl_recyclass", "Análise documental", "Anual", "Parcial", "Médio", "LEG-21", "", F_RD, "",
     "Complementado", "Acrescentadas as EN 13427–13432; novas normas harmonizadas do PPWR em preparação no CEN.", ""),
    ("ISO-011", "ISO/EN", "ISO 22095:2020", "—", "Cadeia de custódia", "Modelos de cadeia de custódia (segregação, balanço de massa).", "Norma técnica de suporte", "Comprador de reciclado", "Material", "Com PCR", "2020-10-01", "Sim",
     "RG-SGA-20 tbl_certificados_pcr", "Auditoria de fornecedor", "Anual", "Parcial", "Médio", "LEG-21", "PAM-26-25", F_CMP, "", "Confirmado", "", ""),
    ("ISO-012", "ISO/EN", "EN 15343:2007", "—", "Rastreabilidade e cálculo de conteúdo reciclado",
     "Rastreabilidade dos reciclados e cálculo do conteúdo reciclado — base dos certificados EuCertPlast/RecyClass e do imposto espanhol.",
     "Norma técnica de suporte", "Comprador de reciclado", "Material", "Com PCR", "2007-11-01", "Sim",
     "RG-SGA-20 tbl_certificados_pcr", "Análise de certificados", "Anual", "Parcial", "Alto", "LEG-21", "PAM-26-25", F_CMP, "2026-12-31",
     "Adicionado", "Norma essencial em falta na matriz do ChatGPT.", ""),
    ("ISO-013", "ISO/EN", "RecyClass — diretrizes de design para reciclagem e metodologia", "—", "Reciclabilidade (voluntária)",
     "Avaliação e certificação de reciclabilidade por classes A–F; base provável para os critérios do PPWR.",
     "Norma voluntária", "Fabricante de embalagens", "Produto", "Todos", "2026-01-01", "Sim",
     "RG-SGA-20 tbl_recyclass, tbl_regras_dfr, Formulario_RecyClass", "Autoavaliação + certificação por terceira parte", "Anual", "Parcial", "Médio", "LEG-21", "PAM-26-24", F_RD, "",
     "Adicionado", "Autoavaliação feita; certificação RecyClass ainda não pedida.", "https://recyclass.eu"),
    ("ISO-014", "ISO/EN", "EN 13430:2004", "—", "Embalagens recuperáveis por reciclagem",
     "Requisitos para declarar uma embalagem recuperável por reciclagem (harmonizada da Diretiva 94/62; substituição por normas PPWR em curso).",
     "Necessita verificação", "Fabricante de embalagens", "Empresa", "Todos", "2004-01-01", "Condicional",
     "RG-SGA-20 tbl_recyclass", "Análise documental", "Anual", "Parcial", "Baixo", "LEG-21", "", F_RD, "", "Adicionado", "", ""),
    ("PT-001", "PT — nacional", "DL 152-D/2017 (UNILEX), alterado pelo DL 102-D/2020", "Arts. 4.º–13.º (RAP)", "Responsabilidade alargada do produtor",
     "Quem coloca embalagens no mercado nacional transfere a responsabilidade para um sistema integrado (entidade gestora) ou individual. A Plasticom é embalador das embalagens de expedição (caixas, filme, paletes); os clientes são embaladores das embalagens que enchem.",
     "Obrigação legal", "Embalador (embalagens de expedição) — e fornecedor de informação aos clientes embaladores", "Empresa", "Expedição", "2018-01-01", "Sim",
     "RG-SGA-04 LEG-16; RG-SGA-20 tbl_emb_expedicao; contrato de adesão NU-2021-0342", "Análise documental", "Anual", "Conforme", "Médio", "LEG-16", "", F_FIN, "",
     "Complementado", "Definido o papel concreto: embalador das embalagens de expedição; não é produtor das embalagens que vende vazias aos embaladores.", "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2017-114337039"),
    ("PT-002", "PT — nacional", "DL 152-D/2017 — capítulo das embalagens", "Arts. 22.º–29.º (confirmar numeração consolidada)", "Resíduos de embalagens recebidos",
     "Gerir os resíduos de embalagens das matérias-primas (big bags, filme, cartão, paletes) através de operadores licenciados.",
     "Obrigação legal", "Utilizador final de embalagens não urbanas", "Empresa", "Empresa", "2018-01-01", "Sim",
     "RG-SGA-13 tbl_residuos (15 01 01/02/03); RG-SGA-04 LEG-01", "Análise documental", "Anual", "Conforme", "Baixo", "LEG-01", "", F_LOG, "", "Confirmado", "", ""),
    ("PT-003", "PT — nacional", "DL 152-D/2017 / contrato com a entidade gestora", "Declarações periódicas", "Declaração de embalagens colocadas no mercado",
     "Declarar à entidade gestora as quantidades de embalagens de expedição colocadas no mercado nacional e pagar a prestação financeira.",
     "Obrigação legal", "Embalador", "Empresa", "Expedição", "2018-01-01", "Sim",
     "RG-SGA-20 tbl_emb_expedicao; RG-SGA-04 OBR-15", "Análise documental", "Anual", "Conforme", "Médio", "LEG-16", "", F_FIN, "2027-02-28", "Complementado", "", ""),
    ("PT-004", "PT — nacional", "Vigilância legislativa (DRE, APA, EUR-Lex)", "—", "Alterações legislativas",
     "Acompanhar a adaptação nacional ao PPWR e os atos delegados/de execução (DfR, reciclado, rotulagem).",
     "Obrigação legal", "Organização", "Empresa", "Empresa", "2026-08-12", "Sim",
     "RG-SGA-04 (vigilância mensal EUR-Lex — PAM-26-10)", "Análise documental", "Mensal", "Parcial", "Médio", "LEG-09", "PAM-26-10", F_SGA, "", "Confirmado", "", ""),
    ("PT-005", "PT — nacional", "Lei 76/2019 e Portaria 331-E/2021 (contribuição sobre embalagens de utilização única)", "—", "Contribuição take-away",
     "Contribuição sobre embalagens de plástico/alumínio de refeições prontas (take-away).", "Obrigação legal", "—", "Empresa", "Nenhum", "2022-07-01", "Não",
     "Carteira de produtos (sem embalagens de take-away)", "Análise documental", "Anual", "Não aplicável", "Baixo", "", "", F_SGA, "", "Adicionado", "Confirmar se algum cliente alimentar usa potes para refeições prontas.", ""),
    ("PT-006", "PT — nacional", "DL 78/2021 (transposição da Diretiva SUP)", "—", "Plásticos de utilização única (PT)", "Ver EU-ENV-007.", "Necessita verificação", "Fabricante de tampas", "Empresa", "Alimentar", "2021-08-24", "Condicional",
     "Ver EU-ENV-007", "Declaração do cliente", "Por ocorrência", "Conforme", "Médio", "LEG-19", "PAM-26-26", F_RD, "2026-11-30", "Adicionado", "Declarações de 04/12/2026: FA-030/031 não usados para bebidas.", ""),
]
REQ_COLS = ["ID_Req", "Grupo", "Fonte", "Artigo_Anexo", "Tema", "Requisito", "Natureza_Obrigacao", "Papel_Plasticom", "Nivel", "Ambito_Produtos",
            "Data_Aplicacao", "Aplicabilidade", "Evidencia_SGA", "Metodo_Verificacao", "Frequencia", "Estado", "Risco", "ID_Legal", "ID_PAM",
            "Responsavel", "Prazo", "Verificacao_ChatGPT", "Nota_Verificacao", "Fonte_Oficial"]
REQ_PRODUTO = [r[0] for r in REQ if r[8] == "Produto"]


def _aplica(req, r):
    """(Aplicável, motivo, estado base, evidência) para produto × requisito."""
    amb, seg = req[9], r["Segmento"]
    iid = req[0]
    if amb == "Todos":
        ok = True
    elif amb == "Alimentar":
        ok = seg == "Alimentar"
    elif amb == "Farmacêutico":
        ok = seg == "Farmacêutico"
    elif amb == "Cosmética":
        ok = seg.startswith("Cosm")
    else:
        ok = False
    if iid == "PHAR-003":
        ok = seg == "Farmacêutico" and r["ID_Tampa"].startswith("TE-")
    motivo = f"Segmento {seg}" + ("" if ok else f" — requisito só para '{amb}'")
    if iid == "PHAR-003" and seg == "Farmacêutico" and not ok:
        motivo = "Pote farmacêutico sem tampa de selo de garantia"
    base = req[15] if ok else "Não aplicável"
    if iid == "EU-ENV-007" and ok:
        motivo = "Frasco alimentar de 0,5–1 L: confirmar se é usado para bebidas (tampas presas)"
    return ("Sim" if ok else "Não"), motivo, base, req[12] if ok else ""


# ------------------------------------------------------------------ outros conteúdos
PAISES_REQ = [
    # (ID, código país, tema, requisito, papel Plasticom, informação a fornecer, autoridade, fonte, natureza, estado)
    ("PAIS-01", "PT", "RAP embalagens", "SIGRE: clientes embaladores aderem a entidade gestora (SPV, Novo Verde, Electrão) pelas embalagens que enchem.", "Fornecedor dos clientes embaladores", "Massa e material por SKU (tbl_recyclass)", "APA / IGAMAOT", "DL 152-D/2017", "Obrigação legal", "Conforme"),
    ("PAIS-02", "PT", "RAP expedição", "A Plasticom declara as embalagens de expedição (cartão, filme, paletes) colocadas no mercado nacional.", "Embalador", "tbl_emb_expedicao", "APA", "DL 152-D/2017", "Obrigação legal", "Conforme"),
    ("PAIS-03", "ES", "RAP embalagens", "RD 1055/2022: produtores de produto (clientes) inscritos no Registo de Produtores; embalagens comerciais/industriais com RAP desde 2025.", "Fornecedor intracomunitário", "Massa e material por SKU; reciclabilidade", "MITECO / CCAA", "Real Decreto 1055/2022", "Obrigação legal", "Em avaliação"),
    ("PAIS-04", "ES", "Imposto sobre plástico", "Imposto especial de 0,45 €/kg sobre plástico não reciclado de embalagens não reutilizáveis; na aquisição intracomunitária paga o adquirente espanhol, que precisa do certificado de reciclado (EN 15343).", "Fornecedor intracomunitário", "Massa de plástico, % reciclado certificado por fatura", "AEAT", "Ley 7/2022, arts. 67.º–83.º", "Requisito contratual", "Parcial"),
    ("PAIS-05", "FR", "Rotulagem Triman / Info-tri", "Embalagens domésticas com logótipo Triman e instruções de triagem (responsabilidade do produtor — cliente).", "Fornecedor", "Material e componentes separáveis", "Ministère de la Transition Écologique / ADEME", "Lei AGEC 2020-105; Decreto 2021-835", "Requisito contratual", "Conforme"),
    ("PAIS-06", "FR", "Óleos minerais nas tintas", "Proibição de óleos minerais (MOSH/MOAH) em tintas de impressão de embalagens.", "Decorador (serigrafia/hot foil)", "Declaração das tintas SS-001/002 sem óleos minerais", "DGCCRF", "Lei AGEC, art. 112.º; Decreto 2020-1725", "Necessita verificação", "Em avaliação"),
    ("PAIS-07", "FR", "Alegações ambientais", "Proibidas alegações 'biodegradável', 'respeitador do ambiente' em embalagens.", "Autor de comunicações", "tbl_alegacoes", "DGCCRF", "Lei AGEC, art. 13.º", "Obrigação legal", "Parcial"),
    ("PAIS-08", "IT", "Rotulagem ambiental", "Rotulagem obrigatória com código de material (Decisão 97/129/CE); no B2B pode ir nos documentos de acompanhamento.", "Fabricante (código no molde ou documento)", "Código alfanumérico do material (tbl_materiais)", "Ministero dell'Ambiente", "D.Lgs. 116/2020, art. 219.º, n.º 5", "Obrigação legal", "Parcial"),
    ("PAIS-09", "IT", "CONAI", "Contributo ambiental CONAI declarado pelo cliente importador (procedimento de importação).", "Fornecedor estrangeiro", "Massa por material por fatura", "CONAI", "D.Lgs. 152/2006", "Requisito contratual", "Conforme"),
    ("PAIS-10", "IT", "Plastic tax", "Imposto sobre embalagens de plástico de utilização única (sucessivamente adiado).", "Fornecedor", "Massa de plástico e % reciclado", "Agenzia delle Dogane", "Lei 160/2019", "Necessita verificação", "Em avaliação"),
    ("PAIS-11", "DE", "VerpackG / LUCID", "Registo LUCID e participação num sistema pelo 'Hersteller' (cliente que enche); modulação pelo padrão mínimo de reciclabilidade (§ 21).", "Fornecedor", "Classe de reciclabilidade por SKU", "ZSVR", "Verpackungsgesetz, §§ 7, 9, 21", "Requisito contratual", "Parcial"),
    ("PAIS-12", "PL", "Embalagens / BDO", "Registo BDO e taxa de produto pelo introdutor (cliente).", "Fornecedor", "Massa e material", "Marszałek województwa", "Lei de 13/06/2013 sobre gestão de embalagens", "Requisito contratual", "Conforme"),
]
CERTS = [
    ("CERT-01", "SUP-002", "PP-PCR", "RecyClass Recycled Plastics Traceability", "RC-RPT-2025-1187", "EN 15343", 0.30, "Pós-consumo", "2025-04-01", "2027-03-31", "Não", ""),
    ("CERT-02", "SUP-004", "HDPE-PCR", "EuCertPlast", "ECP-UK-0452-R1", "EN 15343", 0.30, "Pós-consumo", "2026-12-10", "2028-12-09", "Não", "Renovado em 10/12/2026 (pedido de 09/2026)."),
    ("CERT-03", "SUP-004", "rPET", "EuCertPlast", "ECP-UK-0453-R1", "EN 15343", 0.50, "Pós-consumo", "2026-11-20", "2028-11-19", "Não", "Renovado em 20/11/2026 (PAM-26-25); os lotes de jul–nov/2026 sem certificado contam como polímero virgem."),
    ("CERT-04", "SUP-010", "PP-FG / HDPE-FG (reciclado químico)", "ISCC PLUS (balanço de massa)", "", "ISO 22095 (balanço de massa)", None, "Pós-consumo (químico)", "", "", "Sim (processo autorizado — confirmar)", "Em negociação para cumprir a meta de 10% em alimentar (2030)."),
]
ALEG = [
    ("ALG-01", "Frascos 100% recicláveis", "Reciclabilidade", "Todos os frascos", "Site e catálogo", "ISO 14021 § 7.7; Diretiva 2024/825", "Contrariado pela autoavaliação: PVC, PETG e preto de carbono são classe F", "Retirar", "2026-09-22", "2026-09-27", F_DG, "PAM-26-27"),
    ("ALG-02", "Embalagens eco-friendly / amigas do ambiente", "Genérica", "Portfólio", "Site", "Diretiva 2024/825 (anexo I, ponto 4-A)", "Sem desempenho ambiental excelente reconhecido", "Proibida", "2026-09-22", "2026-09-27", F_DG, "PAM-26-27"),
    ("ALG-03", "Contém 30% de PP reciclado pós-consumo", "Conteúdo reciclado", "SKUs PP-PCR", "Fichas técnicas", "ISO 14021 § 7.8; EN 15343", "CERT-01 válido; balanço de massa por lote", "Aprovada", "2026-09-22", "2027-03-31", F_RD, ""),
    ("ALG-04", "Contém 30% de HDPE reciclado pós-consumo", "Conteúdo reciclado", "SKUs HDPE-PCR", "Fichas técnicas", "ISO 14021 § 7.8; EN 15343", "CERT-02 renovado, válido até 09/12/2028", "Aprovada", "2026-12-10", "2027-06-10", F_RD, "PAM-26-25"),
    ("ALG-05", "Feito com 50% de rPET", "Conteúdo reciclado", "SKUs rPET", "Fichas técnicas e catálogo", "ISO 14021 § 7.8; EN 15343", "CERT-03 expirado em 30/06/2026", "Suspensa", "2026-09-22", "2026-10-31", F_CMP, "PAM-26-25"),
    ("ALG-06", "Reciclável — classe A RecyClass (autoavaliação), onde existam sistemas de recolha", "Reciclabilidade", "SKUs com classe A", "Fichas técnicas", "ISO 14021 § 7.7; RecyClass", "tbl_recyclass (autoavaliação); falta certificação para usar o logótipo", "Em revisão", "2026-09-22", "2027-03-31", F_RD, "PAM-26-24"),
    ("ALG-07", "Pegada de carbono −35% face ao material virgem", "Pegada de carbono", "SKUs com PCR", "Propostas comerciais", "ISO 14067; Diretiva 2024/825", "Pegada simplificada (RG-SGA-19) não verificada", "Em revisão", "2026-09-22", "2027-06-30", F_SGA, ""),
    ("ALG-08", "Embalagem neutra em carbono", "Neutralidade carbónica", "Nenhum", "—", "Diretiva 2024/825 (compensações)", "Baseada em compensações — proibida", "Proibida", "2026-09-22", "2026-09-27", F_DG, "PAM-26-27"),
    ("ALG-09", "Monomaterial: frasco, tampa e rótulo em poliolefinas", "Reciclabilidade", "SKUs PE/PP com tampa e rótulo PE/PP", "Fichas técnicas", "ISO 14021 § 5.7", "tbl_recyclass (Estrutura_Material)", "Aprovada", "2026-09-22", "2027-09-22", F_RD, ""),
    ("ALG-10", "Sem PFAS adicionados", "Substâncias", "Linha alimentar", "Fichas técnicas", "PPWR art. 5.º, n.º 5", "Declaração SUP-010 (07/2026) + flúor total < 50 ppm", "Aprovada", "2026-09-22", "2027-08-12", F_QUA, ""),
]
MATURIDADE = [
    ("MAT-01", "Inventário de produtos e materiais concluído", "Implementado", "RG-SGA-20 tbl_recyclass (113 SKUs), tbl_tampas (36), tbl_materiais (14)", ""),
    ("MAT-02", "Aplicação de cada produto classificada por setor", "Implementado", "tbl_recyclass[Segmento], [Contacto]", ""),
    ("MAT-03", "Papel jurídico da Plasticom definido", "Implementado", "tbl_requisitos_emb[Papel_Plasticom]; RG-SGA-04 tbl_legal[Papel_Plasticom]", ""),
    ("MAT-04", "PPWR avaliado por categoria de embalagem", "Parcial", "tbl_familias_ppwr — declaração UE em 17 de 22 famílias (faltam PP-PG e PET-PG farmacêuticas; PETG e PVC em substituição)", "PAM-26-10"),
    ("MAT-05", "Critérios de reciclabilidade definidos e documentados", "Parcial", "tbl_regras_dfr (regras RecyClass simplificadas); atos delegados do PPWR por publicar", "PAM-26-24"),
    ("MAT-06", "Requisitos de conteúdo reciclado avaliados", "Implementado", "tbl_metas_art7; tbl_recyclass[Gap_2030]; tbl_certificados_pcr", ""),
    ("MAT-07", "Contacto alimentar avaliado quando aplicável", "Implementado", "tbl_aplicabilidade FCM-001 a 003; RG-SGA-04 LEG-17", ""),
    ("MAT-08", "Requisitos de cosméticos avaliados quando aplicável", "Implementado", "tbl_aplicabilidade COS-001, 002, 004; LEG-20", ""),
    ("MAT-09", "Requisitos farmacêuticos avaliados quando aplicável", "Parcial", "PHAR-001 a 006; falta DMF do PET-PG (PHAR-005)", ""),
    ("MAT-10", "Legislação portuguesa identificada e validada", "Implementado", "PT-001 a 006; RG-SGA-04 LEG-01, LEG-13, LEG-16", ""),
    ("MAT-11", "Países de destino com obrigações nacionais mapeados", "Parcial", "tbl_requisitos_pais (6 países; 3 itens por verificar)", "PAM-26-26"),
    ("MAT-12", "Normas ISO/EN classificadas por natureza da obrigação", "Implementado", "tbl_requisitos_emb[Natureza_Obrigacao] (ISO-001 a 014)", ""),
    ("MAT-13", "Responsáveis por requisito definidos", "Implementado", "tbl_requisitos_emb[Responsavel]; RG-SGA-08 tbl_raci (PS-23 a PS-27)", ""),
    ("MAT-14", "Evidências de auditoria identificadas", "Implementado", "tbl_requisitos_emb[Evidencia_SGA]; tbl_aplicabilidade[Evidencia]", ""),
    ("MAT-15", "KPIs definidos e com origem de dados", "Implementado", "RG-SGA-05 KPI-17 a KPI-21; Painel", ""),
    ("MAT-16", "Periodicidade de revisão legal definida", "Implementado", "tbl_requisitos_emb[Frequencia]; RG-SGA-04 OBR-16", ""),
]


# ------------------------------------------------------------------ construção
def build(out):
    rows, caps, s12 = produtos()
    b = Book("RG-SGA-20", "Reciclabilidade e Conformidade de Embalagens (RecyClass / PPWR)", version="00", date=dt.date(2026, 9, 24),
             activities="Complemento — reciclagem e reciclabilidade de embalagens: classificação RecyClass por SKU, graus PPWR, conteúdo reciclado, matriz legal e normativa de produto, países de destino e alegações.",
             clauses="4.3 e) e 6.1.2 (perspetiva de ciclo de vida); 6.1.3 e 9.1.2 (obrigações de conformidade de produto); 8.1 (conceção e requisitos para fornecedores); 7.4 (alegações)",
             purpose="Registo de conformidade de produto das embalagens da Plasticom. A folha Avaliacao_RecyClass tem uma linha por SKU com todos os campos a introduzir na ferramenta online da RecyClass e calcula a classe (A–F), a taxa de reciclabilidade em massa e o grau PPWR indicativo com as regras de tbl_regras_dfr. Liga cada SKU aos requisitos legais aplicáveis (tbl_aplicabilidade), às famílias com declaração UE (tbl_familias_ppwr), aos certificados de reciclado e às vendas por país. A classificação é uma AUTOAVALIAÇÃO com regras simplificadas: o resultado oficial só vem da ferramenta RecyClass / certificação e dos atos delegados do PPWR (critérios de DfR previstos até 2028).",
             links=[("RG-SGA-04 Legal", "ID_Legal liga os requisitos a tbl_legal (LEG-09, LEG-16 a LEG-21)."),
                    ("RG-SGA-05 KPI", "KPI-12 e KPI-17 a KPI-21 são calculados a partir deste registo."),
                    ("RG-SGA-06 PAM", "Ações PAM-26-10 e PAM-26-22 a PAM-26-27."),
                    ("RG-SGA-11 Fornecedores", "tbl_certificados_pcr[ID_Fornecedor] → tbl_fornecedores."),
                    ("RG-SGA-17 / RG-SGA-19", "Evidências do tema DM-11 e indicador ESG-E29 (produtos recicláveis)."),
                    ("Dataset", "Produtos, cores, masterbatch, decoração e vendas: datasets/silver (dim_bottle, dim_cap, dim_ink, fact_production, fact_sales).")])
    b.add_list("Material", [m[0] for m in MATERIAIS])
    b.add_list("CorCorpo", CORES)
    b.add_list("Barreira", LISTA["Barreira / revestimento"])
    b.add_list("Vedante", LISTA["Vedante / liner"])
    b.add_list("Rotulo", LISTA["Tipo de rótulo"])
    b.add_list("Adesivo", LISTA["Adesivo do rótulo"])
    b.add_list("Decoracao", ["Nenhuma", "Serigrafia", "Hot foil metalizado", "Impressão de lote/data"])
    b.add_list("Segmento", ["Cosmética e higiene pessoal", "Alimentar", "Farmacêutico"])
    b.add_list("Classe", CLS)
    b.add_list("Natureza", ["Obrigação legal", "Norma técnica de suporte", "Requisito contratual", "Norma voluntária", "Necessita verificação"])
    b.add_list("Aplicabilidade", ["Sim", "Condicional", "Não", "Futuro"])
    b.add_list("EstadoReq", ["Conforme", "Parcial", "Lacuna", "Em avaliação", "Futuro", "Não aplicável"])
    b.add_list("Risco", ["Alto", "Médio", "Baixo"])
    b.add_list("Verificacao", ["Confirmado", "Complementado", "Corrigido", "Adicionado"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("EstadoAlegacao", ["Aprovada", "Em revisão", "Suspensa", "Retirar", "Proibida"])
    b.add_list("Maturidade", ["Implementado", "Parcial", "Lacuna"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("EstadoAval", ["Autoavaliação (não certificada)", "Carta de compatibilidade RecyClass", "Certificado RecyClass"])

    # ---- parâmetros e metas
    b.table("Parametros", "tbl_param_emb",
            [col("ID_Parametro", 9, desc="Identificador.", key="PK"), col("Parametro", 60, desc="Parâmetro."), col("Valor", 10, "num3", desc="Valor (editável)."),
             col("Unidade", 22, desc="Unidade."), col("Fonte", 60, desc="Fonte / pressuposto.")],
            [dict(zip(["ID_Parametro", "Parametro", "Valor", "Unidade", "Fonte"], p)) for p in PARAM],
            "Parâmetros dos cálculos (limiares PPWR, massas de rótulo e decoração, logística, imposto espanhol, prestações RAP indicativas).",
            title="PARÂMETROS DE CÁLCULO", subtitle="Editar a coluna Valor; as fórmulas das outras folhas atualizam-se", row_height=18)
    ws = b.tables["tbl_param_emb"]["ws"]
    r0 = b.tables["tbl_param_emb"]["last"] + 3
    ws.cell(row=r0 - 1, column=1, value="Metas de teor mínimo de plástico reciclado — PPWR art. 7.º (tabela tbl_metas_art7 na folha Metas_Art7)").font = F_BOLD
    b.table("Metas_Art7", "tbl_metas_art7",
            [col("Categoria_Art7", 40, desc="Categoria de embalagem do art. 7.º.", key="PK"), col("Meta_2030", 10, "pct", desc="Teor mínimo a partir de 01/01/2030.", req=False),
             col("Meta_2040", 10, "pct", desc="Teor mínimo a partir de 01/01/2040.", req=False), col("Base_Legal", 36, desc="Alínea do art. 7.º."), col("Nota", 70, desc="Nota de aplicação.")],
            [dict(zip(["Categoria_Art7", "Meta_2030", "Meta_2040", "Base_Legal", "Nota"], m)) for m in METAS7],
            "Metas de conteúdo reciclado do PPWR por categoria (média por instalação de fabrico e por ano).", row_height=30)

    # ---- materiais
    mcols = [col("Material", 10, desc="Material (dataset).", key="PK"), col("Polimero_Base", 9, desc="Polímero para a regra de DfR."),
             col("Fluxo_Reciclagem", 22, desc="Fluxo de triagem/reciclagem europeu."), col("Densidade_g_cm3", 9, "num3", desc="Densidade típica do polímero."),
             col("Grau", 22, desc="Virgem, reciclado, alimentar, farmacêutico."), col("Pct_PCR", 8, "pct", desc="Teor de reciclado pós-consumo do grau comprado (certificado)."),
             col("Codigo_Identificacao", 14, desc="Marcação ISO 1043-1 / ISO 11469 e código da Decisão 97/129/CE."),
             col("ID_Fornecedor", 10, desc="Fornecedor principal.", key="FK → RG-SGA-11"),
             col("N_SKUs_Corpo", 9, "int", f='=COUNTIF(tbl_recyclass[Material_Corpo],@Material@)', desc="SKUs com este material no corpo."),
             col("Massa_Vendida_kg", 11, "num0", f='=SUMIFS(tbl_recyclass[Massa_Vendida_kg],tbl_recyclass[Material_Corpo],@Material@)', desc="Massa de corpos vendida (12 meses).")]
    b.table("Materiais", "tbl_materiais", mcols,
            [dict(zip(["Material", "Polimero_Base", "Fluxo_Reciclagem", "Densidade_g_cm3", "Grau", "Pct_PCR", "Codigo_Identificacao", "ID_Fornecedor"], m)) for m in MATERIAIS],
            "Dimensão material: polímero, fluxo de reciclagem, densidade, teor de reciclado e marcação.", row_height=18)

    # ---- regras DfR
    rcols = [col("Chave", 40, f='=@Fluxo@&"|"&@Caracteristica@&"|"&@Valor@', desc="Chave de pesquisa (fluxo|característica|valor).", key="PK"),
             col("Fluxo", 20, desc="Fluxo de reciclagem do corpo."), col("Caracteristica", 22, desc="Característica avaliada (campo da ferramenta RecyClass)."),
             col("Valor", 30, desc="Opção escolhida."), col("Classe", 7, dv="Classe", desc="Classe de reciclabilidade A–F atribuída."),
             col("Compatibilidade", 26, f='=CHOOSE(MATCH(@Classe@,{"A","B","C","D","E","F"},0),"Totalmente compatível","Compatibilidade limitada","Compatibilidade limitada (afeta a qualidade)","Problemas significativos","Problemas graves","Não reciclável / não compatível")',
                 desc="Leitura da classe."),
             col("Fracao_Reciclavel", 9, "pct", desc="Fração da massa do componente que acaba em reciclado (1 = reciclado; 0 = perdido)."),
             col("Fundamentacao", 60, desc="Porquê (processo de triagem/lavagem/extrusão)."), col("Recomendacao", 50, desc="Ação de design para melhorar.")]
    b.table("Regras_DfR", "tbl_regras_dfr", rcols,
            [dict(Fluxo=r[0], Caracteristica=r[1], Valor=r[2], Classe=r[3], Fracao_Reciclavel=r[4], Fundamentacao=r[5], Recomendacao=r[6]) for r in R_],
            "Regras de design para reciclagem (interpretação simplificada das diretrizes RecyClass para PE/PP rígidos e garrafas de PET).",
            title="REGRAS DE DESIGN PARA RECICLAGEM (DfR) — BASE DO CÁLCULO RECYCLASS",
            subtitle="Interpretação simplificada das diretrizes RecyClass (HDPE/PP containers, PET bottles) · Classe final = pior característica · Editar Classe/Fração para recalibrar",
            cf=[("Classe", {"A": "green", "B": "blue", "C": "yellow", "D": "orange", "F": "red"})], row_height=30, freeze_col=1)

    # ---- tampas
    tcols = [col("CapId", 22, desc="Tampa (dataset).", key="PK"), col("Descricao", 34, desc="Descrição."), col("Tipo_Abertura", 16, desc="Tipo de abertura."),
             col("Material", 9, dv="Material", desc="Material."), col("Polimero_Base", 8, f='=IFERROR(INDEX(tbl_materiais[Polimero_Base],MATCH(@Material@,tbl_materiais[Material],0)),"")', desc="Polímero."),
             col("Massa_g", 8, "num1", desc="Massa (média mín./máx. da especificação)."), col("Densidade_g_cm3", 9, "num3", f='=IFERROR(INDEX(tbl_materiais[Densidade_g_cm3],MATCH(@Material@,tbl_materiais[Material],0)),"")', desc="Densidade."),
             col("Flutua_Agua", 8, f='=IF(@Densidade_g_cm3@="","",IF(@Densidade_g_cm3@<1,"Sim","Não"))', desc="Flutua no afunda-flutua (separação do PET)."),
             col("Rosca", 9, desc="Acabamento de rosca."), col("Vedante", 14, dv="Vedante", desc="Vedante/liner."),
             col("Pct_PCR", 8, "pct", f='=IFERROR(INDEX(tbl_materiais[Pct_PCR],MATCH(@Material@,tbl_materiais[Material],0)),0)', desc="Teor de reciclado."),
             col("Familia_PPWR", 9, desc="Família PPWR.", key="FK → tbl_familias_ppwr"),
             col("Unid_Vendidas_P12", 11, "num0", desc="Unidades vendidas (ano civil de 2026)."), col("Paises_Venda", 18, desc="Países de destino."),
             col("Massa_Vendida_kg", 10, "num0", f='=@Unid_Vendidas_P12@*@Massa_g@/1000', desc="Massa vendida (kg).")]
    b.table("Tampas", "tbl_tampas", tcols, caps, "Componentes de fecho (tampas) com material, massa e comportamento na reciclagem.", row_height=18)

    # ---- avaliação RecyClass
    def lk(car, val, what="Classe"):
        key = f'@Fluxo_Reciclagem@&"|{car}|"&{val}'
        return f'INDEX(tbl_regras_dfr[{what}],MATCH({key},tbl_regras_dfr[Chave],0))'

    feat_cols = []
    for cname, car, val, _k in FEAT:
        if cname == "Classe_Fluxo":
            f = f'=IFERROR({lk(car, val)},"Sem regra")'
        else:
            f = f'=IF(LEFT(@Fluxo_Reciclagem@,9)="Sem fluxo","—",IFERROR({lk(car, val)},"Sem regra"))'
        feat_cols.append(col(cname, 8, f=f, desc=f"Classe da característica '{car}' (tbl_regras_dfr)."))
    first_c, last_c = FEAT[0][0], FEAT[-1][0]
    rng = f"@{first_c}@:@{last_c}@"
    nmax = "=IF(COUNTIF(" + rng + ',"F"),6,IF(COUNTIF(' + rng + ',"E"),5,IF(COUNTIF(' + rng + ',"D"),4,IF(COUNTIF(' + rng + ',"C"),3,IF(COUNTIF(' + rng + ',"B"),2,IF(COUNTIF(' + rng + ',"A"),1,0))))))'
    keys = ",".join(f'@Fluxo_Reciclagem@&"|{car}|"&{val}' for _c, car, val, _k in FEAT)
    frac = lambda car, val: f'IFERROR({lk(car, val, "Fracao_Reciclavel")},0)'
    acols = [
        col("ID_Avaliacao", 9, desc="Identificador da avaliação.", key="PK"), col("ProductId", 22, desc="SKU (dataset).", key="FK → dataset"),
        col("Formato", 8, desc="Frasco ou pote."), col("Segmento", 20, dv="Segmento", desc="Setor de aplicação."), col("Contacto", 26, desc="Tipo de contacto com o conteúdo."),
        col("Processo_Fabrico", 16, desc="Processo."), col("Familia_PPWR", 9, desc="Família PPWR (declaração UE).", key="FK → tbl_familias_ppwr"),
        col("Volume_ml", 8, "num0", desc="Volume nominal."), col("Dimensao_Max_mm", 9, "num0", desc="Maior dimensão estimada (triagem por tamanho: < 50 mm em 2 dimensões é crítico)."),
        # 1. corpo
        col("Material_Corpo", 10, dv="Material", desc="[RecyClass: corpo — polímero] Material do corpo."),
        col("Polimero_Corpo", 8, f='=IFERROR(INDEX(tbl_materiais[Polimero_Base],MATCH(@Material_Corpo@,tbl_materiais[Material],0)),"")', desc="Polímero base."),
        col("Fluxo_Reciclagem", 20, f='=IFERROR(INDEX(tbl_materiais[Fluxo_Reciclagem],MATCH(@Material_Corpo@,tbl_materiais[Material],0)),"")', desc="Fluxo europeu de reciclagem."),
        col("Categoria_RecyClass", 34, f=('=IF(@Fluxo_Reciclagem@="PE rígido","PE rígido — frascos e contentores (HDPE/LDPE)",IF(@Fluxo_Reciclagem@="PP rígido","PP rígido — frascos, potes e contentores",'
                                          'IF(@Fluxo_Reciclagem@="PET frascos e garrafas",IF(@Cor_Corpo@="Natural / incolor","PET — garrafas/frascos transparentes incolores","PET — garrafas/frascos coloridos ou opacos"),'
                                          '"Sem categoria RecyClass ("&@Polimero_Corpo@&")")))'), desc="[RecyClass: 1.º passo] Categoria de embalagem a escolher na ferramenta."),
        col("Cor_Dataset", 16, desc="Cor no dataset."), col("Cor_Corpo", 22, dv="CorCorpo", desc="[RecyClass: cor/transparência do corpo]."),
        col("Masterbatch_Tipo", 20, desc="Masterbatch (dataset)."), col("Masterbatch_Pct", 8, "pct", desc="Dosagem de masterbatch (fração)."),
        col("Densidade_Corpo_g_cm3", 9, "num3", f='=IFERROR(ROUND(INDEX(tbl_materiais[Densidade_g_cm3],MATCH(@Material_Corpo@,tbl_materiais[Material],0))+@Masterbatch_Pct@*1.2,3),"")',
            desc="[RecyClass: densidade] Polímero + efeito do masterbatch (estimativa)."),
        col("Barreira_Revestimento", 20, dv="Barreira", desc="[RecyClass: barreira/revestimento]."),
        col("Massa_Corpo_g", 8, "num1", desc="Massa do corpo (g)."), col("Origem_Massa", 22, desc="Medida ou estimada."),
        # 2. tampa
        col("ID_Tampa", 22, dv="=" + "Tampas!$A$2:$A$" + str(1 + len(caps)), desc="[RecyClass: fecho] Tampa de referência do sistema.", key="FK → tbl_tampas"),
        col("Material_Tampa", 9, f='=IF(@ID_Tampa@="","",IFERROR(INDEX(tbl_tampas[Material],MATCH(@ID_Tampa@,tbl_tampas[CapId],0)),""))', desc="Material da tampa."),
        col("Polimero_Tampa", 8, f='=IF(@ID_Tampa@="","Sem tampa",IFERROR(INDEX(tbl_materiais[Polimero_Base],MATCH(@Material_Tampa@,tbl_materiais[Material],0)),""))', desc="Polímero da tampa."),
        col("Massa_Tampa_g", 8, "num1", f='=IF(@ID_Tampa@="",0,IFERROR(INDEX(tbl_tampas[Massa_g],MATCH(@ID_Tampa@,tbl_tampas[CapId],0)),0))', desc="Massa da tampa."),
        col("Vedante_Tampa", 14, dv="Vedante", desc="[RecyClass: vedante/liner/válvula]."),
        # 3. rótulo
        col("Rotulo_Tipo", 20, dv="Rotulo", desc="[RecyClass: rótulo/manga] Tipo de rótulo."),
        col("Rotulo_Adesivo", 20, dv="Adesivo", desc="[RecyClass: adesivo] Adesivo do rótulo."),
        col("Rotulo_Cobertura_Pct", 8, "pct", desc="[RecyClass: cobertura] Fração da superfície coberta."),
        col("Massa_Rotulo_g", 8, "num3", desc="Massa do rótulo (área × cobertura × gramagem)."), col("Origem_Rotulo", 28, desc="Origem dos dados do rótulo."),
        # 4. decoração
        col("Decoracao_Tipo", 16, dv="Decoracao", desc="[RecyClass: impressão direta/metalização] Decoração direta (dataset)."),
        col("Decoracao_N_Cores", 7, "int", desc="N.º de cores de serigrafia (dim_ink)."),
        col("Decoracao_Valor", 18, f='=IF(@Decoracao_Tipo@="Serigrafia",IF(@Decoracao_N_Cores@>=3,"Serigrafia ≥ 3 cores","Serigrafia 1–2 cores"),@Decoracao_Tipo@)', desc="Opção de decoração para a regra."),
        col("Massa_Decoracao_g", 8, "num3", desc="Tinta ou metalização depositada (g)."),
        # resultado
        *feat_cols,
        col("Classe_N_Max", 7, "int", f=nmax, desc="Pior classe (1 = A … 6 = F)."),
        col("Classe_RecyClass", 8, f='=IF(@Classe_N_Max@=0,"",INDEX({"A","B","C","D","E","F"},@Classe_N_Max@))', desc="Classe de reciclabilidade (pior característica)."),
        col("Regras_em_Falta", 7, "int", f=f'=COUNTIF({rng},"Sem regra")', desc="Características sem regra (rever tbl_regras_dfr)."),
        col("Ponto_Critico", 16, f=f'=IF(OR(@Classe_RecyClass@="",@Classe_RecyClass@="A"),"—",SUBSTITUTE(INDEX($X$4:$Y$4,MATCH(@Classe_RecyClass@,{rng},0)),"Classe_",""))',
            desc="Característica que determina a classe."),
        col("Recomendacao", 44, f=f'=IF(@Classe_RecyClass@="A","Sem ação — manter o design.",IFERROR(INDEX(tbl_regras_dfr[Recomendacao],MATCH(CHOOSE(MATCH(@Classe_RecyClass@,{rng},0),{keys}),tbl_regras_dfr[Chave],0)),""))',
            desc="Ação de design para subir de classe."),
        col("Massa_Total_g", 8, "num1", f='=@Massa_Corpo_g@+@Massa_Tampa_g@+@Massa_Rotulo_g@+@Massa_Decoracao_g@', desc="Massa da unidade de embalagem."),
        col("Frac_Corpo", 7, "pct", f=f'=MIN({frac("Fluxo de reciclagem", "@Fluxo_Reciclagem@")},{frac("Cor do corpo", "@Cor_Corpo@")})', desc="Fração do corpo reciclada."),
        col("Frac_Tampa", 7, "pct", f=f'={frac("Material da tampa", "@Polimero_Tampa@")}', desc="Fração da tampa reciclada."),
        col("Frac_Rotulo", 7, "pct", f=f'={frac("Tipo de rótulo", "@Rotulo_Tipo@")}', desc="Fração do rótulo reciclada."),
        col("Massa_Reciclavel_g", 8, "num1", f='=@Frac_Corpo@*(@Massa_Corpo_g@+@Massa_Tampa_g@*@Frac_Tampa@+@Massa_Rotulo_g@*@Frac_Rotulo@)', desc="Massa que acaba em reciclado."),
        col("Taxa_Reciclabilidade", 8, "pct1", f='=IFERROR(@Massa_Reciclavel_g@/@Massa_Total_g@,0)', desc="Taxa de reciclabilidade em massa (sem perdas de processo)."),
        col("Grau_Taxa", 8, f=f'=IF(@Taxa_Reciclabilidade@>={_p("P-06")},"A",IF(@Taxa_Reciclabilidade@>={_p("P-07")},"B",IF(@Taxa_Reciclabilidade@>={_p("P-08")},"C","< 70%")))', desc="Grau pela taxa (anexo II do PPWR)."),
        col("Grau_PPWR_Indicativo", 12, f=('=IF(@Classe_RecyClass@="F","Não reciclável (F)",INDEX({"A","B","C","Abaixo de C"},MAX(MIN(@Classe_N_Max@,4),'
                                           'IF(@Grau_Taxa@="A",1,IF(@Grau_Taxa@="B",2,IF(@Grau_Taxa@="C",3,4))))))'), desc="Pior entre a classe RecyClass (A→A, B→B, C→C, D/E→abaixo de C) e o grau pela taxa."),
        col("Isencao_Art6", 16, f='=IF(@Segmento@="Farmacêutico","Isento até 2035","—")', desc="Isenção da reciclabilidade (embalagem imediata de medicamento)."),
        col("Conforme_PPWR_2030", 12, f='=IF(@Isencao_Art6@<>"—",@Isencao_Art6@,IF(OR(@Grau_PPWR_Indicativo@="A",@Grau_PPWR_Indicativo@="B",@Grau_PPWR_Indicativo@="C"),"Sim","Não"))', desc="Graus A–C a partir de 2030."),
        col("Conforme_PPWR_2038", 12, f='=IF(@Isencao_Art6@<>"—",@Isencao_Art6@,IF(OR(@Grau_PPWR_Indicativo@="A",@Grau_PPWR_Indicativo@="B"),"Sim","Não"))', desc="Só A–B a partir de 2038."),
        # conteúdo reciclado
        col("Pct_PCR_Corpo", 8, "pct", f='=IFERROR(INDEX(tbl_materiais[Pct_PCR],MATCH(@Material_Corpo@,tbl_materiais[Material],0)),0)', desc="Reciclado no corpo."),
        col("Pct_PCR_Tampa", 8, "pct", f='=IF(@ID_Tampa@="",0,IFERROR(INDEX(tbl_tampas[Pct_PCR],MATCH(@ID_Tampa@,tbl_tampas[CapId],0)),0))', desc="Reciclado na tampa."),
        col("Conteudo_Reciclado_Pct", 8, "pct1", f='=IFERROR((@Massa_Corpo_g@*@Pct_PCR_Corpo@+@Massa_Tampa_g@*@Pct_PCR_Tampa@)/(@Massa_Corpo_g@+@Massa_Tampa_g@),0)', desc="Reciclado pós-consumo nas partes plásticas da Plasticom."),
        col("Categoria_Art7", 30, f=('=IF(@Segmento@="Farmacêutico","Isenta — medicamentos (art. 7.º)",IF(@Segmento@="Alimentar",IF(@Polimero_Corpo@="PET","Sensível ao contacto — PET","Sensível ao contacto — outros plásticos"),"Outras embalagens de plástico"))'),
            desc="Categoria do art. 7.º."),
        col("Meta_2030", 8, "pct", f='=IFERROR(IF(INDEX(tbl_metas_art7[Meta_2030],MATCH(@Categoria_Art7@,tbl_metas_art7[Categoria_Art7],0))="","",INDEX(tbl_metas_art7[Meta_2030],MATCH(@Categoria_Art7@,tbl_metas_art7[Categoria_Art7],0))),"")', desc="Meta de reciclado 2030."),
        col("Gap_2030", 8, "pct1", f='=IF(@Meta_2030@="","",MAX(0,@Meta_2030@-@Conteudo_Reciclado_Pct@))', desc="Pontos percentuais em falta (indicativo por SKU; a lei avalia a média por instalação/ano)."),
        col("Conforme_Art7_2030", 10, f='=IF(@Meta_2030@="","Isento",IF(@Gap_2030@=0,"Sim","Não"))', desc="Cumpre a meta de 2030 isoladamente?"),
        col("Estrutura_Material", 22, f=('=IF(AND(OR(@Polimero_Tampa@=@Polimero_Corpo@,@Polimero_Tampa@="Sem tampa",AND(OR(@Polimero_Tampa@="PE",@Polimero_Tampa@="PP"),OR(@Polimero_Corpo@="PE",@Polimero_Corpo@="PP"))),'
                                          'OR(@Rotulo_Tipo@="Sem rótulo",AND(ISNUMBER(SEARCH("PE/PP",@Rotulo_Tipo@)),OR(@Polimero_Corpo@="PE",@Polimero_Corpo@="PP")))),"Monomaterial (mesma família)","Multimaterial")'),
            desc="Monomaterial = corpo, tampa e rótulo na mesma família de polímero."),
        # mercado e controlo
        col("Unid_Vendidas_P12", 11, "num0", desc="Unidades vendidas (ano civil de 2026)."), col("N_Clientes_P12", 7, "int", desc="Clientes."),
        col("Paises_Venda", 16, desc="Países de colocação no mercado."),
        col("Massa_Vendida_kg", 10, "num0", f='=@Unid_Vendidas_P12@*@Massa_Corpo_g@/1000', desc="Massa de corpos vendida (kg)."),
        col("N_Requisitos_Aplicaveis", 9, "int", f='=COUNTIFS(tbl_aplicabilidade[ProductId],@ProductId@,tbl_aplicabilidade[Aplicavel],"Sim")', desc="Requisitos legais/normativos aplicáveis ao SKU."),
        col("N_Lacunas", 7, "int", f='=COUNTIFS(tbl_aplicabilidade[ProductId],@ProductId@,tbl_aplicabilidade[Estado_Resumo],"Lacuna")+COUNTIFS(tbl_aplicabilidade[ProductId],@ProductId@,tbl_aplicabilidade[Estado_Resumo],"Não conforme")',
            desc="Requisitos em lacuna ou não conformes."),
        col("Data_Avaliacao", 11, "date", desc="Data da avaliação."), col("Proxima_Revisao", 11, "date", f='=EDATE(@Data_Avaliacao@,12)', desc="Revisão anual ou em alteração de design."),
        col("Avaliador", 22, dv="Funcao", desc="Responsável."), col("Estado_Avaliacao", 22, dv="EstadoAval", desc="Autoavaliação, carta de compatibilidade ou certificado."),
        col("Metodo", 40, desc="Método e versão."),
    ]
    names = [c["name"] for c in acols]
    L = {n: get_column_letter(i + 1) for i, n in enumerate(names)}
    # cabeçalho das colunas de classe para o Ponto_Critico (linha 4)
    for c in acols:
        if c["name"] == "Ponto_Critico":
            c["f"] = c["f"].replace("$X$4:$Y$4", f"${L[first_c]}$4:${L[last_c]}$4")
    b.table("Avaliacao_RecyClass", "tbl_recyclass", acols, rows,
            "Uma linha por SKU: campos da ferramenta RecyClass, classe A–F, taxa de reciclabilidade, grau PPWR, reciclado e mercado.",
            title="AVALIAÇÃO DE RECICLABILIDADE POR SKU — MODELO RECYCLASS + GRAU PPWR (AUTOAVALIAÇÃO)",
            subtitle="Colunas brancas = campos a introduzir na ferramenta online RecyClass · cinzentas = cálculo · Rótulos: cenário típico do cliente (confirmar) · Massas estimadas · Não substitui a certificação RecyClass",
            cf=[("Classe_RecyClass", {"A": "green", "B": "blue", "C": "yellow", "D": "orange", "F": "red"}),
                ("Grau_PPWR_Indicativo", {"Não reciclável": "red", "Abaixo": "orange", "A": "green", "B": "blue", "C": "yellow"}),
                ("Conforme_PPWR_2030", {"Não": "red", "Sim": "green", "Isento": "gray"}), ("Conforme_Art7_2030", {"Não": "orange", "Sim": "green", "Isento": "gray"}),
                ("Regras_em_Falta", "AND(ISNUMBER(@),@>0)", "red")] + [(c[0], {"F": "red", "D": "orange", "C": "yellow", "B": "blue"}) for c in FEAT],
            row_height=18, freeze_col=2)

    # ---- compatibilidade das tampas por fluxo
    comp = []
    for c in caps:
        for fl in (PE, PP, PET):
            comp.append(dict(CapId=c["CapId"], Fluxo_Corpo=fl))
    ccols = [col("CapId", 22, desc="Tampa.", key="FK → tbl_tampas"), col("Fluxo_Corpo", 20, desc="Fluxo do corpo onde a tampa é aplicada."),
             col("Polimero_Tampa", 8, f='=IFERROR(INDEX(tbl_tampas[Polimero_Base],MATCH(@CapId@,tbl_tampas[CapId],0)),"")', desc="Polímero."),
             col("Classe", 7, f='=IFERROR(INDEX(tbl_regras_dfr[Classe],MATCH(@Fluxo_Corpo@&"|Material da tampa|"&@Polimero_Tampa@,tbl_regras_dfr[Chave],0)),"Sem regra")', desc="Classe da tampa nesse fluxo."),
             col("Fracao_Reciclavel", 9, "pct", f='=IFERROR(INDEX(tbl_regras_dfr[Fracao_Reciclavel],MATCH(@Fluxo_Corpo@&"|Material da tampa|"&@Polimero_Tampa@,tbl_regras_dfr[Chave],0)),0)', desc="Fração reciclada."),
             col("Fundamentacao", 50, f='=IFERROR(INDEX(tbl_regras_dfr[Fundamentacao],MATCH(@Fluxo_Corpo@&"|Material da tampa|"&@Polimero_Tampa@,tbl_regras_dfr[Chave],0)),"")', desc="Porquê."),
             col("Recomendacao_Comercial", 30, f='=IF(@Classe@="A","Recomendada",IF(@Classe@="B","Aceitável (perda de massa)","Evitar neste fluxo"))', desc="Orientação para a área comercial.")]
    b.table("Compat_Tampas", "tbl_compat_tampas", ccols, comp, "Compatibilidade de cada tampa com cada fluxo de corpo (guia comercial de combinação frasco + tampa).",
            cf=[("Classe", {"A": "green", "B": "blue", "D": "orange", "F": "red"}), ("Recomendacao_Comercial", {"Evitar": "red", "Aceitável": "yellow", "Recomendada": "green"})], row_height=18)

    # ---- famílias PPWR (inclui a triagem SVHC das embalagens — antes no RG-SGA-21 Artigos_SVHC)
    SVHC_FAM = {"PVC": ("Por confirmar", "Sem declaração do SUP-005 (plastificante e estabilizante desconhecidos); análise GC-MS/XRF antes de expedir (PAM-26-28)."),
                "PET": ("Não", "DEC-03; tinta UV: fotoiniciador 71868-10-5 = 0,018% m/m no frasco decorado (< 0,1%)."),
                "rPET": ("Não", "DEC-04 (desatualizada — pedir nova, PAM-26-34); tinta UV 0,018% m/m (< 0,1%)."),
                "PETG": ("Não", "DEC-03; tinta UV 0,018% m/m (< 0,1%)."),
                "PET-PG": ("Não", "DEC-11."),
                "_": ("Não", "Declarações dos fornecedores do polímero e do masterbatch (RG-SGA-21 tbl_declaracoes).")}
    SVHC_TAMPA_PP = ("Por confirmar", "Masterbatch deslizante/antiestático sem declaração SVHC (DEC-09, PAM-26-34).")
    fam = []
    for fid, nome, tipo, mat in FAMILIAS:
        food = "FG" in mat
        fam.append(dict(ID_Familia=fid, Familia=nome, Tipo=tipo, Material=mat, Documentacao_Tecnica="Sim" if fid in DOC_OK else "Não",
                        Declaracao_UE="Sim" if fid in DOC_OK else "Não", Data_DoC=(dt.date.fromisoformat(DOC_Q4[fid]) if fid in DOC_Q4 else dt.date(2026, 8, 10)) if fid in DOC_OK else None,
                        Metais_Pesados_Evidencia="RM-2026-07 (laboratório acreditado)" if fid in METAIS_LAB else ("Declaração do fornecedor" if fid in METAIS_DECL else "Em falta"),
                        Metais_mg_kg=(18 if fid in METAIS_LAB else None),
                        PFAS_Evidencia="Declaração SUP-010 (07/2026) + flúor total < 50 ppm" if food else "Não aplicável (sem contacto alimentar)",
                        SVHC_Artigo=(SVHC_TAMPA_PP if (tipo == "Tampa" and mat in ("PP", "PP-PCR")) else SVHC_FAM.get(mat, SVHC_FAM["_"]))[0],
                        SVHC_Evidencia=(SVHC_TAMPA_PP if (tipo == "Tampa" and mat in ("PP", "PP-PCR")) else SVHC_FAM.get(mat, SVHC_FAM["_"]))[1],
                        Prazo=dt.date(2026, 12, 31), ID_PAM="PAM-26-10"))
    fcols = [col("ID_Familia", 9, desc="Família PPWR (grupo com a mesma documentação técnica).", key="PK"), col("Familia", 30, desc="Designação."), col("Tipo", 8, desc="Frasco, pote, tampa."),
             col("Material", 10, dv="Material", desc="Material."),
             col("N_SKUs", 7, "int", f='=COUNTIF(tbl_recyclass[Familia_PPWR],@ID_Familia@)+COUNTIF(tbl_tampas[Familia_PPWR],@ID_Familia@)', desc="SKUs na família."),
             col("Documentacao_Tecnica", 10, dv="SimNao", desc="Documentação técnica (anexo VII) completa."), col("Declaracao_UE", 10, dv="SimNao", desc="Declaração UE de conformidade emitida."),
             col("Data_DoC", 11, "date", desc="Data da declaração UE.", req=False), col("Metais_Pesados_Evidencia", 30, desc="Evidência Pb+Cd+Hg+Cr(VI) ≤ 100 mg/kg."),
             col("Metais_mg_kg", 9, "num0", desc="Resultado (soma, mg/kg).", req=False), col("PFAS_Evidencia", 34, desc="PFAS (só contacto alimentar)."),
             col("SVHC_Artigo", 12, desc="SVHC da lista candidata > 0,1% m/m no artigo? (Não / Sim / Por confirmar) — triagem a partir das declarações do RG-SGA-21."),
             col("SVHC_Evidencia", 40, desc="Declarações (RG-SGA-21 tbl_declaracoes) ou cálculo por artigo (acórdão C-106/14)."),
             col("Obrigacao_SVHC", 18, f='=IF(@SVHC_Artigo@="Sim","Art. 33.º + SCIP (+ art. 7.º, n.º 2 se > 1 t/ano)",IF(@SVHC_Artigo@="Por confirmar","Não expedir sem confirmação","Nenhuma"))',
                 desc="Obrigações REACH decorrentes (EU-ENV-008)."),
             col("Pior_Classe_RecyClass", 9, f='=IF(COUNTIF(tbl_recyclass[Familia_PPWR],@ID_Familia@)=0,"(componente)",INDEX({"A","B","C","D","E","F"},_xlfn.MAXIFS(tbl_recyclass[Classe_N_Max],tbl_recyclass[Familia_PPWR],@ID_Familia@)))',
                 desc="Pior classe dos SKUs da família."),
             col("SKUs_Nao_Conformes_2030", 9, "int", f='=COUNTIFS(tbl_recyclass[Familia_PPWR],@ID_Familia@,tbl_recyclass[Conforme_PPWR_2030],"Não")', desc="SKUs abaixo do grau C."),
             col("Estado", 10, f='=IF(AND(@Declaracao_UE@="Sim",@Metais_Pesados_Evidencia@<>"Em falta"),"Conforme","Lacuna")', desc="Conformidade atual (declaração + metais)."),
             col("Prazo", 11, "date", desc="Prazo para concluir."), col("ID_PAM", 10, desc="Ação.", key="FK → RG-SGA-06")]
    b.table("Familias_PPWR", "tbl_familias_ppwr", fcols, fam, "Famílias de embalagem para a documentação técnica e declaração UE de conformidade (base do KPI-12).",
            cf=[("Estado", {"Lacuna": "red", "Conforme": "green"}), ("Pior_Classe_RecyClass", {"F": "red", "D": "orange", "C": "yellow", "B": "blue", "A": "green"})], row_height=30)

    # ---- requisitos
    rq = []
    for r in REQ:
        x = dict(zip(REQ_COLS, r))
        x["Data_Aplicacao"] = D(x["Data_Aplicacao"]) if x["Data_Aplicacao"] else None
        x["Prazo"] = D(x["Prazo"]) if x["Prazo"] else None
        for k in ("ID_Legal", "ID_PAM", "Fonte_Oficial", "Nota_Verificacao"):
            x[k] = x[k] or None
        x["Data_Revisao"] = DAV
        rq.append(x)
    qcols = [col("ID_Req", 10, desc="ID da matriz integrada (IDs propostos pelo ChatGPT + adicionados).", key="PK"), col("Grupo", 16, desc="Grupo."), col("Fonte", 34, desc="Diploma / norma."),
             col("Artigo_Anexo", 26, desc="Artigo / anexo."), col("Tema", 22, desc="Tema."), col("Requisito", 60, desc="O que tem de ser cumprido."),
             col("Natureza_Obrigacao", 18, dv="Natureza", desc="Obrigação legal / norma técnica / contratual / voluntária / necessita verificação."),
             col("Papel_Plasticom", 30, desc="Papel jurídico da Plasticom neste requisito."), col("Nivel", 8, desc="Produto (liga a tbl_aplicabilidade), Material ou Empresa."),
             col("Ambito_Produtos", 12, desc="Produtos abrangidos."), col("Data_Aplicacao", 11, "date", desc="Data de aplicação.", req=False),
             col("Aplicabilidade", 10, dv="Aplicabilidade", desc="Sim / Condicional / Não / Futuro."), col("Evidencia_SGA", 40, desc="Registo/tabela do SGA com a evidência."),
             col("Metodo_Verificacao", 22, desc="Como se verifica."), col("Frequencia", 14, desc="Periodicidade."), col("Estado", 11, dv="EstadoReq", desc="Estado da conformidade."),
             col("Risco", 7, dv="Risco", desc="Impacto do incumprimento."), col("ID_Legal", 8, desc="Requisito no registo legal.", key="FK → RG-SGA-04", req=False),
             col("ID_PAM", 10, desc="Ação.", key="FK → RG-SGA-06", req=False), col("Responsavel", 26, dv="Funcao", desc="Responsável."),
             col("Prazo", 11, "date", desc="Prazo de fecho da lacuna.", req=False), col("Verificacao_ChatGPT", 13, dv="Verificacao", desc="Resultado da verificação da matriz do ChatGPT."),
             col("Nota_Verificacao", 44, desc="O que foi confirmado, corrigido ou acrescentado.", req=False), col("Fonte_Oficial", 30, desc="Ligação oficial.", req=False),
             col("Data_Revisao", 11, "date", desc="Data da revisão."),
             col("N_SKUs_Aplicaveis", 9, "int", f='=COUNTIFS(tbl_aplicabilidade[ID_Req],@ID_Req@,tbl_aplicabilidade[Aplicavel],"Sim")', desc="SKUs a que se aplica (requisitos de produto)."),
             col("N_SKUs_Conformes", 9, "int", f='=COUNTIFS(tbl_aplicabilidade[ID_Req],@ID_Req@,tbl_aplicabilidade[Estado_Resumo],"Conforme")+COUNTIFS(tbl_aplicabilidade[ID_Req],@ID_Req@,tbl_aplicabilidade[Estado_Resumo],"Isento")',
                 desc="SKUs conformes ou isentos."),
             col("Alerta", 22, f='=IF(AND(OR(@Estado@="Lacuna",@Estado@="Parcial"),@ID_PAM@=""),"Lacuna sem ação",IF(AND(@Prazo@<>"",@Prazo@<DataRef,@Estado@<>"Conforme"),"Prazo vencido",IF(@Natureza_Obrigacao@="Necessita verificação","Confirmar aplicabilidade","OK")))',
                 desc="Alerta automático.")]
    b.table("Requisitos_Embalagem", "tbl_requisitos_emb", qcols, rq,
            "Matriz legal e normativa integrada de embalagens (UE, contacto alimentar, cosméticos, farmacêutico, ISO/EN, Portugal) com natureza da obrigação, papel da Plasticom, evidência e verificação da resposta do ChatGPT.",
            title="MATRIZ LEGAL E NORMATIVA DE EMBALAGENS — RECICLAGEM, RECICLABILIDADE E SEGURANÇA DOS MATERIAIS",
            subtitle="IDs EU-ENV/FCM/COS/PHAR/ISO/PT da matriz proposta (ChatGPT), verificados e completados · Não é parecer jurídico — confirmar artigos na versão consolidada (EUR-Lex/DRE)",
            cf=[("Estado", {"Lacuna": "red", "Parcial": "yellow", "Conforme": "green", "Em avaliação": "orange", "Futuro": "blue", "Não aplicável": "gray"}),
                ("Verificacao_ChatGPT", {"Corrigido": "red", "Adicionado": "purple", "Complementado": "blue", "Confirmado": "green"}),
                ("Alerta", {"sem ação": "red", "vencido": "red", "Confirmar": "yellow", "OK": "green"}),
                ("Natureza_Obrigacao", {"verificação": "yellow"})], row_height=70, freeze_col=1)

    # ---- aplicabilidade produto × requisito
    reqd = {r[0]: r for r in REQ}
    ap = []
    for r in rows:
        for rid in REQ_PRODUTO:
            a, mot, base, ev = _aplica(reqd[rid], r)
            ap.append(dict(ProductId=r["ProductId"], ID_Req=rid, Aplicavel=a, Motivo=mot, Estado_Base=base, Evidencia=ev or None))
    rec = lambda c: f'INDEX(tbl_recyclass[{c}],MATCH(@ProductId@,tbl_recyclass[ProductId],0))'
    fam_of = rec("Familia_PPWR")
    famv = lambda c: f'INDEX(tbl_familias_ppwr[{c}],MATCH({fam_of},tbl_familias_ppwr[ID_Familia],0))'
    est = ('=IF(@Aplicavel@="Não","Não aplicável",IFERROR('
           f'IF(@ID_Req@="EU-ENV-002",IF({rec("Conforme_PPWR_2030")}="Sim","Conforme (autoavaliação)",IF({rec("Conforme_PPWR_2030")}="Não","Não conforme em 2030","Isento até 2035")),'
           f'IF(@ID_Req@="EU-ENV-003",IF({rec("Conforme_Art7_2030")}="Sim","Conforme (meta 2030)",IF({rec("Conforme_Art7_2030")}="Não","Lacuna face à meta 2030","Isento")),'
           f'IF(@ID_Req@="EU-ENV-011",IF({famv("Metais_Pesados_Evidencia")}="Em falta","Lacuna","Conforme"),'
           f'IF(@ID_Req@="EU-ENV-013",IF({famv("Declaracao_UE")}="Sim","Conforme","Lacuna"),@Estado_Base@)))),@Estado_Base@))')
    pcols = [col("ProductId", 22, desc="SKU.", key="FK → tbl_recyclass"), col("ID_Req", 10, desc="Requisito.", key="FK → tbl_requisitos_emb"),
             col("Tema", 22, f='=IFERROR(INDEX(tbl_requisitos_emb[Tema],MATCH(@ID_Req@,tbl_requisitos_emb[ID_Req],0)),"")', desc="Tema."),
             col("Segmento", 20, f=f'=IFERROR({rec("Segmento")},"")', desc="Segmento do SKU."),
             col("Aplicavel", 8, dv="SimNao", desc="Aplica-se ao SKU?"), col("Motivo", 40, desc="Justificação da aplicabilidade."),
             col("Estado_Base", 12, dv="EstadoReq", desc="Estado do requisito (quando não é calculado)."),
             col("Estado", 22, f=est, desc="Estado para o SKU (calculado para DfR, reciclado, metais e declaração UE)."),
             col("Estado_Resumo", 12, f=('=IF(ISNUMBER(SEARCH("Não aplicável",@Estado@)),"Não aplicável",IF(ISNUMBER(SEARCH("Isento",@Estado@)),"Isento",IF(ISNUMBER(SEARCH("Não conforme",@Estado@)),"Não conforme",'
                                          'IF(ISNUMBER(SEARCH("Lacuna",@Estado@)),"Lacuna",IF(ISNUMBER(SEARCH("Conforme",@Estado@)),"Conforme",@Estado@)))))'), desc="Estado normalizado (para Power BI)."),
             col("Evidencia", 36, desc="Evidência.", req=False)]
    b.table("Aplicabilidade_Produto", "tbl_aplicabilidade", pcols, ap,
            "Fact_Aplicabilidade: produto × requisito com aplicabilidade, motivo, estado calculado e evidência.",
            cf=[("Estado_Resumo", {"Não conforme": "red", "Lacuna": "red", "Parcial": "yellow", "Conforme": "green", "Isento": "gray", "Em avaliação": "orange", "Futuro": "blue"})], row_height=16)

    # ---- vendas por SKU e país
    vend = []
    g = s12.groupby(["ProductId", "ProductFamily", "Country"]).agg(Unid=("ShippedQty", "sum"), Clientes=("CustomerId", "nunique")).reset_index()
    for x in g.itertuples():
        vend.append(dict(ProductId=x.ProductId, Tipo="Tampa" if x.ProductFamily == "Cap" else "Frasco/pote", Pais=PAIS[x.Country][0], Pais_Nome=PAIS[x.Country][1],
                         N_Clientes=int(x.Clientes), Unidades=int(x.Unid)))
    vcols = [col("ProductId", 22, desc="SKU.", key="FK → tbl_recyclass / tbl_tampas"), col("Tipo", 10, desc="Frasco/pote ou tampa."), col("Pais", 5, desc="País (ISO)."),
             col("Pais_Nome", 10, desc="País."), col("N_Clientes", 7, "int", desc="Clientes."), col("Unidades", 11, "num0", desc="Unidades expedidas (ano civil de 2026)."),
             col("Massa_Unit_g", 8, "num1", f='=IFERROR(IF(@Tipo@="Tampa",INDEX(tbl_tampas[Massa_g],MATCH(@ProductId@,tbl_tampas[CapId],0)),INDEX(tbl_recyclass[Massa_Corpo_g],MATCH(@ProductId@,tbl_recyclass[ProductId],0))),0)', desc="Massa unitária."),
             col("Massa_kg", 10, "num0", f='=@Unidades@*@Massa_Unit_g@/1000', desc="Plástico colocado no mercado (kg)."),
             col("Pct_PCR", 7, "pct", f='=IFERROR(IF(@Tipo@="Tampa",INDEX(tbl_tampas[Pct_PCR],MATCH(@ProductId@,tbl_tampas[CapId],0)),INDEX(tbl_recyclass[Pct_PCR_Corpo],MATCH(@ProductId@,tbl_recyclass[ProductId],0))),0)', desc="Reciclado certificado."),
             col("Massa_Reciclado_kg", 10, "num0", f='=@Massa_kg@*@Pct_PCR@', desc="Plástico reciclado (kg)."),
             col("Massa_Virgem_kg", 10, "num0", f='=@Massa_kg@-@Massa_Reciclado_kg@', desc="Plástico não reciclado (kg)."),
             col("Imposto_ES_EUR", 10, "eur", f=f'=IF(@Pais@="ES",@Massa_Virgem_kg@*{_p("P-01")},0)', desc="Imposto espanhol estimado pago pelo cliente adquirente."),
             col("Grau_PPWR", 12, f='=IF(@Tipo@="Tampa","Componente",IFERROR(INDEX(tbl_recyclass[Grau_PPWR_Indicativo],MATCH(@ProductId@,tbl_recyclass[ProductId],0)),""))', desc="Grau PPWR do SKU.")]
    b.table("Vendas_Pais", "tbl_vendas_embalagem", vcols, vend, "Plástico colocado no mercado por SKU e país (base para RAP, imposto espanhol e metas do art. 7.º).", row_height=16)

    # ---- embalagens de expedição (RAP)
    s12m = s12.assign(Mes=s12.Date.str[:7])
    exp = []
    for (mes, pais), gg in s12m.groupby(["Mes", "Country"]):
        caixas = gg[gg.ProductFamily == "Bottle"].ShippedQty.sum() / PV["P-10"] + gg[gg.ProductFamily == "Cap"].ShippedQty.sum() / PV["P-11"]
        pal = caixas / PV["P-12"]
        for mat, ler, kg, pid in (("Cartão (caixas)", "15 01 01", caixas * PV["P-09"], "P-15"), ("Filme PE estirável", "15 01 02", pal * PV["P-14"], "P-16"),
                                  ("Paletes de madeira (sem retorno)", "15 01 03", pal * PV["P-13"], "P-17")):
            exp.append(dict(Mes=D(mes + "-01"), Pais=PAIS[pais][0], Material_Embalagem=mat, Codigo_LER_Fim_Vida=ler, Massa_kg=round(kg, 1), ID_Param_Valor=pid))
    ecols = [col("Mes", 10, "date", desc="Mês."), col("Pais", 5, desc="País de destino."), col("Material_Embalagem", 26, desc="Material da embalagem de expedição."),
             col("Codigo_LER_Fim_Vida", 9, desc="Código LER quando vira resíduo no cliente."), col("Massa_kg", 10, "num1", desc="Massa colocada no mercado (kg)."),
             col("Regime_RAP", 40, f='=IF(@Pais@="PT","SIGRE — embalagens não urbanas (Plasticom embalador)","Regime do país de destino — confirmar quem é o produtor (PPWR art. 44.º)")', desc="Regime aplicável."),
             col("ID_Param_Valor", 8, desc="Parâmetro da prestação financeira."),
             col("Prestacao_EUR", 10, "eur", f='=IF(@Pais@="PT",@Massa_kg@*INDEX(tbl_param_emb[Valor],MATCH(@ID_Param_Valor@,tbl_param_emb[ID_Parametro],0)),0)', desc="Prestação financeira estimada (valores indicativos).")]
    b.table("Embalagens_Expedicao", "tbl_emb_expedicao", ecols, exp, "Embalagens de expedição colocadas no mercado por mês, país e material — base da declaração RAP (DL 152-D/2017).", row_height=16)

    # ---- países
    pcols2 = [col("ID_Pais_Req", 9, desc="Identificador.", key="PK"), col("Pais", 5, desc="País (ISO)."), col("Tema", 22, desc="Tema."), col("Requisito", 60, desc="Requisito nacional."),
              col("Papel_Plasticom", 26, desc="Papel da Plasticom."), col("Informacao_a_Fornecer", 34, desc="O que a Plasticom tem de dar ao cliente/autoridade."),
              col("Autoridade", 22, desc="Autoridade competente."), col("Fonte_Legal", 30, desc="Diploma."), col("Natureza_Obrigacao", 18, dv="Natureza", desc="Natureza."),
              col("Estado", 11, dv="EstadoReq", desc="Estado."),
              col("N_Clientes", 7, "int", f='=SUMIFS(tbl_vendas_embalagem[N_Clientes],tbl_vendas_embalagem[Pais],@Pais@,tbl_vendas_embalagem[ProductId],"FR-001*")*0+IFERROR(INDEX({8,3,1,1,2,1},MATCH(@Pais@,{"PT","ES","FR","IT","DE","PL"},0)),0)',
                  desc="Clientes no país (dim_customer)."),
              col("Massa_Plastico_kg", 11, "num0", f='=SUMIFS(tbl_vendas_embalagem[Massa_kg],tbl_vendas_embalagem[Pais],@Pais@)', desc="Plástico vendido no país (12 meses)."),
              col("Massa_Reciclado_kg", 11, "num0", f='=SUMIFS(tbl_vendas_embalagem[Massa_Reciclado_kg],tbl_vendas_embalagem[Pais],@Pais@)', desc="Reciclado certificado.")]
    ncli = pd.read_csv(os.path.join(DIMD, "dim_customer.csv")).Country.map(lambda c: PAIS[c][0]).value_counts().to_dict()
    for c in pcols2:
        if c["name"] == "N_Clientes":
            c["f"] = None
            c["desc"] = "Clientes no país (dim_customer)."
    b.table("Requisitos_Pais", "tbl_requisitos_pais", pcols2,
            [dict(zip(["ID_Pais_Req", "Pais", "Tema", "Requisito", "Papel_Plasticom", "Informacao_a_Fornecer", "Autoridade", "Fonte_Legal", "Natureza_Obrigacao", "Estado"], p), N_Clientes=ncli.get(p[1], 0)) for p in PAISES_REQ],
            "Camada nacional por país de destino (RAP, rotulagem, impostos, alegações).",
            cf=[("Estado", {"Parcial": "yellow", "Conforme": "green", "Em avaliação": "orange"}), ("Natureza_Obrigacao", {"verificação": "yellow"})], row_height=45)

    # ---- certificados PCR
    kc = ["ID_Certificado", "ID_Fornecedor", "Material", "Esquema", "N_Certificado", "Norma", "Pct_PCR_Declarado", "Origem", "Data_Emissao", "Validade", "Aprovado_Contacto_Alimentar", "Nota"]
    cr = []
    for c in CERTS:
        x = dict(zip(kc, c))
        x["Data_Emissao"] = D(x["Data_Emissao"]) if x["Data_Emissao"] else None
        x["Validade"] = D(x["Validade"]) if x["Validade"] else None
        x["N_Certificado"] = x["N_Certificado"] or None
        x["Nota"] = x["Nota"] or None
        cr.append(x)
    kcols = [col("ID_Certificado", 9, desc="Identificador.", key="PK"), col("ID_Fornecedor", 10, desc="Fornecedor.", key="FK → RG-SGA-11"), col("Material", 18, desc="Material."),
             col("Esquema", 26, desc="Esquema de certificação."), col("N_Certificado", 16, desc="N.º.", req=False), col("Norma", 16, desc="Norma de referência."),
             col("Pct_PCR_Declarado", 9, "pct", desc="Teor de reciclado declarado.", req=False), col("Origem", 16, desc="Pós-consumo / pós-industrial / químico."),
             col("Data_Emissao", 11, "date", desc="Emissão.", req=False), col("Validade", 11, "date", desc="Validade.", req=False),
             col("Aprovado_Contacto_Alimentar", 16, desc="Processo autorizado pelo Reg. 2022/1616?"), col("Nota", 40, desc="Nota.", req=False),
             col("Dias_para_Expirar", 9, "int", f='=IF(@Validade@="","",@Validade@-DataRef)', desc="Dias até expirar."),
             col("Estado", 14, f='=IF(@Validade@="","Sem certificado",IF(@Dias_para_Expirar@<0,"Expirado",IF(@Dias_para_Expirar@<=90,"Expira ≤ 90 dias","Válido")))', desc="Estado.")]
    b.table("Certificados_PCR", "tbl_certificados_pcr", kcols, cr, "Certificados de conteúdo reciclado por fornecedor e material (EN 15343 / ISO 22095).",
            cf=[("Estado", {"Expirado": "red", "Sem": "orange", "90": "yellow", "Válido": "green"})], row_height=30)

    # ---- alegações
    ka = ["ID_Alegacao", "Texto_Alegacao", "Tipo", "Ambito_Produtos", "Canal", "Norma_Referencia", "Evidencia", "Estado", "Data_Revisao", "Prazo_Acao", "Responsavel", "ID_PAM"]
    al = []
    for a in ALEG:
        x = dict(zip(ka, a))
        x["Data_Revisao"], x["Prazo_Acao"] = D(x["Data_Revisao"]), D(x["Prazo_Acao"])
        x["ID_PAM"] = x["ID_PAM"] or None
        al.append(x)
    lcols = [col("ID_Alegacao", 9, desc="Identificador.", key="PK"), col("Texto_Alegacao", 40, desc="Texto usado."), col("Tipo", 16, desc="Tipo."),
             col("Ambito_Produtos", 22, desc="Produtos a que se refere."), col("Canal", 18, desc="Onde é comunicada."), col("Norma_Referencia", 26, desc="Norma / diploma."),
             col("Evidencia", 40, desc="Evidência de suporte."), col("Estado", 11, dv="EstadoAlegacao", desc="Estado."), col("Data_Revisao", 11, "date", desc="Revisão."),
             col("Prazo_Acao", 11, "date", desc="Prazo."), col("Responsavel", 24, dv="Funcao", desc="Responsável."), col("ID_PAM", 10, desc="Ação.", key="FK → RG-SGA-06", req=False),
             col("Alerta", 20, f='=IF(OR(@Estado@="Retirar",@Estado@="Proibida",@Estado@="Suspensa"),IF(@Prazo_Acao@<=DataRef+7,"RETIRAR JÁ","Retirar até ao prazo"),IF(@Prazo_Acao@<DataRef,"Revisão vencida","OK"))', desc="Alerta.")]
    b.table("Alegacoes", "tbl_alegacoes", lcols, al, "Registo de alegações ambientais de produto (PR-SGA-14; Diretiva 2024/825; ISO 14021).",
            cf=[("Estado", {"Proibida": "red", "Retirar": "red", "Suspensa": "orange", "revisão": "yellow", "Aprovada": "green"}), ("Alerta", {"JÁ": "red", "Retirar": "orange", "vencida": "red", "OK": "green"})], row_height=30)

    # ---- maturidade
    b.table("Maturidade", "tbl_maturidade_emb",
            [col("ID_Item", 8, desc="Item.", key="PK"), col("Item_Checklist", 50, desc="Item do checklist de maturidade (resposta do ChatGPT)."),
             col("Estado", 12, dv="Maturidade", desc="Implementado / Parcial / Lacuna."), col("Evidencia_SGA", 60, desc="Onde está no SGA."), col("ID_PAM", 10, desc="Ação.", req=False)],
            [dict(ID_Item=m[0], Item_Checklist=m[1], Estado=m[2], Evidencia_SGA=m[3], ID_PAM=m[4] or None) for m in MATURIDADE],
            "Checklist de 16 itens da matriz de conformidade (verificação do SGA).", cf=[("Estado", {"Implementado": "green", "Parcial": "yellow", "Lacuna": "red"})], row_height=30)

    _painel(b, len(rows))
    _formulario(b, len(rows))
    b.wb.move_sheet("Painel", offset=-(len(b.wb.sheetnames) - 3))
    return b.save(out)


def _painel(b, n):
    ws = b.sheet("Painel", "Painel: KPI de reciclabilidade, distribuição das classes, graus PPWR, reciclado face às metas e conformidade legal (tabela dinâmica e segmentações).", tab_color="00B050")
    ws["A1"] = "PAINEL DE RECICLABILIDADE E CONFORMIDADE DE EMBALAGENS — PLASTICOM"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Autoavaliação RecyClass (regras simplificadas) e graus PPWR indicativos · vendas de 2026 · atualiza com as tabelas"
    ws["A2"].font = F_SUB
    for c, w in zip("ABCDEFGHIJ", (46, 14, 14, 14, 14, 3, 30, 14, 14, 14)):
        ws.column_dimensions[c].width = w
    R = "tbl_recyclass"
    kpis = [
        ("SKUs avaliados (frascos e potes)", f"=COUNTA({R}[ProductId])", "0"),
        ("SKUs com grau PPWR A–C (não isentos) — KPI-18", f'=COUNTIFS({R}[Conforme_PPWR_2030],"Sim")/(COUNTA({R}[ProductId])-COUNTIF({R}[Segmento],"Farmacêutico"))', "0%"),
        ("Massa vendida com grau A–C (não isentos) — KPI-20", f'=SUMIFS({R}[Massa_Vendida_kg],{R}[Conforme_PPWR_2030],"Sim")/SUMIFS({R}[Massa_Vendida_kg],{R}[Segmento],"<>Farmacêutico")', "0%"),
        ("SKUs classe F (não recicláveis)", f'=COUNTIF({R}[Classe_RecyClass],"F")', "0"),
        ("SKUs isentos até 2035 (farmacêuticos)", f'=COUNTIF({R}[Isencao_Art6],"Isento até 2035")', "0"),
        ("Taxa média de reciclabilidade ponderada pela massa vendida", f"=SUMPRODUCT({R}[Taxa_Reciclabilidade],{R}[Massa_Vendida_kg])/SUM({R}[Massa_Vendida_kg])", "0.0%"),
        ("Conteúdo reciclado ponderado (corpos + tampas vendidos) — KPI-19", "=SUM(tbl_vendas_embalagem[Massa_Reciclado_kg])/SUM(tbl_vendas_embalagem[Massa_kg])", "0.0%"),
        ("Famílias com declaração UE de conformidade — KPI-12", '=COUNTIF(tbl_familias_ppwr[Declaracao_UE],"Sim")/COUNTA(tbl_familias_ppwr[ID_Familia])', "0%"),
        ("Certificados de reciclado válidos — KPI-21", '=(COUNTIF(tbl_certificados_pcr[Estado],"Válido")+COUNTIF(tbl_certificados_pcr[Estado],"Expira*"))/COUNTIFS(tbl_certificados_pcr[Pct_PCR_Declarado],">0")', "0%"),
        ("Imposto espanhol estimado (pago pelos clientes ES, €/ano)", "=SUM(tbl_vendas_embalagem[Imposto_ES_EUR])", "#,##0 €"),
        ("Requisitos da matriz em lacuna / parcial", '=COUNTIF(tbl_requisitos_emb[Estado],"Lacuna")&" / "&COUNTIF(tbl_requisitos_emb[Estado],"Parcial")', "@"),
        ("Checklist de maturidade implementado", '=COUNTIF(tbl_maturidade_emb[Estado],"Implementado")/COUNTA(tbl_maturidade_emb[ID_Item])', "0%"),
        ("Alegações a retirar / proibidas / suspensas", '=COUNTIF(tbl_alegacoes[Estado],"Retirar")+COUNTIF(tbl_alegacoes[Estado],"Proibida")+COUNTIF(tbl_alegacoes[Estado],"Suspensa")', "0"),
    ]
    header_row(ws, 4, ["Indicador", "Valor"])
    for k, (lab, f, fmt) in enumerate(kpis):
        r = 5 + k
        a = ws.cell(row=r, column=1, value=lab)
        a.font, a.border = F_BASE, BORDER
        c = ws.cell(row=r, column=2, value=f)
        c.font, c.border, c.number_format = F_BOLD, BORDER, fmt
    r = 6 + len(kpis)
    ws.cell(row=r, column=1, value="DISTRIBUIÇÃO POR CLASSE RECYCLASS").font = F_BOLD
    header_row(ws, r + 1, ["Classe", "N.º SKUs", "Massa vendida (kg)", "% SKUs", "% massa"])
    top = r + 2
    for k, cl in enumerate(CLS):
        rr = top + k
        ws.cell(row=rr, column=1, value=cl)
        ws.cell(row=rr, column=2, value=f'=COUNTIF({R}[Classe_RecyClass],A{rr})')
        ws.cell(row=rr, column=3, value=f'=SUMIFS({R}[Massa_Vendida_kg],{R}[Classe_RecyClass],A{rr})').number_format = "#,##0"
        ws.cell(row=rr, column=4, value=f'=B{rr}/SUM($B${top}:$B${top + 5})').number_format = "0%"
        ws.cell(row=rr, column=5, value=f'=C{rr}/SUM($C${top}:$C${top + 5})').number_format = "0%"
        for j in range(1, 6):
            ws.cell(row=rr, column=j).border = BORDER
    ch = BarChart()
    ch.type, ch.style, ch.title = "col", 10, "SKUs por classe RecyClass"
    ch.add_data(Reference(ws, min_col=2, min_row=top - 1, max_row=top + 5), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=top, max_row=top + 5))
    ch.height, ch.width, ch.legend = 7, 12, None
    ws.add_chart(ch, "G4")
    r = top + 8
    ws.cell(row=r, column=1, value="GRAU PPWR INDICATIVO × CONFORMIDADE 2030/2038").font = F_BOLD
    header_row(ws, r + 1, ["Grau PPWR", "N.º SKUs", "Massa vendida (kg)"])
    for k, gname in enumerate(["A", "B", "C", "Abaixo de C", "Não reciclável (F)"]):
        rr = r + 2 + k
        ws.cell(row=rr, column=1, value=gname)
        ws.cell(row=rr, column=2, value=f'=COUNTIF({R}[Grau_PPWR_Indicativo],A{rr})')
        ws.cell(row=rr, column=3, value=f'=SUMIFS({R}[Massa_Vendida_kg],{R}[Grau_PPWR_Indicativo],A{rr})').number_format = "#,##0"
    r = r + 9
    ws.cell(row=r, column=1, value="CONTEÚDO RECICLADO FACE ÀS METAS DO ART. 7.º (média da instalação, ponderada pela massa vendida)").font = F_BOLD
    header_row(ws, r + 1, ["Categoria art. 7.º", "Massa vendida (kg)", "Reciclado (%)", "Meta 2030", "Gap (p.p.)"])
    for k, m in enumerate(METAS7):
        rr = r + 2 + k
        ws.cell(row=rr, column=1, value=m[0])
        ws.cell(row=rr, column=2, value=f'=SUMIFS({R}[Massa_Vendida_kg],{R}[Categoria_Art7],A{rr})').number_format = "#,##0"
        ws.cell(row=rr, column=3, value=f'=IFERROR(SUMPRODUCT(({R}[Categoria_Art7]=A{rr})*{R}[Massa_Vendida_kg]*{R}[Conteudo_Reciclado_Pct])/B{rr},"")').number_format = "0.0%"
        ws.cell(row=rr, column=4, value=f'=IFERROR(IF(INDEX(tbl_metas_art7[Meta_2030],MATCH(A{rr},tbl_metas_art7[Categoria_Art7],0))="","",INDEX(tbl_metas_art7[Meta_2030],MATCH(A{rr},tbl_metas_art7[Categoria_Art7],0))),"")').number_format = "0%"
        ws.cell(row=rr, column=5, value=f'=IF(OR(C{rr}="",D{rr}=""),"",MAX(0,D{rr}-C{rr}))').number_format = "0.0%"
    r = r + 9
    ws.cell(row=r, column=1, value="ANÁLISE DINÂMICA (tabela dinâmica e segmentações — atualizar com Dados > Atualizar tudo)").font = F_BOLD
    for rr in range(1, r + 1):
        for cc in (1,):
            ws.cell(row=rr, column=cc).alignment = WRAP_TOP


def _formulario(b, n):
    ws = b.sheet("Formulario_RecyClass", "Ficha de um SKU na ordem dos campos da ferramenta online RecyClass (escolher o SKU na célula B4).", tab_color="0070C0")
    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 60
    ws["A1"] = "FICHA DE PREENCHIMENTO DA FERRAMENTA RECYCLASS (por SKU)"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Escolha o SKU em B4. Os valores vêm de tbl_recyclass; copie-os para recyclass.eu (Recyclability Evaluation Tool) e compare o resultado oficial com o calculado."
    ws["A2"].font = F_SUB
    ws["A4"], ws["B4"] = "SKU (ProductId)", "FR-007-PETG-350"
    ws["A4"].font, ws["B4"].font = F_BOLD, F_BOLD
    ws["B4"].fill = PatternFill("solid", fgColor="FFF2B3")
    t = b.tables["tbl_recyclass"]
    dv = DataValidation(type="list", formula1=f"='Avaliacao_RecyClass'!${t['colmap']['ProductId']}${t['first']}:${t['colmap']['ProductId']}${t['last']}", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B4")
    campos = [
        ("1. INFORMAÇÃO GERAL", None, None), ("Categoria de embalagem na ferramenta", "Categoria_RecyClass", None), ("Formato / segmento", "Formato", "Segmento"),
        ("Volume (ml) / maior dimensão (mm)", "Volume_ml", "Dimensao_Max_mm"), ("Massa total da unidade (g)", "Massa_Total_g", None),
        ("2. CORPO PRINCIPAL", None, None), ("Polímero / material", "Material_Corpo", "Polimero_Corpo"), ("Cor e transparência", "Cor_Corpo", "Cor_Dataset"),
        ("Masterbatch / dosagem", "Masterbatch_Tipo", "Masterbatch_Pct"), ("Densidade (g/cm³)", "Densidade_Corpo_g_cm3", None), ("Barreira / revestimento", "Barreira_Revestimento", None),
        ("Massa do corpo (g)", "Massa_Corpo_g", "Origem_Massa"),
        ("3. FECHO", None, None), ("Tampa (ID) / material", "ID_Tampa", "Material_Tampa"), ("Massa da tampa (g)", "Massa_Tampa_g", None), ("Vedante / liner / válvula", "Vedante_Tampa", None),
        ("4. RÓTULO / MANGA", None, None), ("Tipo de rótulo", "Rotulo_Tipo", "Origem_Rotulo"), ("Adesivo", "Rotulo_Adesivo", None), ("Cobertura da superfície", "Rotulo_Cobertura_Pct", None),
        ("Massa do rótulo (g)", "Massa_Rotulo_g", None),
        ("5. DECORAÇÃO DIRETA", None, None), ("Tipo / n.º de cores", "Decoracao_Tipo", "Decoracao_N_Cores"), ("Massa de tinta/metalização (g)", "Massa_Decoracao_g", None),
        ("6. RESULTADO CALCULADO", None, None), ("Classe RecyClass", "Classe_RecyClass", "Ponto_Critico"), ("Recomendação", "Recomendacao", None),
        ("Taxa de reciclabilidade (massa)", "Taxa_Reciclabilidade", "Grau_Taxa"), ("Grau PPWR indicativo", "Grau_PPWR_Indicativo", "Isencao_Art6"),
        ("Conforme 2030 / 2038", "Conforme_PPWR_2030", "Conforme_PPWR_2038"), ("Conteúdo reciclado / meta 2030", "Conteudo_Reciclado_Pct", "Meta_2030"),
        ("Estrutura", "Estrutura_Material", None), ("Países / requisitos aplicáveis", "Paises_Venda", "N_Requisitos_Aplicaveis"),
    ]
    r = 6
    for lab, c1, c2 in campos:
        a = ws.cell(row=r, column=1, value=lab)
        if c1 is None:
            a.font = F_BOLD
            for j in (1, 2, 3):
                ws.cell(row=r, column=j).fill = FILL_BAND
        else:
            a.font, a.border = F_BASE, BORDER
            for j, cn in ((2, c1), (3, c2)):
                if cn:
                    c = ws.cell(row=r, column=j, value=f'=IFERROR(INDEX({b.ref("tbl_recyclass", cn)},MATCH($B$4,{b.ref("tbl_recyclass", "ProductId")},0)),"")')
                    c.font, c.border, c.alignment = F_BASE, BORDER, WRAP_TOP
                    if cn.endswith("Pct") or cn in ("Taxa_Reciclabilidade", "Meta_2030"):
                        c.number_format = "0%"
        r += 1
    ws.cell(row=r + 1, column=1, value="Nota").font = F_BOLD
    ws.cell(row=r + 1, column=2, value="A classificação oficial é a da ferramenta RecyClass (ou da certificação). Diferenças indicam regras a recalibrar em tbl_regras_dfr. Os critérios de DfR do PPWR (atos delegados) prevalecem quando publicados.").alignment = WRAP_TOP


def postprocess(path):
    """Tabela dinâmica e segmentações no Painel (Excel COM)."""
    import win32com.client as w32
    xl = w32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    wb = xl.Workbooks.Open(os.path.abspath(path))
    try:
        ws = wb.Worksheets("Painel")
        r = 1
        while not str(ws.Cells(r, 1).Value or "").startswith("ANÁLISE DINÂMICA"):
            r += 1
        prow = r + 3
        lo = wb.Worksheets("Avaliacao_RecyClass").ListObjects("tbl_recyclass")
        pc = wb.PivotCaches().Create(1, lo.Name, 6)
        pt = pc.CreatePivotTable(ws.Range(f"A{prow}"), "pvt_recyclass", True, 6)
        pt.PivotFields("Fluxo_Reciclagem").Orientation = 1
        pt.PivotFields("Material_Corpo").Orientation = 1
        pt.PivotFields("Classe_RecyClass").Orientation = 2
        pt.AddDataField(pt.PivotFields("ProductId"), "N.º de SKUs", -4112)
        pt.RowAxisLayout(1)
        pt.PivotCache().RefreshOnFileOpen = True
        pt.TableStyle2 = "PivotStyleLight16"
        left = ws.Range("G1").Left
        top = ws.Range(f"G{prow}").Top
        for k, (fld, cap) in enumerate((("Segmento", "Segmento"), ("Decoracao_Tipo", "Decoração"), ("Grau_PPWR_Indicativo", "Grau PPWR"),
                                         ("Cor_Corpo", "Cor do corpo"), ("Conforme_PPWR_2030", "Conforme 2030"), ("Estrutura_Material", "Estrutura"))):
            sc = wb.SlicerCaches.Add2(pt, fld)
            sc.CrossFilterType = 4
            sl = sc.Slicers.Add(ws)
            sl.Name, sl.Caption = f"slc_{fld}", cap
            sl.Top, sl.Left, sl.Width, sl.Height = top + (k // 3) * 175, left + (k % 3) * 165, 155, 165
        wb.Worksheets("00_LEIA-ME").Activate()
        wb.Save()
    finally:
        wb.Close(False)
        xl.Quit()


if __name__ == "__main__":
    import sys
    import recalc
    p = build(sys.argv[1])
    recalc.recalc([p])
    postprocess(p)
    n, e = recalc.check(p)
    print(p, n, "fórmulas", len(e), "erros", e[:10])
    print(resumo())
