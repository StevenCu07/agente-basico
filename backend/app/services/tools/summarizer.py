from app.services.llm_provider import LLMResult, generate_text


def run_summary(text: str, max_words: int = 140) -> LLMResult:
    system_prompt = (
        "Eres un asistente academico. Resume texto en espanol claro y preciso. "
        f"Limita la respuesta a maximo {max_words} palabras."
    )
    user_prompt = f"Texto a resumir:\n{text}"
    return generate_text(system_prompt=system_prompt, user_prompt=user_prompt, max_output_tokens=500)

