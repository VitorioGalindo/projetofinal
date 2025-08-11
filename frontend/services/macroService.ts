const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

interface IndicatorInfo {
  value: number | null;
  unit: string;
  description: string;
  updated_at: string | null;
}

interface HistoryPoint {
  date: string;
  value: number;
}

async function getIndicators(): Promise<Record<string, IndicatorInfo>> {
  const res = await fetch(`${API_BASE}/macro/indicators`);
  if (!res.ok) {
    throw new Error('Falha ao buscar indicadores macroeconômicos');
  }
  const json = await res.json();
  return json.indicators || {};
}

async function getHistory(indicator: string): Promise<HistoryPoint[]> {
  const res = await fetch(`${API_BASE}/macro/historical/${indicator}`);
  if (!res.ok) {
    throw new Error('Falha ao buscar histórico do indicador');
  }
  const json = await res.json();
  return json.history || [];
}

export const macroService = { getIndicators, getHistory };

