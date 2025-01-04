import { Routes } from '@angular/router';
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
