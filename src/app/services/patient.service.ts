import {Injectable} from '@angular/core';
import {map, tap} from 'rxjs';
import {ResourceService} from './resource.service';
import {IApiResponse} from '../models/api-response';
import {IPatientResponse} from '../models/patient-response.model';
let baseUrl = "http://localhost:8084/api/v1/patients"

@Injectable({
  providedIn: 'root'
})
export class PatientService extends ResourceService<IPatientResponse>{

  fetchPatients() {
    return this.http
      .get<IApiResponse>(baseUrl)
      .pipe(
        map((response) => response.data as IPatientResponse[]),
        tap(this.setResources.bind(this))
      );
  }


}
