import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { InterviewFormComponent } from './interview-form.component';
import { InterviewService } from '../../services/interview.service';

describe('InterviewFormComponent', () => {
  let component: InterviewFormComponent;
  let fixture: ComponentFixture<InterviewFormComponent>;
  let routerSpy: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule],
      declarations: [InterviewFormComponent],
      providers: [
        InterviewService,
        { provide: Router, useValue: routerSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(InterviewFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should start with one empty skill row and support add/remove', () => {
    expect(component.skills.length).toBe(1);
    component.addSkill();
    expect(component.skills.length).toBe(2);
    component.removeSkill(1);
    expect(component.skills.length).toBe(1);
  });

  it('should not submit an invalid form', () => {
    component.onSubmit();
    expect(component.loading).toBeFalse();
    expect(routerSpy.navigate).not.toHaveBeenCalled();
  });

  it('should submit role, industry, skills and job_description', () => {
    const service = TestBed.inject(InterviewService);
    spyOn(service, 'generateQuestions').and.returnValue(of({ interview_id: 42 }));
    const jd = 'Accountant responsible for month-end close and tax filings.';

    component.interviewForm.patchValue({
      name: 'Alice',
      email: 'alice@example.com',
      role: 'Accountant',
      industry: 'Finance',
      job_description: jd
    });
    component.skills.at(0).patchValue({ skill: 'Financial Reporting', years: '5' });
    component.addSkill();
    component.skills.at(1).patchValue({ skill: 'Tax Filing', years: '2' });
    component.onSubmit();

    expect(service.generateQuestions).toHaveBeenCalledWith({
      name: 'Alice',
      email: 'alice@example.com',
      role: 'Accountant',
      industry: 'Finance',
      experience: { 'Financial Reporting': '5', 'Tax Filing': '2' },
      job_description: jd
    });
    expect(routerSpy.navigate).toHaveBeenCalledWith(
      ['/interview', 42], { queryParams: { question: 0 } }
    );
  });
});
