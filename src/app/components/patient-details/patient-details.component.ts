import {Component, inject, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MatCardModule} from '@angular/material/card';
import {MatListModule} from '@angular/material/list';
import {MatIcon} from '@angular/material/icon';
import {ActivatedRoute, Router} from '@angular/router';
import {PatientService} from '../../services/patient.service';
import {IApiResponse} from '../../models/api-response';
import {IPatientWithContactResponse} from '../../models/patient-with-contact-response.model';
import {MatButton} from '@angular/material/button';

@Component({
  selector: 'app-patient-details',
  imports: [
    CommonModule,
    MatCardModule,
    MatListModule,
    MatIcon,
    MatButton
  ],
  standalone: true,
  templateUrl: './patient-details.component.html',
  styleUrl: './patient-details.component.sass'
})
export class PatientDetailsComponent implements OnInit{
  route = inject(ActivatedRoute)
  router = inject(Router)
  patientService = inject(PatientService);
  id: string|null = ""
  patient: IPatientWithContactResponse|null = null
  constructor() {
  }

  ngOnInit(){
    this.id = this.route.snapshot.paramMap.get('id');
    if(this.id != null)
      this.patientService.getPatient(this.id).subscribe({
      next: (data: IApiResponse) => {
        this.patient = data.data as IPatientWithContactResponse
      },
      error: (err) => {
        console.log(err)
      }
    })
  }

  getContactIcon(type: string): string {
    switch (type.toLowerCase()) {
      case 'email':
        return 'email';
      case 'mobile':
        return 'phone';
      case 'fixe':
        return 'phone_in_talk';
      default:
        return 'contact_phone';
    }
  }

  modifierContact(id: string){
    this.router.navigateByUrl('/').then((response: any) => {
      this.router.navigateByUrl("/patients/edit/"+id)
    })
  }
}
