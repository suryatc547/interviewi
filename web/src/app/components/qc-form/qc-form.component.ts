import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InterviewService } from '../../services/qc.service';

@Component({
  selector: 'app-interview-form',
  templateUrl: './qc-form.component.html',
  styleUrls: ['./qc-form.component.css']
})
export class InterviewFormComponent {
  interviewForm: FormGroup;
  loading = false;
  errorMessage = '';

  techStacks = ['MEAN', 'MERN', 'Java Fullstack', 'Python Fullstack'];
  
  stackTechnologies: { [key: string]: string[] } = {
    'MEAN': ['MongoDB', 'Express.js', 'Angular', 'Node.js'],
    'MERN': ['MongoDB', 'Express.js', 'React', 'Node.js'],
    'Java Fullstack': ['Java', 'Spring Boot', 'SQL', 'Angular/React'],
    'Python Fullstack': ['Python', 'Django/Flask', 'SQL', 'Angular/React']
  };

  constructor(
    private fb: FormBuilder,
    private interviewService: InterviewService,
    private router: Router
  ) {
    this.interviewForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      stack: ['', Validators.required],
      experience: this.fb.group({})
    });

    this.interviewForm.get('stack')?.valueChanges.subscribe(stack => {
      this.updateExperienceFields(stack);
    });
  }

  updateExperienceFields(stack: string) {
    const experienceGroup = this.fb.group({});
    const techs = this.stackTechnologies[stack] || [];
    techs.forEach(tech => {
      experienceGroup.addControl(tech, this.fb.control('', Validators.required));
    });
    this.interviewForm.setControl('experience', experienceGroup);
  }

  get experienceControls() {
    return (this.interviewForm.get('experience') as FormGroup).controls;
  }

  getTechnologies() {
    return Object.keys(this.experienceControls);
  }

  onSubmit() {
    if (this.interviewForm.valid) {
      this.loading = true;
      this.errorMessage = '';
      
      this.interviewService.generateQuestions(this.interviewForm.value).subscribe({
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

