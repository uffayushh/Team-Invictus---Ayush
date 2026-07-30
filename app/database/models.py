
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, ForeignKey, TIMESTAMP, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


def gen_uuid():
    return uuid.uuid4()


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True)  
    display_name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    papers = relationship("Paper", back_populates="owner")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    title = Column(Text)
    source_type = Column(String)          # 'upload' | 'arxiv'
    source_url = Column(Text)
    file_path = Column(Text)              # storage path to raw PDF
    status = Column(String, default="pending")
    # pending | parsing | embedding | extracting | ready | failed
    current_step = Column(String, nullable=True)   # fine-grained status (Mistake #14)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    owner = relationship("Profile", back_populates="papers")
    sections = relationship("PaperSection", back_populates="paper", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="paper", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="paper", cascade="all, delete-orphan")


class PaperSection(Base):
    __tablename__ = "paper_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"))
    heading = Column(Text)
    section_order = Column(Integer)
    raw_text = Column(Text)

    paper = relationship("Paper", back_populates="sections")
    chunks = relationship("Chunk", back_populates="section")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"))
    section_id = Column(UUID(as_uuid=True), ForeignKey("paper_sections.id"), nullable=True)
    chunk_index = Column(Integer)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    vector_id = Column(String)   # id of this chunk's vector inside Chroma

    paper = relationship("Paper", back_populates="chunks")
    section = relationship("PaperSection", back_populates="chunks")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"))
    claim_type = Column(String)   # finding | limitation | future_work | contribution | metric
    text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    paper = relationship("Paper", back_populates="claims")
    citations = relationship("Citation", back_populates="claim", cascade="all, delete-orphan")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"))
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id"))
    similarity_score = Column(String, nullable=True)   # cosine sim at retrieval time
    entailment_score = Column(String, nullable=True)   # grounding-check score (Mistake #4)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    claim = relationship("Claim", back_populates="citations")
    chunk = relationship("Chunk") 


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"))
    job_type = Column(String)     # e.g. "process_paper"
    status = Column(String, default="pending")   # pending | running | done | failed
    current_step = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String)   # 'user' | 'assistant'
    content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class GeneratedOutput(Base):
    __tablename__ = "generated_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"))
    output_type = Column(String)   # 'flashcards' | 'slides' | 'concept_map'
    file_path = Column(Text, nullable=True)   # for flashcards/slides
    data = Column(Text, nullable=True)        # JSON blob, for concept_map
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())