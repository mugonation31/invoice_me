import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Client } from '../../models/client.model';

@Component({
  selector: 'app-client-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './client-form.component.html',
  styleUrl: './client-form.component.scss'
})
export class ClientFormComponent implements OnInit {
  @Input() client: Client | null = null;
  @Output() formSubmit = new EventEmitter<Partial<Client>>();
  @Output() formCancel = new EventEmitter<void>();

  clientForm!: FormGroup;
  isEditMode = false;

  constructor(private fb: FormBuilder) {}

  ngOnInit() {
    this.isEditMode = !!this.client;
    this.initForm();
  }

  initForm() {
    this.clientForm = this.fb.group({
      name: [this.client?.name || '', [Validators.required, Validators.maxLength(200)]],
      email: [this.client?.email || '', [Validators.email]],
      phone: [this.client?.phone || '', Validators.maxLength(50)],
      address: [this.client?.address || '', Validators.maxLength(500)]
    });
  }

  onSubmit() {
    if (this.clientForm.valid) {
      const formValue = this.clientForm.value;

      const clientData: Partial<Client> = {
        name: formValue.name.trim(),
        email: formValue.email?.trim() || undefined,
        phone: formValue.phone?.trim() || undefined,
        address: formValue.address?.trim() || undefined
      };

      this.formSubmit.emit(clientData);
      this.resetForm();
    }
  }

  onCancel() {
    this.resetForm();
    this.formCancel.emit();
  }

  resetForm() {
    if (!this.isEditMode) {
      this.clientForm.reset({
        name: '',
        email: '',
        phone: '',
        address: ''
      });
    }
  }

  get name() {
    return this.clientForm.get('name');
  }

  get email() {
    return this.clientForm.get('email');
  }
}
