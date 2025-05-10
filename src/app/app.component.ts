import {Component, inject, OnInit} from '@angular/core';
import {Router, RouterModule, RouterOutlet} from '@angular/router';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatIconModule} from '@angular/material/icon';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {CommonModule} from '@angular/common';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatButtonModule} from '@angular/material/button';
import {LoaderService} from './services/loader.service';
import {MatNativeDateModule} from '@angular/material/core';
import {Observable} from 'rxjs';
import {AuthService} from './services/auth.service';

@Component({
  selector: 'app-root',
  imports: [
    CommonModule,
    RouterOutlet,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    RouterModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatNativeDateModule,
  ],
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.sass'
})
export class AppComponent implements OnInit {
  title = 'patient-front';
  loading = inject(LoaderService).loading;
  isLoggedIn$!: Observable<boolean>;
  currentUser: any;

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.isLoggedIn$ = this.authService.isAuthenticated();
    this.authService.isAuthenticated().subscribe(isLoggedIn => {
      if (isLoggedIn) {
        this.currentUser = this.authService.getCurrentUser();
        console.log(this.currentUser)
      }
    });
  }

  isHomePage(): boolean {
    return this.router.url === '/';
  }

  logout(): void {
    this.authService.logout();
  }
}
