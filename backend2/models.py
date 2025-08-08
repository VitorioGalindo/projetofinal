from backend.database import db  # ✅ CORRIGIDO: Usar mesma instância
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime

# Baseado em scraper/models.py, mas integrado à nossa aplicação

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(Integer, primary_key=True)
    cvm_code = db.Column(Integer, nullable=False)
    company_name = db.Column(String(255), nullable=False)
    trade_name = db.Column(String(255))
    cnpj = db.Column(String(20))
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
    tickers = db.Column(JSON)
    ticker = db.Column(String(10))
    is_active = db.Column(Boolean)
    industry_classification = db.Column(String(255))
    market_cap = db.Column(Float)
    employee_count = db.Column(Integer)
    about = db.Column(Text)
    has_dfp_data = db.Column(Boolean)
    has_itr_data = db.Column(Boolean)
    has_fre_data = db.Column(Boolean)
    last_dfp_year = db.Column(Integer)
    last_itr_quarter = db.Column(String(10))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow)
    activity_description = db.Column(Text)
    capital_structure_summary = db.Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cvm_code': self.cvm_code,
            'company_name': self.company_name,
            'trade_name': self.trade_name,
            'cnpj': self.cnpj,
            'founded_date': self.founded_date.isoformat() if self.founded_date else None,
            'main_activity': self.main_activity,
            'website': self.website,
            'controlling_interest': self.controlling_interest,
            'is_state_owned': self.is_state_owned,
            'is_foreign': self.is_foreign,
            'is_b3_listed': self.is_b3_listed,
            'b3_issuer_code': self.b3_issuer_code,
            'b3_listing_segment': self.b3_listing_segment,
            'b3_sector': self.b3_sector,
            'b3_subsector': self.b3_subsector,
            'b3_segment': self.b3_segment,
            'tickers': self.tickers,
            'ticker': self.ticker,
            'is_active': self.is_active,
            'industry_classification': self.industry_classification,
            'market_cap': self.market_cap,
            'employee_count': self.employee_count,
            'about': self.about,
            'has_dfp_data': self.has_dfp_data,
            'has_itr_data': self.has_itr_data,
            'has_fre_data': self.has_fre_data,
            'last_dfp_year': self.last_dfp_year,
            'last_itr_quarter': self.last_itr_quarter,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'activity_description': self.activity_description,
            'capital_structure_summary': self.capital_structure_summary
        }

class Ticker(db.Model):
    __tablename__ = 'tickers'
    id = db.Column(Integer, primary_key=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False)
    ticker = db.Column(String(10), nullable=False, index=True)
    ticker_type = db.Column(String(50))
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com Company
    company = relationship("Company", backref="ticker_list")
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'ticker': self.ticker,
            'ticker_type': self.ticker_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CVMFinancialData(db.Model):
    __tablename__ = 'cvm_financial_data'
    id = db.Column(Integer, primary_key=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False)
    cvm_code = db.Column(Integer, nullable=False, index=True)
    statement_type = db.Column(String(10), nullable=False)
    year = db.Column(Integer, nullable=False)
    quarter = db.Column(String(10))
    revenue = db.Column(Float)
    net_income = db.Column(Float)
    total_assets = db.Column(Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'cvm_code': self.cvm_code,
            'statement_type': self.statement_type,
            'year': self.year,
            'quarter': self.quarter,
            'revenue': self.revenue,
            'net_income': self.net_income,
            'total_assets': self.total_assets
        }

class CvmDocument(db.Model):
    __tablename__ = 'cvm_documents'
    id = db.Column(Integer, primary_key=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False)
    document_type = db.Column(String(50))
    document_subtype = db.Column(String(50))
    reference_date = db.Column(DateTime)
    delivery_date = db.Column(DateTime)
    version = db.Column(String(20))
    category = db.Column(String(100))
    document_status = db.Column(String(50))
    receipt_number = db.Column(String(50))
    protocol_number = db.Column(String(50))
    document_url = db.Column(String(500))
    file_name = db.Column(String(255))
    file_size = db.Column(Integer)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com Company
    company = relationship("Company", backref="documents")
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'document_type': self.document_type,
            'document_subtype': self.document_subtype,
            'reference_date': self.reference_date.isoformat() if self.reference_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'version': self.version,
            'category': self.category,
            'document_status': self.document_status,
            'receipt_number': self.receipt_number,
            'protocol_number': self.protocol_number,
            'document_url': self.document_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FinancialStatement(db.Model):
    __tablename__ = 'financial_statements'
    id = db.Column(Integer, primary_key=True)
    company_id = db.Column(Integer, ForeignKey('companies.id'), nullable=False)
    statement_type = db.Column(String(50), nullable=False)
    period_type = db.Column(String(20))
    year = db.Column(Integer, nullable=False)
    quarter = db.Column(String(10))
    reference_date = db.Column(DateTime)
    currency = db.Column(String(10), default='BRL')
    scale_factor = db.Column(Integer, default=1000)
    
    # Dados financeiros principais
    revenue = db.Column(Float)
    gross_profit = db.Column(Float)
    operating_income = db.Column(Float)
    net_income = db.Column(Float)
    total_assets = db.Column(Float)
    total_liabilities = db.Column(Float)
    shareholders_equity = db.Column(Float)
    cash_and_equivalents = db.Column(Float)
    
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com Company
    company = relationship("Company", backref="financial_statements")
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'statement_type': self.statement_type,
            'period_type': self.period_type,
            'year': self.year,
            'quarter': self.quarter,
            'reference_date': self.reference_date.isoformat() if self.reference_date else None,
            'currency': self.currency,
            'scale_factor': self.scale_factor,
            'revenue': self.revenue,
            'gross_profit': self.gross_profit,
            'operating_income': self.operating_income,
            'net_income': self.net_income,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'shareholders_equity': self.shareholders_equity,
            'cash_and_equivalents': self.cash_and_equivalents,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
