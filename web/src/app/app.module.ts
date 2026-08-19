import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { InterviewFormComponent } from './components/interview-form/interview-form.component';
import { QuestionAnswerComponent } from './components/question-answer/question-answer.component';
import { ResultsComponent } from './components/results/results.component';
import { ATSFormComponent } from './components/ats-form/ats-form.component';
import { ATSResultsComponent } from './components/ats-results/ats-results.component';
import { InterviewService } from './services/interview.service';

@NgModule({
  declarations: [
    AppComponent,
    InterviewFormComponent,
    QuestionAnswerComponent,
    ResultsComponent,
    ATSFormComponent,
    ATSResultsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule
  ],
  providers: [InterviewService],
  bootstrap: [AppComponent]
})
export class AppModule { }

