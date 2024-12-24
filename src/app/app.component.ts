import {Component, inject} from '@angular/core';
import {RouterModule, RouterOutlet} from '@angular/router';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatIconModule} from '@angular/material/icon';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {CommonModule} from '@angular/common';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatButtonModule} from '@angular/material/button';
import {LoaderService} from './services/loader.service';

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
    MatSnackBarModule
  ],
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.sass'
})
export class AppComponent {
  title = 'patient-front';
  loading = inject(LoaderService).loading;

}
