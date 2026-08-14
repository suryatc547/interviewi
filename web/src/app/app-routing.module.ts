import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { InterviewFormComponent } from './components/interview-form/interview-form.component';
import { QuestionAnswerComponent } from './components/question-answer/question-answer.component';
import { ResultsComponent } from './components/results/results.component';

const routes: Routes = [
  { path: '', component: InterviewFormComponent },
  { path: 'interview/:interviewId', component: QuestionAnswerComponent },
  { path: 'results/:interviewId', component: ResultsComponent },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
