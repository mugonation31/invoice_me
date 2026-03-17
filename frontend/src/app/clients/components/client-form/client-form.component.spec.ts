import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { ClientFormComponent } from './client-form.component';
import { Client } from '../../models/client.model';

describe('ClientFormComponent', () => {
  let component: ClientFormComponent;
  let fixture: ComponentFixture<ClientFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClientFormComponent, ReactiveFormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(ClientFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // Test 24: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 25: should have name as required field
  it('should have name as required field', () => {
    // Arrange
    const nameControl = component.clientForm.get('name');

    // Act - set empty value
    nameControl?.setValue('');
    nameControl?.markAsTouched();

    // Assert
    expect(nameControl?.valid).toBeFalse();
    expect(nameControl?.errors?.['required']).toBeTruthy();
  });

  // Test 26: should emit formSubmit with form data on valid submit
  it('should emit formSubmit with form data on valid submit', () => {
    // Arrange
    let emittedData: Partial<Client> | undefined;
    component.formSubmit.subscribe((data: Partial<Client>) => {
      emittedData = data;
    });

    component.clientForm.setValue({
      name: 'Acme Corp',
      email: 'billing@acme.com',
      phone: '555-0100',
      address: '123 Main St'
    });

    // Act
    component.onSubmit();

    // Assert
    expect(emittedData).toBeDefined();
    expect(emittedData?.name).toBe('Acme Corp');
    expect(emittedData?.email).toBe('billing@acme.com');
    expect(emittedData?.phone).toBe('555-0100');
    expect(emittedData?.address).toBe('123 Main St');
  });

  // Test 27: should emit formCancel on cancel
  it('should emit formCancel on cancel', () => {
    // Arrange
    let cancelCalled = false;
    component.formCancel.subscribe(() => {
      cancelCalled = true;
    });

    // Act
    component.onCancel();

    // Assert
    expect(cancelCalled).toBeTrue();
  });

  // Test 28: should disable submit button when form is invalid
  it('should disable submit button when form is invalid', () => {
    // Arrange - name is empty (invalid)
    component.clientForm.get('name')?.setValue('');
    fixture.detectChanges();

    // Assert
    const compiled = fixture.nativeElement as HTMLElement;
    const submitButton = compiled.querySelector('.btn-submit') as HTMLButtonElement;
    expect(submitButton.disabled).toBeTrue();
  });

  // Test 29: should populate form when editing existing client
  it('should populate form when editing existing client', () => {
    // Arrange
    const existingClient: Client = {
      id: 'client-123',
      name: 'Acme Corp',
      email: 'billing@acme.com',
      phone: '555-0100',
      address: '123 Main St',
      user_id: 'user-123',
      created_at: '2026-01-15T10:00:00',
      updated_at: '2026-01-15T10:00:00',
    };

    // Act - create a new component instance with client input
    component.client = existingClient;
    component.ngOnInit();
    fixture.detectChanges();

    // Assert
    expect(component.isEditMode).toBeTrue();
    expect(component.clientForm.get('name')?.value).toBe('Acme Corp');
    expect(component.clientForm.get('email')?.value).toBe('billing@acme.com');
    expect(component.clientForm.get('phone')?.value).toBe('555-0100');
    expect(component.clientForm.get('address')?.value).toBe('123 Main St');
  });
});
