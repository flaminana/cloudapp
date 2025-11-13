from fastapi import APIRouter, HTTPException, Request
from models.schemas import ObjectiveQuestion, ObjectiveAnswer, ScoreResponse
from services.openrouter import get_objective_question, check_objective_answer

router = APIRouter(prefix="/objective", tags=["Objective Quiz"])

# For a real app, store questions/answers in a DB or session
# For now, we'll send the correct answer back with the question and require the frontend to send it with the answer POST

@router.get("/question", response_model=ObjectiveQuestion)
async def get_question():
    try:
        result = get_objective_question()
        # For now, send all info including the answer (frontend should hide it from the user)
        return ObjectiveQuestion(
            question=result["question"],
            options=result["options"],
            question_number=0,
            answer=result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get question: {e}")

@router.post("/answer", response_model=ScoreResponse)
async def submit_answer(answer: ObjectiveAnswer, request: Request):
    try:
        body = await request.json()
        print ("📦 Received payload:", body)

        # For stateless demo, frontend must send the correct answer in request body
        # In production, store correct answers in backend and use a question_id
        is_correct = check_objective_answer(answer.correct_answer, answer.answer)  # Replace with (correct_answer, answer.answer)
        return ScoreResponse(
            is_correct=is_correct,
            current_score=1 if is_correct else 0,
            question_number=answer.question_number
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check answer: {e}")