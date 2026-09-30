"""Biblioteca comum dos registos do SGQ da Plasticom (NP EN ISO 9001:2026).

Reutiliza a biblioteca do SGA (../../SGA_Sistema-de-gestao-ambiental/_build/sgalib.py) para que os dois
sistemas do SGI tenham exatamente as mesmas convenções:
- cada registo é uma Tabela Excel (ListObject) com uma linha por registo, sem células mescladas;
- colunas calculadas com cabeçalho cinzento e fórmula Excel;
- listas controladas na folha "Listas" (nomes lst_*), "00_LEIA-ME" com controlo documental e "Dicionario_Dados".
Só muda o texto do SGQ (norma, índice, local do repositório) e a data de referência.
"""
import os
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SGA_BUILD = os.path.abspath(os.path.join(HERE, "..", "..", "SGA_Sistema-de-gestao-ambiental", "_build"))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SGA_BUILD not in sys.path:
    sys.path.append(SGA_BUILD)   # no FIM: os build_NN do SGQ têm prioridade sobre os homónimos do SGA

import sgalib as _sga  # noqa: E402
from sgalib import (col, form_block, header_row, Font, PatternFill, Alignment, Border, Side, get_column_letter,  # noqa: E402,F401
                    Table, TableStyleInfo, DataValidation, FormulaRule, DefinedName, Comment,
                    F_BASE, F_BOLD, F_HEAD, F_TITLE, F_SUB, F_LINK, FILL_HEAD, FILL_HEAD_CALC, FILL_CALC, FILL_BAND,
                    WRAP_TOP, CENTER, NUMFMT, CF_COLORS, BORDER, FONT, C_HEAD, C_TITLE)

EMPRESA = _sga.EMPRESA
NORMA = "NP EN ISO 9001:2026"
DATA_REF = dt.date(2026, 12, 31)         # data de referência do SGQ: fecho do ano de 2026 (a revisão pela gestão foi em 28/09/2026)
PER_INI, PER_FIM = "2025-07-01", "2026-12-31"   # período de dados do dataset usado nos registos (18 meses fechados)
AUTOR = "Gerente da Qualidade"
APROVADOR = "Diretor Geral"


class Book(_sga.Book):
    """Livro de registo do SGQ (mesma API do SGA)."""

    def __init__(self, code, title, activities, clauses, purpose, links=None, version="01",
                 elaborated=AUTOR, approved=APROVADOR, date=DATA_REF, retention="5 anos após substituição",
                 guidance=None):
        super().__init__(code, title, activities, clauses, purpose, links=links, version=version,
                         elaborated=elaborated, approved=approved, date=date, retention=retention)
        self.lists["DataReferencia"] = [DATA_REF]
        self.guidance = guidance or []   # [(norma/fonte, como foi aplicada)]

    def table(self, *a, **k):
        ws = super().table(*a, **k)
        t = self.tables[a[1] if len(a) > 1 else k["table_name"]]
        for c in ws[t["hr"]]:
            if c.comment is not None:
                c.comment = Comment(c.comment.text, "SGQ")
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
        ws["A2"] = f"Sistema de Gestão da Qualidade {NORMA} · {EMPRESA} · Registo do SGQ (fábrica simulada)"
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
        kv("Localização", "Repositório controlado do SGQ > Registos_SGQ_Plasticom (a versão eletrónica é a controlada; cópias impressas são não controladas). "
                          "Proteção contra alterações não intencionais (7.5.3.2): edição só pelo dono do registo; histórico de versões no repositório.")
        r += 1
        band("FINALIDADE E ÂMBITO")
        kv("Finalidade", m["purpose"])
        kv("Utilização / atividades", m["activities"])
        kv("Requisitos ISO 9001:2026", m["clauses"])
        if self.guidance:
            r += 1
            band("REFERÊNCIAS DE BOAS PRÁTICAS APLICADAS (orientação — não são requisitos auditáveis da ISO 9001)")
            for k_, v_ in self.guidance:
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
        kv("Chaves", "IDs estáveis e únicos (PK) e referências a IDs de outros registos (FK) permitem juntar tabelas entre ficheiros do SGQ e do SGA — ver SGQ-00_Indice_Modelo_Dados.xlsx.")
        kv("Datas e unidades", f"Datas em formato data (aaaa-mm-dd); números como números; a unidade está no nome da coluna ou no dicionário. Data de referência do SGQ: {DATA_REF:%Y-%m-%d}.")
        kv("Dados", f"Fábrica simulada Plasticom. Dados operacionais e de qualidade extraídos do dataset do projeto (datasets/silver e datasets/dim, período {PER_INI} a {PER_FIM}); "
                    "os campos de gestão que o dataset não tem (datas de resposta, avaliações, decisões) são simulação didática coerente com esses dados.")
        if m["links"]:
            r += 1
            band("LIGAÇÕES A OUTROS REGISTOS")
            for k_, v_ in m["links"]:
                kv(k_, v_)

    def save(self, path):
        """Igual ao SGA, mas com as propriedades do ficheiro do SGQ."""
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
        self.wb.properties.subject = f"SGQ {NORMA} — Plasticom"
        self.wb.save(path)
        return path


def doc_header(ws, code, title, model, ncols, version="01", date=DATA_REF):
    ws["A1"] = "PLASTICOM"
    ws["A1"].font = Font(name=FONT, size=16, bold=True, color=C_HEAD)
    mid = max(2, ncols // 2 - 1)
    ws.cell(row=1, column=mid, value=title).font = Font(name=FONT, size=13, bold=True, color=C_TITLE)
    ws.cell(row=1, column=ncols, value=model).font = F_BOLD
    ws.cell(row=2, column=ncols, value=f"Rev. {version} · {date:%d/%m/%Y}").font = F_BASE
    ws.cell(row=2, column=mid, value=f"{EMPRESA} · {NORMA}").font = F_SUB
    for c in range(1, ncols + 1):
        ws.cell(row=3, column=c).border = Border(bottom=Side(style="medium", color=C_HEAD))


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = F_TITLE
    if sub:
        ws["A2"] = sub
        ws["A2"].font = F_SUB


def cell(ws, r, c, v, fmt=None, bold=False, fill=None, wrap=True, border=True):
    x = ws.cell(row=r, column=c, value=v)
    x.font = F_BOLD if bold else F_BASE
    if wrap:
        x.alignment = WRAP_TOP
    if border:
        x.border = BORDER
    if fmt:
        x.number_format = fmt
    if fill:
        x.fill = fill
    return x


def rows_from(names, tuples, dates=()):
    """Converte tuplos em dicionários pela ordem das colunas de entrada; converte colunas de datas ISO."""
    out = []
    for t in tuples:
        d = dict(zip(names, t))
        for k in dates:
            v = d.get(k)
            d[k] = dt.date.fromisoformat(v) if isinstance(v, str) and v and v[0].isdigit() else (None if isinstance(v, str) else v)
        out.append(d)
    return out


def input_names(cols):
    return [c["name"] for c in cols if not c["f"]]


def fix_chart(ch, smooth=False):
    """Eixos visíveis, uma cor por série e linhas sem suavização (predefinições do openpyxl escondem os eixos no Excel recente)."""
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.varyColors = False
    for s in ch.series:
        if hasattr(s, "smooth"):
            s.smooth = smooth
    return ch
