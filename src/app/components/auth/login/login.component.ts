import { Component } from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../../services/auth.service';
import {Router} from '@angular/router';
import {MatCard, MatCardContent, MatCardHeader, MatCardModule, MatCardTitle} from '@angular/material/card';
import {MatError, MatFormField, MatLabel} from '@angular/material/form-field';
import {MatInput} from '@angular/material/input';
import {NgIf} from '@angular/common';
import {MatButton} from '@angular/material/button';

@Component({
  selector: 'app-login',
  imports: [
    MatCardModule,
    MatCardContent,
    MatCardHeader,
    ReactiveFormsModule,
    MatCardContent,
    MatLabel,
    MatFormField,
    MatInput,
    MatCard,
    NgIf,
    MatButton,
    MatError,
    MatCardTitle,
  ],
  standalone: true,
  templateUrl: './login.component.html',
  styleUrl: './login.component.sass'
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.value).subscribe({
        next: () => {
          const returnUrl = '/patients';
          this.router.navigateByUrl(returnUrl);
        },
        error: (error) => {
          this.errorMessage = 'Identifiants incorrects. Veuillez réessayer.';
          console.error('Erreur de connexion', error);
        }
      });
    }
  }
}
