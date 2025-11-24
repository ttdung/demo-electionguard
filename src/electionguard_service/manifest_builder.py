"""
ElectionGuard Manifest Builder.

Creates an ElectionGuard Manifest from voting event details.
The Manifest defines the election structure: contests, candidates, and ballot styles.
"""
import logging
from typing import List, Optional
from datetime import datetime, timezone
from electionguard.manifest import (
    Manifest,
    InternationalizedText,
    Language,
    GeopoliticalUnit,
    ReportingUnitType,
    ContestDescription,
    SelectionDescription,
    VoteVariationType,
    BallotStyle,
    ElectionType,
)

logger = logging.getLogger(__name__)


def build_manifest(
    event_id: int,
    event_name: str,
    candidate_names: List[str],
    allow_vote_candidate_num: int = 1,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Manifest:
    """
    Build an ElectionGuard Manifest for a voting event.

    Args:
        event_id: Unique event identifier
        event_name: Name of the election event
        candidate_names: List of candidate names
        allow_vote_candidate_num: Number of candidates voters can select (default: 1)
        start_date: Election start date (default: now)
        end_date: Election end date (default: 24 hours from now)

    Returns:
        Manifest: ElectionGuard Manifest object

    Example:
        >>> manifest = build_manifest(
        ...     event_id=1,
        ...     event_name="2024 Student Council",
        ...     candidate_names=["Alice", "Bob", "Carol"],
        ...     allow_vote_candidate_num=1
        ... )
    """
    logger.info(f"Building manifest for event: {event_name} (ID: {event_id})")

    # Set default dates if not provided
    if start_date is None:
        start_date = datetime.now(timezone.utc)
    if end_date is None:
        end_date = datetime.now(timezone.utc)  # Will be overridden by VoteEvent dates

    # Create geopolitical unit (represents the voting jurisdiction)
    gp_unit = GeopoliticalUnit(
        object_id=f"gp-unit-{event_id}",
        name=event_name,
        type=ReportingUnitType.county,  # Using county as generic jurisdiction
    )

    # Create candidate selections
    selections = []
    for idx, candidate_name in enumerate(candidate_names):
        selection = SelectionDescription(
            object_id=f"candidate-{event_id}-{idx}",
            candidate_id=f"candidate-{event_id}-{idx}",
            sequence_order=idx,
        )
        selections.append(selection)

    logger.info(f"Created {len(selections)} candidate selections")

    # Create contest description
    contest = ContestDescription(
        object_id=f"contest-{event_id}",
        electoral_district_id=gp_unit.object_id,
        sequence_order=0,
        vote_variation=VoteVariationType.n_of_m,  # Select N out of M candidates
        number_elected=allow_vote_candidate_num,  # How many can be selected
        votes_allowed=allow_vote_candidate_num,   # Same as number_elected for n-of-m
        name=event_name,
        ballot_selections=selections,
    )

    # Create ballot style (defines which contests appear on the ballot)
    ballot_style = BallotStyle(
        object_id=f"ballot-style-{event_id}",
        geopolitical_unit_ids=[gp_unit.object_id],
        party_ids=None,  # No party affiliation for this demo
        image_uri=None,
    )

    # Create the complete manifest
    manifest = Manifest(
        election_scope_id=f"election-{event_id}",
        spec_version="1.0",
        type=ElectionType.general,  # General election type (enum)
        start_date=start_date,
        end_date=end_date,
        geopolitical_units=[gp_unit],
        parties=[],  # No parties for simplified demo
        candidates=[],  # Candidates are defined in selections
        contests=[contest],
        ballot_styles=[ballot_style],
        name=InternationalizedText(
            text=[Language(value=event_name, language="en")]
        ),
        contact_information=None,
    )

    logger.info(f"Manifest created successfully for event {event_id}")
    return manifest
