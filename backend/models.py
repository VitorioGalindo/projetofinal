# backend/models.py
from . import db
from sqlalchemy.sql import func
from sqlalchemy import (
    String, Integer, DateTime, Numeric, Text, Boolean, ForeignKey, Date, JSON
)
from sqlalchemy.orm import relationship

# --- Modelo definitivo para a tabela 'companies' ---
# Baseado nas imagens image_d3ada7.png e image_d3aa69.png
class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(Integer, primary_key=True)
    cvm_code = db.Column(Integer, unique=True)
    company_name = db.Column(String(255), nullable=False, index=True)
    trade_name = db.Column(String(255))
    cnpj = db.Column(String(20), unique=True)
    founded_date = db.Column(DateTime)
    main_activity = db.Column(Text)
    website = db.Column(String(255))
    controlling_interest = db.Column(String(255))
    is_state_owned = db.Column(Boolean)
    is_foreign = db.Column(Boolean)
    is_b3_listed = db.Column(Boolean)
    b3_issuer_code = db.Column(String(50))
    b3_listing_segment = db.Column(String(100))
    b3_sector = db.Column(String(100))
    b3_subsector = db.Column(String(100))
    b3_segment = db.Column(String(100))
    tickers_json = db.Column('tickers', JSON) # Renomeado para evitar conflito com a relação
    ticker = db.Column(String(10))
    is_active = db.Column(Boolean, default=True)
    industry_classification = db.Column(String(255))
    market_cap = db.Column(Numeric) # Usando Numeric para maior precisão que Float
    employee_count = db.Column(Integer)
    about = db.Column(Text)
    has_dfp_data = db.Column(Boolean)
    has_itr_data = db.Column(Boolean)
    has_fre_data = db.Column(Boolean)
    last_dfp_year = db.Column(Integer)
    last_itr_quarter = db.Column(String(10))
    created_at = db.Column('created_at', DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    activity_description = db.Column(Text)
    capital_structure_summary = db.Column(JSON)

    # Relacionamentos para facilitar as consultas
    financial_data = relationship("CvmFinancialData", back_populates="company")
    cvm_documents = relationship("CvmDocument", back_populates="company")
    ticker_list = relationship("Ticker", back_populates="company") # Nome da relação alterado
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# --- Modelo definitivo para a tabela 'cvm_financial_data' ---
# Baseado na imagem image_d39e4b.png
class CvmFinancialData(db.Model):
    __tablename__ = 'cvm_financial_data'
    
    id = db.Column(Integer, primary_key=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference_date = db.Column(Date)
    report_type = db.Column(String(20))
    report_version = db.Column(String(20))
    cvm_version = db.Column(String(20))
    account_code = db.Column(String(50), nullable=False)
    account_name = db.Column(String(255), nullable=False)
    account_value = db.Column(Numeric(20, 2), nullable=False)
    currency = db.Column(String(10))
    is_fixed = db.Column(Boolean)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="financial_data")

# --- Modelo definitivo para a tabela 'cvm_documents' ---
# Baseado na imagem image_d39e84.png
class CvmDocument(db.Model):
    __tablename__ = 'cvm_documents'
    
    id = db.Column(Integer, primary_key=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    cvm_code = db.Column(Integer)
    document_type = db.Column(String(50), index=True)
    category = db.Column(String(100))
    title = db.Column(String(255))
    delivery_date = db.Column(DateTime(timezone=True), index=True)
    reference_date = db.Column(Date)
    status = db.Column(String(50))
    download_url = db.Column(String(500))
    link = db.Column(String(500))
    file_type = db.Column(String(20))
    content_text = db.Column(Text)
    summary = db.Column(Text)
    extracted_at = db.Column(DateTime(timezone=True))
    process_status = db.Column(String(50))
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="cvm_documents")

# --- MODELO 'Ticker' COM A CORREÇÃO FINAL ---
class Ticker(db.Model):
    __tablename__ = 'tickers'
    id = db.Column(Integer, primary_key=True)
    symbol = db.Column(String(20), unique=True, nullable=False, index=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    
    # ADICIONADO: A coluna 'type' que existe na sua tabela
    type = db.Column(String(50)) 
    
    # REMOVIDO: A coluna 'is_active' que não existe na sua tabela
    # is_active = db.Column(Boolean, default=True)

    company = relationship("Company", back_populates="ticker_list")
    metrics = relationship("AssetMetrics", back_populates="ticker_info", uselist=False, cascade="all, delete-orphan")


class AssetMetrics(db.Model):
    __tablename__ = 'asset_metrics'
    
    symbol = db.Column(String(20), ForeignKey('tickers.symbol'), primary_key=True)
    
    # Adicionando mais campos do mt5.symbol_info()
    description = db.Column(Text)
    sector = db.Column(String(255))
    industry = db.Column(String(255))
    
    # Dados de Preço
    last_price = db.Column(Numeric(10, 2))
    previous_close = db.Column(Numeric(10, 2))
    price_change = db.Column(Numeric(10, 2))
    price_change_percent = db.Column(Numeric(10, 4))
    
    # Dados de Volume e OHLC (Open, High, Low, Close) do dia
    volume = db.Column(Numeric(20, 2))
    open_price = db.Column(Numeric(10, 2))
    high_price = db.Column(Numeric(10, 2))
    low_price = db.Column(Numeric(10, 2))

    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

    ticker_info = relationship("Ticker", back_populates="metrics")


class MarketArticle(db.Model):
    __tablename__ = 'artigos_mercado'

    id = db.Column(Integer, primary_key=True)
    titulo = db.Column(String(255), nullable=False)
    link_url = db.Column(String(500))
    portal = db.Column(String(255))
    resumo = db.Column(Text)
    conteudo_completo = db.Column(Text)
    autor = db.Column(String(255))
    data_publicacao = db.Column(DateTime)
    categoria = db.Column(String(255))
    tickers_relacionados = db.Column(JSON)
    score_impacto = db.Column(Numeric(10, 4))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)

    positions = relationship(
        "PortfolioPosition",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

    daily_values = relationship(
        "PortfolioDailyValue",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )


class PortfolioPosition(db.Model):
    __tablename__ = 'portfolio_positions'

    id = db.Column(Integer, primary_key=True)
    portfolio_id = db.Column(Integer, ForeignKey('portfolios.id'), nullable=False, index=True)
    symbol = db.Column(String(20), ForeignKey('tickers.symbol'), nullable=False)
    quantity = db.Column(Numeric(20, 4), nullable=False)
    avg_price = db.Column(Numeric(10, 2), nullable=False)

    portfolio = relationship("Portfolio", back_populates="positions")
    ticker = relationship("Ticker", foreign_keys=[symbol], primaryjoin="PortfolioPosition.symbol == Ticker.symbol")
    metrics = relationship(
        "AssetMetrics",
        foreign_keys=[symbol],
        primaryjoin="PortfolioPosition.symbol == AssetMetrics.symbol",
        viewonly=True,
        uselist=False,
    )


class PortfolioDailyValue(db.Model):
    __tablename__ = 'portfolio_daily_values'

    id = db.Column(Integer, primary_key=True)
    portfolio_id = db.Column(Integer, ForeignKey('portfolios.id'), nullable=False, index=True)
    date = db.Column(Date, nullable=False, server_default=func.current_date())
    total_value = db.Column(Numeric(20, 2), nullable=False)
    total_cost = db.Column(Numeric(20, 2), nullable=False)
    total_gain = db.Column(Numeric(20, 2), nullable=False)
    total_gain_percent = db.Column(Numeric(10, 4), nullable=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    portfolio = relationship("Portfolio", back_populates="daily_values")

    __table_args__ = (
        db.UniqueConstraint('portfolio_id', 'date', name='uix_portfolio_date'),
    )


class ResearchNote(db.Model):
    __tablename__ = 'research_notes'

    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    last_updated = db.Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
