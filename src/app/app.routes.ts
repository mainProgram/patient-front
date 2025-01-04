import { Routes } from '@angular/router';
import {PatientListComponent} from './components/patient-list/patient-list.component';
import {PatientAddComponent} from './components/patient-add/patient-add.component';
import {PatientDetailsComponent} from './components/patient-details/patient-details.component';
import {PatientUpdateComponent} from './components/patient-update/patient-update.component';
import {CreateComponent} from './components/etudiant/create/create.component';

export const routes: Routes = [
  {
    path: 'etudiants',
    pathMatch: 'full',
    component: CreateComponent,
  },
  {
    path: 'professeurs',
    pathMatch: 'full',
    component: CreateComponent,
  },
  {
    path: 'matieres',
    pathMatch: 'full',
    component: CreateComponent,
  },
  {
    path: 'classes',
    pathMatch: 'full',
    component: CreateComponent,
  },
];
