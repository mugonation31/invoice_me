import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { SettingsService } from '../../services/settings.service';
import { CompanySettings } from '../../models/settings.model';

@Component({
  selector: 'app-settings-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './settings-page.component.html',
  styleUrl: './settings-page.component.scss'
})
export class SettingsPageComponent implements OnInit {
  private fb = inject(FormBuilder);
  private settingsService = inject(SettingsService);

  settingsForm!: FormGroup;
  successMessage = '';
  errorMessage = '';
  loading = false;

  ngOnInit() {
    this.initForm();
    this.loadSettings();
  }

  private initForm() {
    this.settingsForm = this.fb.group({
      company_name: [''],
      company_email: [''],
      company_phone: [''],
      bank_account_name: [''],
      bank_name: [''],
      account_number: [''],
      sort_code: [''],
      iban: [''],
    });
  }

  private loadSettings() {
    this.settingsService.getSettings().subscribe({
      next: (settings: CompanySettings) => {
        this.settingsForm.patchValue({
          company_name: settings.company_name || '',
          company_email: settings.company_email || '',
          company_phone: settings.company_phone || '',
          bank_account_name: settings.bank_account_name || '',
          bank_name: settings.bank_name || '',
          account_number: settings.account_number || '',
          sort_code: settings.sort_code || '',
          iban: settings.iban || '',
        });
      },
      error: () => {
        // No settings yet - form stays empty
      }
    });
  }

  onSave() {
    this.successMessage = '';
    this.errorMessage = '';
    this.loading = true;

    const formValue = this.settingsForm.value;
    this.settingsService.updateSettings(formValue).subscribe({
      next: () => {
        this.successMessage = 'Settings saved successfully';
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to save settings. Please try again.';
        this.loading = false;
      }
    });
  }
}
