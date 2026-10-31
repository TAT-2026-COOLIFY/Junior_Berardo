import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-estoque',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './estoque.component.html',
    styleUrls: ['./estoque.component.css']
})
export class EstoqueComponent implements OnInit {

    produtos: any[] = [];
    categorias: any[] = [];
    categorias_com_produtos: any[] = [];
    fornecedores: any[] = [];
    movimentacoes: any[] = [];
    giroEstoque: any[] = [];

    produtoMenuAberto: number | null = null;

    novaMovimentacao = {
        produto_id: null as number | null,
        tipo: 'ENTRADA',
        quantidade: 0,
        validade: '',
        motivo: '',
        observacao: ''
    };

    novoProduto = {
        nome: '',
        quantidade: 0,
        preco: 0,
        categoria_id: 1,
        fornecedor_id: null as number | null
    };

    constructor(private apiService: ApiService) {}

    ngOnInit(): void {
        this.recarregarTodosOsDados();
    }

    recarregarTodosOsDados(): void {
        this.carregarCategorias();
        this.carregarFornecedores();
        this.carregarEstoque();
        this.carregarMovimentacoes();
        this.carregarGiroEstoque();
    }

    // LEITURA DE DADOS

    carregarCategorias(): void {
        this.apiService.getCategoriasEstoque().subscribe({
            next: (res: any) => {
                const listaGeral = res?.categorias || res || [];

                if (listaGeral.length > 0) {
                    this.categorias = listaGeral.map((c: any) => ({
                        id: c.idCategoria || c.id,
                        idCategoria: c.idCategoria || c.id,
                        nome: c.nome || c.categoria,
                        tipo: c.tipo
                    }));

                    if (!this.categorias_com_produtos || this.categorias_com_produtos.length === 0) {
                        this.categorias_com_produtos = this.categorias.map((c: any) => ({
                            id: c.id,
                            categoria: c.nome,
                            produtos: []
                        }));
                    }

                    if (this.categorias.length > 0 && !this.novoProduto.categoria_id) {
                        this.novoProduto.categoria_id = this.categorias[0].id;
                    }
                }
            },
            error: (err: any) => console.error('Erro ao carregar categorias:', err)
        });
    }

    carregarFornecedores(): void {
        this.apiService.getFornecedores().subscribe({
            next: (res: any) => {
                if (res?.sucesso) {
                    this.fornecedores = res.fornecedores || [];
                }
            },
            error: (err: any) => console.error('Erro ao carregar fornecedores:', err)
        });
    }

    carregarEstoque(): void {
        this.apiService.getEstoque().subscribe({
            next: (res: any) => {
                let dadosAgrupados: any[] = [];

                if (Array.isArray(res)) {
                    dadosAgrupados = res;
                } else if (res?.sucesso && Array.isArray(res.produtos)) {
                    dadosAgrupados = res.produtos;
                } else if (res?.produtos && Array.isArray(res.produtos)) {
                    dadosAgrupados = res.produtos;
                } else if (res?.estoque && Array.isArray(res.estoque)) {
                    dadosAgrupados = res.estoque;
                }

                if (dadosAgrupados && dadosAgrupados.length > 0) {
                    this.categorias_com_produtos = dadosAgrupados;

                    this.produtos = dadosAgrupados.reduce((acumulador: any, bloco: any) => {
                        const listaItens = bloco.produtos || bloco.itens || [];
                        return acumulador.concat(listaItens);
                    }, []);

                    if (this.categorias_com_produtos.length > 0 && this.categorias_com_produtos[0]) {
                        this.novoProduto.categoria_id = this.categorias_com_produtos[0].id;
                    }

                    if (this.novaMovimentacao.produto_id === null && this.produtos.length > 0) {
                        const primProd = this.produtos[0];
                        this.novaMovimentacao.produto_id = primProd.id || primProd.idProduto;
                    }
                }
            },
            error: (err: any) => console.error('Erro crítico ao carregar dados estruturados de estoque:', err)
        });
    }

    carregarMovimentacoes(): void {
        this.apiService.listarMovimentacoes().subscribe({
            next: (res: any) => {
                if (res?.sucesso) {
                    this.movimentacoes = res.movimentacoes || [];
                }
            },
            error: (err: any) => console.error('Erro ao carregar movimentações:', err)
        });
    }

    carregarGiroEstoque(): void {
        this.apiService.getGiroEstoque().subscribe({
            next: (res: any) => {
                if (res?.sucesso) {
                    this.giroEstoque = Array.isArray(res.giro) ? res.giro : [];
                } else {
                    this.giroEstoque = [];
                }
            },
            error: (err: any) => {
                this.giroEstoque = [];
                console.error('Erro ao carregar giro de estoque:', err);
            }
        });
    }


    // REGRAS E AUXILIARES DE PRODUTO E MOVIMENTAÇÃO


    getProdutosPorCategoria(catId: number): any[] {
        return this.produtos.filter((p: any) => (p.categoria_id === catId));
    }

    abrirMenuProduto(id: number): void {
        this.produtoMenuAberto = this.produtoMenuAberto === id ? null : id;
    }

    alterarTipoMovimentacao(): void {
        if (this.novaMovimentacao.tipo !== 'QUEBRA') {
            this.novaMovimentacao.motivo = '';
        }
    }

    cadastrarProduto(): void {
        if (!this.novoProduto.nome.trim()) {
            alert('Informe o nome do insumo.');
            return;
        }

        this.apiService.cadastrarProdutoEstoque(this.novoProduto).subscribe({
            next: (res: any) => {
                alert('Insumo adicionado com sucesso!');
                this.novoProduto.nome = '';
                this.carregarEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao cadastrar produto de estoque.')
        });
    }

    registrarMovimentacao(): void {
        if (!this.novaMovimentacao.produto_id) {
            alert('Selecione um produto.');
            return;
        }

        this.apiService.registrarMovimentacao(this.novaMovimentacao).subscribe({
            next: (res: any) => {
                alert('Movimentação registrada!');
                this.novaMovimentacao.quantidade = 0;
                this.novaMovimentacao.validade = '';
                this.novaMovimentacao.motivo = '';
                this.novaMovimentacao.observacao = '';
                this.carregarEstoque();
                this.carregarMovimentacoes();
                this.carregarGiroEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao processar movimentação manual.')
        });
    }

    alterarQuantidadeProduto(produto: any): void {
        this.produtoMenuAberto = null;

        const qtdAtual = Number(produto.quantidade || 0);

        const novaQtdTxt = prompt(
            `Digite a nova quantidade para "${produto.nome}":`,
            qtdAtual.toString()
        );

        if (novaQtdTxt === null) return;

        const novaQtd = Number(novaQtdTxt.replace(',', '.'));

        if (!Number.isFinite(novaQtd) || novaQtd < 0) {
            alert('Informe uma quantidade válida.');
            return;
        }

        if (novaQtd === qtdAtual) return;

        const diferenca = novaQtd - qtdAtual;
        const tipoMov = diferenca > 0 ? 'ENTRADA' : 'SAIDA';

        this.apiService.registrarMovimentacao({
            produto_id: Number(produto.id || produto.idProduto),
            tipo: tipoMov,
            quantidade: Math.abs(diferenca),
            validade: '',
            motivo: 'Correção de quantidade em estoque',
            observacao: `Quantidade corrigida de ${qtdAtual} para ${novaQtd}.`
        }).subscribe({
            next: (res: any) => {
                alert('Quantidade atualizada com sucesso!');
                this.carregarEstoque();
                this.carregarMovimentacoes();
                this.carregarGiroEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao salvar correção.')
        });
    }


    // OPERAÇÕES COMPLEMENTARES


    criarCategoria(): void {
        const nomeCategoria = prompt('Digite o nome da nova categoria:');

        if (nomeCategoria === null) return;

        const nome = nomeCategoria.trim();

        if (!nome) {
            alert('Informe o nome da categoria.');
            return;
        }

        this.apiService.cadastrarCategoria({
            nome: nome,
            tipo: 'ESTOQUE'
        }).subscribe({
            next: (res: any) => {
                alert('Categoria de estoque adicionada!');
                this.carregarCategorias();
                this.carregarEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao criar categoria.')
        });
    }

    excluirCategoria(id: number, nome: string): void {
        if (!confirm(`Deseja realmente excluir a categoria "${nome}"?`)) {
            return;
        }

        this.apiService.deletarCategoria(id).subscribe({
            next: (res: any) => {
                alert('Categoria removida com sucesso!');
                this.carregarCategorias();
                this.carregarEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao excluir categoria.')
        });
    }

    excluirProduto(id: number): void {
        if (!confirm('Deseja realmente excluir este insumo do estoque?')) {
            return;
        }

        this.apiService.deletarProdutoEstoque(id).subscribe({
            next: (res: any) => {
                alert('Insumo removido com sucesso!');
                this.carregarEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao excluir insumo.')
        });
    }
}
