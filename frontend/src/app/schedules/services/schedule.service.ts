import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from, switchMap } from 'rxjs';
import { SupabaseService } from '../../core/services/supabase.service';
import { Schedule, CreateScheduleRequest, UpdateScheduleRequest } from '../models/schedule.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ScheduleService {
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

  getSchedules(): Observable<Schedule[]> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<Schedule[]>(`${this.apiUrl}/schedules`, { headers })
      )
    );
  }

  getSchedule(id: string): Observable<Schedule> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.get<Schedule>(`${this.apiUrl}/schedules/${id}`, { headers })
      )
    );
  }

  createSchedule(schedule: CreateScheduleRequest): Observable<Schedule> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.post<Schedule>(`${this.apiUrl}/schedules`, schedule, { headers })
      )
    );
  }

  updateSchedule(id: string, updates: UpdateScheduleRequest): Observable<Schedule> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.patch<Schedule>(`${this.apiUrl}/schedules/${id}`, updates, { headers })
      )
    );
  }

  deleteSchedule(id: string): Observable<any> {
    return from(this.getAuthHeaders()).pipe(
      switchMap(headers =>
        this.http.delete(`${this.apiUrl}/schedules/${id}`, { headers })
      )
    );
  }
}
