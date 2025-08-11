import { CompanyNewsItem } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

const getCompanyNews = async (ticker: string): Promise<CompanyNewsItem[]> => {
  const res = await fetch(`${API_BASE}/news/company/${ticker}`);
  if (!res.ok) {
    throw new Error('Falha ao buscar notícias da empresa');
  }
  const json = await res.json();
  const items = (json.news || json.data || json) as any[];
  return items.map((item: any) => ({
    id: String(item.id ?? crypto.randomUUID()),
    title: item.titulo,
    summary: item.resumo,
    source: item.portal,
    publishedDate: item.data_publicacao,
    url: item.link_url,
  }));
};

export const newsService = { getCompanyNews };
