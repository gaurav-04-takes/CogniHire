from sqlalchemy import Column, String, DateTime, Enum, Integer, Boolean, Text, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    doc_type = Column(String, nullable=True) # RESUME or JOB_DESCRIPTION
    classification_confidence = Column(Float, nullable=True)
    classification_status = Column(String, nullable=True) # e.g. "AUTO", "MANUAL"
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentProcessingJobModel(Base):
    __tablename__ = "document_processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, nullable=False, unique=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    chunks_count = Column(Integer, default=0)
    indexed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False) # e.g., "document_uploaded", "query_executed"
    event_data = Column(Text, nullable=True) # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String, nullable=False) # e.g., "retrieval_latency"
    metric_value = Column(Float, nullable=False)
    tags = Column(Text, nullable=True) # JSON string for tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=True)
    query = Column(Text, nullable=True)
    faithfulness_score = Column(Float, nullable=True)
    answer_relevancy_score = Column(Float, nullable=True)
    context_precision_score = Column(Float, nullable=True)
    context_recall_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PromptTrace(Base):
    __tablename__ = "prompt_traces"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_name = Column(String, nullable=False)
    inputs = Column(Text, nullable=True) # JSON string
    output = Column(Text, nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FeedbackRecord(Base):
    __tablename__ = "feedback_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=True)
    response_id = Column(String, nullable=True)
    query = Column(Text, nullable=True)
    score = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
