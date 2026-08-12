from google import genai
import os
import json

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)

    def generate_questions(self, stack, experience_levels):
        print('going to prompt')
        
        prompt = f"""
        You are an expert technical interviewer. Create a list of 10 interview questions for a candidate with the following profile:
        Tech Stack: {stack}
        Experience Levels: {experience_levels}
        
        Ensure the questions are balanced across the technologies in the stack.
        
        Return the response in JSON format with a "questions" key.
        Each question object should have:
        - "text": The question string
        - "topic": The technology/concept
        - "difficulty": Easy, Medium, or Hard
        
        Example format:
        {{
            "questions": [
                {{
                    "text": "...",
                    "topic": "...",
                    "difficulty": "..."
                }}
            ]
        }}
        """
        # print('prompt', prompt)
        # for model in self.client.models.list():
        #     print('model', model)

        model1 = 'gemini-1.5-flash'
        model2 = 'gemini-2.5-flash'

        try:
            response = self.client.models.generate_content(
                model=model1,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json'
                }
            )

            print('response text', response.text)
            
            parsed_output = json.loads(response.text)
            return parsed_output.get("questions", [])
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            # Try once without response_mime_type if it failed
            try:
                response = self.client.models.generate_content(
                    model=model2,
                    contents=prompt
                )
                # Simple parsing for JSON in text
                text = response.text

                print('response text from catch', text)

                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end != -1:
                    parsed_output = json.loads(text[start:end])
                    return parsed_output.get("questions", [])
                return []
            except Exception as e2:
                print(f"Fallback Gemini error: {e2}")
                return []

    def evaluate_answer(self, question_text, question_topic, question_difficulty, answer_text):
        """
        Evaluate a candidate's answer using AI.
        Returns a dict with 'score' (0-10) and 'feedback' (string)
        """
        prompt = f"""
        You are an expert technical interviewer. Evaluate the following answer to a technical interview question.
        
        Question: {question_text}
        Topic: {question_topic}
        Difficulty: {question_difficulty}
        
        Candidate's Answer: {answer_text}
        
        Provide a detailed evaluation with:
        1. A score from 0 to 10 (where 0 is completely incorrect and 10 is perfect)
        2. Detailed feedback on the answer's correctness, completeness, and clarity
        3. Key strengths (if any)
        4. Areas for improvement
        
        Return the response in JSON format:
        {{
            "score": <number 0-10>,
            "feedback": "<detailed feedback>",
            "strengths": ["<strength1>", "<strength2>"],
            "improvements": ["<improvement1>", "<improvement2>"]
        }}
        """
        
        model = 'gemini-1.5-flash'
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json'
                }
            )
            
            parsed_output = json.loads(response.text)
            return {
                'score': parsed_output.get('score', 0),
                'feedback': parsed_output.get('feedback', ''),
                'strengths': parsed_output.get('strengths', []),
                'improvements': parsed_output.get('improvements', [])
            }
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            # Fallback without strict JSON
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                text = response.text
                
                # Try to parse JSON from text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end != -1:
                    parsed_output = json.loads(text[start:end])
                    return {
                        'score': parsed_output.get('score', 0),
                        'feedback': parsed_output.get('feedback', ''),
                        'strengths': parsed_output.get('strengths', []),
                        'improvements': parsed_output.get('improvements', [])
                    }
                
                # If JSON parsing fails, return a default response
                return {
                    'score': 0,
                    'feedback': 'Unable to evaluate answer due to technical error.',
                    'strengths': [],
                    'improvements': []
                }
            except Exception as e2:
                print(f"Fallback evaluation error: {e2}")
                return {
                    'score': 0,
                    'feedback': 'Unable to evaluate answer due to technical error.',
                    'strengths': [],
                    'improvements': []
                }

gemini_service = GeminiService()

