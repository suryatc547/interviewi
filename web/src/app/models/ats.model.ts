export interface ATSScanResult {
  scan_id: number;
  overall_score: number;
  keyword_score: number;
  skills_score: number;
  experience_score: number;
  format_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
}
