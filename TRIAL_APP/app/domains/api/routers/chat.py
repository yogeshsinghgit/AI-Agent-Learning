from fastapi import APIRouter, Request

router = APIRouter(tags=["chat"])

@router.get("/test-llm")
async def test_llm(request: Request):
    llm = request.app.state.app_state.llm.client
    response = await llm.ainvoke("Say hello in 5 words.")
    return {"response": response.content}