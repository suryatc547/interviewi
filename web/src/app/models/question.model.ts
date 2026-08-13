export interface QuestionAnswer {
  id: number;
  text: string;
  ai_score: number;
  ai_feedback: string;
}

export interface Question {
  id: number;
  text: string;
  topic: string;
  difficulty: string;
  score: number;
  answer?: QuestionAnswer | null;
}
