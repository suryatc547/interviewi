import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ATSScanResult } from '../models/ats.model';

@Injectable({
  providedIn: 'root'
})
export class InterviewService {
  private apiUrl = environment.apiUrl;
  private atsApiUrl = environment.apiUrl.replace('/interview', '') + '/ats';

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

  scanATS(resumeFile: File, jobDescription: string): Observable<ATSScanResult> {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);
    return this.http.post<ATSScanResult>(`${this.atsApiUrl}/scan`, formData);
  }

  getATSScan(scanId: number): Observable<ATSScanResult> {
    return this.http.get<ATSScanResult>(`${this.atsApiUrl}/scan/${scanId}`);
  }
}

