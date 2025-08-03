"""
Database connection and management for ShadowWall AI
Handles SQLAlchemy setup and database operations
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: str, echo: bool = False):
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        
    async def initialize(self):
        """Initialize database connections and create tables"""
        try:
            # Create synchronous engine
            if self.database_url.startswith('sqlite'):
                # Special handling for SQLite
                self.engine = create_engine(
                    self.database_url,
                    echo=self.echo,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
                
                # For async SQLite
                async_url = self.database_url.replace('sqlite://', 'sqlite+aiosqlite://')
                self.async_engine = create_async_engine(
                    async_url,
                    echo=self.echo,
                    poolclass=StaticPool
                )
            else:
                # PostgreSQL, MySQL, etc.
                self.engine = create_engine(self.database_url, echo=self.echo)
                
                # Convert to async URL
                if 'postgresql://' in self.database_url:
                    async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
                elif 'mysql://' in self.database_url:
                    async_url = self.database_url.replace('mysql://', 'mysql+aiomysql://')
                else:
                    async_url = self.database_url
                
                self.async_engine = create_async_engine(async_url, echo=self.echo)
            
            # Create session factories
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            await self._create_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            # Import models to register them with Base
            from ..models.threat_models import ThreatEvent, IOC, ThreatPattern
            from ..models.honeypot_models import HoneypotEvent, AttackerProfile
            from ..models.network_models import NetworkEvent, ConnectionEvent
            
            # Create tables asynchronously
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session context manager"""
        if not self.AsyncSessionLocal:
            raise RuntimeError("Database not initialized")
        
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    @asynccontextmanager
    async def get_session(self):
        """Get sync database session context manager"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        
        if self.engine:
            self.engine.dispose()
        
        logger.info("Database connections closed")
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
