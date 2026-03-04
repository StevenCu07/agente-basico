# ENTREGA - AGENTE BASICO (CORTE 1)

Fecha de referencia del documento: **26 de febrero de 2026**  
Fecha de entrega del curso: **4 de marzo de 2026**

## 1. Descripcion general del producto
**Producto:** AulaBot  
**Problema que resuelve:** estudiantes universitarios invierten mucho tiempo en transformar apuntes en material util para estudiar (resumenes, preguntas, tarjetas y cronogramas).  
**Contexto de uso:** preparacion de parciales, quices y entregas semanales en pregrado.  
**Valor que aporta:** acelera estudio y mejora organizacion con herramientas accionables desde un chat unico.  
**Alcance funcional (Corte 1):**
- Chat web funcional.
- Backend API con 6 herramientas academicas.
- Historial y metricas de consumo por usuario.
- Estimador de costo mensual y facturacion proyectada.

## 2. Descripcion general del agente
**Objetivo del agente:** apoyar el estudio con automatizacion de tareas repetitivas y control de costos de uso de LLM.

**Arquitectura general:**
- Frontend: React + Vite.
- Backend: FastAPI.
- Persistencia: SQLite.
- Despliegue: Docker Compose.
- LLM: OpenAI (modo real) o modo mock local (demo sin costo).

**Flujo de funcionamiento:**
1. Usuario ingresa token simple (`user_token`) en el chat.
2. Selecciona herramienta (o usa `/api/chat`).
3. Backend procesa, responde y registra tokens/costo.
4. Dashboard muestra consumo por usuario y global mensual.

**Integracion con herramientas:**
- Cada herramienta tiene endpoint dedicado y tambien puede invocarse por `/api/chat`.
- Se registra uso en `interactions` y agregado mensual en `monthly_aggregates`.

**Tipo de interfaz:** chat HTML (web) + API REST.

## 3. Publico o usuarios objetivo
- Estudiantes universitarios de pregrado.
- Monitores o tutores academicos.
- Grupos de estudio que preparan evaluaciones por temas.

## 4. Herramientas implementadas (6 minimas)
1. `resumir_texto`: sintetiza contenido academico.
2. `generar_quiz`: crea preguntas con opciones y respuesta.
3. `crear_flashcards`: genera tarjetas frente/reverso.
4. `plan_estudio`: construye plan semanal hasta fecha objetivo.
5. `buscar_apuntes`: consulta apuntes guardados por relevancia.
6. `estimar_costo_tokens`: calcula consumo y costo mensual.

## 5. Estimacion de tokens por usuario y costo mensual
**Supuestos de uso promedio:**
- Interacciones por dia: 12
- Tokens entrada por interaccion: 450
- Tokens salida por interaccion: 450
- Total por interaccion: 900
- Dias al mes: 30

**Calculo mensual por usuario:**
- Interacciones/mes = `12 * 30 = 360`
- Tokens/mes = `360 * 900 = 324,000 tokens`

**Estimacion economica (configurada para demo):**
- Precio entrada: `0.20 USD / 1M tokens`
- Precio salida: `0.80 USD / 1M tokens`
- Costo entrada mensual: `(162,000 / 1,000,000) * 0.20 = 0.0324 USD`
- Costo salida mensual: `(162,000 / 1,000,000) * 0.80 = 0.1296 USD`
- **Costo total usuario/mes: 0.1620 USD**

## 6. Estimacion de facturacion total mensual (todos los usuarios)
**Supuesto de usuarios activos mensuales:** 250

**Consumo total mensual:**
- `324,000 tokens/usuario * 250 usuarios = 81,000,000 tokens/mes`

**Facturacion proyectada mensual:**
- `0.1620 USD/usuario * 250 = 40.50 USD/mes`

## 7. Tecnicas de prompt para reducir consumo
- Prompts estructurados por herramienta (formato fijo y objetivo).
- Limites de salida (cantidad de palabras/preguntas/tarjetas).
- Respuestas concisas y orientadas a accion.
- Control de contexto: envio solo de texto necesario por tarea.

## 8. Otras estrategias para mitigar facturacion alta
- Cache por consulta repetida.
- Busqueda por embeddings para enviar solo fragmentos relevantes.
- Resumen progresivo del historial del chat.
- Enrutamiento a modelos economicos para tareas simples.

## 9. Viabilidad de usar diferentes LLM
**Si, es viable y pertinente.**

**Justificacion:**
- Casos diferenciados:
  - Modelo economico: resumen rapido, normalizacion, clasificacion.
  - Modelo de mayor calidad: quiz complejos o contenido con alta exigencia.
- Costos: disminuye costo promedio por solicitud.
- Rendimiento: mejor latencia para operaciones sencillas.
- Precision: se reserva mayor capacidad para tareas donde importa mas la exactitud.

## Requisitos tecnicos validados
- Minimo 6 herramientas funcionales: **cumplido**.
- Interfaz de terminal/chat: **chat HTML implementado**.
- Coherencia producto-agente: **cumplida** (foco academico integral).

