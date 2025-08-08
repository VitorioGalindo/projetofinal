
import React, { useState, useEffect } from 'react';
import { FinancialHistoryRow } from '../types';
import { InformationCircleIcon, ChevronUpIcon } from '../constants';


const HistoricalData: React.FC<{ ticker: string }> = ({ ticker }) => {
    const [rows, setRows] = useState<FinancialHistoryRow[]>([]);
    const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`/api/financials/history/${ticker}`);
                const json = await res.json();
                if (json.success) {
                    const grouped: { [code: string]: FinancialHistoryRow } = {};
                    json.data.forEach((item: any) => {
                        if (!item.reference_date) return;
                        const year = new Date(item.reference_date).getFullYear().toString();
                        if (!grouped[item.account_code]) {
                            grouped[item.account_code] = { id: item.account_code, metric: item.account_name, level: 1, data: {} };
                        }
                        grouped[item.account_code].data[year] = { value: Number(item.account_value) };
                    });
                    setRows(Object.values(grouped));
                }
            } catch (err) {
                console.error('Erro ao buscar histórico financeiro', err);
            }
        };
        fetchData();
    }, [ticker]);

    const years = React.useMemo(() => {
        const set = new Set<string>();
        rows.forEach(row => Object.keys(row.data).forEach(y => set.add(y)));
        return Array.from(set).sort();
    }, [rows]);

    const toggleRow = (rowId: string) => {
        setExpandedRows(prev => {
            const newSet = new Set(prev);
            if (newSet.has(rowId)) {
                newSet.delete(rowId);
            } else {
                newSet.add(rowId);
            }
            return newSet;
        });
    };

    const renderRow = (row: FinancialHistoryRow) => {
        const isExpanded = expandedRows.has(row.id);

        const formatValue = (value: any) => {
            if (value === null || value === undefined) return '-';
            if (typeof value === 'number') {
                 if (Number.isInteger(value)) return value.toLocaleString('pt-BR');
                 return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }
            return value;
        }

        const formatVariance = (value: any) => {
            if (value === null || value === undefined) return '-';
            return `${value.toFixed(2)}%`;
        }

        const varianceColor = (value: any) => {
            if (value === null || value === undefined) return 'text-slate-400';
            return value > 0 ? 'text-green-400' : 'text-red-400';
        }

        return (
            <React.Fragment key={row.id}>
                <tr className="border-b border-slate-700/50 hover:bg-slate-800/60">
                    <td className="px-4 py-2.5 text-sm font-medium text-white whitespace-nowrap bg-slate-800/80 backdrop-blur-sm sticky left-0 z-10" style={{ paddingLeft: `${row.level * 1.5}rem` }}>
                        <div className="flex items-center gap-2">
                           {row.subRows && (
                                <button onClick={() => toggleRow(row.id)} className="text-slate-400 hover:text-white">
                                    <ChevronUpIcon className={`w-4 h-4 transition-transform ${isExpanded ? '' : 'transform rotate-180'}`} />
                                </button>
                            )}
                            <span className={!row.subRows ? 'pl-6' : ''}>{row.metric}</span>
                            <InformationCircleIcon className="w-4 h-4 text-slate-500 hover:text-sky-400 cursor-pointer" />
                        </div>
                    </td>
                    {years.map(year => (
                        <React.Fragment key={year}>
                            <td className="px-4 py-2.5 text-sm text-right text-slate-200 whitespace-nowrap">
                                {formatValue(row.data[year]?.value)}
                            </td>
                            {year !== 'TTM' && (
                                <td className={`px-4 py-2.5 text-sm text-right whitespace-nowrap ${varianceColor(row.data[year]?.variance)}`}>
                                    {formatVariance(row.data[year]?.variance)}
                                </td>
                            )}
                        </React.Fragment>
                    ))}
                </tr>
                {isExpanded && row.subRows && row.subRows.map(subRow => renderRow(subRow))}
            </React.Fragment>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-2xl font-bold text-white">{ticker} - PETRORIO</h1>
                    <p className="text-sm text-slate-400">Petróleo, Gás e Biocombustíveis</p>
                </div>
                <div className="flex items-center gap-2">
                     <button className="px-4 py-2 text-sm font-semibold text-white bg-slate-700/50 border border-slate-600 rounded-md hover:bg-slate-700">Adicione a watchlist</button>
                     <button className="px-4 py-2 text-sm font-semibold text-white bg-slate-700/50 border border-slate-600 rounded-md hover:bg-slate-700">Peça um alalce</button>
                     <button className="px-4 py-2 text-sm font-semibold text-white bg-sky-600 rounded-md hover:bg-sky-500">Visão Geral</button>
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 text-center">
                 <div><p className="text-sm text-slate-400">Valor de Ação</p><p className="text-xl font-bold text-white">R$ 42,66</p></div>
                 <div><p className="text-sm text-slate-400">LPA</p><p className="text-xl font-bold text-white">12,94</p></div>
                 <div><p className="text-sm text-slate-400">VPA</p><p className="text-xl font-bold text-white">29,66</p></div>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="flex justify-end items-center mb-4">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-white">Tipos de análise</span>
                        <button className="px-3 py-1.5 text-xs font-semibold text-slate-200 bg-slate-700 rounded-md hover:bg-slate-600">Análise Horizontal</button>
                        <button className="px-3 py-1.5 text-xs font-semibold text-slate-200 bg-slate-700 rounded-md hover:bg-slate-600">Análise Vertical</button>
                    </div>
                </div>
                <div className="overflow-x-auto border border-slate-700 rounded-lg">
                    <table className="w-full text-sm text-left text-slate-300">
                        <thead className="text-xs text-slate-400 uppercase bg-slate-700/50 sticky top-0 z-20">
                            <tr>
                                <th scope="col" className="px-4 py-3 font-medium whitespace-nowrap bg-slate-800/80 backdrop-blur-sm sticky left-0 z-10">Histórico de DRE</th>
                                {years.map(year => (
                                    <React.Fragment key={year}>
                                        <th scope="col" className="px-4 py-3 font-medium text-right whitespace-nowrap">{year}</th>
                                        {year !== 'TTM' && <th scope="col" className="px-4 py-3 font-medium text-right whitespace-nowrap">H - var%</th>}
                                    </React.Fragment>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {rows.map(row => renderRow(row))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default HistoricalData;
