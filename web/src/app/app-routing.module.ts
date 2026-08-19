import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { InterviewFormComponent } from './components/interview-form/interview-form.component';
import { QuestionAnswerComponent } from './components/question-answer/question-answer.component';
import { ResultsComponent } from './components/results/results.component';
import { ATSFormComponent } from './components/ats-form/ats-form.component';
import { ATSResultsComponent } from './components/ats-results/ats-results.component';

const routes: Routes = [
  { path: '', component: InterviewFormComponent },
  { path: 'interview/:interviewId', component: QuestionAnswerComponent },
  { path: 'results/:interviewId', component: ResultsComponent },
  { path: 'ats', component: ATSFormComponent },
  { path: 'ats/results/:scanId', component: ATSResultsComponent },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
