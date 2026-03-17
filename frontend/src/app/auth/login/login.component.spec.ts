import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { LoginComponent } from './login.component';
import { SupabaseService } from '../../core/services/supabase.service';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let mockSupabaseService: { signIn: jasmine.Spy };
  let router: Router;

  beforeEach(async () => {
    mockSupabaseService = {
      signIn: jasmine.createSpy('signIn').and.returnValue(Promise.resolve({}))
    };

    await TestBed.configureTestingModule({
      imports: [LoginComponent, RouterTestingModule],
      providers: [
        { provide: SupabaseService, useValue: mockSupabaseService }
      ]
    }).compileComponents();

    router = TestBed.inject(Router);
    spyOn(router, 'navigate');

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have empty email and password initially', () => {
    expect(component.email).toBe('');
    expect(component.password).toBe('');
  });

  it('should display error when fields are empty on submit', async () => {
    // Arrange: leave fields empty
    component.email = '';
    component.password = '';

    // Act
    await component.onLogin();

    // Assert
    expect(component.errorMessage).toBe('Please enter email and password');
    expect(mockSupabaseService.signIn).not.toHaveBeenCalled();
  });

  it('should display error for invalid email format', async () => {
    // Arrange
    component.email = 'not-an-email';
    component.password = 'password123';

    // Act
    await component.onLogin();

    // Assert
    expect(component.errorMessage).toBe('Please enter a valid email');
    expect(mockSupabaseService.signIn).not.toHaveBeenCalled();
  });

  it('should call signIn and navigate to /dashboard on success', async () => {
    // Arrange
    component.email = 'test@test.com';
    component.password = 'password123';

    // Act
    await component.onLogin();

    // Assert
    expect(mockSupabaseService.signIn).toHaveBeenCalledWith('test@test.com', 'password123');
    expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
  });

  it('should display error on failed login', async () => {
    // Arrange
    mockSupabaseService.signIn.and.returnValue(Promise.reject(new Error('Invalid credentials')));
    component.email = 'test@test.com';
    component.password = 'wrongpassword';

    // Act
    await component.onLogin();

    // Assert
    expect(component.errorMessage).toBe('Invalid email or password');
  });
});
