import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { Invoice } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './invoice-list.component.html',
  styleUrl: './invoice-list.component.scss'
})
export class InvoiceListComponent implements OnInit {
  private invoiceService = inject(InvoiceService);
  private router = inject(Router);

  invoices: Invoice[] = [];
  loading = false;
  error: string | null = null;

  ngOnInit() {
    this.loadInvoices();
  }

  loadInvoices() {
    this.loading = true;
    this.error = null;

    this.invoiceService.getInvoices().subscribe({
      next: (invoices) => {
        this.invoices = invoices;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load invoices. Please try again.';
        console.error('Error loading invoices:', err);
        this.loading = false;
      }
    });
  }

  navigateToNew() {
    this.router.navigate(['/invoices/new']);
  }

  navigateToDetail(invoice: Invoice) {
    this.router.navigate(['/invoices', invoice.id]);
  }

  formatCurrency(amount: number | undefined): string {
    if (amount === undefined || amount === null) return '£0.00';
    return '£' + amount.toFixed(2);
  }

  trackByInvoiceId(index: number, invoice: Invoice): string {
    return invoice.id || index.toString();
  }
}
