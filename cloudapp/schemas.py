from pydantic import BaseModel
from typing import List

class ObjectiveQuestion(BaseModel):
    question: str
    options: List[str]
    question_number: int
    answer: str

class ObjectiveAnswer(BaseModel):
    user_id: str
    question_number: int
    correct_answer: str
    answer: str 

class ScoreResponse(BaseModel):
    is_correct: bool
    current_score: int
    question_number: int

class PronunciationWord(BaseModel):
    word: str
    translation: str
    word_number: int

class PronunciationResult(BaseModel):
    recognized: str
    score: int
    feedback: str

class ConversationPrompt(BaseModel):
    prompt: str
    prompt_id: int

class ConversationResult(BaseModel):
    recognized: str
    score: int
    feedback: str

class DailyPrompt(BaseModel):
    prompt_id: str
    sentence: str  # e.g. "Ich ___ zur Schule."

class STTResult(BaseModel):
    recognized_text: str

class FinalAnswer(BaseModel):
    prompt_id: str
    user_id: str
    final_text: str

class ScoreFeedback(BaseModel):
    score: int
    feedback: str
    total_score: int
    question_number: int
    is_finished: bool

class PronunciationAttempt(BaseModel):
    word_id: str
    user_id: str
    target_word: str
    recognized_text: str