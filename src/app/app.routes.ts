import { Routes } from '@angular/router';
import {PatientListComponent} from './components/patient-list/patient-list.component';
import {PatientAddComponent} from './components/patient-add/patient-add.component';
import {PatientDetailsComponent} from './components/patient-details/patient-details.component';
import {PatientUpdateComponent} from './components/patient-update/patient-update.component';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    component: PatientListComponent,
  },
  {
    path: 'add',
    component: PatientAddComponent,
  },
  {
    path: 'patients/:id',
    component: PatientDetailsComponent,
  },
  {
    path: 'patients/edit/:id',
    component: PatientUpdateComponent,
  },
];
