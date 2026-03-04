import math
import os


def estimate_tokens_from_text(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def prices_per_million() -> tuple[float, float]:
    input_price = float(os.getenv("TOKEN_PRICE_INPUT", "0.20"))
    output_price = float(os.getenv("TOKEN_PRICE_OUTPUT", "0.80"))
    return input_price, output_price


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> dict[str, float | str]:
    input_price, output_price = prices_per_million()
    input_cost = (prompt_tokens / 1_000_000) * input_price
    output_cost = (completion_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost
    return {
        "input_cost": round(input_cost, 8),
        "output_cost": round(output_cost, 8),
        "total_cost": round(total_cost, 8),
        "currency": os.getenv("DEFAULT_CURRENCY", "USD"),
    }

