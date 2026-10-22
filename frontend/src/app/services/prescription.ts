import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Medicine{
  name: string | null;
  dosage: string | null;
  frequency: string | null;
  duration: string | null;
  instructions: string | null;
}

export interface PrescriptionData {
  patient_name: string | null;
  doctor_name: string | null;
  date: string | null;
  diagnosis: string | null;
  medicines: Medicine[];
}

export interface UploadResponse {
  filename: string;
  data: PrescriptionData;
}

@Injectable({
  providedIn: 'root',
})
export class Prescription {
  
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  uploadPrescription(file : File): Observable<UploadResponse>{
    const formData = new FormData(); 
    formData.append('file', file);
    return this.http.post<UploadResponse>('${this.apiUrl}/upload', formData);
  }
  
}
