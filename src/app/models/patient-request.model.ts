import {IContactRequest} from './contact-request.model';

export interface IPatientRequest {
  nom: string;
  prenom: string;
  sexe: string;
  taille: number;
  poids: number;
  dateNaissance: Date;
  contacts: IContactRequest[];
}
