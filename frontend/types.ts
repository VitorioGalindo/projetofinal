export type Page = 
  | 'portfolio' 
  | 'ai-assistant'
  | 'overview' 
  | 'history' 
  | 'comparator' 
  | 'insider-radar' 
  | 'research'
  | 'company-news'
  | 'cvm-docs'
  | 'sell-side-data'
  | 'market-data'
  | 'market-overview'
  | 'macro-data'
  | 'yield-curve'
  | 'screening'
  | 'fundamentalist'
  | 'flow-data'
  | 'sell-side';

export interface Asset {
  ticker: string;
  price: number;
  dailyChange: number;
  contribution: number;
  quantity: number;
  positionValue: number;
  positionPercent: number;
  targetPercent: number;
  difference: number;
  adjustment: number;
}

export interface PortfolioSummary {
  id: number;
  name: string;
  total_value: number;
  total_cost: number;
  total_gain: number;
  total_gain_percent: number;
  holdings: PortfolioHolding[];
}

export interface PortfolioDailyValue {
  date: string;
  total_value: number;
  total_cost: number;
  total_gain: number;
  total_gain_percent: number;
}

export interface PortfolioHolding {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  value: number;
  cost: number;
  gain: number;
  gain_percent: number;
}

export interface ChatMessage {
  role: 'user' | 'model';
  content: string;
  files?: { name: string; type: string; size: number }[];
}

export interface Chat {
  id: string;
  title: string;
  messages: ChatMessage[];
}

// Market News Page Types
export interface CompanyMention {
    ticker: string;
    name: string;
    relevance: number; // 0 to 1
}

export interface AiAnalysis {
    summary: string;
    sentiment: 'Positivo' | 'Negativo' | 'Neutro';
    mentionedCompanies: CompanyMention[];
    relatedNews: { id: string; headline: string }[];
    relatedEvents: { id: string; title: string }[];
}

export interface MarketNewsArticle {
    id: number;
    headline: string;
    source: string;
    timestamp: string;
    content: string;
    url: string;
    imageUrl?: string;
    tags?: string[];
    aiAnalysis?: AiAnalysis;
}


export interface YieldCurvePoint {
  ativo: string;
  ultimo: number;
  ultimoChange: number;
  bps: number;
  ajusteAnterior: number;
  dv1: number;
  abertura: number;
  maxima: number;
  minima: number;
  fechamento: number;
}

export interface CopomSimulation {
  reuniao: string;
  ano: number;
  expectativa: string;
  codigo: string;
  cv: number;
  ultimo: number;
  projetado: number;
  diferenca: number;
  dv1: number;
  pnl: number;
  dus: number;
}

export interface SelicHistoryPoint {
    date: string;
    value: number;
}


export interface InsiderTrade {
    ticker: string;
    value: number;
    type: 'buy' | 'sell';
}

export interface MacroIndicator {
    name: string;
    value: string;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
    historicalData: { date: string; value: number }[];
}

export interface FundamentalIndicator {
    label: string;
    value: string | number;
}

export interface FinancialStatementItem {
    item: string;
    value: string;
    change?: string;
    changeType?: 'positive' | 'negative' | 'neutral';
}

export interface EditableAsset {
  id: number;
  ticker: string;
  quantity: number;
  targetWeight: number;
}

export interface DailyMetric {
  id: string;
  label: string;
  value: number;
}

export interface SuggestedPortfolioAsset {
  ticker: string;
  company: string;
  currency: 'BRL' | 'USD';
  currentPrice: number;
  targetPrice: number;
  upsideDownside: number;
  mktCap: number;
  pe26: number | string;
  pe5yAvg: number | string;
  deltaPe: number | string;
  evEbitda26: number | string;
  evEbitda5yAvg: number | string;
  deltaEvEbitda: number | string;
  epsGrowth26: number | string;
  ibovWeight: number;
  portfolioWeight: number;
  owUw: number;
}

export interface SectorWeight {
  sector: string;
  ibovWeight: number;
  portfolioWeight: number;
  owUw: number;
}

// Company Overview Page Types
export interface TechnicalSignal {
  id: number;
  type: 'COMPRA' | 'VENDA';
  timeframe: string;
  status: string;
  close: string;
  entry: string;
  setup: string;
  category: 'Geral' | '15 min' | '30 min' | '60 min' | 'Diário' | 'Semanal';
}

export interface InsiderDataPoint {
    date: string;
    price: number;
    buyVolume: number;
    sellVolume: number;
}

export interface RelevantFact {
    id: string;
    title: string;
    date: string;
    time: string;
}

export interface Shareholder {
    name: string;
    percentage: number;
}

// Historical Data Page Types
export interface YearlyData {
    value: number | string | null;
    variance?: number | null;
}

export interface FinancialHistoryRow {
    id: string;
    metric: string;
    level: number;
    isHeader?: boolean;
    data: { [year: string]: YearlyData };
    subRows?: FinancialHistoryRow[];
}

// Insider Radar Page Types
export interface ConsolidatedInsiderTrade {
  ticker: string;
  buyAbsolute: number;
  sellAbsolute: number;
  buyMarketCap: number;
  sellMarketCap: number;
}

export interface InsiderTransaction {
    id: string;
    date: string;
    price: number;
    quantity: number;
    balance: number;
    player: string;
    volumePercent: number;
    broker: string;
    modality: string;
    freeFloatPercent: number;
    capitalPercent: number;
    type: 'Compra' | 'Venda';
}

export interface InsiderPricePoint {
    date: string;
    price: number;
    transactionType?: 'Compra' | 'Venda';
}

export interface AnalyticalSummaryItem {
    name: string;
    balance: number;
    freeFloat: number;
    capital: number;
}

// CVM Documents Page Types
export interface CvmDocument {
  id: string;
  date: string;
  company: string;
  category: string;
  subject: string;
  link: string;
}

export interface CvmCompany {
  id: number;
  ticker: string;
  company_name: string;
}

export interface CvmDocumentType {
  code: string;
  name: string;
  description: string;
}

// Market Overview Page Types
export interface MarketPerformanceItem {
  name: string;
  lastPrice: number;
  ytd: number;
  ifr: number;
  m1: number;
  m3: number;
  m6: number;
  m12: number;
  ytd2: number;
}

export interface StockPerformanceItem {
  ticker: string;
  lastPrice: number;
  change: number;
  ifr: number;
  m1: number;
  m3: number;
  m6: number;
  m12: number;
  ytd: number;
}

export interface TopMover {
  ticker: string;
  lastPrice: number;
  change: number;
  volume: number;
}

export interface SectorParticipation {
  name: string;
  weight: number;
  change: number;
  companies: number;
  color: string;
}

export interface SentimentData {
  value: number;
  history: { date: string, value: number }[];
}

// Screening Page Types
export interface ScreeningFormula {
  id: string;
  name: string;
  author?: string;
  icon: React.ReactNode;
}

export interface ScreeningResultCompany {
  rank: number;
  ticker: string;
  cota: number;
  [key: string]: any; // Allow dynamic properties for different formulas
}

export interface Metric {
  id: string;
  name: string;
}

export interface MetricCategory {
  id: string;
  name: string;
  metrics: Metric[];
}

// Flow Data Page Types
export interface DailyFlow {
    date: string;
    estrangeiro: number;
    institucional: number;
    instituicoesFinanceiras: number;
    pessoasFisicas: number;
    outros: number;
}

export interface AccumulatedFlowPoint {
    date: string;
    Estrangeiro: number;
    Institucional: number;
    'Instituições Financeiras': number;
    'Pessoas Físicas': number;
    Outros: number;
    IBOV: number;
}

export interface MonthlyFlow {
    month: string;
    value: number;
}

export interface DetailedDailyFlow {
    date: string;
    aVista: number;
    futuro: number;
    total: number;
}

export interface DetailedMonthlyFlow {
    date: string;
    aVista: number | string;
    futuro: number | string;
    total: number | string;
}

export interface FlowChartPoint {
    date: string;
    'Fluxo R$': number;
    'Fechamento IBOV'?: number;
    'Fluxo à vista'?: number;
    'Fluxo Futuro'?: number;
}

export interface AccumulatedAnnualFlowPoint {
    date: string;
    y2025: number;
    y2024: number;
    y2023: number;
    y2022: number;
    y2021: number;
}

// Sell Side Data Page Types
export interface SectorNode {
    name: string;
    children?: SectorNode[];
}

export interface StockGuideData {
  sector: string;
  company: string;
  ticker: string;
  rating: string;
  marketCap: number | string;
  volume: {
    media12M: number | string;
    pctMedia: number | string;
  };
  price: {
    ultimo: number | string;
    alvo: number | string;
    upside: number | string;
  };
  performance: {
    semana: number | string;
    mes: number | string;
    ano: number | string;
  };
  pl: {
    '2025E': number | string;
    '2026E': number | string;
  };
  evEbitda: {
    '2025E': number | string;
    '2026E': number | string;
  };
  pvp: {
    '2025E': number | string;
    '2026E': number | string;
  };
  dividendYield: {
    '2025E': number | string;
    '2026E': number | string;
  };
  dividaLiquidaEbitda: {
    '2025E': number | string;
    '2026E': number | string;
  };
  roe: {
    '2025E': number | string;
    '2026E': number | string;
  };
  isMedian?: boolean;
}

// Research Page Types
export interface ResearchNote {
    id: number;
    title: string;
    summary: string;
    content: string;
    last_updated: string;
}

// Company News Page Types
export interface CompanyNewsItem {
  id: number;
  url: string;
  title: string;
  summary: string;
  source: string;
  publishedDate: string;
}

export interface CompanyNewsBlock {
  ticker: string;
  newsItems: CompanyNewsItem[];
}