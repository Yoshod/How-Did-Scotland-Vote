# Results Dataclass

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Results:
    yes_count: int
    no_count: int
    abstain_count: int
    total_votes: int
    scot_pass: bool
    agreement: bool
    vote_percentage: int
    yes_percentage: int
    no_percentage: int
    abstain_percentage: int
