import { useState } from "react";

import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";

type View = "chat" | "dashboard";

export default function App() {
  const [view, setView] = useState<View>("chat");
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <main className="container">
      <header className="header">
        <div>
          <h1>AulaBot</h1>
          <p>Agente academico para resumen, quiz, flashcards, plan de estudio y busqueda.</p>
        </div>
        <nav className="tabs">
          <button className={view === "chat" ? "active" : ""} onClick={() => setView("chat")}>
            Chat
          </button>
          <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}>
            Dashboard
          </button>
        </nav>
      </header>

      {view === "chat" ? <ChatPage onTokenUpdated={() => setRefreshKey((prev) => prev + 1)} /> : <DashboardPage refreshKey={refreshKey} />}
    </main>
  );
}

