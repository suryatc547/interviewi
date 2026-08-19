import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InterviewService } from '../../services/interview.service';

@Component({
  selector: 'app-ats-form',
  templateUrl: './ats-form.component.html',
  styleUrls: ['./ats-form.component.css']
})
export class ATSFormComponent {
  atsForm: FormGroup;
  loading = false;
  errorMessage = '';
  selectedFile: File | null = null;
  fileName = '';
  dragOver = false;

  readonly MAX_JD_LENGTH = 20000;
  readonly MAX_FILE_SIZE = 2 * 1024 * 1024;

  constructor(
    private fb: FormBuilder,
    private interviewService: InterviewService,
    private router: Router
  ) {
    this.atsForm = this.fb.group({
      job_description: ['', [Validators.required, Validators.maxLength(this.MAX_JD_LENGTH)]]
    });
  }

  get jdCharCount(): number {
    return this.atsForm.get('job_description')?.value?.length || 0;
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.setFile(input.files[0]);
    }
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragOver = false;
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.setFile(event.dataTransfer.files[0]);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave() {
    this.dragOver = false;
  }

  private setFile(file: File) {
    this.errorMessage = '';

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      this.errorMessage = 'Only PDF files are accepted.';
      return;
    }

    if (file.size > this.MAX_FILE_SIZE) {
      this.errorMessage = 'File is too large. Maximum size is 2 MB.';
      return;
    }

    this.selectedFile = file;
    this.fileName = file.name;
  }

  removeFile() {
    this.selectedFile = null;
    this.fileName = '';
  }

  onSubmit() {
    if (!this.selectedFile || !this.atsForm.valid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.interviewService.scanATS(
      this.selectedFile,
      this.atsForm.value.job_description.trim()
    ).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.router.navigate(['/ats/results', response.scan_id]);
      },
      error: (err: any) => {
        console.error('Error:', err);
        this.loading = false;
        this.errorMessage = err.error?.error || 'Failed to analyze resume. Please try again.';
      }
    });
  }
}
