import {Component, inject} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from "@angular/forms";
import {Router, RouterLink} from "@angular/router";
import {MatDatepicker, MatDatepickerModule, MatDatepickerToggle} from "@angular/material/datepicker";
import {MatFormField, MatFormFieldModule, MatLabel} from "@angular/material/form-field";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatButton, MatIconButton} from "@angular/material/button";
import {MatInput, MatInputModule} from "@angular/material/input";
import {MatNativeDateModule} from "@angular/material/core";
import {CommonModule} from "@angular/common";
import {EtudiantService} from "../../../services/etudiant.service";
import {MatIcon} from "@angular/material/icon";

@Component({
  selector: 'app-create',
  imports: [
    MatDatepickerToggle,
    MatLabel,
    MatFormField,
    MatDatepicker,
    MatSelect,
    MatOption,
    ReactiveFormsModule,
    MatInput,
    MatButton,
    MatNativeDateModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatFormFieldModule,
    MatInputModule,
    CommonModule,
    MatIcon,
    MatIconButton,
    RouterLink
  ],
  standalone: true,
  templateUrl: './create.component.html',
  styleUrl: './create.component.sass'
})
export class CreateComponent {
  etudiantForm: FormGroup;
  etudiantService = inject(EtudiantService);
  router = inject(Router);

  constructor(private fb: FormBuilder) {

    this.etudiantForm = this.fb.group({
      nom: ['', Validators.required],
      prenom: ['', Validators.required],
      dateNaissance: ['', Validators.required],
      sexe: ['', Validators.required],
      matricule: ['', Validators.required],
    });
  }

  onSubmit(): void {
    if (this.etudiantForm.valid) {
      this.etudiantService.addEtudiant(this.etudiantForm.value).subscribe({
        next: (data: any) => {
          this.router.navigateByUrl('/').then((response: any) => {
            this.router.navigateByUrl("/etudiants/"+data.id)
          })
        },
        error: (err) => {
          console.log(err)
        }
      })
    } else {
      console.error('Formulaire invalide');
    }
  }

  public get f(){  return this.etudiantForm.controls }
}
