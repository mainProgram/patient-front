import {IContactResponse} from './contact-response.model';

export interface IPatientWithContactResponse {
  id: string;
  nom: string;
  prenom: string;
  sexe: string;
  dateNaissance: Date;
  taille: number;
  poids: number;
  contacts: IContactResponse[];
}
