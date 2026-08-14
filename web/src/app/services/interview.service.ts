import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class InterviewService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  generateQuestions(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/generate`, data);
  }

  getQuestions(interviewId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/questions/${interviewId}`);
  }

  submitAnswer(questionId: number, answerText: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/answer`, {
      question_id: questionId,
      answer_text: answerText
    });
  }

  evaluateAnswer(answerId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/evaluate/${answerId}`, {});
  }
}

