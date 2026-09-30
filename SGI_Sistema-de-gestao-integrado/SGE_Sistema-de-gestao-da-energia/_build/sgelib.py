"""Biblioteca comum dos registos do SGE da Plasticom (NP EN ISO 50001:2019 = ISO 50001:2018 + Amd 1:2024; ISO 50006:2023).

Reutiliza a biblioteca do SGA (../../SGA_Sistema-de-gestao-ambiental/_build/sgalib.py) e as utilidades do SGQ
(../../SGI_Sistema-de-gestao-da-qualidade/_build/sgqlib.py) para que os três sistemas do SGI tenham as mesmas convenções:
- cada registo é uma Tabela Excel (ListObject) com uma linha por registo, sem células mescladas;
- colunas calculadas com cabeçalho cinzento e fórmula Excel;
- listas controladas na folha "Listas" (nomes lst_*), "00_LEIA-ME" com controlo documental e "Dicionario_Dados".
O LEIA-ME do SGE cita, em cada registo, os requisitos da ISO 50001, as normas de orientação e os requisitos legais usados.
"""
import os
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SGI = os.path.abspath(os.path.join(HERE, "..", ".."))
SGA_BUILD = os.path.join(SGI, "SGA_Sistema-de-gestao-ambiental", "_build")
SGQ_BUILD = os.path.join(SGI, "SGI_Sistema-de-gestao-da-qualidade", "_build")
SGA_REG = os.path.join(SGI, "SGA_Sistema-de-gestao-ambiental", "Registos_SGA_Plasticom")
SGQ_REG = os.path.join(SGI, "SGI_Sistema-de-gestao-da-qualidade", "Registos_SGQ_Plasticom")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
for p in (SGQ_BUILD, SGA_BUILD):   # no FIM: os build_NN do SGE têm prioridade sobre os homónimos do SGQ/SGA
    if p not in sys.path:
        sys.path.append(p)

import sgalib as _sga  # noqa: E402
from sgalib import (col, form_block, header_row, Font, PatternFill, Alignment, Border, Side, get_column_letter,  # noqa: E402,F401
                    Table, TableStyleInfo, DataValidation, FormulaRule, DefinedName, Comment,
                    F_BASE, F_BOLD, F_HEAD, F_TITLE, F_SUB, F_LINK, FILL_HEAD, FILL_HEAD_CALC, FILL_CALC, FILL_BAND,
                    WRAP_TOP, CENTER, NUMFMT, CF_COLORS, BORDER, FONT, C_HEAD, C_TITLE)
from sgqlib import title, cell, rows_from, input_names, fix_chart  # noqa: E402,F401

EMPRESA = _sga.EMPRESA
NORMA = "NP EN ISO 50001:2019 (ISO 50001:2018 + Amd 1:2024)"
NORMA_CURTA = "ISO 50001:2018"
DATA_REF = dt.date(2026, 12, 31)         # data de referência do SGE: fecho do ano de 2026 (1.ª revisão pela gestão e auditoria já realizadas)
PER_INI, PER_FIM = "2025-03-01", "2026-12-31"   # período dos dados de energia: RG-SGA-13 (fonte única) mar/2025–dez/2026
LBE_INI, LBE_FIM = "2025-03-01", "2026-02-28"   # período de referência da LBE (12 meses, antes dos compressores VSD)
REP_INI, REP_FIM = "2026-03-01", "2026-12-31"   # período de reporte
AUTOR = "Gestor(a) de Energia"
APROVADOR = "Diretor Geral"

NUMFMT.setdefault("kwh", "#,##0")


class Book(_sga.Book):
    """Livro de registo do SGE (mesma API do SGA e do SGQ)."""

    def __init__(self, code, title, activities, clauses, purpose, links=None, version="01",
                 elaborated=AUTOR, approved=APROVADOR, date=DATA_REF, retention="5 anos após substituição",
                 guidance=None, legal=None):
        super().__init__(code, title, activities, clauses, purpose, links=links, version=version,
                         elaborated=elaborated, approved=approved, date=date, retention=retention)
        self.lists["DataReferencia"] = [DATA_REF]
        self.guidance = guidance or []   # [(norma/fonte, como foi aplicada)]
        self.legal = legal or []         # [(diploma, obrigação aplicada)]

    def table(self, *a, **k):
        ws = super().table(*a, **k)
        t = self.tables[a[1] if len(a) > 1 else k["table_name"]]
        for c in ws[t["hr"]]:
            if c.comment is not None:
                c.comment = Comment(c.comment.text, "SGE")
        return ws

    def sheet(self, name, description, tab_color=None):
        ws = super().sheet(name, description, tab_color)
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        return ws

    def _write_readme(self):
        ws = self.readme
        ws.sheet_view.showGridLines = False
        ws.sheet_properties.tabColor = C_HEAD
        ws.column_dimensions["A"].width = 30
        ws.column_dimensions["B"].width = 110
        ws["A1"] = f"{self.code} — {self.title}"
        ws["A1"].font = F_TITLE
        ws["A2"] = f"Sistema de Gestão da Energia {NORMA} · {EMPRESA} · Registo do SGE (fábrica simulada)"
        ws["A2"].font = F_SUB
        r = 4

        def band(text):
            nonlocal r
            ws.cell(row=r, column=1, value=text).font = F_BOLD
            for c in (1, 2):
                ws.cell(row=r, column=c).fill = FILL_BAND
            r += 1

        def kv(k, v):
            nonlocal r
            a = ws.cell(row=r, column=1, value=k)
            a.font, a.alignment = F_BOLD, WRAP_TOP
            b = ws.cell(row=r, column=2, value=v)
            b.font, b.alignment = F_BASE, WRAP_TOP
            if isinstance(v, (dt.date, dt.datetime)):
                b.number_format = "yyyy-mm-dd"
                b.alignment = Alignment(horizontal="left", vertical="top")
            r += 1

        m = self.meta
        band("CONTROLO DO DOCUMENTO (7.5 — informação documentada)")
        kv("Código do registo", self.code)
        kv("Título", self.title)
        kv("Versão / Revisão", m["version"])
        kv("Data de emissão", m["date"])
        kv("Elaborado por", m["elaborated"])
        kv("Aprovado por", m["approved"])
        kv("Estado", "Em vigor")
        kv("Retenção", m["retention"])
        kv("Localização", "Repositório controlado do SGE > Registos_SGE_Plasticom (a versão eletrónica é a controlada; cópias impressas são não controladas). "
                          "Controlo da informação documentada comum ao SGI: PR-SGA-08 (7.5.3 — distribuição, acesso, versão, retenção).")
        r += 1
        band("FINALIDADE E ÂMBITO")
        kv("Finalidade", m["purpose"])
        kv("Utilização / atividades", m["activities"])
        kv("Requisitos ISO 50001:2018", m["clauses"])
        if self.guidance:
            r += 1
            band("NORMAS DE ORIENTAÇÃO E REFERÊNCIAS APLICADAS (orientação — não são requisitos auditáveis da ISO 50001)")
            for k_, v_ in self.guidance:
                kv(k_, v_)
        if self.legal:
            r += 1
            band("REQUISITOS LEGAIS E OUTROS REQUISITOS APLICADOS (4.2, 9.1.2 — lista completa no RG-SGE-11)")
            for k_, v_ in self.legal:
                kv(k_, v_)
        r += 1
        band("ESTRUTURA DO FICHEIRO")
        for s, d in self.sheets_info:
            kv(s, d)
        kv("Dicionario_Dados", "Descrição de cada coluna de cada tabela: tipo, origem (entrada/calculado), domínio, obrigatoriedade e chaves.")
        r += 1
        band("CONVENÇÕES (prontas para análise de dados e machine learning)")
        kv("Tabelas", "Cada registo é uma Tabela Excel com nome próprio (tbl_*): uma linha = um registo, cabeçalho único, sem células mescladas. Ler com pandas "
                      "(pd.read_excel(ficheiro, sheet_name=folha, header=<linha do cabeçalho - 1>)) ou Power BI (Obter Dados > Tabela).")
        kv("Cabeçalho cinzento", "Coluna CALCULADA por fórmula — não escrever por cima. As restantes colunas são de entrada.")
        kv("Validação", "Colunas com lista controlada só aceitam valores da folha Listas (evita categorias duplicadas por grafia diferente).")
        kv("Chaves", "IDs estáveis e únicos (PK) e referências a IDs de outros registos (FK) permitem juntar tabelas entre ficheiros do SGE, do SGA e do SGQ — ver SGE-00_Indice_Modelo_Dados.xlsx.")
        kv("Datas e unidades", f"Datas em formato data (aaaa-mm-dd); energia em kWh (MWh quando indicado); a unidade está no nome da coluna ou no dicionário. Data de referência do SGE: {DATA_REF:%Y-%m-%d}.")
        kv("Dados", f"Fábrica simulada Plasticom. Eletricidade mensal por uso: fonte única RG-SGA-13 (tbl_dados_ambientais, mar/2025 a dez/2026, "
                    "já com o efeito das ações de energia de out–dez/2026). Produção e horas de marcha por máquina: "
                    "dataset do projeto (datasets/silver). Dados que o dataset não tem (campanha de medição por máquina, faturas por período tarifário, gasóleo, "
                    "compressores, SGCIE) são simulação didática coerente com esses dados e estão marcados como tal.")
        if m["links"]:
            r += 1
            band("LIGAÇÕES A OUTROS REGISTOS")
            for k_, v_ in m["links"]:
                kv(k_, v_)

    def save(self, path):
        """Igual ao SGA, mas com as propriedades do ficheiro do SGE."""
        self._write_lists()
        self._write_readme()
        self._write_dictionary()
        order = [self.readme] + [s for s in self.wb.worksheets if s.title not in ("00_LEIA-ME", "Listas", "Dicionario_Dados")]
        for n in ("Listas", "Dicionario_Dados"):
            if n in self.wb.sheetnames:
                order.append(self.wb[n])
        self.wb._sheets = order
        self.wb.active = 0
        for ws in self.wb.worksheets:
            ws.sheet_view.tabSelected = ws is self.readme
        self.wb.properties.creator = AUTOR
        self.wb.properties.title = f"{self.code} {self.title}"
        self.wb.properties.subject = f"SGE {NORMA} — Plasticom"
        self.wb.save(path)
        return path


def notes(ws, r, items, width_a=26, width_b=120):
    """Bloco de notas (rótulo | texto) numa folha de apresentação."""
    ws.column_dimensions["A"].width = max(ws.column_dimensions["A"].width or 0, width_a)
    for k_, v_ in items:
        a = ws.cell(row=r, column=1, value=k_)
        a.font, a.alignment = F_BOLD, WRAP_TOP
        b = ws.cell(row=r, column=2, value=v_)
        b.font, b.alignment = F_BASE, WRAP_TOP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=10)
        ws.row_dimensions[r].height = max(15, 15 * (1 + len(str(v_)) // 150))
        r += 1
    return r
