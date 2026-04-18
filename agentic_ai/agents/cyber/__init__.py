"""
Cyber Division - Offensive & Defensive Security Agents
========================================================

This package contains security-focused agents for both defensive (Blue Team)
and offensive (Red Team) operations.

Agents:
- SecurityOperationsAgent: SOC automation, incident response
- VulnerabilityManagementAgent: Scanning, patch management
- RedTeamAgent: Penetration testing, adversary emulation
- MalwareAnalysisAgent: Reverse engineering, threat intel
- KaliAgent: Kali Linux tool orchestration (600+ tools)
- CloudSecurityAgent: Multi-cloud CSPM
- SecurityAgent: Threat detection, code scanning
"""

from agentic_ai.agents.cyber.soc import SecurityOperationsAgent
from agentic_ai.agents.cyber.vulnman import VulnerabilityManagementAgent
from agentic_ai.agents.cyber.redteam import RedTeamAgent
from agentic_ai.agents.cyber.malware import MalwareAnalysisAgent
from agentic_ai.agents.cyber.kali import KaliAgent

__all__ = [
    # Blue Team
    'SecurityOperationsAgent',
    'VulnerabilityManagementAgent',
    
    # Red Team
    'RedTeamAgent',
    'MalwareAnalysisAgent',
    'KaliAgent',
]
