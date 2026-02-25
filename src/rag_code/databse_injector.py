import os
from dotenv import load_dotenv
import logging
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_dir = Path(__file__).resolve().parent.parent / "logs"

# Ensure the logs directory exists
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_dir / f"Database_Injector_log_{log_timestamp}.txt"
)
logger = logging.getLogger(__name__)

_=load_dotenv()

class DATABASEINJECTOR:
    def __init__(self, config):
        self.host = os.getenv("DATABASE_HOST")
        self.port=os.getenv("DATABASE_PORT")
        self.database=os.getenv("DATABASE_NAME")
        self.user=os.getenv("DATABASE_USER")
        self.password=os.getenv("DATABASE_PASSWORD")
        self.conn = None
        self._connect()
        self._ensure_extensions()
        self._create_schema()
    def _connect(self):
        """Connect to PostgreSQL database."""
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.conn.autocommit = True
    def _ensure_extensions(self):
        """Ensure pgvector extension is installed."""
        if not self.conn:
            logger.error("[ERROR] Database connection Not Established.")
        else:
            with self.conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    def _create_schema(self):
        """Create database schema."""
        if not self.conn:
            logger.error("[ERROR] Database connection Not Established.")
        else:
            with self.conn.cursor() as cur:
                # NOTE: Do NOT drop tables on initialization - this causes data loss!
                # Tables should only be dropped manually when needed for a fresh start.
                # Only create tables if they don't exist
                # Create teststep_chunks table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS {table_chunks} (
                        chunk_id SERIAL PRIMARY KEY,
                        parent_testcase_id VARCHAR(255),
                        original_chunk TEXT NOT NULL,
                        normalized_chunk TEXT NOT NULL,
                        action_verb VARCHAR(100),
                        primary_object VARCHAR(255),
                        placeholders JSONB,
                        embedding vector(%s),
                        cluster_id INTEGER,
                        chunk_index INTEGER,
                        normalization_version VARCHAR(10),
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """.format(table_chunks=self.table_chunks), (self.config.embedding.dim,))
                
                # Create HNSW index for teststep_chunks
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_{table_chunks}_embedding 
                    ON {table_chunks} 
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64);
                """.format(table_chunks=self.table_chunks))
                
                # Create indexes for joins
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_{table_chunks}_cluster_id 
                    ON {table_chunks}(cluster_id);
                """.format(table_chunks=self.table_chunks))
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_{table_chunks}_parent_id 
                    ON {table_chunks}(parent_testcase_id);
                """.format(table_chunks=self.table_chunks))