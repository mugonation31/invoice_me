import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ScheduleService } from '../../services/schedule.service';
import { Schedule } from '../../models/schedule.model';

@Component({
  selector: 'app-schedule-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './schedule-list.component.html',
  styleUrl: './schedule-list.component.scss'
})
export class ScheduleListComponent implements OnInit {
  private scheduleService = inject(ScheduleService);
  private router = inject(Router);

  schedules: Schedule[] = [];
  loading = false;
  error: string | null = null;

  ngOnInit() {
    this.loadSchedules();
  }

  loadSchedules() {
    this.loading = true;
    this.error = null;

    this.scheduleService.getSchedules().subscribe({
      next: (schedules) => {
        this.schedules = schedules;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load schedules. Please try again.';
        console.error('Error loading schedules:', err);
        this.loading = false;
      }
    });
  }

  addSchedule() {
    this.router.navigate(['/schedules/new']);
  }

  toggleActive(schedule: Schedule) {
    if (!schedule.id) return;
    this.scheduleService.updateSchedule(schedule.id, { active: !schedule.active }).subscribe({
      next: () => this.loadSchedules(),
      error: (err) => {
        console.error('Error toggling schedule:', err);
        this.error = 'Failed to update schedule.';
      }
    });
  }

  deleteSchedule(schedule: Schedule) {
    if (!schedule.id) return;

    if (confirm('Are you sure you want to delete this schedule?')) {
      this.scheduleService.deleteSchedule(schedule.id).subscribe({
        next: () => this.loadSchedules(),
        error: (err) => {
          console.error('Error deleting schedule:', err);
          this.error = 'Failed to delete schedule.';
        }
      });
    }
  }

  getRecurrenceLabel(recurrence: string): string {
    const labels: Record<string, string> = {
      once: 'Once',
      weekly: 'Weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      yearly: 'Yearly',
    };
    return labels[recurrence] || recurrence;
  }

  trackByScheduleId(index: number, schedule: Schedule): string {
    return schedule.id || index.toString();
  }
}
