import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SupabaseService } from '../../core/services/supabase.service';
import { map, take } from 'rxjs/operators';

export const authGuard: CanActivateFn = (_route, state) => {
  const supabaseService = inject(SupabaseService);
  const router = inject(Router);

  // Check if user is authenticated
  return supabaseService.currentUser$.pipe(
    take(1),
    map(user => {
      if (user) {
        // User is authenticated, allow access
        return true;
      } else {
        // User is not authenticated, redirect to login
        router.navigate(['/login'], {
          queryParams: { returnUrl: state.url }
        });
        return false;
      }
    })
  );
};
