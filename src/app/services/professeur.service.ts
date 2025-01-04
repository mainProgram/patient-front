import { Injectable } from '@angular/core';
import {ResourceService} from './resource.service';
import {IApiResponse} from '../models/api-response';
import {map, tap} from 'rxjs';
import {IProfesseurResponse} from '../models/professeur/professeur-response.model';
import {IProfesseurRequest} from '../models/professeur/professeur-request.model';
let baseUrl = "http://localhost:8090/api/v1/professeurs"

@Injectable({
  providedIn: 'root'
})
export class ProfesseurService extends ResourceService<IProfesseurResponse>{

  fetchProfesseurs() {
    return this.http
      .get<IApiResponse>(baseUrl)
      .pipe(
        map((response) => response.data as IProfesseurResponse[]),
        tap(this.setResources.bind(this))
      );
  }

  addProfesseur(professeur: IProfesseurRequest) {
    return this.http
      .post<IApiResponse>(baseUrl, professeur)
      .pipe(
        map((response) => response.data as IProfesseurResponse[]),
        tap(this.setResources.bind(this))
      );
  }

  getProfesseur(id: string) {
    return this.http
      .get<IApiResponse>(baseUrl+ "/"+ id)
  }

  deleteProfesseur(id: string) {
    return this.http
      .delete<IApiResponse>(`${baseUrl}/${id}`)
      .pipe(tap(() => this.removeResource(id)));
  }

  updateProfesseur(id:string, professeur: IProfesseurRequest) {
    return this.http
      .put<IApiResponse>(`${baseUrl}/${id}`, professeur)
      .pipe(
        map((response) => response.data as IProfesseurResponse[]),
        tap(this.setResources.bind(this))
      );
  }
}
