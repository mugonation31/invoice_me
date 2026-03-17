import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { ClientService } from '../../../clients/services/client.service';
import { Client } from '../../../clients/models/client.model';
import { Invoice, CreateInvoiceRequest } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './invoice-form.component.html',
  styleUrl: './invoice-form.component.scss'
})
export class InvoiceFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private invoiceService = inject(InvoiceService);
  private clientService = inject(ClientService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  invoiceForm!: FormGroup;
  clients: Client[] = [];
  loading = false;
  error: string | null = null;
  isEditMode = false;
  invoiceId: string | null = null;

  ngOnInit() {
    this.initForm();
    this.loadClients();

    this.invoiceId = this.route.snapshot.paramMap.get('id');
    if (this.invoiceId) {
      this.isEditMode = true;
      this.loadInvoice(this.invoiceId);
    }
  }

  private initForm() {
    const today = new Date().toISOString().split('T')[0];

    this.invoiceForm = this.fb.group({
      client_id: ['', Validators.required],
      issue_date: [today],
      due_date: ['', Validators.required],
      tax_rate: [0],
      notes: [''],
      line_items: this.fb.array([this.createLineItem()])
    });
  }

  private createLineItem(): FormGroup {
    return this.fb.group({
      description: ['', Validators.required],
      quantity: [1, [Validators.required, Validators.min(0.01)]],
      rate: [0, [Validators.required, Validators.min(0)]]
    });
  }

  get lineItems(): FormArray {
    return this.invoiceForm.get('line_items') as FormArray;
  }

  addLineItem() {
    this.lineItems.push(this.createLineItem());
  }

  removeLineItem(index: number) {
    if (this.lineItems.length > 0) {
      this.lineItems.removeAt(index);
    }
  }

  getLineItemAmount(index: number): number {
    const item = this.lineItems.at(index);
    const quantity = item.get('quantity')?.value || 0;
    const rate = item.get('rate')?.value || 0;
    return quantity * rate;
  }

  get subtotal(): number {
    let total = 0;
    for (let i = 0; i < this.lineItems.length; i++) {
      total += this.getLineItemAmount(i);
    }
    return total;
  }

  get taxAmount(): number {
    const taxRate = this.invoiceForm.get('tax_rate')?.value || 0;
    return this.subtotal * taxRate / 100;
  }

  get totalDue(): number {
    return this.subtotal + this.taxAmount;
  }

  formatCurrency(amount: number): string {
    return '£' + amount.toFixed(2);
  }

  private loadClients() {
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.clients = clients;
      },
      error: (err) => {
        console.error('Error loading clients:', err);
      }
    });
  }

  private loadInvoice(id: string) {
    this.loading = true;
    this.invoiceService.getInvoice(id).subscribe({
      next: (invoice: Invoice) => {
        this.populateForm(invoice);
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load invoice.';
        console.error('Error loading invoice:', err);
        this.loading = false;
      }
    });
  }

  private populateForm(invoice: Invoice) {
    this.invoiceForm.patchValue({
      client_id: invoice.client_id,
      issue_date: invoice.issue_date,
      due_date: invoice.due_date,
      tax_rate: invoice.tax_rate,
      notes: invoice.notes || ''
    });

    // Clear existing line items and add invoice's line items
    this.lineItems.clear();
    if (invoice.line_items && invoice.line_items.length > 0) {
      for (const item of invoice.line_items) {
        const lineItemGroup = this.fb.group({
          description: [item.description, Validators.required],
          quantity: [item.quantity, [Validators.required, Validators.min(0.01)]],
          rate: [item.rate, [Validators.required, Validators.min(0)]]
        });
        this.lineItems.push(lineItemGroup);
      }
    } else {
      this.lineItems.push(this.createLineItem());
    }
  }

  onSubmit() {
    if (this.invoiceForm.invalid) return;

    this.loading = true;
    this.error = null;

    const formValue = this.invoiceForm.value;
    const request: CreateInvoiceRequest = {
      client_id: formValue.client_id,
      issue_date: formValue.issue_date,
      due_date: formValue.due_date,
      tax_rate: formValue.tax_rate,
      notes: formValue.notes || undefined,
      line_items: formValue.line_items.map((item: any) => ({
        description: item.description,
        quantity: item.quantity,
        rate: item.rate
      }))
    };

    if (this.isEditMode && this.invoiceId) {
      this.invoiceService.updateInvoice(this.invoiceId, request).subscribe({
        next: () => {
          this.router.navigate(['/invoices', this.invoiceId]);
        },
        error: (err) => {
          this.error = 'Failed to update invoice.';
          console.error('Error updating invoice:', err);
          this.loading = false;
        }
      });
    } else {
      this.invoiceService.createInvoice(request).subscribe({
        next: (invoice) => {
          this.router.navigate(['/invoices']);
        },
        error: (err) => {
          this.error = 'Failed to create invoice.';
          console.error('Error creating invoice:', err);
          this.loading = false;
        }
      });
    }
  }

  onCancel() {
    this.router.navigate(['/invoices']);
  }
}
