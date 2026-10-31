import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-fornecedores',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './fornecedores.component.html',
  styleUrls: ['./fornecedores.component.css']
})
export class FornecedoresComponent implements OnInit {
  fornecedores: any[] = [];
  cnpjInvalido: boolean = false;
  emailInvalido: boolean = false;
  celularInvalido: boolean = false;
  editandoFornecedor: boolean = false;
  fornecedorEditandoId: number | null = null;

  novoFornecedor = {
    nome_empresa: '',
    cnpj: '',
    contato: '',
    email: '',
    celular: '',
    endereco: ''
  };

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.carregarFornecedores();
  }

  carregarFornecedores(): void {
    this.apiService.getFornecedores().subscribe({
      next: (res: any) => {
        if (res.sucesso) this.fornecedores = res.fornecedores || [];
      },
      error: (err) => console.error('Erro ao carregar fornecedores:', err)
    });
  }


  // MÁSCARAS DE ENTRADA

  aplicarMascaraCNPJ(event: any): void {
    let valor = event.target.value.replace(/\D/g, '');
    if (valor.length > 14) valor = valor.substring(0, 14);

    if (valor.length > 12) {
      valor = valor.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{1,2})$/, '$1.$2.$3/$4-$5');
    } else if (valor.length > 8) {
      valor = valor.replace(/^(\d{2})(\d{3})(\d{3})(\d{1,4})$/, '$1.$2.$3/$4');
    } else if (valor.length > 5) {
      valor = valor.replace(/^(\d{2})(\d{3})(\d{1,3})$/, '$1.$2.$3');
    } else if (valor.length > 2) {
      valor = valor.replace(/^(\d{2})(\d{1,3})$/, '$1.$2');
    }

    this.novoFornecedor.cnpj = valor;
    this.validarCNPJEmTempoReal();
  }

  aplicarMascaraCelular(event: any): void {
    let valor = event.target.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.substring(0, 11);

    if (valor.length > 7) {
      valor = valor.replace(/^(\d{2})(\d{5})(\d{1,4})$/, '($1) $2-$3');
    } else if (valor.length > 2) {
      valor = valor.replace(/^(\d{2})(\d{1,5})$/, '($1) $2');
    } else if (valor.length > 0) {
      valor = valor.replace(/^(\d{1,2})$/, '($1');
    }

    this.novoFornecedor.celular = valor;
    this.validarCelularEmTempoReal();
  }


  // ALGORITMOS DE VALIDAÇÃO

  validarCNPJ(cnpj: string): boolean {
    const limpo = cnpj.replace(/\D/g, '');
    if (limpo.length !== 14 || /^(\d)\1+$/.test(limpo)) return false;

    let tamanho = 12;
    let numeros = limpo.substring(0, tamanho);
    let soma = 0;
    let pos = 5;

    for (let i = 0; i < tamanho; i++) {
      soma += parseInt(numeros.charAt(i), 10) * pos--;
      if (pos < 2) pos = 9;
    }

    let resto = soma % 11;
    let digito1 = resto < 2 ? 0 : 11 - resto;
    if (digito1 !== parseInt(limpo.charAt(12), 10)) return false;

    tamanho = 13;
    numeros = limpo.substring(0, tamanho);
    soma = 0;
    pos = 6;

    for (let i = 0; i < tamanho; i++) {
      soma += parseInt(numeros.charAt(i), 10) * pos--;
      if (pos < 2) pos = 9;
    }

    resto = soma % 11;
    let digito2 = resto < 2 ? 0 : 11 - resto;
    return digito2 === parseInt(limpo.charAt(13), 10);
  }

  validarCNPJEmTempoReal(): void {
    const limpo = this.novoFornecedor.cnpj.replace(/\D/g, '');
    this.cnpjInvalido = limpo.length === 14 ? !this.validarCNPJ(this.novoFornecedor.cnpj) : false;
  }

  validarEmail(email: string): boolean {
    if (!email.trim()) return true;
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  validarEmailEmTempoReal(): void {
    this.emailInvalido = !this.validarEmail(this.novoFornecedor.email);
  }

  validarCelular(celular: string): boolean {
    if (!celular.trim()) return true;
    return celular.replace(/\D/g, '').length === 11;
  }

  validarCelularEmTempoReal(): void {
    this.celularInvalido = !this.validarCelular(this.novoFornecedor.celular);
  }


  // PERSISTÊNCIA, EDIÇÃO E EXCLUSÃO

  salvarFornecedor(): void {
    if (!this.novoFornecedor.nome_empresa.trim() || !this.novoFornecedor.cnpj.trim()) {
      alert('Preencha os campos obrigatórios: Razão Social e CNPJ.');
      return;
    }

    if (!this.validarCNPJ(this.novoFornecedor.cnpj) || !this.validarEmail(this.novoFornecedor.email) || !this.validarCelular(this.novoFornecedor.celular)) {
      alert('Existem campos inválidos no formulário. Verifique os dados e tente novamente.');
      return;
    }

    if (this.editandoFornecedor && this.fornecedorEditandoId !== null) {

      this.apiService.atualizarFornecedor(this.fornecedorEditandoId, this.novoFornecedor).subscribe({
        next: (res: any) => {
          if (res.sucesso) {
            alert('Fornecedor atualizado com sucesso!');
            this.limparFormulario();
            this.carregarFornecedores();
          }
        },
        error: (err) => alert(err.error?.erro || 'Erro ao atualizar fornecedor.')
      });
    } else {

      this.apiService.cadastrarFornecedor(this.novoFornecedor).subscribe({
        next: (res: any) => {
          if (res.sucesso) {
            alert('Fornecedor cadastrado com sucesso!');
            this.limparFormulario();
            this.carregarFornecedores();
          }
        },
        error: (err) => alert(err.error?.erro || 'Erro ao cadastrar fornecedor.')
      });
    }
  }

  editarFornecedor(fornecedor: any): void {
    this.editandoFornecedor = true;
    this.fornecedorEditandoId = fornecedor.idFornecedores || fornecedor.id;

    this.novoFornecedor = {
      nome_empresa: fornecedor.nome_empresa || '',
      cnpj: fornecedor.cnpj || '',
      contato: fornecedor.contato || '',
      email: fornecedor.email || '',
      celular: fornecedor.celular || '',
      endereco: fornecedor.endereco || ''
    };

    this.validarCNPJEmTempoReal();
    this.validarEmailEmTempoReal();
    this.validarCelularEmTempoReal();
  }

  cancelarEdicao(): void {
    this.limparFormulario();
  }

  limparFormulario(): void {
    this.novoFornecedor = { nome_empresa: '', cnpj: '', contato: '', email: '', celular: '', endereco: '' };
    this.cnpjInvalido = this.emailInvalido = this.celularInvalido = this.editandoFornecedor = false;
    this.fornecedorEditandoId = null;
  }

  excluirFornecedor(id: number): void {
    if (confirm('Deseja realmente remover este fornecedor do catálogo?')) {
      this.apiService.deletarFornecedor(id).subscribe({
        next: () => {
          alert('Fornecedor removido com sucesso!');
          this.carregarFornecedores();
        },
        error: (err) => alert(err.error?.erro || 'Erro ao deletar fornecedor.')
      });
    }
  }
}
