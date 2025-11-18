from fastapi import APIRouter, HTTPException, Request
from models.schemas import ObjectiveQuestion, ObjectiveAnswer, ScoreResponse
from services.openrouter import get_objective_question, check_objective_answer
from models.db import save_objective_score

user_state = {}

router = APIRouter(prefix="/objective", tags=["Objective Quiz"])

# For a real app, store questions/answers in a DB or session
# For now, we'll send the correct answer back with the question and require the frontend to send it with the answer POST

@router.get("/question", response_model=ObjectiveQuestion)
async def get_question():
    try:
        result = get_objective_question()
        
        #Check for error response
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"OpenRouter error: {result['error']}")
        
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
    raw = await request.body()
    print("📨 Raw request body:", raw.decode())

    user_id = answer.user_id
    if user_id not in user_state:
        user_state[user_id] = {"score": 0, "question": 0}

    try: 
        for item in answer.answers:
            if check_objective_answer(item.correct_answer, item.answer):
                user_state[user_id]["score"] += 1
            user_state[user_id]["question"] += 1

        # Only save to Supabase when user finishes all 5 questions
        if user_state[user_id]["question"] >= 5:
            save_objective_score(
                user_id,
                correct=user_state[user_id]["score"],
                available=5
            )

        return ScoreResponse(
            is_correct=True,
            current_score=user_state[user_id]["score"],
            question_number=user_state[user_id]["question"]
        ) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check answer: {e}")
