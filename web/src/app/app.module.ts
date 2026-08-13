import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { InterviewFormComponent } from './components/qc-form/qc-form.component';
import { QuestionAnswerComponent } from './components/question-answer/question-answer.component';
import { ResultsComponent } from './components/results/results.component';
import { InterviewService } from './services/qc.service';

@NgModule({
  declarations: [
    AppComponent,
    InterviewFormComponent,
    QuestionAnswerComponent,
    ResultsComponent
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

