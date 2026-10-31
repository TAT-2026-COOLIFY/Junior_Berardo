import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-clientes',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './clientes.component.html',
    styleUrls: ['./clientes.component.css']
})
export class ClientesComponent implements OnInit {

    clientes: any[] = [];
    modoEdicao: boolean = false;
    clienteSendoEditadoId: number | null = null;

    novoCliente = {
        nome: '',
        cpf: '',
        telefone: ''
    };

    premiacaoSelecionada = {
        cliente_id: null as number | null,
        pontos: null as number | null,
        premio: ''
    };

    constructor(private apiService: ApiService) {}

    ngOnInit(): void {
        this.carregarClientes();
    }

    carregarClientes(): void {
        this.apiService.getClientes().subscribe({
            next: (res: any) => {
                if (res?.sucesso) {
                    this.clientes = res.clientes || [];

                    if (
                        this.clientes.length > 0 &&
                        !this.premiacaoSelecionada.cliente_id
                    ) {
                        this.premiacaoSelecionada.cliente_id =
                            this.clientes[0].id;
                    }
                }
            },
            error: (err: any) =>
                console.error('Erro ao carregar clientes:', err)
        });
    }

    getIniciais(nome: string): string {
        if (!nome) return 'CL';

        const partes = nome.trim().split(' ');

        if (partes.length === 1) {
            return partes[0].substring(0, 2).toUpperCase();
        }

        return (
            partes[0][0] + partes[partes.length - 1][0]
        ).toUpperCase();
    }

    aplicarMascaraCPF(event: any): void {
        let v = event.target.value.replace(/\D/g, '');

        if (v.length > 11) {
            v = v.substring(0, 11);
        }

        if (v.length > 9) {
            v = v.replace(
                /^(\d{3})(\d{3})(\d{3})(\d{1,2})$/,
                '$1.$2.$3-$4'
            );
        } else if (v.length > 6) {
            v = v.replace(
                /^(\d{3})(\d{3})(\d+)$/,
                '$1.$2.$3'
            );
        } else if (v.length > 3) {
            v = v.replace(
                /^(\d{3})(\d+)$/,
                '$1.$2'
            );
        }

        this.novoCliente.cpf = v;
        event.target.value = v;
    }

    aplicarMascaraTelefone(event: any): void {
        let v = event.target.value.replace(/\D/g, '');

        if (v.length > 11) {
            v = v.substring(0, 11);
        }

        if (v.length > 10) {
            v = v.replace(
                /^(\d{2})(\d{5})(\d{4})$/,
                '($1) $2-$3'
            );
        } else if (v.length > 6) {
            v = v.replace(
                /^(\d{2})(\d{4})(\d{1,4})$/,
                '($1) $2-$3'
            );
        } else if (v.length > 2) {
            v = v.replace(
                /^(\d{2})(\d+)$/,
                '($1) $2'
            );
        } else if (v.length > 0) {
            v = v.replace(/^(\d+)$/, '($1');
        }

        this.novoCliente.telefone = v;
        event.target.value = v;
    }

    cadastrarCliente(): void {
        this.salvarCliente();
    }

    formatarNomeDigitacao(): void {
    }

    premiacaoDisponivel(cliente: any): boolean {
        if (
            !cliente ||
            !cliente.premiacao ||
            cliente.premiacao === 'Sem Premiação'
        ) {
            return false;
        }

        const match = cliente.premiacao.match(/(\d+)\s*Pontos/i);

        if (!match) return false;

        const pontosNecessarios = parseInt(match[1], 10);

        return (cliente.compras_realizadas || 0) >= pontosNecessarios;
    }

    salvarCliente(): void {
        const cpfLimpo = this.novoCliente.cpf.replace(/\D/g, '');
        const telLimpo = this.novoCliente.telefone.replace(/\D/g, '');

        if (
            !this.novoCliente.nome.trim() ||
            !cpfLimpo ||
            !telLimpo
        ) {
            alert('Todos os campos são obrigatórios!');
            return;
        }

        const dadosCliente = {
            nome: this.novoCliente.nome.trim(),
            cpf: this.novoCliente.cpf,
            telefone: this.novoCliente.telefone
        };

        if (this.modoEdicao && this.clienteSendoEditadoId) {
            this.apiService
                .atualizarCliente(
                    this.clienteSendoEditadoId,
                    dadosCliente
                )
                .subscribe({
                    next: (res: any) => {
                        alert(
                            'Dados do cliente atualizados com sucesso!'
                        );
                        this.cancelarEdicao();
                        this.carregarClientes();
                    },
                    error: (err: any) =>
                        alert(
                            err.error?.erro ||
                            'Erro ao atualizar dados do cliente.'
                        )
                });
        } else {
            this.apiService
                .cadastrarCliente({
                    ...dadosCliente,
                    premiacao: 'Sem Premiação'
                })
                .subscribe({
                    next: (res: any) => {
                        alert(
                            'Cliente adicionado com sucesso ao Clube!'
                        );
                        this.limparFormulario();
                        this.carregarClientes();
                    },
                    error: (err: any) =>
                        alert(
                            err.error?.erro ||
                            'Erro ao registrar novo cliente.'
                        )
                });
        }
    }

    prepararEdicao(cliente: any): void {
        this.modoEdicao = true;
        this.clienteSendoEditadoId = cliente.id;

        this.novoCliente = {
            nome: cliente.nome,
            cpf: cliente.cpf,
            telefone: cliente.telefone
        };
    }

    cancelarEdicao(): void {
        this.modoEdicao = false;
        this.clienteSendoEditadoId = null;
        this.limparFormulario();
    }

    limparFormulario(): void {
        this.novoCliente = {
            nome: '',
            cpf: '',
            telefone: ''
        };
    }

    salvarPremiacao(): void {
        if (!this.premiacaoSelecionada.cliente_id) {
            alert(
                'Selecione um cliente para atribuir o benefício!'
            );
            return;
        }

        const pontos = Number(this.premiacaoSelecionada.pontos);
        const premio = this.premiacaoSelecionada.premio.trim();

        if (!pontos || pontos <= 0 || !premio) {
            alert(
                'Informe uma quantidade válida de pontos e a descrição do prêmio.'
            );
            return;
        }

        const regraFinal = `${pontos} Pontos (${premio})`;

        this.apiService
            .atualizarPremiacaoCliente(
                this.premiacaoSelecionada.cliente_id,
                regraFinal
            )
            .subscribe({
                next: (res: any) => {
                    alert(
                        `Premiação salva!\n\nRegra: ${regraFinal}`
                    );

                    this.premiacaoSelecionada.pontos = null;
                    this.premiacaoSelecionada.premio = '';

                    this.carregarClientes();
                },
                error: (err: any) =>
                    alert(
                        err.error?.erro ||
                        'Erro ao salvar premiação.'
                    )
            });
    }

    resgatarPremiacao(cliente: any): void {
        if (cliente && cliente.id) {
            this.resgatarPremio(cliente.id);
        }
    }

    resgatarPremio(id: number): void {
        this.apiService.resgatarPremiacaoCliente(id).subscribe({
            next: (res: any) => {
                alert(
                    res?.mensagem || 'Premiação resgatada!'
                );
                this.carregarClientes();
            },
            error: (err: any) =>
                alert(
                    err.error?.erro ||
                    'Erro ao processar resgate.'
                )
        });
    }

    excluirCliente(id: number): void {
        if (
            !confirm(
                'Deseja realmente remover este cliente do Clube?'
            )
        ) {
            return;
        }

        this.apiService.excluirCliente(id).subscribe({
            next: (res: any) => {
                alert(
                    'Cliente removido do sistema com sucesso!'
                );
                this.carregarClientes();
            },
            error: (err: any) =>
                alert(
                    err.error?.erro ||
                    'Erro ao excluir cadastro.'
                )
        });
    }
}
