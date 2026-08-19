import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ATSScanResult } from '../../models/ats.model';
import { InterviewService } from '../../services/interview.service';

@Component({
  selector: 'app-ats-results',
  templateUrl: './ats-results.component.html',
  styleUrls: ['./ats-results.component.css']
})
export class ATSResultsComponent implements OnInit {
  scanId!: number;
  result: ATSScanResult | null = null;
  isLoading = true;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private interviewService: InterviewService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.scanId = +params['scanId'];
      this.loadResults();
    });
  }

  loadResults() {
    this.isLoading = true;
    this.errorMessage = '';

    this.interviewService.getATSScan(this.scanId).subscribe({
      next: (response: any) => {
        this.result = response;
        this.isLoading = false;
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.error?.error || 'Failed to load scan results';
        console.error('Error loading results:', error);
      }
    });
  }

  get overallPercentage(): number {
    return this.result?.overall_score || 0;
  }

  get scoreGrade(): string {
    const score = this.overallPercentage;
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Needs Improvement';
  }

  get scoreGradeClass(): string {
    const score = this.overallPercentage;
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'poor';
  }

  getScoreClass(score: number): string {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'poor';
  }

  startNewScan() {
    this.router.navigate(['/ats']);
  }
}
