import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ClientService } from './client.service';
import { SupabaseService } from '../../core/services/supabase.service';
import { Client } from '../models/client.model';

describe('ClientService', () => {
  let service: ClientService;
  let httpMock: HttpTestingController;
  let mockSupabaseService: { getAccessToken: jasmine.Spy };

  const mockClient: Client = {
    id: 'client-123',
    name: 'Acme Corp',
    email: 'billing@acme.com',
    phone: '555-0100',
    address: '123 Main St',
    user_id: 'user-123',
    created_at: '2026-01-15T10:00:00',
    updated_at: '2026-01-15T10:00:00',
  };

  beforeEach(() => {
    mockSupabaseService = {
      getAccessToken: jasmine.createSpy('getAccessToken').and.returnValue(Promise.resolve('fake-token'))
    };

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        ClientService,
        { provide: SupabaseService, useValue: mockSupabaseService }
      ]
    });

    service = TestBed.inject(ClientService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  // Test 11: should be created
  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  // Test 12: should call GET /api/clients with auth headers
  it('should call GET /api/clients with auth headers on getClients()', (done: DoneFn) => {
    service.getClients().subscribe(clients => {
      expect(clients).toEqual([mockClient]);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/clients'));
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush([mockClient]);
    });
  });

  // Test 13: should call POST /api/clients with client data
  it('should call POST /api/clients with client data on createClient()', (done: DoneFn) => {
    const createData = { name: 'Acme Corp', email: 'billing@acme.com' };

    service.createClient(createData).subscribe(client => {
      expect(client).toEqual(mockClient);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/clients'));
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(createData);
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush(mockClient);
    });
  });

  // Test 14: should call GET /api/clients/{id}
  it('should call GET /api/clients/{id} on getClient()', (done: DoneFn) => {
    service.getClient('client-123').subscribe((client: Client) => {
      expect(client).toEqual(mockClient);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/clients/client-123'));
      expect(req.request.method).toBe('GET');
      req.flush(mockClient);
    });
  });

  // Test 15: should call PATCH /api/clients/{id}
  it('should call PATCH /api/clients/{id} on updateClient()', (done: DoneFn) => {
    const updates = { name: 'Acme Corporation' };

    service.updateClient('client-123', updates).subscribe((client: Client) => {
      expect(client.name).toBe('Acme Corporation');
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/clients/client-123'));
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual(updates);
      req.flush({ ...mockClient, name: 'Acme Corporation' });
    });
  });

  // Test 16: should call DELETE /api/clients/{id}
  it('should call DELETE /api/clients/{id} on deleteClient()', (done: DoneFn) => {
    service.deleteClient('client-123').subscribe((result: any) => {
      expect(result).toBeTruthy();
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/clients/client-123'));
      expect(req.request.method).toBe('DELETE');
      req.flush({ message: 'Client deleted successfully' });
    });
  });
});
