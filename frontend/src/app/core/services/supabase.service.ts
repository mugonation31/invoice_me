import { Injectable } from '@angular/core';
import { createClient, SupabaseClient, User, Session } from '@supabase/supabase-js';
import { environment } from '../../../environments/environment';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class SupabaseService {
    private supabase: SupabaseClient;

    private currentUserSubject: BehaviorSubject<User | null>;
    public currentUser$: Observable<User | null>;

    constructor() {
        this.supabase = createClient(
            environment.supabase.url,
            environment.supabase.anonKey
        );

        this.currentUserSubject = new BehaviorSubject<User | null>(null);
        this.currentUser$ = this.currentUserSubject.asObservable();

        this.loadSession();
    }

    private async loadSession() {
        const { data } = await this.supabase.auth.getSession();
        if (data.session?.user) {
            this.currentUserSubject.next(data.session.user);
        }

        this.supabase.auth.onAuthStateChange((event, session) => {
            console.log('Auth state change:', event);
            this.currentUserSubject.next(session?.user ?? null);
        });
    }

    async signUp(email: string, password: string, name: string) {
        const { data, error } = await this.supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    name: name
                }
            }
        });
        if (error) throw error;
        return data;
    }

    async signIn(email: string, password: string) {
        const { data, error } = await this.supabase.auth.signInWithPassword({
            email,
            password
        });

        if (error) throw error;
        return data;
    }

    async signOut() {
        const { error } = await this.supabase.auth.signOut();
        if (error) throw error;
    }

    async getSession(): Promise<Session | null> {
        const { data } = await this.supabase.auth.getSession();
        return data.session;
    }

    async getAccessToken(): Promise<string | null> {
        const session = await this.getSession();
        return session?.access_token ?? null;
    }

    getCurrentUser(): User | null {
        return this.currentUserSubject.value;
    }
}
