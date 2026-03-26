import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { SupabaseService } from '../../core/services/supabase.service';
import { User } from '@supabase/supabase-js';

@Component({
  selector: 'app-navigation',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './navigation.component.html',
  styleUrl: './navigation.component.scss'
})
export class NavigationComponent implements OnInit {
  private supabaseService = inject(SupabaseService);
  private router = inject(Router);

  // Store current user info
  currentUser: User | null = null;
  userName: string = '';
  menuOpen = false;

  toggleMenu() {
    this.menuOpen = !this.menuOpen;
  }

  closeMenu() {
    this.menuOpen = false;
  }

  ngOnInit() {
    // Subscribe to user changes (login/logout events)
    this.supabaseService.currentUser$.subscribe(user => {
      this.currentUser = user;
      // Get user's name from metadata or email
      this.userName = user?.user_metadata?.['name'] || user?.email?.split('@')[0] || 'User';
    });
  }

  /**
   * Logout the current user
   */
  async logout() {
    try {
      await this.supabaseService.signOut();
      this.router.navigate(['/login']);
    } catch (error) {
      console.error('Error logging out:', error);
    }
  }
}
