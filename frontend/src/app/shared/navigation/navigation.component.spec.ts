import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { BehaviorSubject } from 'rxjs';
import { NavigationComponent } from './navigation.component';
import { SupabaseService } from '../../core/services/supabase.service';

describe('NavigationComponent', () => {
  let component: NavigationComponent;
  let fixture: ComponentFixture<NavigationComponent>;
  let mockCurrentUser$: BehaviorSubject<any>;
  let mockSupabaseService: { currentUser$: BehaviorSubject<any>; signOut: jasmine.Spy };
  let router: Router;

  beforeEach(async () => {
    mockCurrentUser$ = new BehaviorSubject<any>(null);
    mockSupabaseService = {
      currentUser$: mockCurrentUser$,
      signOut: jasmine.createSpy('signOut').and.returnValue(Promise.resolve())
    };

    await TestBed.configureTestingModule({
      imports: [NavigationComponent, RouterTestingModule],
      providers: [
        { provide: SupabaseService, useValue: mockSupabaseService }
      ]
    }).compileComponents();

    router = TestBed.inject(Router);
    spyOn(router, 'navigate');

    fixture = TestBed.createComponent(NavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should not show nav when user is not logged in', () => {
    // Arrange: user is null (default)
    fixture.detectChanges();

    // Assert: nav element should not be in DOM
    const nav = fixture.nativeElement.querySelector('nav');
    expect(nav).toBeNull();
  });

  it('should show nav with user name when user is logged in', () => {
    // Arrange: set a logged-in user
    mockCurrentUser$.next({
      id: '123',
      email: 'test@test.com',
      user_metadata: { name: 'John Doe' }
    });
    fixture.detectChanges();

    // Assert: nav should be visible with user name
    const nav = fixture.nativeElement.querySelector('nav');
    expect(nav).toBeTruthy();
    const userName = fixture.nativeElement.querySelector('.user-name');
    expect(userName.textContent).toContain('John Doe');
  });

  it('should call signOut and navigate to /login on logout', async () => {
    // Arrange: user is logged in
    mockCurrentUser$.next({ id: '123', email: 'test@test.com', user_metadata: { name: 'Test' } });
    fixture.detectChanges();

    // Act
    await component.logout();

    // Assert
    expect(mockSupabaseService.signOut).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('should display nav links for Dashboard, Clients, Invoices, Schedules, Settings', () => {
    // Arrange: user is logged in
    mockCurrentUser$.next({ id: '123', email: 'test@test.com', user_metadata: { name: 'Test' } });
    fixture.detectChanges();

    // Assert: check for nav links
    const navLinks = fixture.nativeElement.querySelectorAll('.nav-links a');
    const linkTexts = Array.from(navLinks).map((link: any) => link.textContent.trim());

    expect(linkTexts).toContain('Dashboard');
    expect(linkTexts).toContain('Clients');
    expect(linkTexts).toContain('Invoices');
    expect(linkTexts).toContain('Schedules');
    expect(linkTexts).toContain('Settings');
  });
});
