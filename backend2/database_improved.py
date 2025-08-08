"""
Database manager melhorado com pool de conexões e retry logic
"""
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DisconnectionError
import os
import logging
import time
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connection_retries = 3
        self.retry_delay = 2
        self.is_healthy = False
        self.initialize_database()
    
    def initialize_database(self):
        """Inicializa conexão com pool de conexões e retry logic"""
        try:
            database_url = self.get_database_url()
            logger.info(f"🔄 Conectando ao PostgreSQL: {self.mask_password(database_url)}")
            
            # Pool de conexões otimizado
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=5,  # Reduzido para evitar limite de conexões
                max_overflow=10,
                pool_pre_ping=True,  # Verifica conexões antes de usar
                pool_recycle=3600,   # Recicla conexões a cada hora
                pool_timeout=30,     # Timeout para obter conexão do pool
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "finance_dashboard",
                    "options": "-c statement_timeout=30000"  # 30s timeout para queries
                },
                echo=False  # Desabilitar logs SQL em produção
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Testar conexão com retry
            self.test_connection_with_retry()
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
            self.engine = None
            self.SessionLocal = None
            self.is_healthy = False
    
    def test_connection_with_retry(self):
        """Testa conexão com retry logic"""
        for attempt in range(self.connection_retries):
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT 1 as test"))
                    test_value = result.scalar()
                    if test_value == 1:
                        logger.info("✅ Conexão PostgreSQL estabelecida com sucesso")
                        self.is_healthy = True
                        return True
                        
            except (OperationalError, DisconnectionError) as e:
                logger.warning(f"⚠️ Tentativa {attempt + 1}/{self.connection_retries} falhou: {e}")
                if attempt < self.connection_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("❌ Todas as tentativas de conexão falharam")
                    self.is_healthy = False
                    
        return False
    
    def get_database_url(self):
        """Constrói URL do banco a partir das variáveis de ambiente"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        name = os.getenv('DB_NAME', 'postgres')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        if not all([host, port, name, user, password]):
            logger.warning("⚠️ Variáveis de ambiente do banco não configuradas completamente")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    def mask_password(self, url: str) -> str:
        """Mascara a senha na URL para logs"""
        if '@' in url and ':' in url:
            parts = url.split('@')
            if len(parts) == 2:
                user_pass = parts[0].split('//')[-1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    return url.replace(user_pass, f"{user}:****")
        return url
    
    @contextmanager
    def get_session(self):
        """Context manager para sessões do banco com retry"""
        session = None
        try:
            if not self.SessionLocal:
                self.initialize_database()
            
            if self.SessionLocal:
                session = self.SessionLocal()
                yield session
            else:
                logger.error("❌ Não foi possível criar sessão do banco")
                yield None
                
        except (OperationalError, DisconnectionError) as e:
            logger.error(f"❌ Erro de conexão na sessão: {e}")
            # Tentar reconectar
            self.initialize_database()
            yield None
            
        except Exception as e:
            logger.error(f"❌ Erro na sessão do banco: {e}")
            if session:
                session.rollback()
            yield None
            
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    logger.error(f"❌ Erro ao fechar sessão: {e}")
    
    def get_session_direct(self):
        """Retorna sessão direta (para compatibilidade com código existente)"""
        try:
            if not self.SessionLocal:
                self.initialize_database()
            
            if self.SessionLocal:
                return self.SessionLocal()
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao criar sessão direta: {e}")
            return None
    
    def health_check(self) -> dict:
        """Verifica saúde da conexão com o banco"""
        try:
            if not self.engine:
                return {
                    'status': 'unhealthy',
                    'error': 'Engine não inicializado',
                    'connected': False
                }
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                
                # Verificar estatísticas do pool
                pool = self.engine.pool
                pool_status = {
                    'size': pool.size(),
                    'checked_in': pool.checkedin(),
                    'checked_out': pool.checkedout(),
                    'overflow': pool.overflow(),
                    'invalid': pool.invalid()
                }
                
                self.is_healthy = True
                return {
                    'status': 'healthy',
                    'connected': True,
                    'version': version,
                    'pool_status': pool_status
                }
                
        except Exception as e:
            logger.error(f"❌ Health check falhou: {e}")
            self.is_healthy = False
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connected': False
            }
    
    def execute_query_safe(self, query: str, params: dict = None):
        """Executa query com tratamento de erro e retry"""
        for attempt in range(self.connection_retries):
            try:
                with self.get_session() as session:
                    if session:
                        if params:
                            result = session.execute(text(query), params)
                        else:
                            result = session.execute(text(query))
                        session.commit()
                        return result
                        
            except Exception as e:
                logger.error(f"❌ Erro na query (tentativa {attempt + 1}): {e}")
                if attempt < self.connection_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise e
        
        return None
    
    def is_database_healthy(self) -> bool:
        """Retorna status de saúde do banco"""
        return self.is_healthy
    
    def reconnect(self):
        """Força reconexão com o banco"""
        logger.info("🔄 Forçando reconexão com o banco...")
        if self.engine:
            self.engine.dispose()
        self.initialize_database()
    
    def close_all_connections(self):
        """Fecha todas as conexões do pool"""
        if self.engine:
            self.engine.dispose()
            logger.info("🔌 Todas as conexões do pool foram fechadas")

# Instância global melhorada
db_manager = DatabaseManager()

# Função de compatibilidade para código existente
def get_db_session():
    """Função de compatibilidade para código existente"""
    return db_manager.get_session_direct()

# Context manager para uso moderno
def get_db():
    """Context manager para uso moderno"""
    return db_manager.get_session()

