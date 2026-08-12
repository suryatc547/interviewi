import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { InterviewService } from '../../services/qc.service';

interface Question {
  id: number;
  text: string;
  topic: string;
  difficulty: string;
  score: number;
  answer?: {
    id: number;
    text: string;
    ai_score: number;
    ai_feedback: string;
  } | null;
}

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {
  interviewId!: number;
  questions: Question[] = [];
  isLoading = true;
  errorMessage = '';

  expandedQuestionId: number | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private interviewService: InterviewService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.interviewId = +params['interviewId'];
      this.loadResults();
    });
  }

  loadResults() {
    this.isLoading = true;
    this.errorMessage = '';

    this.interviewService.getQuestions(this.interviewId).subscribe({
      next: (response: any) => {
        this.questions = response.questions;
        this.isLoading = false;
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.error?.error || 'Failed to load results';
        console.error('Error loading results:', error);
      }
    });
  }

  get overallScore(): number {
    if (this.questions.length === 0) return 0;
    const total = this.questions.reduce((sum, q) => sum + (q.answer?.ai_score || 0), 0);
    return Math.round((total / this.questions.length) * 10) / 10; // Round to 1 decimal
  }

  get overallPercentage(): number {
    return Math.round((this.overallScore / 10) * 100);
  }

  get answeredQuestions(): number {
    return this.questions.filter(q => q.answer).length;
  }

  get scoreGrade(): string {
    const score = this.overallScore;
    if (score >= 9) return 'Excellent';
    if (score >= 7) return 'Good';
    if (score >= 5) return 'Average';
    if (score >= 3) return 'Below Average';
    return 'Needs Improvement';
  }

  get scoreGradeClass(): string {
    const score = this.overallScore;
    if (score >= 9) return 'excellent';
    if (score >= 7) return 'good';
    if (score >= 5) return 'average';
    if (score >= 3) return 'below-average';
    return 'poor';
  }

  toggleQuestionDetails(questionId: number) {
    if (this.expandedQuestionId === questionId) {
      this.expandedQuestionId = null;
    } else {
      this.expandedQuestionId = questionId;
    }
  }

  isQuestionExpanded(questionId: number): boolean {
    return this.expandedQuestionId === questionId;
  }

  getScoreClass(score: number): string {
    if (score >= 9) return 'excellent';
    if (score >= 7) return 'good';
    if (score >= 5) return 'average';
    if (score >= 3) return 'below-average';
    return 'poor';
  }

  startNewInterview() {
    this.router.navigate(['/']);
  }

  retakeInterview() {
    this.router.navigate(['/interview', this.interviewId], { queryParams: { question: 0 } });
  }
}
