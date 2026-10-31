import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email: string = '';
  senha: string = '';
  mensagemErro: string = '';
  mensagemSucesso: string = '';
  carregando: boolean = false;

  // Controle do Modal "Esqueceu a Senha"
  modalEsqueciAberto: boolean = false;
  emailRecuperacao: string = '';
  novaSenha: string = '';
  confirmarNovaSenha: string = '';
  erroRecuperacao: string = '';
  sucessoRecuperacao: string = '';
  carregandoRecuperacao: boolean = false;

  constructor(private apiService: ApiService, private router: Router) {}

  fazerLogin(): void {
    if (!this.email || !this.senha) {
      this.mensagemErro = 'Preencha o e-mail e a senha.';
      return;
    }

    this.carregando = true;
    this.mensagemErro = '';
    this.mensagemSucesso = '';

    this.apiService.login({ email: this.email, senha: this.senha }).subscribe({
      next: (res: any) => {
        this.carregando = false;
        if (res.sucesso) {
          this.router.navigate(['/vendas']);
        } else {
          this.mensagemErro = res.erro || 'Falha no login.';
        }
      },
      error: (err: any) => {
        this.carregando = false;
        this.mensagemErro = err.error?.erro || 'E-mail ou senha incorretos.';
      }
    });
  }

  abrirModalEsqueci(): void {
    this.emailRecuperacao = this.email || '';
    this.novaSenha = '';
    this.confirmarNovaSenha = '';
    this.erroRecuperacao = '';
    this.sucessoRecuperacao = '';
    this.modalEsqueciAberto = true;
  }

  fecharModalEsqueci(): void {
    this.modalEsqueciAberto = false;
  }

  salvarNovaSenha(): void {
    this.erroRecuperacao = '';
    this.sucessoRecuperacao = '';

    if (!this.emailRecuperacao.trim()) {
      this.erroRecuperacao = 'Informe seu e-mail cadastrado.';
      return;
    }
    if (!this.novaSenha || this.novaSenha.length < 4) {
      this.erroRecuperacao = 'A nova senha deve ter no mínimo 4 caracteres.';
      return;
    }
    if (this.novaSenha !== this.confirmarNovaSenha) {
      this.erroRecuperacao = 'As senhas não coincidem!';
      return;
    }

    this.carregandoRecuperacao = true;
    this.apiService.redefinirSenha({
      email: this.emailRecuperacao,
      nova_senha: this.novaSenha
    }).subscribe({
      next: (res: any) => {
        this.carregandoRecuperacao = false;
        if (res.sucesso) {
          this.sucessoRecuperacao = 'Senha alterada com sucesso!';
          setTimeout(() => {
            this.fecharModalEsqueci();
            this.email = this.emailRecuperacao;
            this.senha = '';
            this.mensagemSucesso = 'Senha redefinida com sucesso! Faça login com a nova senha.';
          }, 1500);
        } else {
          this.erroRecuperacao = res.erro || 'Erro ao redefinir senha.';
        }
      },
      error: (err: any) => {
        this.carregandoRecuperacao = false;
        this.erroRecuperacao = err.error?.erro || 'E-mail não encontrado ou erro no servidor.';
      }
    });
  }
}
