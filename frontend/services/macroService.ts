import { MacroIndicator } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

interface MacroHistoryPoint {
  date: string;
  value: number;
}

const getIndicators = async (): Promise<MacroIndicator[]> => {
  const res = await fetch(`${API_BASE}/macro/indicators`);
  if (!res.ok) {
    throw new Error('Falha ao buscar indicadores macroeconômicos');
  }
  const data = await res.json();
  return (data.indicators || data) as MacroIndicator[];
};

const getHistory = async (indicator: string): Promise<MacroHistoryPoint[]> => {
  const res = await fetch(`${API_BASE}/macro/historical/${indicator}`);
  if (!res.ok) {
    throw new Error('Falha ao buscar histórico macroeconômico');
  }
  const data = await res.json();
  return (data.history || data) as MacroHistoryPoint[];
};

export const macroService = { getIndicators, getHistory };

