import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { InvoiceService } from './invoice.service';
import { SupabaseService } from '../../core/services/supabase.service';
import { Invoice } from '../models/invoice.model';

describe('InvoiceService', () => {
  let service: InvoiceService;
  let httpMock: HttpTestingController;
  let mockSupabaseService: { getAccessToken: jasmine.Spy };

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
    notes: 'Test invoice',
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

  beforeEach(() => {
    mockSupabaseService = {
      getAccessToken: jasmine.createSpy('getAccessToken').and.returnValue(Promise.resolve('fake-token'))
    };

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        InvoiceService,
        { provide: SupabaseService, useValue: mockSupabaseService }
      ]
    });

    service = TestBed.inject(InvoiceService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  // Test 1: should be created
  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  // Test 2: should call GET /api/invoices with auth headers on getInvoices()
  it('should call GET /api/invoices with auth headers on getInvoices()', (done: DoneFn) => {
    service.getInvoices().subscribe(invoices => {
      expect(invoices).toEqual([mockInvoice]);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices'));
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush([mockInvoice]);
    });
  });

  // Test 3: should call GET /api/invoices/{id} on getInvoice()
  it('should call GET /api/invoices/{id} on getInvoice()', (done: DoneFn) => {
    service.getInvoice('inv-123').subscribe((invoice: Invoice) => {
      expect(invoice).toEqual(mockInvoice);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices/inv-123'));
      expect(req.request.method).toBe('GET');
      req.flush(mockInvoice);
    });
  });

  // Test 4: should call POST /api/invoices with invoice data on createInvoice()
  it('should call POST /api/invoices with invoice data on createInvoice()', (done: DoneFn) => {
    const createData = {
      client_id: 'client-123',
      due_date: '2026-03-31',
      line_items: [{ description: 'Web Dev', quantity: 10, rate: 100 }]
    };

    service.createInvoice(createData).subscribe(invoice => {
      expect(invoice).toEqual(mockInvoice);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices'));
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(createData);
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush(mockInvoice);
    });
  });

  // Test 5: should call PATCH /api/invoices/{id} on updateInvoice()
  it('should call PATCH /api/invoices/{id} on updateInvoice()', (done: DoneFn) => {
    const updates = { notes: 'Updated notes' };

    service.updateInvoice('inv-123', updates).subscribe((invoice: Invoice) => {
      expect(invoice.notes).toBe('Updated notes');
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices/inv-123'));
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual(updates);
      req.flush({ ...mockInvoice, notes: 'Updated notes' });
    });
  });

  // Test 6: should call DELETE /api/invoices/{id} on deleteInvoice()
  it('should call DELETE /api/invoices/{id} on deleteInvoice()', (done: DoneFn) => {
    service.deleteInvoice('inv-123').subscribe((result: any) => {
      expect(result).toBeTruthy();
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices/inv-123'));
      expect(req.request.method).toBe('DELETE');
      req.flush({ message: 'Invoice deleted successfully' });
    });
  });

  // Test 7: should call PATCH /api/invoices/{id}/status on updateStatus()
  it('should call PATCH /api/invoices/{id}/status on updateStatus()', (done: DoneFn) => {
    service.updateStatus('inv-123', 'paid').subscribe((invoice: Invoice) => {
      expect(invoice.status).toBe('paid');
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices/inv-123/status'));
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual({ status: 'paid' });
      req.flush({ ...mockInvoice, status: 'paid' });
    });
  });

  // Test 8: should call GET /api/invoices/{id}/pdf as blob on downloadPdf()
  it('should call GET /api/invoices/{id}/pdf as blob on downloadPdf()', (done: DoneFn) => {
    const mockBlob = new Blob(['%PDF-fake'], { type: 'application/pdf' });

    service.downloadPdf('inv-123', 'INV-001').subscribe((blob: Blob) => {
      expect(blob).toBeTruthy();
      expect(blob.type).toBe('application/pdf');
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices/inv-123/pdf'));
      expect(req.request.method).toBe('GET');
      expect(req.request.responseType).toBe('blob');
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush(mockBlob);
    });
  });

  // Test 9: should call POST /api/invoices/{id}/send on sendInvoice()
  it('should call POST /api/invoices/{id}/send on sendInvoice()', (done: DoneFn) => {
    service.sendInvoice('inv-123').subscribe((result: any) => {
      expect(result.message).toBe('Invoice sent successfully');
      expect(result.status).toBe('sent');
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/invoices/inv-123/send'));
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush({ message: 'Invoice sent successfully', status: 'sent' });
    });
  });
});
