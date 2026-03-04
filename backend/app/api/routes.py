from datetime import date, timedelta

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    ChatRequest,
    CostEstimateRequest,
    DocumentCreateRequest,
    FlashcardsRequest,
    QuizRequest,
    SearchRequest,
    StudyPlanRequest,
    SummaryRequest,
)
from app.db.repository import (
    get_global_metrics,
    get_or_create_user,
    get_user_metrics,
    list_documents,
    record_interaction,
    save_document,
)
from app.db.session import get_connection
from app.services.costs import estimate_cost, estimate_tokens_from_text
from app.services.tools.flashcards import run_flashcards
from app.services.tools.notes_search import run_search
from app.services.tools.quiz_generator import run_quiz
from app.services.tools.study_planner import run_study_plan
from app.services.tools.summarizer import run_summary

router = APIRouter(tags=["aulabot"])


def _detect_tool(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ["resumen", "resumir", "sintetiza"]):
        return "resumir"
    if any(word in lowered for word in ["quiz", "preguntas", "evaluacion"]):
        return "quiz"
    if any(word in lowered for word in ["flashcard", "tarjetas"]):
        return "flashcards"
    if any(word in lowered for word in ["plan", "estudio", "cronograma"]):
        return "plan"
    if any(word in lowered for word in ["buscar", "apunte", "nota"]):
        return "buscar"
    if any(word in lowered for word in ["costo", "tokens", "precio"]):
        return "cost"
    return "resumir"


def _register_interaction(user_token: str, tool: str, input_text: str, output_text: str, prompt_tokens: int, completion_tokens: int) -> dict:
    total_tokens = prompt_tokens + completion_tokens
    cost_data = estimate_cost(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    with get_connection() as conn:
        user_id = get_or_create_user(conn, user_token=user_token)
        record_interaction(
            conn=conn,
            user_id=user_id,
            tool=tool,
            input_chars=len(input_text),
            output_chars=len(output_text),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=float(cost_data["total_cost"]),
        )
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": cost_data,
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/documents")
def create_document(payload: DocumentCreateRequest) -> dict:
    with get_connection() as conn:
        user_id = get_or_create_user(conn, payload.user_token)
        doc_id = save_document(conn, user_id, payload.title, payload.content)
    return {"document_id": doc_id, "message": "Documento guardado"}


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    tool = payload.tool or _detect_tool(payload.message)
    combined_input = payload.message if not payload.context else f"{payload.context}\n\n{payload.message}"

    if tool == "resumir":
        llm_result = run_summary(combined_input)
        usage = _register_interaction(payload.user_token, tool, combined_input, llm_result.text, llm_result.prompt_tokens, llm_result.completion_tokens)
        return {"tool_used": tool, "response": llm_result.text, "token_usage": usage}

    if tool == "quiz":
        llm_result = run_quiz(combined_input)
        usage = _register_interaction(payload.user_token, tool, combined_input, llm_result.text, llm_result.prompt_tokens, llm_result.completion_tokens)
        return {"tool_used": tool, "response": llm_result.text, "token_usage": usage}

    if tool == "flashcards":
        llm_result = run_flashcards(combined_input)
        usage = _register_interaction(payload.user_token, tool, combined_input, llm_result.text, llm_result.prompt_tokens, llm_result.completion_tokens)
        return {"tool_used": tool, "response": llm_result.text, "token_usage": usage}

    if tool == "plan":
        dynamic_target = (date.today() + timedelta(days=30)).isoformat()
        output = run_study_plan(
            topics=[part.strip() for part in combined_input.split(",") if part.strip()],
            available_hours_per_week=8,
            target_date=dynamic_target,
        )
        prompt_tokens = estimate_tokens_from_text(combined_input)
        completion_tokens = estimate_tokens_from_text(output)
        usage = _register_interaction(payload.user_token, tool, combined_input, output, prompt_tokens, completion_tokens)
        return {"tool_used": tool, "response": output, "token_usage": usage}

    if tool == "buscar":
        with get_connection() as conn:
            user_id = get_or_create_user(conn, payload.user_token)
            docs = list_documents(conn, user_id)
        results = run_search(payload.message, docs, top_k=3)
        if results:
            lines = [f"- {item['title']} (score={item['score']}): {item['snippet']}" for item in results]
            output = "Resultados encontrados:\n" + "\n".join(lines)
        else:
            output = "No se encontraron apuntes relacionados."
        prompt_tokens = estimate_tokens_from_text(combined_input)
        completion_tokens = estimate_tokens_from_text(output)
        usage = _register_interaction(payload.user_token, tool, combined_input, output, prompt_tokens, completion_tokens)
        return {"tool_used": tool, "response": output, "results": results, "token_usage": usage}

    if tool == "cost":
        output = (
            "Usa /api/cost/estimate para calculo detallado mensual. "
            "Incluye interacciones diarias y tokens promedio de entrada/salida."
        )
        prompt_tokens = estimate_tokens_from_text(combined_input)
        completion_tokens = estimate_tokens_from_text(output)
        usage = _register_interaction(payload.user_token, tool, combined_input, output, prompt_tokens, completion_tokens)
        return {"tool_used": tool, "response": output, "token_usage": usage}

    raise HTTPException(status_code=400, detail="Herramienta no soportada")


@router.post("/tools/resumir")
def resumir(payload: SummaryRequest) -> dict:
    result = run_summary(payload.text, payload.max_words)
    usage = _register_interaction(payload.user_token, "resumir", payload.text, result.text, result.prompt_tokens, result.completion_tokens)
    return {"response": result.text, "token_usage": usage}


@router.post("/tools/quiz")
def quiz(payload: QuizRequest) -> dict:
    result = run_quiz(payload.text, payload.questions)
    usage = _register_interaction(payload.user_token, "quiz", payload.text, result.text, result.prompt_tokens, result.completion_tokens)
    return {"response": result.text, "token_usage": usage}


@router.post("/tools/flashcards")
def flashcards(payload: FlashcardsRequest) -> dict:
    result = run_flashcards(payload.text, payload.cards)
    usage = _register_interaction(payload.user_token, "flashcards", payload.text, result.text, result.prompt_tokens, result.completion_tokens)
    return {"response": result.text, "token_usage": usage}


@router.post("/tools/plan")
def plan(payload: StudyPlanRequest) -> dict:
    output = run_study_plan(payload.topics, payload.available_hours_per_week, payload.target_date)
    prompt_tokens = estimate_tokens_from_text("\n".join(payload.topics))
    completion_tokens = estimate_tokens_from_text(output)
    usage = _register_interaction(payload.user_token, "plan", "\n".join(payload.topics), output, prompt_tokens, completion_tokens)
    return {"response": output, "token_usage": usage}


@router.post("/tools/buscar")
def buscar(payload: SearchRequest) -> dict:
    with get_connection() as conn:
        user_id = get_or_create_user(conn, payload.user_token)
        docs = list_documents(conn, user_id)
    results = run_search(payload.query, docs, top_k=payload.top_k)
    output = "Sin resultados." if not results else f"Se encontraron {len(results)} resultado(s)."
    prompt_tokens = estimate_tokens_from_text(payload.query)
    completion_tokens = estimate_tokens_from_text(output)
    usage = _register_interaction(payload.user_token, "buscar", payload.query, output, prompt_tokens, completion_tokens)
    return {"response": output, "results": results, "token_usage": usage}


@router.post("/cost/estimate")
def cost_estimate(payload: CostEstimateRequest) -> dict:
    monthly_prompt_tokens = payload.daily_interactions * payload.days * payload.avg_tokens_in
    monthly_completion_tokens = payload.daily_interactions * payload.days * payload.avg_tokens_out
    monthly_total_tokens = monthly_prompt_tokens + monthly_completion_tokens
    costs = estimate_cost(prompt_tokens=monthly_prompt_tokens, completion_tokens=monthly_completion_tokens)
    return {
        "daily_interactions": payload.daily_interactions,
        "days": payload.days,
        "monthly_prompt_tokens": monthly_prompt_tokens,
        "monthly_completion_tokens": monthly_completion_tokens,
        "monthly_total_tokens": monthly_total_tokens,
        "monthly_cost": costs,
    }


@router.get("/metrics/user/{user_token}")
def metrics_user(user_token: str) -> dict:
    with get_connection() as conn:
        data = get_user_metrics(conn, user_token)
    if not data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return data


@router.get("/metrics/global")
def metrics_global() -> dict:
    with get_connection() as conn:
        return get_global_metrics(conn)
