# AulaBot - Agente Academico (Corte 1)

Proyecto full stack dockerizado con:
- Backend `FastAPI` + `SQLite`
- Frontend `React + Vite`
- 6 herramientas funcionales para apoyo academico

## Herramientas implementadas
1. `resumir_texto`
2. `generar_quiz`
3. `crear_flashcards`
4. `plan_estudio`
5. `buscar_apuntes`
6. `estimar_costo_tokens`

## Ejecutar con Docker
1. Verificar Docker Desktop encendido.
2. Desde la raiz del proyecto:

```bash
docker compose up -d --build
```

3. Abrir:
- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`

## Variables de entorno
El archivo `.env` ya viene configurado en modo demo:
- `LLM_MODE=mock` para funcionar sin API key.

Para usar OpenAI real:
1. Cambiar `LLM_MODE=openai`
2. Configurar `OPENAI_API_KEY`

## Endpoints principales
- `POST /api/chat`
- `POST /api/tools/resumir`
- `POST /api/tools/quiz`
- `POST /api/tools/flashcards`
- `POST /api/tools/plan`
- `POST /api/tools/buscar`
- `POST /api/cost/estimate`
- `GET /api/metrics/user/{user_token}`
- `GET /api/metrics/global`

## Pruebas backend
Desde `backend/`:

```bash
pytest -q
```

## Documentacion de entrega
- [Documento de entrega](docs/ENTREGA_CORTE1.md)
- [Script de sustentacion](docs/SCRIPT_DEMO.md)

