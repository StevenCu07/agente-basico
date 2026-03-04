from app.services.llm_provider import LLMResult, generate_text


def run_quiz(content: str, questions: int = 5) -> LLMResult:
    system_prompt = (
        "Eres un generador de quiz academico. Crea preguntas en espanol con formato:\n"
        "1) Pregunta\nA) ...\nB) ...\nC) ...\nRespuesta: X\n"
        f"Genera exactamente {questions} preguntas."
    )
    user_prompt = f"Contenido base:\n{content}"
    return generate_text(system_prompt=system_prompt, user_prompt=user_prompt, max_output_tokens=800)

