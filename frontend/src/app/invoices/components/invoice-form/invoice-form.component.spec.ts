import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { InvoiceFormComponent } from './invoice-form.component';
import { InvoiceService } from '../../services/invoice.service';
import { ClientService } from '../../../clients/services/client.service';
import { Client } from '../../../clients/models/client.model';

describe('InvoiceFormComponent', () => {
  let component: InvoiceFormComponent;
  let fixture: ComponentFixture<InvoiceFormComponent>;
  let mockInvoiceService: {
    createInvoice: jasmine.Spy;
    getInvoice: jasmine.Spy;
    updateInvoice: jasmine.Spy;
  };
  let mockClientService: {
    getClients: jasmine.Spy;
  };
  let mockRouter: { navigate: jasmine.Spy };

  const mockClients: Client[] = [
    { id: 'client-1', name: 'Acme Corp', email: 'billing@acme.com' },
    { id: 'client-2', name: 'Beta Inc', email: 'info@beta.com' },
  ];

  beforeEach(async () => {
    mockInvoiceService = {
      createInvoice: jasmine.createSpy('createInvoice').and.returnValue(of({ id: 'inv-new' })),
      getInvoice: jasmine.createSpy('getInvoice'),
      updateInvoice: jasmine.createSpy('updateInvoice'),
    };

    mockClientService = {
      getClients: jasmine.createSpy('getClients').and.returnValue(of(mockClients)),
    };

    mockRouter = {
      navigate: jasmine.createSpy('navigate'),
    };

    await TestBed.configureTestingModule({
      imports: [InvoiceFormComponent, ReactiveFormsModule],
      providers: [
        { provide: InvoiceService, useValue: mockInvoiceService },
        { provide: ClientService, useValue: mockClientService },
        { provide: Router, useValue: mockRouter },
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => null } } } },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(InvoiceFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // Test 1: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 2: should have required form fields (client_id, due_date)
  it('should have required form fields', () => {
    const clientId = component.invoiceForm.get('client_id');
    const dueDate = component.invoiceForm.get('due_date');

    // client_id is required
    clientId?.setValue('');
    clientId?.markAsTouched();
    expect(clientId?.valid).toBeFalse();

    // due_date is required
    dueDate?.setValue('');
    dueDate?.markAsTouched();
    expect(dueDate?.valid).toBeFalse();
  });

  // Test 3: should load clients for dropdown on init
  it('should load clients for dropdown on init', () => {
    expect(mockClientService.getClients).toHaveBeenCalled();
    expect(component.clients.length).toBe(2);
    expect(component.clients[0].name).toBe('Acme Corp');
  });

  // Test 4: should start with one empty line item
  it('should start with one empty line item', () => {
    expect(component.lineItems.length).toBe(1);
    const firstItem = component.lineItems.at(0);
    expect(firstItem.get('description')?.value).toBe('');
    expect(firstItem.get('quantity')?.value).toBe(1);
    expect(firstItem.get('rate')?.value).toBe(0);
  });

  // Test 5: should add a line item when addLineItem is called
  it('should add a line item when addLineItem is called', () => {
    expect(component.lineItems.length).toBe(1);

    component.addLineItem();

    expect(component.lineItems.length).toBe(2);
  });

  // Test 6: should remove a line item when removeLineItem is called
  it('should remove a line item when removeLineItem is called', () => {
    component.addLineItem();
    expect(component.lineItems.length).toBe(2);

    component.removeLineItem(0);

    expect(component.lineItems.length).toBe(1);
  });

  // Test 7: should calculate line item amount as quantity times rate
  it('should calculate line item amount as quantity times rate', () => {
    const firstItem = component.lineItems.at(0);
    firstItem.get('quantity')?.setValue(5);
    firstItem.get('rate')?.setValue(100);

    expect(component.getLineItemAmount(0)).toBe(500);
  });

  // Test 8: should calculate subtotal, tax, and total
  it('should calculate subtotal, tax, and total', () => {
    // Set up first line item
    const firstItem = component.lineItems.at(0);
    firstItem.get('quantity')?.setValue(10);
    firstItem.get('rate')?.setValue(100);

    // Add second line item
    component.addLineItem();
    const secondItem = component.lineItems.at(1);
    secondItem.get('quantity')?.setValue(5);
    secondItem.get('rate')?.setValue(50);

    // Set tax rate to 20%
    component.invoiceForm.get('tax_rate')?.setValue(20);

    // subtotal = 1000 + 250 = 1250
    expect(component.subtotal).toBe(1250);
    // tax = 1250 * 20 / 100 = 250
    expect(component.taxAmount).toBe(250);
    // total = 1250 + 250 = 1500
    expect(component.totalDue).toBe(1500);
  });
});
