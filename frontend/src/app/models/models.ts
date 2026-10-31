// --- 1. PRODUTO & CATEGORIA ---
export interface Categoria {
  idCategoria?: number;
  nome: string;
  tipo: 'VENDA' | 'ESTOQUE';
}

export interface Produto {
  id?: number;
  nome: string;
  preco: number;
  quantidade: number;
  ingredientes?: string;
  imagem?: string;
  categoria?: string;
  categoria_tipo?: 'VENDA' | 'ESTOQUE';
  categoria_id?: number;
}

// --- 2. VENDAS & CARRINHO ---
export interface ItemCarrinho {
  nome: string;
}

export interface NovaVendaRequest {
  valor_total: number;
  metodo_pagamento: string;
  itens: ItemCarrinho[];
}

export interface Venda {
  id: number;
  data: string;
  valor_total: number;
  metodo_pagamento: string;
}

// --- 3. CLIENTE ---
export interface Cliente {
  id?: number;
  nome: string;
  cpf: string;
  telefone?: string;
  premiacao?: string;
}

// --- 4. FORNECEDOR ---
export interface Fornecedor {
  idFornecedores?: number;
  nome_empresa: string;
  cnpj: string;
  contato?: string;
  email?: string;
  celular?: string;
  endereco?: string;
}

// --- 5. DASHBOARD & INDICADORES ---
export interface DashboardResumo {
  sucesso: boolean;
  resumo: {
    total_faturado: number;
    total_vendas_realizadas: number;
    total_clientes: number;
    total_produtos: number;
    itens_estoque_baixo: { id: number; nome: string; qtd: number }[];
  };
}
