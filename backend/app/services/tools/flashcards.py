from app.services.llm_provider import LLMResult, generate_text


def run_flashcards(content: str, cards: int = 6) -> LLMResult:
    system_prompt = (
        "Eres un generador de flashcards. Responde solo en espanol y en formato:\n"
        "Tarjeta 1\nFrente: ...\nReverso: ...\n"
        f"Genera exactamente {cards} tarjetas."
    )
    user_prompt = f"Material de estudio:\n{content}"
    return generate_text(system_prompt=system_prompt, user_prompt=user_prompt, max_output_tokens=800)

