import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ScheduleService } from './schedule.service';
import { SupabaseService } from '../../core/services/supabase.service';
import { Schedule } from '../models/schedule.model';

describe('ScheduleService', () => {
  let service: ScheduleService;
  let httpMock: HttpTestingController;
  let mockSupabaseService: { getAccessToken: jasmine.Spy };

  const mockSchedule: Schedule = {
    id: 'sched-123',
    user_id: 'user-123',
    client_id: 'client-123',
    client_name: 'Acme Corp',
    description: 'Monthly retainer',
    line_items: [
      { description: 'Monthly Retainer', quantity: 1, rate: 5000 },
    ],
    tax_rate: 10,
    recurrence: 'monthly',
    next_run_date: '2026-04-01',
    auto_send: false,
    active: true,
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
        ScheduleService,
        { provide: SupabaseService, useValue: mockSupabaseService }
      ]
    });

    service = TestBed.inject(ScheduleService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  // Test 13: should create ScheduleService
  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  // Test 14: should call GET /api/schedules with auth headers
  it('should call GET /api/schedules with auth headers on getSchedules()', (done: DoneFn) => {
    service.getSchedules().subscribe(schedules => {
      expect(schedules).toEqual([mockSchedule]);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/schedules'));
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush([mockSchedule]);
    });
  });

  // Test 15: should call POST /api/schedules with schedule data
  it('should call POST /api/schedules with schedule data on createSchedule()', (done: DoneFn) => {
    const createData = {
      client_id: 'client-123',
      description: 'Monthly retainer',
      recurrence: 'monthly' as const,
      next_run_date: '2026-04-01',
      tax_rate: 10,
      auto_send: false,
      line_items: [{ description: 'Monthly Retainer', quantity: 1, rate: 5000 }],
    };

    service.createSchedule(createData).subscribe(schedule => {
      expect(schedule).toEqual(mockSchedule);
      done();
    });

    setTimeout(() => {
      const req = httpMock.expectOne(r => r.url.includes('/api/schedules'));
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(createData);
      expect(req.request.headers.get('Authorization')).toBe('Bearer fake-token');
      req.flush(mockSchedule);
    });
  });
});
