import { CompanyNewsItem, MarketNewsArticle } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

export const getCompanyNews = async (
  ticker: string
): Promise<CompanyNewsItem[]> => {
  const res = await fetch(`${API_BASE}/news/company/${ticker}`);
  if (!res.ok) {
    throw new Error('Falha ao buscar notícias da empresa');
  }
  const json = await res.json();
  const items = (json.news || json.data || json) as any[];
  return items.map((item: any, idx: number) => ({
    id: Number(item.id ?? Date.now() + idx),
    title: item.titulo,
    summary: item.resumo,
    source: item.portal,
    publishedDate: item.data_publicacao,
    url: item.link_url || item.url,
  }));
};

export const getLatestNews = async (
  limit = 10
): Promise<MarketNewsArticle[]> => {
  const res = await fetch(`${API_BASE}/news/latest?limit=${limit}`);
  if (!res.ok) {
    throw new Error('Falha ao buscar últimas notícias');
  }
  const json = await res.json();
  const items = (json.news || json.data || json) as any[];
  return items.map((item: any, idx: number) => ({
    id: Number(item.id ?? idx),
    headline: item.titulo,
    source: item.portal,
    timestamp: item.data_publicacao,
    summary: item.resumo,
    content:
      item.conteudo_completo ||
      item.conteudo ||
      item.content ||
      item.resumo,
    url: item.link_url,
    imageUrl: item.imagem_url || item.image_url,
    tags: item.tags,
    aiAnalysis: item.aiAnalysis,
  }));
};

export const newsService = { getCompanyNews, getLatestNews };

