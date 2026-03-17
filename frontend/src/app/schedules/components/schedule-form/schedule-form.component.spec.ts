import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { ScheduleFormComponent } from './schedule-form.component';
import { ScheduleService } from '../../services/schedule.service';
import { ClientService } from '../../../clients/services/client.service';
import { Client } from '../../../clients/models/client.model';

describe('ScheduleFormComponent', () => {
  let component: ScheduleFormComponent;
  let fixture: ComponentFixture<ScheduleFormComponent>;
  let mockScheduleService: {
    createSchedule: jasmine.Spy;
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
    mockScheduleService = {
      createSchedule: jasmine.createSpy('createSchedule').and.returnValue(of({ id: 'sched-new' })),
    };

    mockClientService = {
      getClients: jasmine.createSpy('getClients').and.returnValue(of(mockClients)),
    };

    mockRouter = {
      navigate: jasmine.createSpy('navigate'),
    };

    await TestBed.configureTestingModule({
      imports: [ScheduleFormComponent, ReactiveFormsModule],
      providers: [
        { provide: ScheduleService, useValue: mockScheduleService },
        { provide: ClientService, useValue: mockClientService },
        { provide: Router, useValue: mockRouter },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ScheduleFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // Test 19: should create the component
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // Test 20: should have required fields (client_id, next_run_date, recurrence)
  it('should have required fields', () => {
    const clientId = component.scheduleForm.get('client_id');
    const nextRunDate = component.scheduleForm.get('next_run_date');
    const recurrence = component.scheduleForm.get('recurrence');

    // client_id is required
    clientId?.setValue('');
    clientId?.markAsTouched();
    expect(clientId?.valid).toBeFalse();

    // next_run_date is required
    nextRunDate?.setValue('');
    nextRunDate?.markAsTouched();
    expect(nextRunDate?.valid).toBeFalse();

    // recurrence is required
    recurrence?.setValue('');
    recurrence?.markAsTouched();
    expect(recurrence?.valid).toBeFalse();
  });

  // Test 21: should load clients for dropdown on init
  it('should load clients for dropdown on init', () => {
    expect(mockClientService.getClients).toHaveBeenCalled();
    expect(component.clients.length).toBe(2);
    expect(component.clients[0].name).toBe('Acme Corp');
  });
});
