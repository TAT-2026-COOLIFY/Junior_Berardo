import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'PremiArte Açaí';

  constructor(private router: Router) {}

  // Verifica se a rota atual é a tela de Login para ocultar o menu lateral
  isLoginPage(): boolean {
    const url = this.router.url;
    return url === '/login' || url === '/' || url === '';
  }

  // Faz o logout e redireciona para a tela de login
  fazerLogout(): void {
    this.router.navigate(['/login']);
  }
}
