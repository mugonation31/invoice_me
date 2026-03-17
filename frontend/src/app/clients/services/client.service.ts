import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from, switchMap } from 'rxjs';
import { SupabaseService } from '../../core/services/supabase.service';
import { Client, CreateClientRequest, UpdateClientRequest } from '../models/client.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ClientService {
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
   * Get all clients for the current user
   */
  getClients(): Observable<Client[]> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<Client[]>(`${this.apiUrl}/clients`, { headers })
      )
    );
  }

  /**
   * Get a single client by ID
   */
  getClient(id: string): Observable<Client> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<Client>(`${this.apiUrl}/clients/${id}`, { headers })
      )
    );
  }

  /**
   * Create a new client
   */
  createClient(client: CreateClientRequest): Observable<Client> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.post<Client>(`${this.apiUrl}/clients`, client, { headers })
      )
    );
  }

  /**
   * Update an existing client
   */
  updateClient(id: string, updates: UpdateClientRequest): Observable<Client> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.patch<Client>(`${this.apiUrl}/clients/${id}`, updates, { headers })
      )
    );
  }

  /**
   * Delete a client
   */
  deleteClient(id: string): Observable<any> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.delete(`${this.apiUrl}/clients/${id}`, { headers })
      )
    );
  }
}
