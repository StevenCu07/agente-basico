from datetime import date, timedelta


def run_study_plan(topics: list[str], available_hours_per_week: int, target_date: str) -> str:
    cleaned_topics = [t.strip() for t in topics if t.strip()]
    if not cleaned_topics:
        return "No se encontraron temas para planificar."

    today = date.today()
    try:
        end_date = date.fromisoformat(target_date)
    except ValueError:
        return "Fecha objetivo invalida. Use formato YYYY-MM-DD."

    if end_date <= today:
        return "La fecha objetivo debe ser posterior al dia actual."

    weeks = max(1, ((end_date - today).days // 7) + 1)
    hours_per_topic = max(1, available_hours_per_week // max(1, len(cleaned_topics)))

    lines = [
        f"Plan de estudio desde {today.isoformat()} hasta {end_date.isoformat()}",
        f"Semanas estimadas: {weeks}",
        f"Horas disponibles por semana: {available_hours_per_week}",
        "",
    ]

    current = today
    for week in range(1, weeks + 1):
        week_end = min(end_date, current + timedelta(days=6))
        topic = cleaned_topics[(week - 1) % len(cleaned_topics)]
        lines.append(
            f"Semana {week} ({current.isoformat()} a {week_end.isoformat()}): "
            f"{topic} - {hours_per_topic}h recomendadas"
        )
        current = week_end + timedelta(days=1)
        if current > end_date:
            break

    return "\n".join(lines)

