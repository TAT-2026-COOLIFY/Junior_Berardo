import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { VendasComponent } from './components/vendas/vendas.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { EstoqueComponent } from './components/estoque/estoque.component';
import { ClientesComponent } from './components/clientes/clientes.component';
import { FornecedoresComponent } from './components/fornecedores/fornecedores.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'vendas', component: VendasComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'estoque', component: EstoqueComponent },
  { path: 'clientes', component: ClientesComponent },
  { path: 'fornecedores', component: FornecedoresComponent },
  { path: '**', redirectTo: 'login' }
];
