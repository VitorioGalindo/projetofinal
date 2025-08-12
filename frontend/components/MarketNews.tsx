
import React, { useState, useEffect, useMemo } from 'react';
import { MarketNewsArticle } from '../types';
import { StarIcon, CurrencyDollarIcon, XMarkIcon, ArrowRightIcon } from '../constants';
import { newsService } from '../services/newsService';
const MarketNews: React.FC = () => {
    const [activeTab, setActiveTab] = useState('Últimas');
    const [newsArticles, setNewsArticles] = useState<MarketNewsArticle[]>([]);
    const [selectedArticle, setSelectedArticle] = useState<MarketNewsArticle | null>(null);
    const [portalFilter, setPortalFilter] = useState('');
    const [order, setOrder] = useState<'asc' | 'desc'>('desc');

    const portals = useMemo(() => Array.from(new Set(newsArticles.map(n => n.source))), [newsArticles]);

    const [limit, setLimit] = useState(50);

    const handleSelectArticle = async (article: MarketNewsArticle) => {
        setSelectedArticle(article);
        if (!article.aiAnalysis) {
            try {
                const analysis = await newsService.analyzeNews(article.id);
                const updated = { ...article, aiAnalysis: analysis };
                setSelectedArticle(updated);
                setNewsArticles(prev => prev.map(n => (n.id === article.id ? updated : n)));
            } catch (err) {
                console.error('Erro ao analisar notícia', err);
            }
        }
    };

    useEffect(() => {
        (async () => {
            try {
                const data = await newsService.getLatestNews(limit, portalFilter || undefined, order);
                setNewsArticles(data);
                if (data.length > 0) {
                    await handleSelectArticle(data[0]);
                } else {
                    setSelectedArticle(null);
                }
            } catch (err) {
                console.error('Erro ao carregar notícias', err);
            }
        })();
    }, [limit, portalFilter, order]);

    return (
        <div className="flex h-full gap-4 text-slate-300">
            {/* Coluna Esquerda: Feed de Notícias */}
            <div className="w-1/3 max-w-sm flex flex-col h-full bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-3 border-b border-slate-700 pb-3">
                    <div className="flex items-center space-x-1">
                        <button onClick={() => setActiveTab('Últimas')} className={`px-3 py-1 text-sm font-semibold rounded-md ${activeTab === 'Últimas' ? 'bg-slate-700 text-white' : 'hover:bg-slate-700/50'}`}>Últimas</button>
                        <button onClick={() => setActiveTab('Populares')} className="flex items-center gap-1 px-3 py-1 text-sm font-semibold rounded-md hover:bg-slate-700/50">
                            <StarIcon /> Populares
                        </button>
                        <button onClick={() => setActiveTab('Cripto')} className="flex items-center gap-1 px-3 py-1 text-sm font-semibold rounded-md hover:bg-slate-700/50">
                            <CurrencyDollarIcon /> Cripto
                        </button>
                    </div>
                    <div className="flex items-center gap-2">
                        <select
                            value={portalFilter}
                            onChange={(e) => setPortalFilter(e.target.value)}
                            className="bg-slate-800 text-slate-300 text-sm rounded-md border border-slate-700 px-2 py-1"
                        >
                            <option value="">Todos</option>
                            {portals.map(portal => (
                                <option key={portal} value={portal}>{portal.toUpperCase()}</option>
                            ))}
                        </select>
                        <select
                            value={order}
                            onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')}
                            className="bg-slate-800 text-slate-300 text-sm rounded-md border border-slate-700 px-2 py-1"
                        >
                            <option value="desc">Mais recentes</option>
                            <option value="asc">Mais antigas</option>
                        </select>
                    </div>
                </div>
                <div className="flex-grow overflow-y-auto pr-1">
                    {newsArticles
                        .filter(n => !portalFilter || n.source === portalFilter)
                        .map(news => (
                        <div
                            key={news.id}
                            onClick={() => setSelectedArticle(news)}
                            className={`p-2.5 rounded-md cursor-pointer mb-1 ${
                                selectedArticle?.id === news.id ? 'bg-slate-700' : 'hover:bg-slate-700/50'
                            }`}
                        >
                            <p className="text-sm font-semibold text-white leading-tight">{news.title}</p>
                            <p className="text-xs text-slate-400 mt-1">{news.summary}</p>
                            <div className="flex items-center justify-between mt-1.5">
                                <span className="text-xs text-slate-400">{news.source.toUpperCase()}</span>
                                <span className="text-xs text-slate-500">{new Date(news.timestamp).toLocaleDateString()}</span>
                            </div>
                        </div>
                    ))}
                    <button
                        onClick={() => setLimit(prev => prev + 50)}
                        className="w-full mt-2 py-1 text-sm text-sky-400 rounded hover:bg-slate-700/50"
                    >
                        Carregar mais
                    </button>
                </div>
                <div className="border-t border-slate-700 mt-2 pt-2 text-center text-xs text-slate-500">
                    Finalize seu cadastro para desbloquear notícias exclusivas.
                </div>
            </div>

            {/* Coluna Central: Artigo */}
            <div className="flex-1 flex flex-col bg-slate-800/50 p-4 rounded-lg border border-slate-700 overflow-y-auto">
                {selectedArticle ? (
                    <>
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h1 className="text-2xl font-bold text-white">{selectedArticle.title}</h1>
                                <p className="text-sm text-slate-400 mt-1">{new Date(selectedArticle.timestamp).toLocaleDateString()} • {selectedArticle.source}</p>
                            </div>
                            <button onClick={() => setSelectedArticle(newsArticles[0] || null)} className="p-1 text-slate-400 hover:text-white rounded-full hover:bg-slate-700">
                                <XMarkIcon className="w-5 h-5"/>
                            </button>
                        </div>
                        {selectedArticle.imageUrl && (
                            <img
                                src={selectedArticle.imageUrl}
                                alt={selectedArticle.title}
                                className="w-full h-64 object-cover rounded-lg mb-4"
                            />
                        )}
                        <div className="prose prose-invert prose-sm text-slate-300 max-w-none">
                            <p>{selectedArticle.summary}</p>
                            <div className="whitespace-pre-line">{selectedArticle.content}</div>
                            <a href={selectedArticle.url} target="_blank" rel="noopener" className="text-sky-400">Ler no portal</a>
                        </div>
                        {selectedArticle.tags && (
                            <div className="mt-4 flex gap-2">
                                {selectedArticle.tags.map(tag => (
                                    <span key={tag} className="bg-slate-700 text-xs font-semibold px-2 py-1 rounded">{tag}</span>
                                ))}
                            </div>
                        )}
                    </>
                ) : <div className="flex items-center justify-center h-full text-slate-500">Selecione uma notícia para ler</div>}
            </div>

            {/* Coluna Direita: Análise */}
            <div className="w-1/3 max-w-sm flex flex-col gap-4">
                 {selectedArticle?.aiAnalysis ? (
                    <>
                    <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                        <h3 className="text-base font-semibold text-white mb-2">Análise por IA</h3>
                        <p className="text-sm text-slate-400 mb-1">Sentimento: <span className={`font-semibold ${
                            selectedArticle.aiAnalysis.sentiment === 'Positivo' ? 'text-green-400' :
                            selectedArticle.aiAnalysis.sentiment === 'Negativo' ? 'text-red-400' : 'text-amber-400'
                        }`}>{selectedArticle.aiAnalysis.sentiment}</span></p>
                        <p className="text-sm text-slate-300">{selectedArticle.aiAnalysis.summary}</p>
                    </div>

                    <div className="flex-grow bg-slate-800/50 p-4 rounded-lg border border-slate-700 flex flex-col">
                        <h3 className="text-base font-semibold text-white mb-3">Ativos Mencionados</h3>
        <div className="space-y-3 flex-grow overflow-y-auto">
            {selectedArticle.aiAnalysis.mentionedCompanies.map(company => (
                <div key={company.ticker}>
                    <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-semibold text-white">{company.name} ({company.ticker})</span>
                        <span className="text-xs text-slate-400">{ (company.relevance * 100).toFixed(0) }%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-1.5">
                        <div className="bg-sky-500 h-1.5 rounded-full" style={{ width: `${company.relevance * 100}%` }}></div>
                    </div>
                </div>
            ))}
        </div>
        <div className="border-t border-slate-700 mt-3 pt-3">
            <h3 className="text-base font-semibold text-white mb-2">Notícias Relacionadas</h3>
            <div className="space-y-2 text-sm">
                {selectedArticle.aiAnalysis.relatedNews.map(item => (
                    <a href="#" key={item.id} className="flex items-center justify-between text-slate-300 hover:text-sky-400 group">
                        <span>{item.headline}</span>
                        <ArrowRightIcon />
                    </a>
                ))}
            </div>
        </div>
    </div>
    </>
                 ) : null}
            </div>
        </div>
    );
};

export default MarketNews;
