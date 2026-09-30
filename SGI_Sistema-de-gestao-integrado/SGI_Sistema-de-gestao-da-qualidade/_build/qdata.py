"""Acesso ao dataset do projeto (datasets/silver e datasets/dim) para os registos do SGQ.

Período: 2025-07-01 a 2026-08-31 (18 meses fechados até à data de referência 2026-12-31).
O estado de CAPA e reclamações é recalculado À DATA DE REFERÊNCIA: uma CAPA fechada no dataset depois de
31/12/2026 conta como aberta/atrasada no SGQ (o registo mostra o que se sabia nessa data).
"""
import os
import datetime as dt
import pandas as pd
from sgqlib import DATA_REF, PER_INI, PER_FIM

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SILVER = os.path.join(ROOT, "datasets", "silver")
DIM = os.path.join(ROOT, "datasets", "dim")
REF = pd.Timestamp(DATA_REF)

T_DEFEITO = {
    "Missing or Illegible Label": "Rótulo em falta ou ilegível",
    "Wrong Product Shipped": "Produto errado expedido",
    "Late Delivery": "Entrega atrasada",
    "Short Shipment (Quantity Shortfall)": "Quantidade inferior à encomendada",
    "Deformation/Collapsed Bottle": "Frasco deformado / colapsado",
    "Foreign Material / Contamination": "Material estranho / contaminação",
    "Broken/Cracked Cap": "Tampa partida / fissurada",
    "Bottle Leaking": "Frasco com fuga",
    "Weight Out of Specification": "Peso fora de especificação",
    "Wall Thickness Out of Specification": "Espessura de parede fora de especificação",
    "Incorrect Color": "Cor incorreta",
    "Cap Back-off (Reopens After Closing / Torque Retention Failure)": "Tampa desaperta após fecho (retenção de binário)",
    "Torque Too Low": "Binário de abertura demasiado baixo",
    "Torque Too High": "Binário de abertura demasiado alto",
    "Tamper Band Separation": "Separação do anel de inviolabilidade",
}
# natureza da reclamação: produto (qualidade) vs. serviço (logística/documentação)
NATUREZA = {k: ("Serviço / logística" if k in ("Late Delivery", "Short Shipment (Quantity Shortfall)", "Wrong Product Shipped", "Missing or Illegible Label") else "Produto")
            for k in T_DEFEITO}
T_SEV = {"Critical": "Crítica", "Major": "Maior", "Minor": "Menor"}
T_ORIGEM_NC = {"Lot Rejection": "Rejeição de lote (inspeção final)", "Incoming Inspection": "Inspeção de receção",
               "Lot Concession/Deviation": "Concessão / derrogação de lote", "Lot Rework": "Retrabalho de lote",
               "Customer Complaint": "Reclamação de cliente", "Customer Audit": "Auditoria de cliente"}
T_CAT_NC = {"In-Process Quality Deviation": "Desvio de qualidade em processo", "Decoration Quality Deviation": "Desvio de qualidade na decoração",
            "Raw Material Non-Conformance": "Não conformidade de matéria-prima", "Raw Material Deviation": "Desvio de matéria-prima",
            "Mold Wear": "Desgaste de molde", "Proactive Sampling Tightening": "Reforço preventivo da amostragem"}
T_AREA = {"Production": "Produção", "Supplier Quality": "Qualidade de fornecedores", "Quality": "Qualidade"}
T_CAUSA = {"Raw Material": "Material", "Machine/Equipment": "Máquina", "Method/Procedure": "Método", "Man (Operator)": "Mão de obra",
           "Mold/Tooling": "Molde / ferramenta", "Tooling / Mold Wear": "Molde / ferramenta", "Customer Requirement": "Requisito do cliente"}
T_EFIC = {"Effective": "Eficaz", "Not Effective": "Não eficaz", "Pending": "Por avaliar"}
T_TIPO_CAPA = {"Corrective": "Corretiva", "Preventive": "Preventiva"}
T_DISP = {"Approved - First Pass": "Aprovado à primeira", "Rejected - Scrapped": "Rejeitado — sucata",
          "Approved - Reworked": "Aprovado após retrabalho", "Rejected - Segregated": "Rejeitado — segregado para triagem",
          "Approved - Released on Deviation": "Aprovado por concessão"}
T_PROC = {"Injection Molding": "INJ", "Blow Molding": "SOP", "Screen Printing": "SER", "Hot Foil Stamping": "HFS"}
T_CARACT = {"Weight": "Peso", "Height": "Altura", "Neck Diameter": "Diâmetro do gargalo", "Thickness": "Espessura de parede",
            "Overflow Volume": "Volume de transbordo", "Leakage": "Estanquidade (fuga)", "Flash": "Rebarba", "Bubbles": "Bolhas",
            "Black Specks": "Pontos negros", "Stain": "Mancha", "Transparency": "Transparência", "Color": "Cor", "Burr": "Rebarba de corte",
            "Migration Test (Food Contact)": "Ensaio de migração (contacto alimentar)", "Mouth Diameter": "Diâmetro da boca",
            "Drop Test": "Ensaio de queda", "Stack Load": "Carga de empilhamento", "Diameter": "Diâmetro", "Torque": "Binário de abertura",
            "Thread": "Rosca", "Sealing": "Vedação", "Short Shot": "Injeção incompleta", "Tamper Band Separation": "Anel de inviolabilidade",
            "Registration": "Registo de impressão", "Centering": "Centragem", "Coverage": "Cobertura de tinta", "Smudge": "Borrão",
            "Pinholes": "Microfuros", "Adhesion": "Aderência", "Cure": "Cura", "Removal Force": "Força de remoção",
            "Foil Transfer": "Transferência do foil", "Foil Adhesion": "Aderência do foil", "Melt Flow Index": "Índice de fluidez (MFI)",
            "Density": "Densidade", "Moisture Content": "Humidade", "Tensile Strength at Yield": "Tensão de cedência",
            "Foreign Matter / Contamination": "Matéria estranha / contaminação"}
T_CLASSE = {"Critical": "Crítica", "Major": "Maior", "Minor": "Menor"}
T_EQUIP = {"Scale 0.01 g": "Balança 0,01 g", "Scale 0.001 g": "Balança analítica 0,001 g", "Caliper": "Paquímetro digital",
           "Gauge": "Calibre passa/não passa", "Thickness Gauge": "Medidor de espessura por ultrassons", "Graduated Cylinder": "Proveta graduada",
           "Leak Tester": "Equipamento de ensaio de estanquidade", "D65 Light Booth": "Cabine de luz D65", "Migration Test Cell": "Célula de migração",
           "ASTM D2463 Drop Rig": "Banco de ensaio de queda ASTM D2463", "Universal Testing Machine": "Máquina universal de ensaios",
           "Torque Wrench": "Torquímetro digital", "Tamper Band Tester": "Equipamento de ensaio do anel de inviolabilidade",
           "Registration Gauge": "Régua / calibre de registo", "Colorimeter": "Colorímetro", "Lupa 10x": "Lupa 10x",
           "ASTM D3359 Kit": "Kit de aderência ASTM D3359", "MEK Rub Test": "Kit de ensaio MEK", "Melt Indexer": "Plastómetro (MFI)",
           "Density Column": "Coluna de densidade", "Karl Fischer Titration": "Titulador Karl Fischer"}
T_REACAO = {"Adjust Parameters": "Ajustar parâmetros", "Adjust Mold": "Ajustar molde", "Block Lot": "Bloquear lote", "Adjust Process": "Ajustar processo",
            "Segregate": "Segregar", "Adjust Cleaning": "Reforçar limpeza", "Adjust Raw Material": "Rever matéria-prima", "Adjust Masterbatch": "Ajustar masterbatch",
            "Adjust Closure": "Ajustar fecho do molde", "Adjust Machine": "Ajustar máquina", "Adjust Pressure": "Ajustar pressão",
            "Change Masterbatch Lot": "Trocar lote de masterbatch", "Adjust Screen": "Ajustar ecrã", "Adjust Registration": "Ajustar registo",
            "Adjust Ink/Pressure": "Ajustar tinta / pressão", "Adjust Ink Formula": "Ajustar formulação da tinta", "Adjust Speed": "Ajustar velocidade",
            "Clean Screen": "Limpar ecrã", "Reprocess (UV Re-cure)": "Reprocessar (nova cura UV)", "Quarantine & Notify Supplier": "Quarentena e notificar fornecedor",
            "Reject Lot": "Rejeitar lote"}
T_FREQ = {"Every 30 min": "A cada 30 min", "Every 1 h": "A cada 1 h", "Every 2 h": "A cada 2 h", "Per lot": "Por lote", "Setup + 30 min": "No arranque + a cada 30 min",
          "Continuous": "Contínua", "Per incoming lot": "Por lote recebido"}
T_OWNER = {"Quality": "Qualidade", "Laboratory": "Laboratório", "Operator": "Operador"}


def rd(name, folder=SILVER, **k):
    return pd.read_csv(os.path.join(folder, name), low_memory=False, **k)


def periodo(df, col):
    d = pd.to_datetime(df[col].astype(str).str[:10])
    return df[(d >= PER_INI) & (d <= PER_FIM)].copy()


def to_date(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NaT:
        return None
    try:
        return pd.Timestamp(str(v)[:10]).date()
    except Exception:
        return None


def customers():
    return rd("dim_customer.csv", DIM)


def suppliers():
    return rd("dim_supplier.csv", DIM)


def production():
    return periodo(rd("fact_production_processed.csv"), "Date")


def sales():
    return periodo(rd("fact_sales_processed.csv"), "Date")


def complaints():
    c = periodo(rd("fact_customer_complaints_processed.csv"), "Date")
    c["Res"] = pd.to_datetime(c["ResolutionDate"])
    c.loc[c["Res"] > REF, "Res"] = pd.NaT       # ainda não resolvida à data de referência
    return c


def nonconformance():
    return periodo(rd("fact_nonconformance_processed.csv"), "Date")


def capa():
    c = periodo(rd("fact_capa_processed.csv"), "OpenDate")
    c["Close"] = pd.to_datetime(c["CloseDate"])
    c.loc[c["Close"] > REF, "Close"] = pd.NaT
    c["Due"] = pd.to_datetime(c["DueDate"])
    return c


def supplier_complaints():
    s = periodo(rd("fact_supplier_complaints_processed.csv"), "Date")
    s["Res"] = pd.to_datetime(s["DateResolved"])
    s.loc[s["Res"] > REF, "Res"] = pd.NaT
    return s


def rm_lots():
    return periodo(rd("fact_raw_material_lot_disposition_processed.csv"), "Date")


def lot_dispositions():
    """Decisões de libertação de lote (frascos, tampas, decoração) num só formato."""
    out = []
    b = periodo(rd("fact_bottle_disposition_lot_cq_processed.csv"), "ProductionDate")
    b["Familia"], b["Produto"], b["Lote"] = "Frasco", b["BottleId"], b["ProductBatch"]
    c = periodo(rd("fact_cap_disposition_lot_cq_processed.csv"), "ProductionDate")
    c["Familia"], c["Produto"], c["Lote"] = "Tampa / pote", c["CapId"], c["ProductBatch"]
    k = periodo(rd("fact_ink_disposition_lot_cq_processed.csv"), "ProductionDate")
    k["Familia"], k["Produto"], k["Lote"] = "Decoração", k["BottleId"], k["PrintLot"]
    k["VariablesDecision"] = "N/A"
    for d in (b, c, k):
        out.append(d[["Lote", "WorkOrder", "ProductionDate", "Shift", "MachineId", "Familia", "Produto", "LotSize", "CodeLetter", "SampleSize",
                      "CriticalDefects", "MajorDefects", "MinorDefects", "VariablesDecision", "AttributesDecision", "FinalLotDecision",
                      "DispositionDetail", "LotDecisionDateTime", "Remarks", "Inspector", "LotId"]])
    return pd.concat(out, ignore_index=True).sort_values(["ProductionDate", "Lote"]).reset_index(drop=True)


def monthly(df, col):
    return pd.to_datetime(df[col].astype(str).str[:10]).dt.strftime("%Y-%m")
