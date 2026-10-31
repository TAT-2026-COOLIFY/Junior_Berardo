import io
from fpdf import FPDF
from backend.models import Produto


class PremiArtePDF(FPDF):
    def __init__(self, titulo_relatorio):
        super().__init__()
        self.titulo_relatorio = titulo_relatorio

    def header(self):
        self.set_fill_color(46, 29, 117)
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 218, 45)
        self.set_font("Arial", "B", 18)
        self.cell(
            0,
            8,
            "PREMIARTE AÇAÍ".encode(
                'latin-1',
                'replace'
            ).decode('latin-1'),
            align='C'
        )
        self.ln(8)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "I", 10)
        self.cell(
            0,
            4,
            "Sistema de Gestão Financeira Integrado".encode(
                'latin-1',
                'replace'
            ).decode('latin-1'),
            align='C'
        )
        self.ln(6)
        self.set_font("Arial", "B", 11)
        self.cell(
            0,
            5,
            self.titulo_relatorio.encode(
                'latin-1',
                'replace'
            ).decode('latin-1'),
            align='C'
        )
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(178, 190, 195)
        self.cell(
            0,
            10,
            f"Página {self.page_no()}".encode(
                'latin-1',
                'replace'
            ).decode('latin-1'),
            align='C'
        )


def gerar_pdf_vendas(vendas, titulo):
    total_periodo = sum(
        v.valor_total
        for v in vendas
    )

    pdf = PremiArtePDF(titulo)
    pdf.add_page()
    pdf.ln(15)

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(92, 70, 193)
    pdf.set_text_color(255, 255, 255)

    pdf.cell(
        40,
        10,
        "Data da Venda",
        border=1,
        align='C',
        fill=True
    )

    pdf.cell(
        60,
        10,
        "Produto",
        border=1,
        align='C',
        fill=True
    )

    pdf.cell(
        50,
        10,
        "Método de Pagamento".encode(
            'latin-1',
            'replace'
        ).decode('latin-1'),
        border=1,
        align='C',
        fill=True
    )

    pdf.cell(
        40,
        10,
        "Valor Faturado",
        border=1,
        align='C',
        fill=True
    )

    pdf.ln()

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(45, 52, 54)

    cor_alternada = False

    for v in vendas:

        produtos_venda = []

        for item in v.itens:

            produto = (
                Produto.query
                .filter_by(
                    idProduto=item.produto_id
                )
                .first()
            )

            if produto:
                produtos_venda.append(
                    produto.nome
                )

        if produtos_venda:
            nomes_produtos = ", ".join(
                produtos_venda
            )
        else:
            nomes_produtos = "Produto não informado"

        nomes_produtos = (
            nomes_produtos
            .encode('latin-1', 'replace')
            .decode('latin-1')
        )

        pdf.set_fill_color(
            248,
            248,
            252
        ) if cor_alternada else pdf.set_fill_color(
            255,
            255,
            255
        )

        pdf.cell(
            40,
            8,
            v.data.strftime(
                '%d/%m/%Y - %H:%M'
            ),
            border=1,
            align='C',
            fill=True
        )

        pdf.cell(
            60,
            8,
            nomes_produtos,
            border=1,
            align='C',
            fill=True
        )

        pdf.cell(
            50,
            8,
            str(
                v.metodo_pagamento or ''
            ).encode(
                'latin-1',
                'replace'
            ).decode('latin-1'),
            border=1,
            align='C',
            fill=True
        )

        pdf.cell(
            40,
            8,
            f"R$ {v.valor_total:.2f}",
            border=1,
            align='R',
            fill=True
        )

        pdf.ln()

        cor_alternada = not cor_alternada

    if not vendas:
        pdf.cell(
            190,
            10,
            "Nenhuma venda registrada no período selecionado.".encode(
                'latin-1',
                'replace'
            ).decode('latin-1'),
            border=1,
            align='C'
        )
        pdf.ln()

    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(46, 29, 117)

    pdf.cell(
        100,
        10,
        f"Quantidade de vendas: {len(vendas)}".encode(
            'latin-1',
            'replace'
        ).decode('latin-1'),
        align='L'
    )

    pdf.set_fill_color(255, 218, 45)

    pdf.cell(
        90,
        10,
        f"TOTAL ACUMULADO: R$ {total_periodo:.2f}",
        border=1,
        align='C',
        fill=True
    )

    pdf_bytes = pdf.output()

    return io.BytesIO(
        pdf_bytes
        if isinstance(pdf_bytes, bytes)
        else bytes(pdf_bytes)
    )
