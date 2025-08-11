import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, Legend } from 'recharts';
import { MacroIndicator } from '../types';
import { macroService } from '../services/macroService';

const formatNumber = (value: number) =>
  value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const IndicatorCard: React.FC<{ indicator: MacroIndicator }> = ({ indicator }) => {
    const changeColor = indicator.changeType === 'positive' ? 'text-green-400' : indicator.changeType === 'negative' ? 'text-red-400' : 'text-slate-400';
    
    return (
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 flex flex-col justify-between">
            <div>
                <p className="text-sm text-slate-400">{indicator.name}</p>
                <p className="text-2xl font-bold text-white my-1">{indicator.value}</p>
                <p className={`text-sm font-semibold ${changeColor}`}>{indicator.change}</p>
            </div>
            <div className="h-20 -mx-4 -mb-4 mt-2">
                 <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={indicator.historicalData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id={`color${indicator.name.replace(/\s/g, '')}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', fontSize: '12px', padding: '4px 8px' }}
                            itemStyle={{ color: '#cbd5e1' }}
                            labelStyle={{ display: 'none' }}
                        />
                        <Area type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={2} fillOpacity={1} fill={`url(#color${indicator.name.replace(/\s/g, '')})`} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};


const MacroData: React.FC = () => {
  const colors = ['#38bdf8', '#a78bfa', '#f472b6', '#fb923c', '#4ade80', '#facc15'];
  const [macroData, setMacroData] = useState<MacroIndicator[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const indicators = await macroService.getIndicators();
        const entries = Object.entries(indicators);
        const mapped = await Promise.all(
          entries.map(async ([key, info]) => {
            const history = await macroService.getHistory(key);
            const formattedHistory = history.map((h) => ({
              date: new Date(h.date).toLocaleDateString('pt-BR', { month: 'short' }).replace('.', ''),
              value: h.value,
            }));
            const latest = history[history.length - 1]?.value ?? 0;
            const prev = history[history.length - 2]?.value ?? latest;
            const diff = latest - prev;
            const changeType: 'positive' | 'negative' | 'neutral' = diff > 0 ? 'positive' : diff < 0 ? 'negative' : 'neutral';
            return {
              name: info.description || key,
              value: `${formatNumber(latest)}${info.unit ? ` ${info.unit}` : ''}`,
              change: `${diff > 0 ? '+' : ''}${formatNumber(diff)}${info.unit ? ` ${info.unit}` : ''}`,
              changeType,
              historicalData: formattedHistory,
            } as MacroIndicator;
          })
        );
        setMacroData(mapped);
      } catch (err) {
        console.error('Erro ao carregar dados macro', err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-white">Dados Macroeconômicos</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {macroData.map((indicator) => (
          <IndicatorCard key={indicator.name} indicator={indicator} />
        ))}
      </div>
      <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4">Histórico Comparativo (Normalizado)</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis
              stroke="#94a3b8"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(val) => val.toFixed(2)}
            />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#cbd5e1' }} />
            <Legend wrapperStyle={{ fontSize: '14px' }} />
            {macroData.map((d, index) => (
              <Line
                key={d.name}
                type="monotone"
                dataKey="value"
                data={d.historicalData}
                name={d.name}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MacroData;
