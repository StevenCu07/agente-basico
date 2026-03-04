# Script de Sustentacion (12-15 minutos)

## 1) Introduccion (2 min)
- Problema: sobrecarga de estudio y poca estructura.
- Solucion: AulaBot, agente academico con 6 herramientas.
- Valor: ahorro de tiempo + mejor preparacion + control de costos.

## 2) Arquitectura (2 min)
- Frontend React (chat + dashboard).
- Backend FastAPI (herramientas y metricas).
- SQLite para persistencia local.
- Docker Compose para levantar todo con un comando.

## 3) Demo funcional (5 min)
1. Abrir chat en `http://localhost:5173`.
2. Ejecutar `resumir`.
3. Ejecutar `quiz`.
4. Guardar un apunte.
5. Ejecutar `buscar` sobre ese apunte.
6. Mostrar tokens y costo de cada interaccion.

## 4) Costos y facturacion (3 min)
- Ir al Dashboard.
- Mostrar metricas por usuario y metricas globales.
- Ejecutar estimador mensual con ejemplo de 12 interacciones/dia.
- Explicar proyeccion de usuarios y facturacion total.

## 5) Cierre tecnico (2 min)
- Explicar tecnicas de reduccion de tokens.
- Explicar estrategia multi-LLM (modelo economico + modelo preciso).
- Mencionar modo `mock` para pruebas sin costo y modo `openai` para operacion real.

