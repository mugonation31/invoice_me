import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { ClientListComponent } from './client-list.component';
import { ClientService } from '../../services/client.service';
import { Client } from '../../models/client.model';
import { of, throwError, NEVER } from 'rxjs';

describe('ClientListComponent', () => {
  let component: ClientListComponent;
  let fixture: ComponentFixture<ClientListComponent>;
  let mockClientService: {
    getClients: jasmine.Spy;
    deleteClient: jasmine.Spy;
    createClient: jasmine.Spy;
    updateClient: jasmine.Spy;
  };

  const mockClients: Client[] = [
    {
      id: 'client-1',
      name: 'Acme Corp',
      email: 'billing@acme.com',
      phone: '555-0100',
      address: '123 Main St',
      user_id: 'user-123',
      created_at: '2026-01-15T10:00:00',
      updated_at: '2026-01-15T10:00:00',
    },
    {
      id: 'client-2',
      name: 'Beta Inc',
      email: 'info@beta.com',
      user_id: 'user-123',
      created_at: '2026-01-16T10:00:00',
      updated_at: '2026-01-16T10:00:00',
    },
  ];

  beforeEach(async () => {
    mockClientService = {
      getClients: jasmine.createSpy('getClients').and.returnValue(of(mockClients)),
      deleteClient: jasmine.createSpy('deleteClient').and.returnValue(of({ message: 'deleted' })),
      createClient: jasmine.createSpy('createClient').and.returnValue(of(mockClients[0])),
      updateClient: jasmine.createSpy('updateClient').and.returnValue(of(mockClients[0])),
    };

    await TestBed.configureTestingModule({
      imports: [ClientListComponent],
      providers: [
        { provide: ClientService, useValue: mockClientService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ClientListComponent);
    component = fixture.componentInstance;
  });

  // Test 17: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 18: should load clients on init
  it('should load clients on init', () => {
    // Act
    fixture.detectChanges(); // triggers ngOnInit

    // Assert
    expect(mockClientService.getClients).toHaveBeenCalled();
    expect(component.clients.length).toBe(2);
    expect(component.loading).toBeFalse();
  });

  // Test 19: should display client cards when clients exist
  it('should display client cards when clients exist', () => {
    // Act
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    // Assert
    const cards = compiled.querySelectorAll('.client-card');
    expect(cards.length).toBe(2);
    expect(cards[0].textContent).toContain('Acme Corp');
    expect(cards[1].textContent).toContain('Beta Inc');
  });

  // Test 20: should show empty state when no clients
  it('should show empty state when no clients', () => {
    // Arrange
    mockClientService.getClients.and.returnValue(of([]));

    // Act
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    // Assert
    const emptyState = compiled.querySelector('.empty-state');
    expect(emptyState).toBeTruthy();
    expect(emptyState?.textContent).toContain('No clients');
  });

  // Test 21: should show loading state
  it('should show loading state when data is being fetched', () => {
    // Arrange - make getClients return an observable that never completes
    mockClientService.getClients.and.returnValue(NEVER);

    // Act
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    // Assert
    expect(component.loading).toBeTrue();
    const loading = compiled.querySelector('.loading');
    expect(loading).toBeTruthy();
    expect(loading?.textContent).toContain('Loading');
  });

  // Test 22: should toggle form visibility
  it('should toggle form visibility', () => {
    // Arrange
    fixture.detectChanges();
    expect(component.showForm).toBeFalse();

    // Act
    component.toggleForm();

    // Assert
    expect(component.showForm).toBeTrue();

    // Act again
    component.toggleForm();
    expect(component.showForm).toBeFalse();
  });

  // Test 23: should call deleteClient when delete is confirmed
  it('should call deleteClient when delete is confirmed', () => {
    // Arrange
    fixture.detectChanges();
    spyOn(window, 'confirm').and.returnValue(true);

    // Act
    component.deleteClient(mockClients[0]);

    // Assert
    expect(mockClientService.deleteClient).toHaveBeenCalledWith('client-1');
  });
});
