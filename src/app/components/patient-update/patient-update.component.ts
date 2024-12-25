import {Component, inject, OnInit} from '@angular/core';
import {MatIcon} from '@angular/material/icon';
import {MatDatepicker, MatDatepickerModule, MatDatepickerToggle} from '@angular/material/datepicker';
import {MatFormField, MatFormFieldModule, MatLabel} from '@angular/material/form-field';
import {MatOption, MatSelect} from '@angular/material/select';
import {FormArray, FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {MatButton, MatIconButton} from '@angular/material/button';
import {MatInput, MatInputModule} from '@angular/material/input';
import {MatNativeDateModule} from '@angular/material/core';
import {CommonModule} from '@angular/common';
import {PatientService} from '../../services/patient.service';
import {ActivatedRoute, Router} from '@angular/router';
import {IApiResponse} from '../../models/api-response';
import {IPatientWithContactResponse} from '../../models/patient-with-contact-response.model';

@Component({
  selector: 'app-patient-update',
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
  standalone: true,
  templateUrl: './patient-update.component.html',
  styleUrl: './patient-update.component.sass'
})
export class PatientUpdateComponent implements OnInit{
  id: string|null = "";
  route = inject(ActivatedRoute)
  patientForm: FormGroup;
  patientService = inject(PatientService);
  router = inject(Router);
  patient: IPatientWithContactResponse|null = null

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id');
    if(this.id != null)
      this.patientService.getPatient(this.id).subscribe({
        next: (data: IApiResponse) => {
          this.patient = data.data as IPatientWithContactResponse

          const contactFormGroups = this.patient.contacts.map(contact =>
            this.fb.group({
              type: [contact.type, Validators.required],
              contact: [contact.contact, Validators.required],
            })
          );

          this.patientForm = this.fb.group({
            nom: [this.patient.nom, Validators.required],
            prenom: [this.patient.prenom, Validators.required],
            dateNaissance: [this.patient.dateNaissance, Validators.required],
            sexe: [this.patient.sexe, Validators.required],
            taille: [this.patient.taille, Validators.required],
            poids: [this.patient.poids, Validators.required],
            contacts: this.fb.array(contactFormGroups),
          });
        },
        error: (err) => {
          console.log(err)
        }
      })
  }
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
    if (this.patientForm.valid && this.id != null) {
      this.patientService.updatePatient(this.id, this.patientForm.value).subscribe({
        next: (data: any) => {
          this.router.navigateByUrl('/').then((response: any) => {
            this.router.navigateByUrl("/patients/"+data.id)
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
