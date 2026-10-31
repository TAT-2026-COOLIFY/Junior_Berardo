import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-vendas',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './vendas.component.html',
    styleUrls: ['./vendas.component.css']
})
export class VendasComponent implements OnInit {

    produtos: any[] = [];
    categorias: any[] = [];

    produtosEstoque: any[] = [];
    categoriasEstoque: any[] = [];

    clientes: any[] = [];
    carrinho: any[] = [];

    termoBusca: string = '';
    metodoPagamento: string = 'Dinheiro';
    clienteSelecionadoId: number | null = null;

    modalAberto: boolean = false;
    modalClienteAberto: boolean = false;
    modalOpcoesAberto: boolean = false;

    // Lógica de Recheios
    modalRecheiosAberto: boolean = false;
    produtoAcaiAtual: any = null;
    listaDeRecheiosDinamica: any[] = [];

    // Edição / Controle de Menus
    produtoSelecionado: any = null;
    produtoMenuAberto: number | null = null;

    // Variáveis de Edição
    modalEditarAberto: boolean = false;
    produtoEmEdicao: any = { id: null, nome: '', preco: 0, ingredientes: '' };

    cpfInvalido: boolean = false;
    telefoneInvalido: boolean = false;

    novoProduto: any = {
        nome: '',
        categoria_id: null,
        preco: 0,
        ingredientes: '',
        imagem: ''
    };

    novaCategoria: any = {
        nome: '',
        tipo: 'VENDA'
    };

    novoCliente: any = {
        nome: '',
        cpf: '',
        telefone: '',
        premiacao: 'Sem Premiação'
    };

    totalVenda: number = 0;

    constructor(private apiService: ApiService) {}

    ngOnInit(): void {
        this.verificarECriarRecheiosPadrao(); // <-- Função adicionada aqui

        this.carregarCategorias();
        this.carregarCardapio();

        this.carregarCategoriasEstoque();
        this.carregarEstoque();

        this.carregarClientes();
        this.verificarEstoqueBaixo();
    }



    verificarECriarRecheiosPadrao(): void {
        this.apiService.getCategoriasCardapio().subscribe({
            next: (res: any) => {
                const categoriasList = res && res.sucesso ? res.categorias || [] : (Array.isArray(res) ? res : []);
                const palavrasChave = ['recheio', 'adicional', 'acompanhamento', 'complemento'];

                const temCategoriaRecheio = categoriasList.some((c: any) =>
                    palavrasChave.some(palavra => (c.nome || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "").includes(palavra))
                );

                if (!temCategoriaRecheio) {
                    const dadosCategoria = { nome: 'Recheios', tipo: 'VENDA' };
                    this.apiService.cadastrarCategoria(dadosCategoria).subscribe({
                        next: (resCat: any) => {
                            if (resCat?.sucesso) {
                                const idCategoria = resCat.id || resCat.categoria?.id;
                                if (idCategoria) {
                                    const recheiosPadrao = ['Morango', 'Leite Ninho', 'Leite Condensado', 'Paçoca', 'Banana'];
                                    recheiosPadrao.forEach(nomeRecheio => {
                                        this.apiService.cadastrarProdutoCardapio({
                                            nome: nomeRecheio,
                                            categoria_id: idCategoria,
                                            preco: 2.00,
                                            ingredientes: '',
                                            imagem: ''
                                        }).subscribe();
                                    });

                                    setTimeout(() => {
                                        this.carregarCategorias();
                                        this.carregarCardapio();
                                    }, 1000);
                                }
                            }
                        }
                    });
                }
            }
        });
    }

    verificarEstoqueBaixo(): void {
        this.apiService.getDashboard().subscribe({
            next: (res: any) => {
                if (res?.sucesso && res.resumo?.itens_estoque_baixo?.length > 0) {
                    const produtosEstoqueBaixo = res.resumo.itens_estoque_baixo
                        .map((produto: any) => `• ${produto.nome} (Estoque Baixo)`)
                        .join('\n');

                    alert(`ATENÇÃO!\n\nExistem produtos com estoque baixo:\n\n${produtosEstoqueBaixo}`);
                }
            },
            error: (err: any) => console.error('Erro ao verificar estoque:', err)
        });
    }

    // COMUNICAÇÃO COM A API


    carregarCategorias(): void {
        this.apiService.getCategoriasCardapio().subscribe({
            next: (res: any) => {
                this.categorias = res && res.sucesso ? res.categorias || [] : (Array.isArray(res) ? res : []);
            },
            error: (err: any) => this.categorias = []
        });
    }

    carregarCategoriasEstoque(): void {
        this.apiService.getCategoriasEstoque().subscribe({
            next: (res: any) => {
                this.categoriasEstoque = res && res.sucesso ? res.categorias || [] : (Array.isArray(res) ? res : []);
            },
            error: (err: any) => this.categoriasEstoque = []
        });
    }

    carregarCardapio(): void {
        this.apiService.getCardapio().subscribe({
            next: (res: any) => {
                this.produtos = res && res.sucesso ? res.produtos || [] : (Array.isArray(res) ? res : []);
            },
            error: (err: any) => this.produtos = []
        });
    }

    carregarEstoque(): void {
    this.apiService.getEstoque().subscribe({
        next: (res: any) => {
            if (Array.isArray(res)) {
                this.produtosEstoque = res.flatMap((grupo: any) =>
                    Array.isArray(grupo?.produtos) ? grupo.produtos : [grupo]
                );
            } else {
                this.produtosEstoque = res?.produtos || [];
            }
        },
        error: (err: any) => this.produtosEstoque = []
    });
}


    // EXCLUSÃO E CRIAÇÃO DE CATEGORIA


    cadastrarCategoria(): void {
        const nome = (this.novaCategoria.nome || '').trim();
        if (!nome) {
            alert('Informe o nome da categoria.');
            return;
        }

        const dadosCategoria = { nome: nome, tipo: 'VENDA' };
        this.apiService.cadastrarCategoria(dadosCategoria).subscribe({
            next: (res: any) => {
                if (res?.sucesso === false) {
                    alert(res.erro || 'Não foi possível cadastrar a categoria.');
                    return;
                }
                alert(res?.mensagem || 'Categoria cadastrada com sucesso!');
                this.modalOpcoesAberto = false;
                this.novaCategoria = { nome: '', tipo: 'VENDA' };
                this.carregarCategorias();
            },
            error: (err: any) => alert(err.error?.erro || err.error?.mensagem || 'Erro ao cadastrar categoria.')
        });
    }

    excluirCategoria(cat: any): void {
        const id = cat.id || cat.idCategoria;

        const produtosNaCategoria = this.getProdutosFiltradosPorCategoria(id);
        if (produtosNaCategoria.length > 0) {
            alert('Não é possível excluir esta categoria porque possui produtos vinculados. Exclua os produtos primeiro.');
            return;
        }

        if (confirm(`Excluir permanentemente a categoria "${cat.nome}"?`)) {
            this.apiService.deletarCategoria(id).subscribe({
                next: (res: any) => {
                    alert('Categoria excluída com sucesso!');
                    this.carregarCategorias();
                },
                error: (err: any) => {
                    console.error('Erro ao excluir categoria:', err);
                    alert(err.error?.erro || 'Não foi possível excluir a categoria.');
                }
            });
        }
    }


    // CRUD DE PRODUTOS


    abrirModalNovoProduto(): void {
        this.modalAberto = true;
        this.novoProduto = {
            nome: '',
            categoria_id: this.categorias.length > 0 ? this.categorias[0].id : null,
            preco: 0,
            ingredientes: '',
            imagem: ''
        };
    }

    fecharModalNovoProduto(): void {
        this.modalAberto = false;
    }

    salvarNovoProduto(): void {
        this.apiService.cadastrarProdutoCardapio(this.novoProduto).subscribe({
            next: (res: any) => {
                if (res.sucesso) {
                    alert('Produto adicionado ao cardápio com sucesso!');
                    this.carregarCardapio();
                    this.fecharModalNovoProduto();
                }
            },
            error: (err: any) => alert('Erro ao salvar produto.')
        });
    }

    retirarDeVenda(id: number): void {
        if (confirm('Tem certeza que deseja retirar este produto de venda? (Ele ficará inativo no estoque)')) {
            this.apiService.excluirProdutoCardapio(id).subscribe({
                next: (res: any) => {
                    if (res.sucesso) this.carregarCardapio();
                },
                error: (err: any) => alert(err.error?.erro || 'Erro ao remover produto.')
            });
        }
    }

    abrirModalEditarProduto(produto: any): void {
        this.produtoEmEdicao = {
            id: produto.id,
            nome: produto.nome,
            preco: produto.preco,
            ingredientes: produto.ingredientes || ''
        };
        this.modalEditarAberto = true;
    }

    fecharModalEditarProduto(): void {
        this.modalEditarAberto = false;
    }

    salvarEdicaoProduto(): void {
        const id = this.produtoEmEdicao.id;
        const dadosAtualizados = {
            preco: this.produtoEmEdicao.preco,
            ingredientes: this.produtoEmEdicao.ingredientes
        };

        this.apiService.atualizarProdutoCardapio(id, dadosAtualizados).subscribe({
            next: (res: any) => {
                alert('Produto atualizado com sucesso!');
                this.carregarCardapio();
                this.carregarEstoque();
                this.fecharModalEditarProduto();
            },
            error: (err: any) => {
                console.error('Erro ao editar:', err);
                alert('Erro ao atualizar produto.');
            }
        });
    }


    // FILTROS E BUSCA


    getProdutosFiltradosPorCategoria(catId: number): any[] {
        let filtrados = this.produtos.filter((p: any) => (p.categoria_id === catId || p.idCategoria === catId));
        if (this.termoBusca && this.termoBusca.trim() !== '') {
            filtrados = filtrados.filter((p: any) => p.nome.toLowerCase().includes(this.termoBusca.toLowerCase()));
        }
        return filtrados;
    }

    temProdutosExibidos(): boolean {
        return this.categorias.some(cat => this.getProdutosFiltradosPorCategoria(cat.id || cat.idCategoria).length > 0);
    }

    todasAsCategorias(): any[] {
        return [...this.categorias, ...this.categoriasEstoque];
    }

    todosOsProdutos(): any[] {
        return [...this.produtos, ...this.produtosEstoque];
    }


    // RECHEIOS DO AÇAÍ


    adicionarAoCarrinho(produto: any): void {
        const nomeLower = (produto.nome || '').toLowerCase();

        if (nomeLower.includes('açaí') || nomeLower.includes('acai')) {
            this.produtoAcaiAtual = JSON.parse(JSON.stringify(produto));
            this.prepararListaRecheios();
            this.modalRecheiosAberto = true;
        } else {
            this.inserirNoCarrinho(produto);
        }
    }

    prepararListaRecheios(): void {
        const palavrasChave = ['recheio', 'adicional', 'acompanhamento', 'complemento', 'extra', 'opcional'];

        const categoriasRecheio = this.todasAsCategorias().filter(c => {
            const nomeCat = (c.nome || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "");
            return palavrasChave.some(palavra => nomeCat.includes(palavra));
        });

        const idsRecheio = categoriasRecheio.map(c => c.id || c.idCategoria);

        const produtosRecheio = this.todosOsProdutos().filter(p => {
            const idCatProd = p.categoria_id || p.idCategoria;
            const nomeProd = (p.nome || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "");

            return idsRecheio.includes(idCatProd) || nomeProd.includes('recheio') || nomeProd.includes('adicional') || nomeProd.includes('complemento');
        });

        const map = new Map();
        const unique = [];
        for (const item of produtosRecheio) {
            const nomeItem = (item.nome || '').toLowerCase();
            if (nomeItem.includes('açaí') || nomeItem.includes('acai')) continue;

            if (!map.has(item.id)) {
                map.set(item.id, true);
                unique.push({ ...item, quantidade_selecionada: 0 });
            }
        }

        this.listaDeRecheiosDinamica = unique;
    }

    alterarQtdRecheio(recheio: any, delta: number): void {
        const novaQtd = (recheio.quantidade_selecionada || 0) + delta;
        if (novaQtd >= 0) {
            recheio.quantidade_selecionada = novaQtd;
        }
    }

    confirmarAcaiComRecheios(): void {
        if (!this.produtoAcaiAtual) return;

        this.inserirNoCarrinho(this.produtoAcaiAtual);

        this.listaDeRecheiosDinamica.forEach(recheio => {
            if (recheio.quantidade_selecionada > 0) {
                let recheioCarrinho = JSON.parse(JSON.stringify(recheio));
                recheioCarrinho.quantidade_carrinho = recheio.quantidade_selecionada;
                this.inserirItemSeparado(recheioCarrinho);
            }
        });

        this.fecharModalRecheios();
    }

    fecharModalRecheios(): void {
        this.modalRecheiosAberto = false;
        this.produtoAcaiAtual = null;
        this.calcularTotal();
    }


    // CARRINHO DE COMPRAS E CÁLCULOS


    inserirNoCarrinho(produto: any): void {
        const itemExistente = this.carrinho.find(item => item.id === produto.id && !this.isRecheio(item));
        if (itemExistente) {
            itemExistente.quantidade_carrinho = (itemExistente.quantidade_carrinho || 1) + 1;
        } else {
            this.carrinho.push({ ...produto, quantidade_carrinho: 1, preco_total: produto.preco });
        }
        this.calcularTotal();
    }

    inserirItemSeparado(produto: any): void {
        const itemExistente = this.carrinho.find(item => item.id === produto.id);
        if (itemExistente) {
            itemExistente.quantidade_carrinho += produto.quantidade_carrinho;
        } else {
            this.carrinho.push({ ...produto });
        }
    }

    isRecheio(item: any): boolean {
        const nomeProdStr = (item.nome || '').toLowerCase();
        if (nomeProdStr.includes('açaí') || nomeProdStr.includes('acai')) return false;

        const palavrasChave = ['recheio', 'adicional', 'acompanhamento', 'complemento', 'extra', 'opcional'];
        const idCatItem = item.categoria_id || item.idCategoria;

        if (idCatItem) {
            const cat = this.todasAsCategorias().find(c => (c.id || c.idCategoria) === idCatItem);
            if (cat) {
                const nomeCat = (cat.nome || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "");
                if (palavrasChave.some(palavra => nomeCat.includes(palavra))) return true;
            }
        }

        const nomeProd = (item.nome || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "");
        return nomeProd.includes('recheio') || nomeProd.includes('adicional') || nomeProd.includes('complemento');
    }

    removerProdutoDoCarrinho(produto: any): void {
        const index = this.carrinho.findIndex(item => item.id === produto.id);
        if (index !== -1) {
            if (this.carrinho[index].quantidade_carrinho > 1) {
                this.carrinho[index].quantidade_carrinho -= 1;
            } else {
                this.carrinho.splice(index, 1);
            }
        }
        this.calcularTotal();
    }

    removerDoCarrinho(index: number): void {
        this.carrinho.splice(index, 1);
        this.calcularTotal();
    }

    calcularTotal(): void {
        let qtdCoposAcai = 0;
        let totalDaCompra = 0;

        this.carrinho.forEach(item => {
            const nomeLower = (item.nome || '').toLowerCase();

            if (nomeLower.includes('açaí') || nomeLower.includes('acai')) {
                qtdCoposAcai += (item.quantidade_carrinho || 1);
                item.preco_total = item.preco * (item.quantidade_carrinho || 1);
                totalDaCompra += item.preco_total;
            }
            else if (!this.isRecheio(item)) {
                item.preco_total = item.preco * (item.quantidade_carrinho || 1);
                totalDaCompra += item.preco_total;
            }
        });

        let recheiosGratisDisponiveis = qtdCoposAcai * 2;

        this.carrinho.forEach(item => {
            if (this.isRecheio(item)) {
                let subtotalRecheio = 0.0;
                let qtd = (item.quantidade_carrinho || 1);

                for (let i = 0; i < qtd; i++) {
                    if (recheiosGratisDisponiveis > 0) {
                        recheiosGratisDisponiveis -= 1;
                    } else {
                        subtotalRecheio += 2.00;
                    }
                }

                item.preco_total = subtotalRecheio;
                item.preco_unitario_tela = qtd > 0 ? (subtotalRecheio / qtd) : 0;
                totalDaCompra += subtotalRecheio;
            }
        });

        this.totalVenda = totalDaCompra;
    }

    limparCarrinho(): void {
        this.carrinho = [];
        this.totalVenda = 0;
        this.clienteSelecionadoId = null;
    }

    cancelarVenda(): void {
        if (confirm('Deseja cancelar a venda atual e limpar o carrinho?')) {
            this.limparCarrinho();
        }
    }

    // CLIENTES E MÁSCARAS


    carregarClientes(): void {
        this.apiService.getClientes().subscribe({
            next: (res: any) => {
                this.clientes = res && res.sucesso ? res.clientes || [] : (Array.isArray(res) ? res : []);
            },
            error: (err: any) => this.clientes = []
        });
    }

    aplicarMascaraCPF(event: any): void {
        let valor = event.target.value.replace(/\D/g, '');
        if (valor.length > 11) valor = valor.substring(0, 11);

        if (valor.length > 9) {
            valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, '$1.$2.$3-$4');
        } else if (valor.length > 6) {
            valor = valor.replace(/^(\d{3})(\d{3})(\d{1,3})$/, '$1.$2.$3');
        } else if (valor.length > 3) {
            valor = valor.replace(/^(\d{3})(\d{1,3})$/, '$1.$2');
        }

        event.target.value = valor;
        this.novoCliente.cpf = valor;
        this.validarCPFEmTempoReal();
    }

    aplicarMascaraTelefone(event: any): void {
        let valor = event.target.value.replace(/\D/g, '');
        if (valor.length > 11) valor = valor.substring(0, 11);

        if (valor.length > 10) {
            valor = valor.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
        } else if (valor.length > 6) {
            valor = valor.replace(/^(\d{2})(\d{4})(\d{1,4})$/, '($1) $2-$3');
        } else if (valor.length > 2) {
            valor = valor.replace(/^(\d{2})(\d{1,4})$/, '($1) $2');
        } else if (valor.length > 0) {
            valor = '(' + valor;
        }

        event.target.value = valor;
        this.novoCliente.telefone = valor;
        this.validarTelefoneEmTempoReal();
    }

    validarCPF(cpf: string): boolean {
        const limpo = cpf.replace(/\D/g, '');
        if (limpo.length !== 11 || /^(\d)\1+$/.test(limpo)) return false;

        let soma = 0;
        for (let i = 0; i < 9; i++) {
            soma += Number(limpo.charAt(i)) * (10 - i);
        }
        let resto = (soma * 10) % 11;
        if (resto === 10) resto = 0;
        if (resto !== Number(limpo.charAt(9))) return false;

        soma = 0;
        for (let i = 0; i < 10; i++) {
            soma += Number(limpo.charAt(i)) * (11 - i);
        }
        resto = (soma * 10) % 11;
        return (resto === 10 ? 0 : resto) === Number(limpo.charAt(10));
    }

    validarCPFEmTempoReal(): void {
        const limpo = this.novoCliente.cpf.replace(/\D/g, '');
        this.cpfInvalido = limpo.length === 11 ? !this.validarCPF(this.novoCliente.cpf) : false;
    }

    validarTelefone(telefone: string): boolean {
        if (!telefone || !telefone.trim()) return false;
        const limpo = telefone.replace(/\D/g, '');
        return limpo.length === 10 || limpo.length === 11;
    }

    validarTelefoneEmTempoReal(): void {
        const limpo = this.novoCliente.telefone.replace(/\D/g, '');
        this.telefoneInvalido = limpo ? !this.validarTelefone(this.novoCliente.telefone) : false;
    }

    cadastrarCliente(): void {
        if (this.cpfInvalido || this.telefoneInvalido || !this.novoCliente.nome) {
            alert('Por favor, verifique se os dados estão corretos antes de salvar.');
            return;
        }

        this.apiService.cadastrarCliente(this.novoCliente).subscribe({
            next: (res: any) => {
                alert(res.mensagem || 'Cliente cadastrado com sucesso!');
                this.carregarClientes();
                this.clienteSelecionadoId = res.id;
                this.modalClienteAberto = false;
                this.novoCliente = { nome: '', cpf: '', telefone: '', premiacao: 'Sem Premiação' };
            },
            error: (err: any) => alert(err.error?.erro || 'Erro ao realizar o cadastro do cliente.')
        });
    }


    // FINALIZAR VENDA

    finalizarVenda(): void {
        if (this.carrinho.length === 0) {
            alert('Erro: O carrinho de compras está vazio!');
            return;
        }

        const payloadVenda = {
            valor_total: this.totalVenda,
            metodo_pagamento: this.metodoPagamento,
            cliente_id: this.clienteSelecionadoId,
            itens: this.carrinho.map(item => ({
                produto_id: item.idProduto || item.id,
                quantidade: item.quantidade_carrinho || 1,
                preco_unitario: item.preco_unitario_tela !== undefined ? item.preco_unitario_tela : item.preco,
                subtotal: item.preco_total
            }))
        };

        this.apiService.registrarVenda(payloadVenda).subscribe({
            next: (res: any) => {
                alert('Sucesso: Venda registrada com o ID ' + res.venda_id);
                this.limparCarrinho();
                this.carregarCardapio();
                this.carregarEstoque();
            },
            error: (err: any) => alert(err.error?.erro || 'Erro interno de comunicação.')
        });
    }
}
