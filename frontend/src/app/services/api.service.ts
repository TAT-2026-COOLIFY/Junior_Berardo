import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private readonly baseUrl = '/api';

  constructor(private http: HttpClient) {}

  login(credenciais: { email: string; senha: string; }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, credenciais);
  }

  redefinirSenha(dados: { email: string; nova_senha: string; }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/redefinir-senha`, dados);
  }

  getDashboard(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/dashboard`);
  }

  getDashboard24h(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/dashboard/financeiro-24h`);
  }

  getCategorias(tipo?: string): Observable<any> {
    const url = tipo ? `${this.baseUrl}/categorias?tipo=${tipo}` : `${this.baseUrl}/categorias`;
    return this.http.get<any>(url);
  }

  getCategoriasEstoque(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/categorias?tipo=ESTOQUE`);
  }

  getCategoriasCardapio(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/categorias?tipo=VENDA`);
  }

  cadastrarCategoria(categoria: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/categorias`, categoria);
  }

  deletarCategoria(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/categorias/${id}`);
  }

  getCardapio(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/cardapio`);
  }

  cadastrarProdutoCardapio(produto: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/cardapio`, produto);
  }

  atualizarPrecoProduto(id: number, preco: number): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/cardapio/${id}/preco`, { preco });
  }

  atualizarIngredientesProduto(id: number, ingredientes: string): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/cardapio/${id}/ingredientes`, { ingredientes });
  }

  atualizarProdutoCardapio(id: number, produto: { preco?: number; ingredientes?: string; }): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/cardapio/${id}`, produto);
  }

  excluirProdutoCardapio(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/cardapio/${id}`);
  }

  getEstoque(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/estoque`);
  }

  cadastrarProdutoEstoque(produto: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/estoque`, produto);
  }

  atualizarProdutoEstoque(id: number, produto: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/estoque/${id}`, produto);
  }

  deletarProdutoEstoque(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/estoque/${id}`);
  }

  registrarMovimentacao(movimentacao: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/estoque/movimentacoes`, movimentacao);
  }

  listarMovimentacoes(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/estoque/movimentacoes`);
  }

  getGiroEstoque(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/estoque/giro`);
  }

  getVendas(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/vendas`);
  }

  registrarVenda(venda: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/vendas`, venda);
  }

  excluirVenda(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/vendas/${id}`);
  }

  getClientes(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/clientes`);
  }

  cadastrarCliente(cliente: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/clientes`, cliente);
  }

  registrarClienteNoCaixa(cliente: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/clientes`, cliente);
  }

  atualizarCliente(id: number, cliente: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/clientes/${id}`, cliente);
  }

  excluirCliente(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/clientes/${id}`);
  }

  atualizarPremiacaoCliente(id: number, premiacao: string): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/clientes/${id}/premiacao`, { premiacao });
  }

  resgatarPremiacaoCliente(id: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/clientes/${id}/resgatar-premiacao`, {});
  }

  getFornecedores(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/fornecedores`);
  }

  cadastrarFornecedor(fornecedor: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/fornecedores`, fornecedor);
  }

  atualizarFornecedor(id: number, fornecedor: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/fornecedores/${id}`, fornecedor);
  }

  deletarFornecedor(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/fornecedores/${id}`);
  }

  downloadRelatorioPdf(periodo: string = 'geral'): void {
    let p = 'geral';
    if (periodo.toLowerCase().includes('semana')) p = 'semana';
    if (periodo.toLowerCase().includes('mes') || periodo.toLowerCase().includes('mÃªs')) p = 'mes';
    window.open(`${this.baseUrl}/relatorios/vendas/pdf?periodo=${p}`, '_blank');
  }
}

