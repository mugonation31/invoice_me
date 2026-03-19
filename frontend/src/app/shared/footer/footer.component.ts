import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <footer class="app-footer">
      <div class="footer-content">
        <span class="footer-brand">Invoice Me</span>
        <span class="footer-divider">·</span>
        <span class="footer-copy">© {{ currentYear }} Million.Business Ltd. All rights reserved.</span>
      </div>
    </footer>
  `,
  styles: [`
    .app-footer {
      background: #2d3748;
      padding: 1.25rem 2rem;
      text-align: center;
    }

    .footer-content {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .footer-brand {
      font-size: 0.875rem;
      font-weight: 600;
      color: #e2e8f0;
    }

    .footer-divider {
      color: #718096;
    }

    .footer-copy {
      font-size: 0.8125rem;
      color: #a0aec0;
    }
  `]
})
export class FooterComponent {
  currentYear = new Date().getFullYear();
}
