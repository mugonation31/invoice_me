import { CreateLineItem } from '../../invoices/models/invoice.model';

export interface Schedule {
  id?: string;
  user_id?: string;
  client_id: string;
  client_name?: string;
  description?: string;
  line_items: CreateLineItem[];
  tax_rate: number;
  recurrence: 'once' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  next_run_date: string;
  auto_send: boolean;
  active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateScheduleRequest {
  client_id: string;
  description?: string;
  line_items: CreateLineItem[];
  tax_rate?: number;
  recurrence: 'once' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  next_run_date: string;
  auto_send?: boolean;
}

export interface UpdateScheduleRequest {
  client_id?: string;
  description?: string;
  line_items?: CreateLineItem[];
  tax_rate?: number;
  recurrence?: 'once' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  next_run_date?: string;
  auto_send?: boolean;
  active?: boolean;
}
