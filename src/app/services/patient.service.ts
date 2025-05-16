import {Injectable} from '@angular/core';
import {map, tap} from 'rxjs';
import {ResourceService} from './resource.service';
import {IApiResponse} from '../models/api-response';
import {IPatientResponse} from '../models/patient-response.model';
import {IPatientRequest} from '../models/patient-request.model';
import {IPatientWithContactResponse} from '../models/patient-with-contact-response.model';

@Injectable({
  providedIn: 'root'
})
export class PatientService extends ResourceService<IPatientResponse>{
  private apiBaseUrl: string = '';

  constructor() {
    super();
    // Charger la configuration depuis le fichier assets/config.json
    fetch('/assets/config.json')
      .then(response => response.json())
      .then(config => {
        this.apiBaseUrl = `${config.apiUrl}/v1/patients`;
        console.log('API Base URL pour patients configurée:', this.apiBaseUrl);
      })
      .catch(error => {
        console.error('Erreur lors du chargement de la configuration:', error);
        // Fallback à l'URL du conteneur backend
        this.apiBaseUrl = 'http://backend-api:8080/api/v1/patients';
      });
  }

  fetchPatients() {
    return this.http
      .get<IApiResponse>(this.apiBaseUrl)
      .pipe(
        map((response) => response.data as IPatientResponse[]),
        tap(this.setResources.bind(this))
      );
  }

  addPatient(patient: IPatientRequest) {
    return this.http
      .post<IApiResponse>(this.apiBaseUrl, patient)
      .pipe(
        map((response) => response.data as IPatientWithContactResponse[]),
        tap(this.setResources.bind(this))
      );
  }

  getPatient(id: string) {
    return this.http
      .get<IApiResponse>(`${this.apiBaseUrl}/${id}`)
  }

  deletePatient(id: string) {
    return this.http
      .delete<IApiResponse>(`${this.apiBaseUrl}/${id}`)
      .pipe(tap(() => this.removeResource(id)));
  }

  updatePatient(id:string, patient: IPatientRequest) {
    return this.http
      .put<IApiResponse>(`${this.apiBaseUrl}/${id}`, patient)
      .pipe(
        map((response) => response.data as IPatientWithContactResponse[]),
        tap(this.setResources.bind(this))
      );
  }
}
