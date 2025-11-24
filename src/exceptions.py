"""Custom exception classes for domain errors."""


class DomainException(Exception):
    """Base exception for all domain errors."""
    pass


class EventNotFoundException(DomainException):
    """Raised when a vote event is not found."""
    pass


class CustomerNotFoundException(DomainException):
    """Raised when a customer is not found."""
    pass


class InvalidCustomerSecretException(DomainException):
    """Raised when customer secret is invalid."""
    pass


class AlreadyVotedException(DomainException):
    """Raised when customer has already voted in an event."""
    pass


class InvalidSelectionCountException(DomainException):
    """Raised when selection count doesn't match event requirements."""
    pass


class EventNotActiveException(DomainException):
    """Raised when event is not in active voting state."""
    pass


class VoteNotFoundException(DomainException):
    """Raised when a vote is not found."""
    pass


class DuplicateCustomerException(DomainException):
    """Raised when customer with unique_id already exists."""
    pass


class InvalidCandidatesException(DomainException):
    """Raised when selected candidates are invalid for the event."""
    pass


class InvalidEventStateException(DomainException):
    """Raised when event is in an invalid state for the requested operation."""
    pass


class CustomerAlreadyExistsException(DomainException):
    """Raised when customer with unique_id already exists."""
    pass


class InvalidVoteSelectionException(DomainException):
    """Raised when vote selection is invalid."""
    pass
