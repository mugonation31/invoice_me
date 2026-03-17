import { routes } from './app.routes';

describe('App Routes', () => {
  it('should have routes configured', () => {
    expect(routes.length).toBeGreaterThan(0);
  });

  it('should have a default redirect to /login', () => {
    const defaultRoute = routes.find(r => r.path === '');
    expect(defaultRoute).toBeTruthy();
    expect(defaultRoute?.redirectTo).toBe('/login');
  });

  it('should have a login route', () => {
    const route = routes.find(r => r.path === 'login');
    expect(route).toBeTruthy();
  });

  it('should have a signup route', () => {
    const route = routes.find(r => r.path === 'signup');
    expect(route).toBeTruthy();
  });

  it('should have a dashboard route', () => {
    const route = routes.find(r => r.path === 'dashboard');
    expect(route).toBeTruthy();
  });

  it('should have a clients route', () => {
    const route = routes.find(r => r.path === 'clients');
    expect(route).toBeTruthy();
  });

  it('should have an invoices route', () => {
    const route = routes.find(r => r.path === 'invoices');
    expect(route).toBeTruthy();
  });

  it('should have a new invoice route', () => {
    const route = routes.find(r => r.path === 'invoices/new');
    expect(route).toBeTruthy();
  });

  it('should have an invoice detail route', () => {
    const route = routes.find(r => r.path === 'invoices/:id');
    expect(route).toBeTruthy();
  });

  it('should have a settings route', () => {
    const route = routes.find(r => r.path === 'settings');
    expect(route).toBeTruthy();
  });
});
