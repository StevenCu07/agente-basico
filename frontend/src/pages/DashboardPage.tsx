import { FormEvent, useEffect, useState } from "react";

import { estimateCost, fetchGlobalMetrics, fetchUserMetrics } from "../services/api";
import type { GlobalMetrics, UserMetrics } from "../types";

interface DashboardPageProps {
  refreshKey: number;
}

export default function DashboardPage({ refreshKey }: DashboardPageProps) {
  const [userToken, setUserToken] = useState("estudiante_demo");
  const [globalMetrics, setGlobalMetrics] = useState<GlobalMetrics | null>(null);
  const [userMetrics, setUserMetrics] = useState<UserMetrics | null>(null);
  const [estimateValue, setEstimateValue] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchGlobalMetrics()
      .then(setGlobalMetrics)
      .catch((err) => setError(err instanceof Error ? err.message : "Error"));
  }, [refreshKey]);

  const loadUserMetrics = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      const metrics = await fetchUserMetrics(userToken);
      setUserMetrics(metrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar metricas");
    }
  };

  const runEstimate = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const result = await estimateCost({
        daily_interactions: 12,
        avg_tokens_in: 450,
        avg_tokens_out: 450,
        days: 30,
      });
      setEstimateValue(`${result.monthly_total_tokens} tokens/mes | ${result.monthly_cost.total_cost} ${result.monthly_cost.currency}`);
    } catch (err) {
      setEstimateValue(err instanceof Error ? err.message : "Error al estimar");
    }
  };

  return (
    <div className="grid">
      <section className="card">
        <h2>Metricas globales</h2>
        {!globalMetrics && <p>Sin datos aun.</p>}
        {globalMetrics && (
          <ul className="metric-list">
            <li>Mes: {globalMetrics.month}</li>
            <li>Tokens: {globalMetrics.total_tokens}</li>
            <li>Interacciones: {globalMetrics.interactions}</li>
            <li>Usuarios activos: {globalMetrics.active_users}</li>
            <li>Costo total: {globalMetrics.total_cost} USD</li>
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Metricas por usuario</h2>
        <form onSubmit={loadUserMetrics} className="form">
          <label>
            Token de usuario
            <input value={userToken} onChange={(e) => setUserToken(e.target.value)} />
          </label>
          <button type="submit">Consultar</button>
        </form>
        {userMetrics && (
          <ul className="metric-list">
            <li>Mes: {userMetrics.month}</li>
            <li>Tokens: {userMetrics.total_tokens}</li>
            <li>Interacciones: {userMetrics.interactions}</li>
            <li>Costo: {userMetrics.total_cost} USD</li>
          </ul>
        )}
      </section>

      <section className="card full">
        <h2>Estimador rapido de consumo mensual</h2>
        <form onSubmit={runEstimate} className="form inline">
          <button type="submit">Calcular con ejemplo (12 interacciones/dia)</button>
        </form>
        {estimateValue && <p className="muted">{estimateValue}</p>}
      </section>

      {error && <p className="error full">{error}</p>}
    </div>
  );
}

