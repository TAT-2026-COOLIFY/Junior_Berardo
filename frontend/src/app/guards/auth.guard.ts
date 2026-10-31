import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const usuarioLogado = localStorage.getItem('usuarioLogado');

  if (usuarioLogado === 'true') {
    return true;
  } else {
    router.navigate(['/login']);
    return false;
  }
};
