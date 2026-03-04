import { FormEvent, useMemo, useState } from "react";

import { createDocument, sendChat } from "../services/api";
import type { ChatResponse, ToolName } from "../types";

interface ChatPageProps {
  onTokenUpdated: () => void;
}

const TOOL_OPTIONS: { value: ToolName; label: string }[] = [
  { value: "resumir", label: "Resumir texto" },
  { value: "quiz", label: "Generar quiz" },
  { value: "flashcards", label: "Crear flashcards" },
  { value: "plan", label: "Plan de estudio" },
  { value: "buscar", label: "Buscar apuntes" },
  { value: "cost", label: "Info de costos" },
];

export default function ChatPage({ onTokenUpdated }: ChatPageProps) {
  const [userToken, setUserToken] = useState("estudiante_demo");
  const [tool, setTool] = useState<ToolName>("resumir");
  const [message, setMessage] = useState("");
  const [context, setContext] = useState("");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [docTitle, setDocTitle] = useState("");
  const [docContent, setDocContent] = useState("");
  const [docMessage, setDocMessage] = useState("");

  const estimatedText = useMemo(() => {
    if (!response) return "";
    const cost = response.token_usage.estimated_cost;
    return `${response.token_usage.total_tokens} tokens | ${cost.total_cost} ${cost.currency}`;
  }, [response]);

  const handleChat = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await sendChat({
        user_token: userToken,
        message,
        context: context || undefined,
        tool,
      });
      setResponse(result);
      onTokenUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al consultar el agente");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveDocument = async (event: FormEvent) => {
    event.preventDefault();
    setDocMessage("");
    try {
      const result = await createDocument({ user_token: userToken, title: docTitle, content: docContent });
      setDocMessage(`Documento ${result.document_id} guardado`);
      setDocTitle("");
      setDocContent("");
    } catch (err) {
      setDocMessage(err instanceof Error ? err.message : "No se pudo guardar el documento");
    }
  };

  return (
    <div className="grid">
      <section className="card">
        <h2>Chat del agente</h2>
        <form onSubmit={handleChat} className="form">
          <label>
            Token de usuario
            <input value={userToken} onChange={(e) => setUserToken(e.target.value)} required minLength={3} />
          </label>
          <label>
            Herramienta
            <select value={tool} onChange={(e) => setTool(e.target.value as ToolName)}>
              {TOOL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Mensaje
            <textarea value={message} onChange={(e) => setMessage(e.target.value)} rows={6} required />
          </label>
          <label>
            Contexto opcional
            <textarea value={context} onChange={(e) => setContext(e.target.value)} rows={3} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Procesando..." : "Enviar"}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="card">
        <h2>Resultado</h2>
        {!response && <p>Envia un mensaje para ver la respuesta.</p>}
        {response && (
          <>
            <p>
              <strong>Herramienta:</strong> {response.tool_used}
            </p>
            <pre>{response.response}</pre>
            <p className="muted">{estimatedText}</p>
          </>
        )}
      </section>

      <section className="card full">
        <h2>Cargar apuntes para la herramienta de busqueda</h2>
        <form onSubmit={handleSaveDocument} className="form">
          <label>
            Titulo
            <input value={docTitle} onChange={(e) => setDocTitle(e.target.value)} required />
          </label>
          <label>
            Contenido
            <textarea value={docContent} onChange={(e) => setDocContent(e.target.value)} rows={4} required />
          </label>
          <button type="submit">Guardar apunte</button>
        </form>
        {docMessage && <p className="muted">{docMessage}</p>}
      </section>
    </div>
  );
}

