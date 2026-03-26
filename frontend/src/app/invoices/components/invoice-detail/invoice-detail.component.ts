import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { SettingsService } from '../../../settings/services/settings.service';
import { Invoice } from '../../models/invoice.model';
import { CompanySettings } from '../../../settings/models/settings.model';

@Component({
  selector: 'app-invoice-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './invoice-detail.component.html',
  styleUrl: './invoice-detail.component.scss'
})
export class InvoiceDetailComponent implements OnInit {
  private invoiceService = inject(InvoiceService);
  private settingsService = inject(SettingsService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  invoice: Invoice | null = null;
  settings: CompanySettings | null = null;
  loading = false;
  downloadingPdf = false;
  sendingEmail = false;
  error: string | null = null;
  successMessage: string | null = null;

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadInvoice(id);
      this.loadSettings();
    }
  }

  private loadInvoice(id: string) {
    this.loading = true;
    this.invoiceService.getInvoice(id).subscribe({
      next: (invoice) => {
        this.invoice = invoice;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load invoice.';
        console.error('Error loading invoice:', err);
        this.loading = false;
      }
    });
  }

  private loadSettings() {
    this.settingsService.getSettings().subscribe({
      next: (settings) => {
        this.settings = settings;
      },
      error: () => {
        // Settings may not exist yet
      }
    });
  }

  formatCurrency(amount: number | undefined): string {
    if (amount === undefined || amount === null) return '£0.00';
    return '£' + amount.toFixed(2);
  }

  navigateToEdit() {
    if (this.invoice?.id) {
      this.router.navigate(['/invoices', this.invoice.id, 'edit']);
    }
  }

  markAsPaid() {
    if (!this.invoice?.id) return;

    this.invoiceService.updateStatus(this.invoice.id, 'paid').subscribe({
      next: (updated) => {
        this.invoice = updated;
      },
      error: (err) => {
        this.error = 'Failed to update status.';
        console.error('Error updating status:', err);
      }
    });
  }

  deleteInvoice() {
    if (!this.invoice?.id) return;

    if (confirm('Are you sure you want to delete this invoice?')) {
      this.invoiceService.deleteInvoice(this.invoice.id).subscribe({
        next: () => {
          this.router.navigate(['/invoices']);
        },
        error: (err) => {
          this.error = 'Failed to delete invoice.';
          console.error('Error deleting invoice:', err);
        }
      });
    }
  }

  sendInvoice() {
    if (!this.invoice?.id) return;

    this.sendingEmail = true;
    this.error = null;
    this.successMessage = null;
    this.invoiceService.sendInvoice(this.invoice.id).subscribe({
      next: (result) => {
        if (this.invoice) {
          this.invoice = { ...this.invoice, status: 'sent' };
        }
        this.successMessage = result.message;
        this.sendingEmail = false;
        setTimeout(() => this.successMessage = null, 5000);
      },
      error: (err) => {
        this.error = 'Failed to send invoice.';
        console.error('Error sending invoice:', err);
        this.sendingEmail = false;
      }
    });
  }

  downloadPdf() {
    if (!this.invoice?.id || !this.invoice?.invoice_number) return;

    this.downloadingPdf = true;
    this.invoiceService.downloadPdf(this.invoice.id, this.invoice.invoice_number).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.invoice!.invoice_number}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: (err) => {
        this.error = 'Failed to download PDF.';
        console.error('Error downloading PDF:', err);
        this.downloadingPdf = false;
      }
    });
  }

  goBack() {
    this.router.navigate(['/invoices']);
  }
}
