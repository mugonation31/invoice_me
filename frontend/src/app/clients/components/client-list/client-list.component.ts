import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ClientService } from '../../services/client.service';
import { Client } from '../../models/client.model';
import { ClientFormComponent } from '../client-form/client-form.component';

@Component({
  selector: 'app-client-list',
  standalone: true,
  imports: [CommonModule, ClientFormComponent],
  templateUrl: './client-list.component.html',
  styleUrl: './client-list.component.scss'
})
export class ClientListComponent implements OnInit {
  private clientService = inject(ClientService);

  clients: Client[] = [];
  loading = false;
  error: string | null = null;
  showForm = false;
  editingClient: Client | null = null;

  ngOnInit() {
    this.loadClients();
  }

  loadClients() {
    this.loading = true;
    this.error = null;

    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.clients = clients;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load clients. Please try again.';
        console.error('Error loading clients:', err);
        this.loading = false;
      }
    });
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.editingClient = null;
    }
  }

  editClient(client: Client) {
    this.editingClient = client;
    this.showForm = true;
  }

  deleteClient(client: Client) {
    if (!client.id) return;

    if (confirm('Are you sure you want to delete this client?')) {
      this.clientService.deleteClient(client.id).subscribe({
        next: () => {
          this.loadClients();
        },
        error: (err) => {
          console.error('Error deleting client:', err);
          this.error = 'Failed to delete client. Please try again.';
        }
      });
    }
  }

  onFormSubmit(clientData: Partial<Client>) {
    if (!clientData.name || !clientData.email) {
      this.error = 'Name and email are required';
      return;
    }

    this.loading = true;
    this.error = null;

    const request = {
      name: clientData.name,
      email: clientData.email,
      phone: clientData.phone,
      address: clientData.address
    };

    if (this.editingClient?.id) {
      this.clientService.updateClient(this.editingClient.id, request).subscribe({
        next: (updatedClient) => {
          const index = this.clients.findIndex(c => c.id === updatedClient.id);
          if (index !== -1) {
            this.clients[index] = updatedClient;
          }
          this.showForm = false;
          this.editingClient = null;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error updating client:', err);
          this.error = 'Failed to update client. Please try again.';
          this.loading = false;
        }
      });
    } else {
      this.clientService.createClient(request).subscribe({
        next: (newClient) => {
          this.clients.unshift(newClient);
          this.showForm = false;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error creating client:', err);
          this.error = 'Failed to create client. Please try again.';
          this.loading = false;
        }
      });
    }
  }

  onFormCancel() {
    this.showForm = false;
    this.editingClient = null;
  }

  trackByClientId(index: number, client: Client): string {
    return client.id || index.toString();
  }
}
