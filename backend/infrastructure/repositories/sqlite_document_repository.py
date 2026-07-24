import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from backend.core.domain.document import DocumentRecord, DocumentStatus, DocumentType
from backend.core.interfaces.document_repository import IDocumentRepository

class SQLiteDocumentRepository(IDocumentRepository):
    def __init__(self, db_path: str = "documents.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    document_type TEXT,
                    status TEXT,
                    uploaded_at TEXT,
                    chunk_count INTEGER,
                    error_message TEXT
                )
            """)
            conn.commit()

    def _row_to_record(self, row) -> DocumentRecord:
        return DocumentRecord(
            id=row[0],
            filename=row[1],
            document_type=DocumentType(row[2]) if row[2] else DocumentType.UNKNOWN,
            status=DocumentStatus(row[3]) if row[3] else DocumentStatus.UPLOADED,
            uploaded_at=datetime.fromisoformat(row[4]) if row[4] else datetime.utcnow(),
            chunk_count=row[5] or 0,
            error_message=row[6]
        )

    def save(self, record: DocumentRecord) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, filename, document_type, status, uploaded_at, chunk_count, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.filename,
                record.document_type.value,
                record.status.value,
                record.uploaded_at.isoformat(),
                record.chunk_count,
                record.error_message
            ))
            conn.commit()

    def get(self, document_id: str) -> Optional[DocumentRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
        return None

    def get_all(self) -> List[DocumentRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def delete(self, document_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            conn.commit()
