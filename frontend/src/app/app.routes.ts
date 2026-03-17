import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login.component';
import { SignupComponent } from './auth/signup/signup.component';
import { DashboardComponent } from './dashboard/components/dashboard/dashboard.component';
import { ClientListComponent } from './clients/components/client-list/client-list.component';
import { InvoiceListComponent } from './invoices/components/invoice-list/invoice-list.component';
import { InvoiceFormComponent } from './invoices/components/invoice-form/invoice-form.component';
import { InvoiceDetailComponent } from './invoices/components/invoice-detail/invoice-detail.component';
import { SettingsPageComponent } from './settings/components/settings-page/settings-page.component';
import { authGuard } from './auth/guards/auth.guard';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'signup', component: SignupComponent },
    { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
    { path: 'clients', component: ClientListComponent, canActivate: [authGuard] },
    { path: 'invoices', component: InvoiceListComponent, canActivate: [authGuard] },
    { path: 'invoices/new', component: InvoiceFormComponent, canActivate: [authGuard] },
    { path: 'invoices/:id', component: InvoiceDetailComponent, canActivate: [authGuard] },
    { path: 'invoices/:id/edit', component: InvoiceFormComponent, canActivate: [authGuard] },
    { path: 'settings', component: SettingsPageComponent, canActivate: [authGuard] },
    { path: '', redirectTo: '/login', pathMatch: 'full' }
];
