export interface LineItem {
  id?: string;
  description: string;
  quantity: number;
  rate: number;
  amount: number;
  sort_order?: number;
  created_at?: string;
}

export interface CreateLineItem {
  description: string;
  quantity: number;
  rate: number;
}

export interface Invoice {
  id?: string;
  user_id?: string;
  client_id: string;
  client_name?: string;
  client_email?: string;
  invoice_number?: string;
  status?: 'draft' | 'sent' | 'paid' | 'overdue';
  issue_date: string;
  due_date: string;
  tax_rate: number;
  subtotal?: number;
  tax_amount?: number;
  total_due?: number;
  notes?: string;
  line_items?: LineItem[];
  created_at?: string;
  updated_at?: string;
}

export interface CreateInvoiceRequest {
  client_id: string;
  issue_date?: string;
  due_date: string;
  tax_rate?: number;
  notes?: string;
  line_items: CreateLineItem[];
}

export interface UpdateInvoiceRequest {
  client_id?: string;
  issue_date?: string;
  due_date?: string;
  tax_rate?: number;
  notes?: string;
  status?: string;
  line_items?: CreateLineItem[];
}
