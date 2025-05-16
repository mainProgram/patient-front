import { Routes } from '@angular/router';
import {PatientListComponent} from './components/patient-list/patient-list.component';
import {PatientAddComponent} from './components/patient-add/patient-add.component';
import {PatientDetailsComponent} from './components/patient-details/patient-details.component';
import {PatientUpdateComponent} from './components/patient-update/patient-update.component';
import {AuthGuard} from './core/guards/auth.guard';
import {LoginComponent} from './components/auth/login/login.component';

export const routes: Routes = [
  {
    path: 'login',
    pathMatch: 'full',
    component: LoginComponent,
  },
  {
    path: '',
    pathMatch: 'full',
    component: PatientListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'patients',
    component: PatientListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'patients/add',
    component: PatientAddComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'patients/:id',
    component: PatientDetailsComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'patients/edit/:id',
    component: PatientUpdateComponent,
    canActivate: [AuthGuard]
  },
];
