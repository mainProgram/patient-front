import {Injectable} from '@angular/core';
import {tap} from 'rxjs';
import {IPatientRequest} from '../models/patient-request.model';
import {ResourceService} from './resource.service';
import {IPatientWithContactResponse} from '../models/patient-with-contact-response.model';
let baseUrl = "http://localhost:8084/api/v1/patients"

@Injectable({
  providedIn: 'root'
})
export class PatientContactService extends ResourceService<IPatientWithContactResponse>{

  addPatient(patient: IPatientRequest) {
    return this.http
      .post<IPatientWithContactResponse>(baseUrl, patient)
      .pipe(tap(this.upsertResource));
  }

  updatePatient(id:string, patient: IPatientRequest) {
    return this.http
      .put<IPatientWithContactResponse>(`${baseUrl}/${id}`, patient)
      .pipe(tap(this.upsertResource));
  }

}
