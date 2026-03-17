import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ScheduleListComponent } from './schedule-list.component';
import { ScheduleService } from '../../services/schedule.service';
import { Schedule } from '../../models/schedule.model';
import { of, NEVER } from 'rxjs';

describe('ScheduleListComponent', () => {
  let component: ScheduleListComponent;
  let fixture: ComponentFixture<ScheduleListComponent>;
  let mockScheduleService: {
    getSchedules: jasmine.Spy;
    deleteSchedule: jasmine.Spy;
    updateSchedule: jasmine.Spy;
  };

  const mockSchedules: Schedule[] = [
    {
      id: 'sched-1',
      client_id: 'client-1',
      client_name: 'Acme Corp',
      description: 'Monthly retainer',
      line_items: [{ description: 'Retainer', quantity: 1, rate: 5000 }],
      tax_rate: 10,
      recurrence: 'monthly',
      next_run_date: '2026-04-01',
      auto_send: false,
      active: true,
      user_id: 'user-123',
      created_at: '2026-03-01T10:00:00',
      updated_at: '2026-03-01T10:00:00',
    },
    {
      id: 'sched-2',
      client_id: 'client-2',
      client_name: 'Beta Inc',
      description: 'Weekly consulting',
      line_items: [{ description: 'Consulting', quantity: 2, rate: 1000 }],
      tax_rate: 0,
      recurrence: 'weekly',
      next_run_date: '2026-03-20',
      auto_send: true,
      active: true,
      user_id: 'user-123',
      created_at: '2026-03-01T10:00:00',
      updated_at: '2026-03-01T10:00:00',
    },
  ];

  beforeEach(async () => {
    mockScheduleService = {
      getSchedules: jasmine.createSpy('getSchedules').and.returnValue(of(mockSchedules)),
      deleteSchedule: jasmine.createSpy('deleteSchedule').and.returnValue(of({ message: 'deleted' })),
      updateSchedule: jasmine.createSpy('updateSchedule').and.returnValue(of(mockSchedules[0])),
    };

    await TestBed.configureTestingModule({
      imports: [ScheduleListComponent],
      providers: [
        { provide: ScheduleService, useValue: mockScheduleService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ScheduleListComponent);
    component = fixture.componentInstance;
  });

  // Test 16: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 17: should load schedules on init
  it('should load schedules on init', () => {
    // Act
    fixture.detectChanges(); // triggers ngOnInit

    // Assert
    expect(mockScheduleService.getSchedules).toHaveBeenCalled();
    expect(component.schedules.length).toBe(2);
    expect(component.loading).toBeFalse();
  });

  // Test 18: should display schedule cards when schedules exist
  it('should display schedule cards when schedules exist', () => {
    // Act
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    // Assert
    const cards = compiled.querySelectorAll('.schedule-card');
    expect(cards.length).toBe(2);
    expect(cards[0].textContent).toContain('Acme Corp');
    expect(cards[1].textContent).toContain('Beta Inc');
  });
});
