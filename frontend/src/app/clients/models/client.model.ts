export interface Client {
  id?: string;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  user_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateClientRequest {
  name: string;
  email: string;
  phone?: string;
  address?: string;
}

export interface UpdateClientRequest {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
}
