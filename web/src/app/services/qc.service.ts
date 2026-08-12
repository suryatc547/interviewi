import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class InterviewService {
  private apiUrl = 'http://localhost:5000/api/interview';

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

