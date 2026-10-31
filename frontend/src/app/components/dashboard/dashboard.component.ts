import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

    resumo = {
        faturamento_ultimas_24h: 0,
        total_vendas_ultimas_24h: 0,
        ticket_medio_24h: 0,
        itens_estoque_baixo: [] as any[]
    };

    vendas: any[] = [];

    constructor(private apiService: ApiService) {}

    ngOnInit(): void {
        this.carregarDashboardBase();
        this.carregarDadosFinanceiros24h();
    }


    // REQUISITOS DE ESTOQUE

    carregarDashboardBase(): void {
        this.apiService.getDashboard().subscribe({
            next: (res: any) => {
                if (res && res.sucesso && res.resumo) {
                    this.resumo.itens_estoque_baixo = res.resumo.itens_estoque_baixo || [];
                }
            },
            error: (err: any) => console.error('Erro ao carregar estoque baixo:', err)
        });
    }


    // REQUISITOS FINANCEIROS

    carregarDadosFinanceiros24h(): void {
        this.apiService.getDashboard24h().subscribe({
            next: (res: any) => {
                if (res && res.resumo) {
                    this.resumo.faturamento_ultimas_24h = res.resumo.faturamento_ultimas_24h || 0.0;
                    this.resumo.total_vendas_ultimas_24h = res.resumo.total_vendas_ultimas_24h || 0;
                    this.resumo.ticket_medio_24h = res.resumo.ticket_medio_24h || 0.0;
                    this.vendas = res.vendas || [];
                }
            },
            error: (err: any) => console.error('Erro ao carregar painel de 24h:', err)
        });
    }


    // AUDITORIA E EXCLUSÃO DE VENDAS

    excluirVenda(id: number): void {
        if (!confirm('Deseja realmente reverter e excluir esta venda? O estoque dos itens será devolvido.')) {
            return;
        }

        this.apiService.excluirVenda(id).subscribe({
            next: (res: any) => {
                alert(res?.mensagem || 'Venda desfeita com sucesso!');
                this.carregarDashboardBase();
                this.carregarDadosFinanceiros24h();
            },
            error: (err: any) => {
                console.error('Erro ao excluir venda:', err);
                alert(err?.error?.erro || 'Erro ao reverter venda no servidor.');
            }
        });
    }


    // EXPORTAÇÃO IMPRESSA (EMISSÃO DE DOCUMENTOS PDF)

    gerarPdfVendas(periodo: string = 'geral'): void {
        this.apiService.downloadRelatorioPdf(periodo);
    }
}
