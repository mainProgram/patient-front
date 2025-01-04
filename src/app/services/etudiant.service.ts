import { Injectable } from '@angular/core';
import {ResourceService} from './resource.service';
import {IApiResponse} from '../models/api-response';
import {map, tap} from 'rxjs';
import {IEtudiantResponse} from '../models/etudiant/etudiant-response.model';
import {IEtudiantRequest} from '../models/etudiant/etudiant-request.model';
let baseUrl = "http://localhost:8090/api/v1/etudiants"

@Injectable({
  providedIn: 'root'
})
export class EtudiantService extends ResourceService<IEtudiantResponse>{

  fetchEtudiants() {
    return this.http
      .get<IApiResponse>(baseUrl)
      .pipe(
        map((response) => response.data as IEtudiantResponse[]),
        tap(this.setResources.bind(this))
      );
  }

  addEtudiant(etudiant: IEtudiantRequest) {
    return this.http
      .post<IApiResponse>(baseUrl, etudiant)
      .pipe(
        map((response) => response.data as IEtudiantResponse[]),
        tap(this.setResources.bind(this))
      );
  }

  getEtudiant(id: number) {
    return this.http
      .get<IApiResponse>(baseUrl+ "/"+ id)
  }

  deleteEtudiant(id: number) {
    return this.http
      .delete<IApiResponse>(`${baseUrl}/${id}`)
      .pipe(tap(() => this.removeResource(id)));
  }

  updateEtudiant(id:number, etudiant: IEtudiantRequest) {
    return this.http
      .put<IApiResponse>(`${baseUrl}/${id}`, etudiant)
      .pipe(
        map((response) => response.data as IEtudiantResponse[]),
        tap(this.setResources.bind(this))
      );
  }
}
