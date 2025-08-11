import { MacroIndicator } from '../types';

interface MacroApiResponse {
  success: boolean;
  indicators: Record<string, { value: number; unit: string; description: string; updated_at: string | null }>;
}

export async function fetchMacroIndicators(): Promise<MacroIndicator[]> {
  const res = await fetch('/api/macro/indicators');
  if (!res.ok) throw new Error('Failed to fetch indicators');
  const data: MacroApiResponse = await res.json();
  return Object.entries(data.indicators).map(([name, info]) => ({
    name,
    value: String(info.value),
    change: '',
    changeType: 'neutral',
    historicalData: [],
  }));
}