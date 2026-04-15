"""
Agentic AI Consensus Module
============================

Consensus mechanisms for multi-agent decision making.
"""

from .engine import ConsensusEngine
from .proposal import Proposal, Vote, VoteOption, ConsensusResult

__all__ = [
    'ConsensusEngine',
    'Proposal',
    'Vote',
    'VoteOption',
    'ConsensusResult',
]
