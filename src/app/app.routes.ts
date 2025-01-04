import { Routes } from '@angular/router';
import {CreateComponent} from './components/etudiant/create/create.component';
import {ListEtudiantComponent} from "./components/etudiant/list-etudiant/list-etudiant.component";
import {DetailEtudiantComponent} from "./components/etudiant/detail-etudiant/detail-etudiant.component";

export const routes: Routes = [
  {
    path: 'etudiants/create',
    pathMatch: 'full',
    component: CreateComponent,
  },
  {
    path: 'etudiants',
    pathMatch: 'full',
    component: ListEtudiantComponent,
  },
  {
    path: 'etudiants/:id',
    pathMatch: 'full',
    component: DetailEtudiantComponent,
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
