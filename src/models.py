"""Database models for the ElectionGuard demo."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, Float, Index, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class EventStatus(str, PyEnum):
    """Vote event status enum."""
    INIT = "INIT"
    INVOTING = "INVOTING"
    TALLING = "TALLING"
    END = "END"


class VoteEvent(Base):
    """
    Vote event model storing election details and ElectionGuard cryptographic materials.

    Represents a complete voting event (e.g., "2024 Student Council Election").
    Contains the election manifest, joint public key, and cryptographic context
    required for ElectionGuard encryption and tallying.
    """
    __tablename__ = "vote_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    from_date = Column(DateTime, nullable=False)
    to_date = Column(DateTime, nullable=False)
    status = Column(
        Enum(EventStatus),
        default=EventStatus.INVOTING,
        nullable=False
    )
    allow_vote_candidate_num = Column(Integer, default=1, nullable=False)

    # ElectionGuard specific fields (stored as JSON)
    election_manifest = Column(Text, nullable=True)
    # ElectionGuard Manifest JSON - defines contests, candidates, ballot styles

    joint_public_key = Column(Text, nullable=True)
    # Joint Election Public Key JSON - used to encrypt ballots

    crypto_context = Column(Text, nullable=True)
    # ElectionGuard CryptoContext JSON - cryptographic parameters

    # Tally results
    total_votes = Column(Integer, default=0, nullable=False)
    encrypted_tally = Column(Text, nullable=True)
    # Encrypted tally JSON - homomorphic aggregation of all encrypted ballots

    plaintext_tally = Column(Text, nullable=True)
    # Plaintext tally JSON - decrypted vote counts per candidate

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    end_at = Column(DateTime, nullable=True)
    # Timestamp when event status changed to END

    # Relationships
    candidates = relationship("Candidate", back_populates="event", lazy="select")

    __table_args__ = (
        Index('ix_vote_events_status', 'status'),
    )

    def __repr__(self):
        return f"<VoteEvent(id={self.id}, name='{self.name}', status={self.status})>"


class Candidate(Base):
    """
    Candidate model for each voting event.

    Represents a candidate in a voting event. Multiple candidates belong to one event.
    Vote counts and percentages are populated after tally execution.
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('vote_events.id'), nullable=False)
    name = Column(String(255), nullable=False)

    # Relationships
    event = relationship("VoteEvent", back_populates="candidates")

    # Results after tally (populated after execute-tally-election)
    vote_count = Column(Integer, default=0, nullable=False)
    vote_percentage = Column(Float, default=0.0, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        Index('ix_candidates_event_id', 'event_id'),
        Index('ix_candidates_event_name', 'event_id', 'name', unique=True),
    )

    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', event_id={self.event_id})>"


class Customer(Base):
    """
    Customer (voter) model with simplified authentication.

    Stores voter registration information. For MVP, uses simple UUID-based
    authentication via customer_secret. In production, would integrate with
    proper authentication system.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    # Unique identifier (e.g., email, username) - must be unique

    customer_secret = Column(String(255), unique=True, nullable=False)
    # Secret token (UUID) used for authentication when casting votes

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        Index('ix_customers_unique_id', 'unique_id', unique=True),
        Index('ix_customers_secret', 'customer_secret', unique=True),
    )

    def __repr__(self):
        return f"<Customer(id={self.id}, unique_id='{self.unique_id}')>"


class EventCustomer(Base):
    """
    Event-specific customer registration junction table.

    Links customers to specific voting events they're registered for.
    Allows the same customer (unique_id) to register for multiple events
    while maintaining event-specific registration tracking.
    """
    __tablename__ = "event_customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('vote_events.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    registered_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    event = relationship("VoteEvent")
    customer = relationship("Customer")

    __table_args__ = (
        Index('ix_event_customers_event_id', 'event_id'),
        Index('ix_event_customers_unique', 'event_id', 'customer_id', unique=True),
    )

    def __repr__(self):
        return f"<EventCustomer(id={self.id}, event_id={self.event_id}, customer_id={self.customer_id})>"


class CustomerVote(Base):
    """
    Customer vote record storing encrypted ballots.

    Each record represents one encrypted ballot cast by a customer.
    Contains the ElectionGuard CiphertextBallot, zero-knowledge proofs,
    and a verification code that voters can use to verify their vote.

    The actual ballot content remains encrypted forever - only the aggregated
    tally is decrypted.
    """
    __tablename__ = "customer_votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('vote_events.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)

    # Relationships
    event = relationship("VoteEvent")
    customer = relationship("Customer")

    # ElectionGuard specific fields
    vote_secret = Column(String(255), unique=True, nullable=False)
    # Verification code (e.g., 'COOK-7HMCG-NOTION-9329D') - used by voter to verify their vote

    encrypted_ballot = Column(Text, nullable=False)
    # CiphertextBallot JSON - ElectionGuard encrypted ballot

    ballot_proofs = Column(Text, nullable=False)
    # Zero-knowledge proofs JSON - Chaum-Pedersen proofs, range proofs

    # Vote selections (stored for verification, NOT decrypted from ballot)
    selected_candidate_ids = Column(Text, nullable=False)
    # JSON array of selected candidate IDs - stored separately for verification API

    vote_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        Index('ix_customer_votes_event_customer', 'event_id', 'customer_id', unique=True),
        Index('ix_customer_votes_vote_secret', 'vote_secret', unique=True),
        Index('ix_customer_votes_event_id', 'event_id'),
    )

    def __repr__(self):
        return f"<CustomerVote(id={self.id}, event_id={self.event_id}, customer_id={self.customer_id})>"
