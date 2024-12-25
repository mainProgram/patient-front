import {Component, inject} from '@angular/core';
import {FormArray, FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {PatientService} from '../../services/patient.service';
import {MatIcon} from '@angular/material/icon';
import {MatDatepicker, MatDatepickerModule, MatDatepickerToggle} from '@angular/material/datepicker';
import {MatFormField, MatFormFieldModule, MatLabel} from '@angular/material/form-field';
import {MatOption, MatSelect} from '@angular/material/select';
import {MatButton, MatIconButton} from '@angular/material/button';
import {MatInput, MatInputModule} from '@angular/material/input';
import {MatNativeDateModule} from '@angular/material/core';
import {CommonModule} from '@angular/common';
import {Router} from '@angular/router';

@Component({
  imports: [
    MatIcon,
    MatDatepickerToggle,
    MatLabel,
    MatFormField,
    MatDatepicker,
    MatSelect,
    MatOption,
    ReactiveFormsModule,
    MatIconButton,
    MatInput,
    MatButton,
    MatNativeDateModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatFormFieldModule,
    MatInputModule,
    CommonModule
  ],
  selector: 'app-patient-add',
  standalone: true,
  styleUrl: './patient-add.component.sass',
  templateUrl: './patient-add.component.html'
})
export class PatientAddComponent {
  patientForm: FormGroup;
  patientService = inject(PatientService);
  router = inject(Router);

  constructor(private fb: FormBuilder) {

    this.patientForm = this.fb.group({
      nom: ['', Validators.required],
      prenom: ['', Validators.required],
      dateNaissance: ['', Validators.required],
      sexe: ['', Validators.required],
      taille: ['', Validators.required],
      poids: ['', Validators.required],
      contacts: this.fb.array([this.createContactGroup()]),
    });
  }

  createContactGroup(): FormGroup {
    return this.fb.group({
      type: ['', Validators.required],
      contact: ['', Validators.required],
    });
  }

  get contacts(): FormArray {
    return this.patientForm.get('contacts') as FormArray;
  }

  addContact(): void {
    const contactGroup = this.fb.group({
      type: ['', Validators.required],
      contact: ['', Validators.required],
    });
    this.contacts.push(contactGroup);
  }

  removeContact(index: number): void {
    this.contacts.removeAt(index);
  }

  onSubmit(): void {
    if (this.patientForm.valid) {
      console.log('Formulaire soumis', this.patientForm.value);
      this.patientService.addPatient(this.patientForm.value).subscribe({
        next: (data: any) => {
          console.log(data)
          this.router.navigateByUrl('/').then((response: any) => {
            this.router.navigateByUrl("/")
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

  public get f(){  return this.patientForm.controls }
}
