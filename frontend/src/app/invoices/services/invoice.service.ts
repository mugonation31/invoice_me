import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from, switchMap } from 'rxjs';
import { SupabaseService } from '../../core/services/supabase.service';
import { Invoice, CreateInvoiceRequest, UpdateInvoiceRequest } from '../models/invoice.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class InvoiceService {
  private http = inject(HttpClient);
  private supabaseService = inject(SupabaseService);

  private apiUrl = environment.apiUrl || 'http://localhost:8000/api';

  private async getAuthHeaders(): Promise<HttpHeaders> {
    const token = await this.supabaseService.getAccessToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  getInvoices(): Observable<Invoice[]> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<Invoice[]>(`${this.apiUrl}/invoices`, { headers })
      )
    );
  }

  getInvoice(id: string): Observable<Invoice> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<Invoice>(`${this.apiUrl}/invoices/${id}`, { headers })
      )
    );
  }

  createInvoice(invoice: CreateInvoiceRequest): Observable<Invoice> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.post<Invoice>(`${this.apiUrl}/invoices`, invoice, { headers })
      )
    );
  }

  updateInvoice(id: string, updates: UpdateInvoiceRequest): Observable<Invoice> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.patch<Invoice>(`${this.apiUrl}/invoices/${id}`, updates, { headers })
      )
    );
  }

  deleteInvoice(id: string): Observable<any> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.delete(`${this.apiUrl}/invoices/${id}`, { headers })
      )
    );
  }

  updateStatus(id: string, status: string): Observable<Invoice> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.patch<Invoice>(`${this.apiUrl}/invoices/${id}/status`, { status }, { headers })
      )
    );
  }
}
