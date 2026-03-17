import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of, NEVER } from 'rxjs';
import { InvoiceListComponent } from './invoice-list.component';
import { InvoiceService } from '../../services/invoice.service';
import { Invoice } from '../../models/invoice.model';

describe('InvoiceListComponent', () => {
  let component: InvoiceListComponent;
  let fixture: ComponentFixture<InvoiceListComponent>;
  let mockInvoiceService: {
    getInvoices: jasmine.Spy;
    deleteInvoice: jasmine.Spy;
  };
  let mockRouter: { navigate: jasmine.Spy };

  const mockInvoices: Invoice[] = [
    {
      id: 'inv-1',
      client_id: 'client-1',
      client_name: 'Acme Corp',
      invoice_number: 'INV-001',
      status: 'draft',
      issue_date: '2026-03-01',
      due_date: '2026-03-31',
      tax_rate: 20,
      subtotal: 1000,
      tax_amount: 200,
      total_due: 1200,
    },
    {
      id: 'inv-2',
      client_id: 'client-2',
      client_name: 'Beta Inc',
      invoice_number: 'INV-002',
      status: 'paid',
      issue_date: '2026-02-01',
      due_date: '2026-02-28',
      tax_rate: 0,
      subtotal: 500,
      tax_amount: 0,
      total_due: 500,
    },
    {
      id: 'inv-3',
      client_id: 'client-3',
      client_name: 'Gamma Ltd',
      invoice_number: 'INV-003',
      status: 'sent',
      issue_date: '2026-03-10',
      due_date: '2026-04-10',
      tax_rate: 10,
      subtotal: 2000,
      tax_amount: 200,
      total_due: 2200,
    },
    {
      id: 'inv-4',
      client_id: 'client-4',
      client_name: 'Delta Co',
      invoice_number: 'INV-004',
      status: 'overdue',
      issue_date: '2026-01-01',
      due_date: '2026-01-31',
      tax_rate: 0,
      subtotal: 300,
      tax_amount: 0,
      total_due: 300,
    },
  ];

  beforeEach(async () => {
    mockInvoiceService = {
      getInvoices: jasmine.createSpy('getInvoices').and.returnValue(of(mockInvoices)),
      deleteInvoice: jasmine.createSpy('deleteInvoice').and.returnValue(of({ message: 'deleted' })),
    };

    mockRouter = {
      navigate: jasmine.createSpy('navigate'),
    };

    await TestBed.configureTestingModule({
      imports: [InvoiceListComponent],
      providers: [
        { provide: InvoiceService, useValue: mockInvoiceService },
        { provide: Router, useValue: mockRouter },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(InvoiceListComponent);
    component = fixture.componentInstance;
  });

  // Test 1: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 2: should load invoices on init
  it('should load invoices on init', () => {
    fixture.detectChanges();

    expect(mockInvoiceService.getInvoices).toHaveBeenCalled();
    expect(component.invoices.length).toBe(4);
    expect(component.loading).toBeFalse();
  });

  // Test 3: should display invoice cards when invoices exist
  it('should display invoice cards when invoices exist', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    const cards = compiled.querySelectorAll('.invoice-card');
    expect(cards.length).toBe(4);
    expect(cards[0].textContent).toContain('INV-001');
    expect(cards[0].textContent).toContain('Acme Corp');
  });

  // Test 4: should show status badges with correct CSS classes
  it('should show status badges with correct CSS classes', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    const badges = compiled.querySelectorAll('.status-badge');
    expect(badges.length).toBe(4);
    expect(badges[0].classList).toContain('status-draft');
    expect(badges[1].classList).toContain('status-paid');
    expect(badges[2].classList).toContain('status-sent');
    expect(badges[3].classList).toContain('status-overdue');
  });

  // Test 5: should show empty state when no invoices
  it('should show empty state when no invoices', () => {
    mockInvoiceService.getInvoices.and.returnValue(of([]));

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    const emptyState = compiled.querySelector('.empty-state');
    expect(emptyState).toBeTruthy();
    expect(emptyState?.textContent).toContain('No invoices');
  });

  // Test 6: should show loading state when data is being fetched
  it('should show loading state when data is being fetched', () => {
    mockInvoiceService.getInvoices.and.returnValue(NEVER);

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(component.loading).toBeTrue();
    const loading = compiled.querySelector('.loading');
    expect(loading).toBeTruthy();
    expect(loading?.textContent).toContain('Loading');
  });
});
