import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Question } from '../../models/question.model';
import { InterviewService } from '../../services/interview.service';

@Component({
  selector: 'app-question-answer',
  templateUrl: './question-answer.component.html',
  styleUrls: ['./question-answer.component.css']
})
export class QuestionAnswerComponent implements OnInit {
  interviewId!: number;
  questions: Question[] = [];
  currentQuestionIndex: number = 0;
  currentQuestion?: Question;
  userAnswer: string = '';
  
  readonly MAX_ANSWER_LENGTH = 5000;
  
  isSaving = false;
  saveMessage = '';
  isLoading = true;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private interviewService: InterviewService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.interviewId = +params['interviewId'];
      this.loadQuestions();
    });

    // Check if there's a specific question index in query params
    this.route.queryParams.subscribe(params => {
      if (params['question']) {
        this.currentQuestionIndex = +params['question'];
      }
    });
  }

  loadQuestions() {
    this.isLoading = true;
    this.errorMessage = '';

    this.interviewService.getQuestions(this.interviewId).subscribe({
      next: (response: any) => {
        this.questions = response.questions;
        this.isLoading = false;
        
        if (this.questions.length === 0) {
          this.errorMessage = 'No questions found for this interview';
          return;
        }

        // Load the current question
        this.loadCurrentQuestion();
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.error?.error || 'Failed to load questions';
        console.error('Error loading questions:', error);
      }
    });
  }

  loadCurrentQuestion() {
    if (this.currentQuestionIndex >= 0 && this.currentQuestionIndex < this.questions.length) {
      this.currentQuestion = this.questions[this.currentQuestionIndex];
      this.userAnswer = this.currentQuestion.answer?.text || '';
    }
  }

  getCharacterCount(): number {
    return this.userAnswer?.length || 0;
  }

  getRemainingCharacters(): number {
    return this.MAX_ANSWER_LENGTH - this.getCharacterCount();
  }

  isAnswerTooLong(): boolean {
    return this.getCharacterCount() > this.MAX_ANSWER_LENGTH;
  }

  getCharacterCountClass(): string {
    const remaining = this.getRemainingCharacters();
    if (remaining < 0) return 'error';
    if (remaining < 500) return 'warning';
    return '';
  }

  onAnswerChange() {
    this.saveMessage = '';
    this.errorMessage = '';
  }

  get progress(): number {
    if (this.questions.length === 0) return 0;
    return Math.round(((this.currentQuestionIndex + 1) / this.questions.length) * 100);
  }

  get isLastQuestion(): boolean {
    return this.currentQuestionIndex === this.questions.length - 1;
  }

  get isFirstQuestion(): boolean {
    return this.currentQuestionIndex === 0;
  }

  previousQuestion() {
    if (this.currentQuestionIndex > 0) {
      this.currentQuestionIndex--;
      this.loadCurrentQuestion();
      this.updateQueryParams();
    }
  }

  updateQueryParams() {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { question: this.currentQuestionIndex },
      queryParamsHandling: 'merge'
    });
  }

  saveAndNext() {
    if (!this.userAnswer?.trim()) {
      this.saveMessage = 'Please enter an answer';
      return;
    }

    if (this.isAnswerTooLong()) {
      this.saveMessage = 'Answer is too long!';
      return;
    }

    if (!this.currentQuestion) return;

    this.isSaving = true;
    this.saveMessage = '';

    // Save answer
    this.interviewService.submitAnswer(this.currentQuestion.id, this.userAnswer).subscribe({
      next: (response: any) => {
        // Update the question's answer data
        if (this.currentQuestion) {
          this.currentQuestion.answer = {
            id: response.answer_id,
            text: this.userAnswer,
            ai_score: 0,
            ai_feedback: ''
          };
        }

        // Trigger evaluation in background (don't wait for it)
        this.evaluateInBackground(response.answer_id);

        this.isSaving = false;
        this.saveMessage = '✓ Answer saved!';

        // Navigate to next question or results
        setTimeout(() => {
          if (this.isLastQuestion) {
            // Go to results page
            this.router.navigate(['/results', this.interviewId]);
          } else {
            // Go to next question
            this.currentQuestionIndex++;
            this.loadCurrentQuestion();
            this.updateQueryParams();
            this.saveMessage = '';
          }
        }, 500);
      },
      error: (error: any) => {
        this.isSaving = false;
        this.saveMessage = error.error?.error || 'Failed to save answer';
        console.error('Error saving answer:', error);
      }
    });
  }

  evaluateInBackground(answerId: number) {
    // Fire and forget - evaluation happens in background
    this.interviewService.evaluateAnswer(answerId).subscribe({
      next: (response: any) => {
        console.log('Background evaluation completed:', response);
      },
      error: (error: any) => {
        console.error('Background evaluation failed:', error);
      }
    });
  }

  skipQuestion() {
    if (this.isLastQuestion) {
      this.router.navigate(['/results', this.interviewId]);
    } else {
      this.currentQuestionIndex++;
      this.loadCurrentQuestion();
      this.updateQueryParams();
    }
  }

  canSubmit(): boolean {
    return !!this.userAnswer?.trim() && !this.isAnswerTooLong() && !this.isSaving;
  }
}
