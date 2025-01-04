import {Component, inject, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MatCardModule} from '@angular/material/card';
import {MatListModule} from '@angular/material/list';
import {ActivatedRoute} from '@angular/router';
import {MatButton} from '@angular/material/button';
import {IEtudiantResponse} from "../../../models/etudiant/etudiant-response.model";
import {EtudiantService} from "../../../services/etudiant.service";
import {IApiResponse} from "../../../models/api-response";
@Component({
  selector: 'app-detail-etudiant',
  imports: [
    CommonModule,
    MatCardModule,
    MatListModule,
    MatButton
  ],
  standalone: true,
  templateUrl: './detail-etudiant.component.html',
  styleUrl: './detail-etudiant.component.sass'
})
export class DetailEtudiantComponent implements OnInit{
  route = inject(ActivatedRoute)
  etudiantService = inject(EtudiantService);
  id: number|null = 0
  etudiant: IEtudiantResponse|null = null
  constructor() {
  }

  ngOnInit(){
    let id = this.route.snapshot.paramMap.get('id');
    if(id != null){
      this.id = +id;
      this.etudiantService.getEtudiant(this.id).subscribe({
        next: (data: IApiResponse) => {
          this.etudiant = data.data as IEtudiantResponse
        },
        error: (err) => {
          console.log(err)
        }
      })
    }
  }

  modifier(id: number){

  }
}
