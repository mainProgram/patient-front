import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of, tap } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'current_user';
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  private apiUrl: string = '';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Charger la configuration depuis le fichier assets/config.json
    fetch('/assets/config.json')
      .then(response => response.json())
      .then(config => {
        this.apiUrl = config.apiUrl;
        console.log('API URL configurée:', this.apiUrl);
      })
      .catch(error => {
        console.error('Erreur lors du chargement de la configuration:', error);
        // Fallback à l'URL du conteneur backend
        this.apiUrl = 'http://backend-api:8080/api';
      });
  }

  login(credentials: {username: string, password: string}): Observable<any> {
    // Utiliser l'URL configurée au lieu d'une URL codée en dur
    const loginUrl = `${this.apiUrl}/auth/signin`;
    console.log('Tentative de connexion à:', loginUrl);

    return this.http.post<any>(loginUrl, credentials)
      .pipe(
        tap(response => {
          localStorage.setItem(this.TOKEN_KEY, response.token);
          localStorage.setItem(this.USER_KEY, JSON.stringify(response.username));
          this.isAuthenticatedSubject.next(true);
        })
      );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }

  isAuthenticated(): Observable<boolean> {
    return this.isAuthenticatedSubject.asObservable();
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getCurrentUser(): any {
    const userStr = localStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user && user.roles && user.roles.includes(role);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }
}
