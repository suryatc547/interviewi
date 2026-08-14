import { Component } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InterviewService } from '../../services/interview.service';

@Component({
  selector: 'app-interview-form',
  templateUrl: './interview-form.component.html',
  styleUrls: ['./interview-form.component.css']
})
export class InterviewFormComponent {
  interviewForm: FormGroup;
  loading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private interviewService: InterviewService,
    private router: Router
  ) {
    this.interviewForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      role: ['', Validators.required],
      industry: ['', Validators.required],
      skills: this.fb.array([], Validators.required),
      job_description: ['']
    });

    this.addSkill();
  }

  get skills(): FormArray {
    return this.interviewForm.get('skills') as FormArray;
  }

  addSkill(): void {
    this.skills.push(this.fb.group({
      skill: ['', Validators.required],
      years: ['', [Validators.required, Validators.pattern(/^[0-9]+(\.[0-9]+)?$/)]]
    }));
  }

  removeSkill(index: number): void {
    this.skills.removeAt(index);
  }

  onSubmit() {
    if (this.interviewForm.valid) {
      this.loading = true;
      this.errorMessage = '';

      const formValue = this.interviewForm.value;
      const experience: { [skill: string]: string } = {};
      for (const row of formValue.skills) {
        if (row.skill && row.skill.trim()) {
          experience[row.skill.trim()] = row.years;
        }
      }

      this.interviewService.generateQuestions({
        name: formValue.name,
        email: formValue.email,
        role: formValue.role,
        industry: formValue.industry,
        experience,
        job_description: formValue.job_description
      }).subscribe({
        next: (response: any) => {
          this.loading = false;
          // Navigate to the question answering page
          this.router.navigate(['/interview', response.interview_id], { queryParams: { question: 0 } });
        },
        error: (err: any) => {
          console.error('Error:', err);
          this.loading = false;
          this.errorMessage = err.error?.error || 'Failed to generate questions. Please try again.';
        }
      });
    }
  }
}
