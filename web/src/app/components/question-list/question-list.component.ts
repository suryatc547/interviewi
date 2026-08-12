import { Component, Input, OnInit } from '@angular/core';
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
  userAnswer?: string;
  isSaving?: boolean;
  isEvaluating?: boolean;
  saveMessage?: string;
  evaluationError?: string;
}

@Component({
  selector: 'app-question-list',
  templateUrl: './question-list.component.html',
  styleUrls: ['./question-list.component.css']
})
export class QuestionListComponent implements OnInit {
  @Input() questions: Question[] = [];
  @Input() user: any;
  @Input() interviewId!: number;

  readonly MAX_ANSWER_LENGTH = 5000;

  constructor(private interviewService: InterviewService) { }

  ngOnInit() {
    // Initialize userAnswer field for each question
    this.questions.forEach(q => {
      q.userAnswer = q.answer?.text || '';
    });
  }

  getCharacterCount(question: Question): number {
    return question.userAnswer?.length || 0;
  }

  getRemainingCharacters(question: Question): number {
    return this.MAX_ANSWER_LENGTH - this.getCharacterCount(question);
  }

  isAnswerTooLong(question: Question): boolean {
    return this.getCharacterCount(question) > this.MAX_ANSWER_LENGTH;
  }

  getCharacterCountClass(question: Question): string {
    const remaining = this.getRemainingCharacters(question);
    if (remaining < 0) return 'error';
    if (remaining < 500) return 'warning';
    return '';
  }

  onAnswerChange(question: Question) {
    // Clear previous messages
    question.saveMessage = '';
    question.evaluationError = '';
  }

  saveAnswer(question: Question) {
    if (!question.userAnswer?.trim()) {
      question.saveMessage = 'Please enter an answer';
      return;
    }

    if (this.isAnswerTooLong(question)) {
      question.saveMessage = 'Answer is too long!';
      return;
    }

    question.isSaving = true;
    question.saveMessage = '';

    this.interviewService.submitAnswer(question.id, question.userAnswer!).subscribe({
      next: (response: any) => {
        question.isSaving = false;
        question.saveMessage = '✓ Answer saved successfully!';
        
        // Update the answer object with the returned answer_id
        if (!question.answer) {
          question.answer = {
            id: response.answer_id,
            text: question.userAnswer!,
            ai_score: 0,
            ai_feedback: ''
          };
        } else {
          question.answer.id = response.answer_id;
          question.answer.text = question.userAnswer!;
        }

        // Clear success message after 3 seconds
        setTimeout(() => {
          question.saveMessage = '';
        }, 3000);
      },
      error: (error: any) => {
        question.isSaving = false;
        question.saveMessage = error.error?.error || 'Failed to save answer';
        console.error('Error saving answer:', error);
      }
    });
  }

  evaluateAnswer(question: Question) {
    if (!question.answer?.id) {
      question.evaluationError = 'Please save your answer first';
      return;
    }

    question.isEvaluating = true;
    question.evaluationError = '';

    this.interviewService.evaluateAnswer(question.answer.id).subscribe({
      next: (response: any) => {
        question.isEvaluating = false;
        
        // Update the question with evaluation results
        if (question.answer) {
          question.answer.ai_score = response.ai_score;
          question.answer.ai_feedback = response.ai_feedback;
        }
        question.score = response.ai_score;

        // Show success message
        question.saveMessage = '✓ Answer evaluated successfully!';
        setTimeout(() => {
          question.saveMessage = '';
        }, 3000);
      },
      error: (error: any) => {
        question.isEvaluating = false;
        question.evaluationError = error.error?.error || 'Failed to evaluate answer';
        console.error('Error evaluating answer:', error);
      }
    });
  }

  hasAnswer(question: Question): boolean {
    return !!question.userAnswer && question.userAnswer.trim().length > 0;
  }

  hasEvaluation(question: Question): boolean {
    return !!question.answer?.ai_feedback;
  }

  shouldShowSaveButton(question: Question): boolean {
    return this.hasAnswer(question) && !this.isAnswerTooLong(question);
  }

  shouldShowEvaluateButton(question: Question): boolean {
    return !!question.answer?.id && !question.isEvaluating;
  }
}

