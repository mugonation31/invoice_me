import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ScheduleService } from '../../services/schedule.service';
import { ClientService } from '../../../clients/services/client.service';
import { Client } from '../../../clients/models/client.model';
import { CreateScheduleRequest } from '../../models/schedule.model';

@Component({
  selector: 'app-schedule-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './schedule-form.component.html',
  styleUrl: './schedule-form.component.scss'
})
export class ScheduleFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private scheduleService = inject(ScheduleService);
  private clientService = inject(ClientService);
  private router = inject(Router);

  scheduleForm!: FormGroup;
  clients: Client[] = [];
  loading = false;
  error: string | null = null;

  recurrenceOptions = [
    { value: 'once', label: 'Once' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'yearly', label: 'Yearly' },
  ];

  ngOnInit() {
    this.initForm();
    this.loadClients();
  }

  private initForm() {
    this.scheduleForm = this.fb.group({
      client_id: ['', Validators.required],
      description: [''],
      recurrence: ['', Validators.required],
      next_run_date: ['', Validators.required],
      auto_send: [false],
      tax_rate: [0],
      line_items: this.fb.array([this.createLineItem()])
    });
  }

  private createLineItem(): FormGroup {
    return this.fb.group({
      description: ['', Validators.required],
      quantity: [1, [Validators.required, Validators.min(0.01)]],
      rate: [0, [Validators.required, Validators.min(0)]]
    });
  }

  get lineItems(): FormArray {
    return this.scheduleForm.get('line_items') as FormArray;
  }

  addLineItem() {
    this.lineItems.push(this.createLineItem());
  }

  removeLineItem(index: number) {
    if (this.lineItems.length > 0) {
      this.lineItems.removeAt(index);
    }
  }

  getLineItemAmount(index: number): number {
    const item = this.lineItems.at(index);
    const quantity = item.get('quantity')?.value || 0;
    const rate = item.get('rate')?.value || 0;
    return quantity * rate;
  }

  get subtotal(): number {
    let total = 0;
    for (let i = 0; i < this.lineItems.length; i++) {
      total += this.getLineItemAmount(i);
    }
    return total;
  }

  get taxAmount(): number {
    const taxRate = this.scheduleForm.get('tax_rate')?.value || 0;
    return this.subtotal * taxRate / 100;
  }

  get totalDue(): number {
    return this.subtotal + this.taxAmount;
  }

  formatCurrency(amount: number): string {
    return '\u00a3' + amount.toFixed(2);
  }

  private loadClients() {
    this.clientService.getClients().subscribe({
      next: (clients) => {
        this.clients = clients;
      },
      error: (err) => {
        console.error('Error loading clients:', err);
      }
    });
  }

  onSubmit() {
    if (this.scheduleForm.invalid) return;

    this.loading = true;
    this.error = null;

    const formValue = this.scheduleForm.value;
    const request: CreateScheduleRequest = {
      client_id: formValue.client_id,
      description: formValue.description || undefined,
      recurrence: formValue.recurrence,
      next_run_date: formValue.next_run_date,
      auto_send: formValue.auto_send,
      tax_rate: formValue.tax_rate,
      line_items: formValue.line_items.map((item: any) => ({
        description: item.description,
        quantity: item.quantity,
        rate: item.rate
      }))
    };

    this.scheduleService.createSchedule(request).subscribe({
      next: () => {
        this.router.navigate(['/schedules']);
      },
      error: (err) => {
        this.error = 'Failed to create schedule.';
        console.error('Error creating schedule:', err);
        this.loading = false;
      }
    });
  }

  onCancel() {
    this.router.navigate(['/schedules']);
  }
}
