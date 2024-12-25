import {Component, inject} from '@angular/core';
import {PatientService} from '../../services/patient.service';
import {take} from 'rxjs';
import {MatIconModule} from '@angular/material/icon';
import {CommonModule} from '@angular/common';
import {MatListModule} from '@angular/material/list';
import {MatButtonModule} from '@angular/material/button';
import {PatientContactService} from '../../services/patient.contact.service';
import {Router} from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-patient-list',
  imports: [CommonModule, MatListModule, MatButtonModule, MatIconModule],
  standalone: true,
  templateUrl: './patient-list.component.html',
  styleUrl: './patient-list.component.sass'
})
export class PatientListComponent {
  router = inject(Router);
  patientService = inject(PatientService);
  patientContactService = inject(PatientContactService);

  constructor() {
    this.patientService.fetchPatients().pipe(take(1)).subscribe();
  }

  get patients() {
    return this.patientService.resources;
  }

  seeDetails(id: string){
    this.router.navigateByUrl('/').then((response: any) => {
      this.router.navigateByUrl("/patients/"+id)
    })
  }

  deletePatient(id: string){
    Swal.fire({
      title: 'Suppression',
      text: 'Voulez-vous vraiment vous supprimer le patient ?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Supprimer',
      cancelButtonText: 'Annuler'
    }).then((result) => {
      if (result.value) {
        Swal.fire(
          'Succès',
          'Suppression réussie !',
          'success'
        ).then(()=>{
          this.patientService.deletePatient(id).subscribe({
            next: (data) => {
              console.log(data)
            }
          })
        })
      }
    })
  }
}
