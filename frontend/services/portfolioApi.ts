import { PortfolioSummary, PortfolioDailyValue } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

export async function getPortfolioSummary(id: number): Promise<PortfolioSummary> {
  const res = await fetch(`${API_BASE}/portfolio/${id}/summary`);
  if (!res.ok) {
    throw new Error('Falha ao buscar portfólio');
  }
  const data = await res.json();
  return data.portfolio as PortfolioSummary;
}

export async function savePortfolioSnapshot(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/portfolio/${id}/snapshot`, { method: 'POST' });
  if (!res.ok) {
    throw new Error('Falha ao salvar snapshot');
  }
}

export async function upsertPositions(
  id: number,
  positions: { symbol: string; quantity: number; avg_price: number }[],
): Promise<void> {
  const res = await fetch(`${API_BASE}/portfolio/${id}/positions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(positions),
  });
  if (!res.ok) {
    throw new Error('Falha ao salvar posições');
  }
}

export async function getPortfolioDailyValues(id: number): Promise<PortfolioDailyValue[]> {
  const res = await fetch(`${API_BASE}/portfolio/${id}/daily-values`);
  if (!res.ok) {
    throw new Error('Falha ao buscar histórico do portfólio');
  }
  const data = await res.json();
  return data.values as PortfolioDailyValue[];
}

export async function updateDailyMetrics(
  id: number,
  metrics: { id: string; value: number }[],
): Promise<void> {
  const res = await fetch(`${API_BASE}/portfolio/${id}/daily-metrics`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metrics),
  });
  if (!res.ok) {
    throw new Error('Falha ao atualizar métricas');
  }
}
export const portfolioApi = {
  getPortfolioSummary,
  savePortfolioSnapshot,
  upsertPositions,
  getPortfolioDailyValues,
  updateDailyMetrics,
};

