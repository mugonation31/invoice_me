import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { InvoiceDetailComponent } from './invoice-detail.component';
import { InvoiceService } from '../../services/invoice.service';
import { SettingsService } from '../../../settings/services/settings.service';
import { Invoice } from '../../models/invoice.model';
import { CompanySettings } from '../../../settings/models/settings.model';

describe('InvoiceDetailComponent', () => {
  let component: InvoiceDetailComponent;
  let fixture: ComponentFixture<InvoiceDetailComponent>;
  let mockInvoiceService: {
    getInvoice: jasmine.Spy;
    updateStatus: jasmine.Spy;
    deleteInvoice: jasmine.Spy;
  };
  let mockSettingsService: {
    getSettings: jasmine.Spy;
  };
  let mockRouter: { navigate: jasmine.Spy };

  const mockInvoice: Invoice = {
    id: 'inv-123',
    user_id: 'user-123',
    client_id: 'client-123',
    client_name: 'Acme Corp',
    client_email: 'billing@acme.com',
    invoice_number: 'INV-001',
    status: 'draft',
    issue_date: '2026-03-01',
    due_date: '2026-03-31',
    tax_rate: 20,
    subtotal: 1000,
    tax_amount: 200,
    total_due: 1200,
    notes: 'Payment due within 30 days',
    line_items: [
      {
        id: 'li-1',
        description: 'Web Development',
        quantity: 10,
        rate: 100,
        amount: 1000,
        sort_order: 0,
        created_at: '2026-03-01T10:00:00',
      },
    ],
    created_at: '2026-03-01T10:00:00',
    updated_at: '2026-03-01T10:00:00',
  };

  const mockSettings: CompanySettings = {
    id: 'settings-1',
    company_name: 'My Company Ltd',
    company_email: 'info@mycompany.com',
  };

  beforeEach(async () => {
    mockInvoiceService = {
      getInvoice: jasmine.createSpy('getInvoice').and.returnValue(of(mockInvoice)),
      updateStatus: jasmine.createSpy('updateStatus').and.returnValue(of({ ...mockInvoice, status: 'paid' })),
      deleteInvoice: jasmine.createSpy('deleteInvoice').and.returnValue(of({ message: 'deleted' })),
    };

    mockSettingsService = {
      getSettings: jasmine.createSpy('getSettings').and.returnValue(of(mockSettings)),
    };

    mockRouter = {
      navigate: jasmine.createSpy('navigate'),
    };

    await TestBed.configureTestingModule({
      imports: [InvoiceDetailComponent],
      providers: [
        { provide: InvoiceService, useValue: mockInvoiceService },
        { provide: SettingsService, useValue: mockSettingsService },
        { provide: Router, useValue: mockRouter },
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => 'inv-123' } } } },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(InvoiceDetailComponent);
    component = fixture.componentInstance;
  });

  // Test 1: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 2: should load invoice on init
  it('should load invoice on init', () => {
    fixture.detectChanges();

    expect(mockInvoiceService.getInvoice).toHaveBeenCalledWith('inv-123');
    expect(component.invoice).toBeTruthy();
    expect(component.invoice?.invoice_number).toBe('INV-001');
  });

  // Test 3: should display invoice data
  it('should display invoice data', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('INV-001');
    expect(compiled.textContent).toContain('Acme Corp');
    expect(compiled.textContent).toContain('2026-03-01');
    expect(compiled.textContent).toContain('2026-03-31');
  });

  // Test 4: should display line items table
  it('should display line items table', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    const rows = compiled.querySelectorAll('.line-item-row');
    expect(rows.length).toBe(1);
    expect(rows[0].textContent).toContain('Web Development');
    expect(rows[0].textContent).toContain('10');
    expect(rows[0].textContent).toContain('100');
  });

  // Test 5: should have action buttons
  it('should have action buttons', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    const editBtn = compiled.querySelector('.btn-edit');
    const paidBtn = compiled.querySelector('.btn-mark-paid');
    const deleteBtn = compiled.querySelector('.btn-delete');

    expect(editBtn).toBeTruthy();
    expect(paidBtn).toBeTruthy();
    expect(deleteBtn).toBeTruthy();
  });
});
