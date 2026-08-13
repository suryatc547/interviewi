import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { InterviewService } from './qc.service';

describe('InterviewService', () => {
  let service: InterviewService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(InterviewService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should POST /generate with payload', () => {
    const payload = { name: 'Alice', stack: 'Python' };
    service.generateQuestions(payload).subscribe(res => expect(res).toEqual({ interview_id: 1 }));

    const req = httpMock.expectOne('http://localhost:5000/api/interview/generate');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush({ interview_id: 1 });
  });

  it('should GET /questions/:id', () => {
    service.getQuestions(7).subscribe(res => expect(res).toEqual({ questions: [] }));

    const req = httpMock.expectOne('http://localhost:5000/api/interview/questions/7');
    expect(req.request.method).toBe('GET');
    req.flush({ questions: [] });
  });

  it('should POST /answer with question_id and answer_text', () => {
    service.submitAnswer(3, 'My answer').subscribe(res => expect(res).toEqual({ answer_id: 9 }));

    const req = httpMock.expectOne('http://localhost:5000/api/interview/answer');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ question_id: 3, answer_text: 'My answer' });
    req.flush({ answer_id: 9 });
  });

  it('should POST /evaluate/:answerId', () => {
    service.evaluateAnswer(9).subscribe(res => expect(res).toEqual({ ai_score: 8 }));

    const req = httpMock.expectOne('http://localhost:5000/api/interview/evaluate/9');
    expect(req.request.method).toBe('POST');
    req.flush({ ai_score: 8 });
  });
});
