import { StockGuideData } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

export async function getStockGuideData(): Promise<StockGuideData[]> {
  const res = await fetch(`${API_BASE}/market/stock-guide`);
  if (!res.ok) {
    throw new Error('Falha ao buscar dados do stock guide');
  }
  const data = await res.json();
  return (data.stockGuide || data.data || data) as StockGuideData[];
}

export const stockGuideService = { getStockGuideData };
