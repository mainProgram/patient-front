import {Component, inject} from '@angular/core';
import {MatIconModule} from "@angular/material/icon";
import {MatButtonModule} from "@angular/material/button";
import {MatListModule} from "@angular/material/list";
import {CommonModule} from "@angular/common";
import {Router} from "@angular/router";
import {EtudiantService} from "../../../services/etudiant.service";
import {take} from "rxjs";
import Swal from 'sweetalert2';
@Component({
  selector: 'app-list-etudiant',
  imports: [CommonModule, MatListModule, MatButtonModule, MatIconModule],
  standalone: true,
  templateUrl: './list-etudiant.component.html',
  styleUrl: './list-etudiant.component.sass'
})
export class ListEtudiantComponent {
  router = inject(Router);
  etudiantService = inject(EtudiantService);

  constructor() {
    this.etudiantService.fetchEtudiants().pipe(take(1)).subscribe();
  }

  get etudiants() {
    return this.etudiantService.resources;
  }

  seeDetails(id: number){
    this.router.navigateByUrl('/').then((response: any) => {
      this.router.navigateByUrl("/etudiants/"+id)
    })
  }

  modifierEtudiant(id: number){
    this.router.navigateByUrl('/').then((response: any) => {
      this.router.navigateByUrl("/etudiants/"+id)
    })
  }

  deleteEtudiant(id: number){
    Swal.fire({
      title: 'Suppression',
      text: 'Voulez-vous vraiment vous supprimer le etudiant ?',
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
          this.etudiantService.deleteEtudiant(id).subscribe({
            next: (data) => {
              console.log(data)
            }
          })
        })
      }
    })
  }
}

