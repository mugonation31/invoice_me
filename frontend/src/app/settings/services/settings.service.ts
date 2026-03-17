import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from, switchMap } from 'rxjs';
import { SupabaseService } from '../../core/services/supabase.service';
import { CompanySettings } from '../models/settings.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private http = inject(HttpClient);
  private supabaseService = inject(SupabaseService);

  private apiUrl = environment.apiUrl || 'http://localhost:8000/api';

  /**
   * Get authorization headers with JWT token
   */
  private async getAuthHeaders(): Promise<HttpHeaders> {
    const token = await this.supabaseService.getAccessToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  /**
   * Get company settings for the current user
   */
  getSettings(): Observable<CompanySettings> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<CompanySettings>(`${this.apiUrl}/settings`, { headers })
      )
    );
  }

  /**
   * Create or update company settings
   */
  updateSettings(settings: Partial<CompanySettings>): Observable<CompanySettings> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.put<CompanySettings>(`${this.apiUrl}/settings`, settings, { headers })
      )
    );
  }
}
