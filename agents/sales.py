"""
Sales Agent - CRM and customer relations
==========================================

Specialized agent for:
- Customer relationship management
- Sales pipeline tracking
- Lead qualification
- Proposal generation
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

from .base import BaseAgent, AgentStatus, Permission, Tool


class SalesAgent(BaseAgent):
    """
    Sales agent for CRM and customer relations.
    
    Specialized in:
    - Lead management and qualification
    - Sales pipeline tracking
    - Proposal and quote generation
    - Customer communication
    
    Model: gemma3:12b (communication-focused)
    Permission: STANDARD (CRM access)
    """
    
    agent_type = "sales"
    
    SALES_SYSTEM_PROMPT = """You are a professional sales agent. Your responsibilities:

1. Manage customer relationships professionally
2. Track leads through the sales pipeline
3. Qualify leads based on budget, authority, need, timeline (BANT)
4. Generate accurate proposals and quotes
5. Maintain CRM data quality
6. Follow up with prospects appropriately

When communicating with customers:
- Be professional and courteous
- Focus on solving customer problems
- Provide accurate information
- Never pressure or manipulate
- Respect customer timelines

When qualifying leads:
- Assess budget availability
- Identify decision makers
- Understand actual needs
- Determine purchase timeline"""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        crm_path: Optional[str] = None,
        **kwargs
    ):
        if "permission" not in kwargs:
            kwargs["permission"] = Permission.STANDARD
        
        super().__init__(
            agent_id=agent_id,
            name=name or "SalesAgent",
            **kwargs
        )
        
        self.crm_path = Path(crm_path) if crm_path else None
        self._leads: Dict[str, Dict] = {}
        self._opportunities: Dict[str, Dict] = {}
        self._register_sales_tools()
    
    def _register_sales_tools(self):
        """Register sales-specific tools."""
        
        self.register_tool(Tool(
            name="create_lead",
            description="Create a new lead in CRM",
            func=self._tool_create_lead,
            parameters={
                "type": "object",
                "properties": {
                    "lead_name": {"type": "string"},
                    "company": {"type": "string"},
                    "email": {"type": "string"},
                    "source": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["lead_name", "company", "email"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="qualify_lead",
            description="Qualify a lead using BANT criteria",
            func=self._tool_qualify_lead,
            parameters={
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "budget": {"type": "string"},
                    "authority": {"type": "string"},
                    "need": {"type": "string"},
                    "timeline": {"type": "string"},
                },
                "required": ["lead_id"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="create_opportunity",
            description="Create a sales opportunity from qualified lead",
            func=self._tool_create_opportunity,
            parameters={
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "value": {"type": "number"},
                    "products": {"type": "array", "items": {"type": "string"}},
                    "expected_close": {"type": "string"},
                },
                "required": ["lead_id", "value"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="generate_proposal",
            description="Generate a proposal document",
            func=self._tool_generate_proposal,
            parameters={
                "type": "object",
                "properties": {
                    "opportunity_id": {"type": "string"},
                    "template": {"type": "string"},
                    "custom_terms": {"type": "object"},
                },
                "required": ["opportunity_id"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="update_pipeline",
            description="Update opportunity pipeline stage",
            func=self._tool_update_pipeline,
            parameters={
                "type": "object",
                "properties": {
                    "opportunity_id": {"type": "string"},
                    "stage": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["opportunity_id", "stage"],
            },
            requires_permission=Permission.STANDARD,
        ))
    
    # === Tool Implementations ===
    
    async def _tool_create_lead(
        self,
        lead_name: str,
        company: str,
        email: str,
        source: str = "unknown",
        notes: str = "",
    ) -> Dict[str, Any]:
        """Create a new lead."""
        import uuid
        
        lead_id = str(uuid.uuid4())[:8]
        
        lead = {
            "id": lead_id,
            "name": lead_name,
            "company": company,
            "email": email,
            "source": source,
            "notes": notes,
            "status": "new",
            "created_at": datetime.utcnow().isoformat(),
            "qualified": False,
        }
        
        self._leads[lead_id] = lead
        
        self.log("lead_created", {"lead_id": lead_id, "company": company})
        
        return {
            "status": "created",
            "lead_id": lead_id,
            "lead": lead,
        }
    
    async def _tool_qualify_lead(
        self,
        lead_id: str,
        budget: str = "",
        authority: str = "",
        need: str = "",
        timeline: str = "",
    ) -> Dict[str, Any]:
        """Qualify a lead using BANT."""
        if lead_id not in self._leads:
            return {"error": f"Lead not found: {lead_id}"}
        
        lead = self._leads[lead_id]
        
        # BANT scoring
        scores = {
            "budget": bool(budget),
            "authority": bool(authority),
            "need": bool(need),
            "timeline": bool(timeline),
        }
        
        qualified = all(scores.values())
        
        lead["qualified"] = qualified
        lead["qualification"] = {
            "budget": budget,
            "authority": authority,
            "need": need,
            "timeline": timeline,
            "scores": scores,
            "qualified": qualified,
        }
        lead["status"] = "qualified" if qualified else "disqualified"
        
        self.log("lead_qualified", {"lead_id": lead_id, "qualified": qualified})
        
        return {
            "lead_id": lead_id,
            "qualified": qualified,
            "scores": scores,
            "details": lead["qualification"],
        }
    
    async def _tool_create_opportunity(
        self,
        lead_id: str,
        value: float,
        products: Optional[List[str]] = None,
        expected_close: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a sales opportunity."""
        import uuid
        
        if lead_id not in self._leads:
            return {"error": f"Lead not found: {lead_id}"}
        
        lead = self._leads[lead_id]
        
        if not lead.get("qualified"):
            return {"error": "Lead must be qualified first"}
        
        opp_id = str(uuid.uuid4())[:8]
        
        opportunity = {
            "id": opp_id,
            "lead_id": lead_id,
            "company": lead["company"],
            "contact": lead["name"],
            "value": value,
            "products": products or [],
            "stage": "proposal",
            "expected_close": expected_close,
            "created_at": datetime.utcnow().isoformat(),
            "history": [],
        }
        
        self._opportunities[opp_id] = opportunity
        
        self.log("opportunity_created", {"opp_id": opp_id, "value": value})
        
        return {
            "status": "created",
            "opportunity_id": opp_id,
            "opportunity": opportunity,
        }
    
    async def _tool_generate_proposal(
        self,
        opportunity_id: str,
        template: str = "standard",
        custom_terms: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate a proposal document."""
        if opportunity_id not in self._opportunities:
            return {"error": f"Opportunity not found: {opportunity_id}"}
        
        opp = self._opportunities[opportunity_id]
        
        prompt = f"""Generate a professional sales proposal for:

Company: {opp['company']}
Contact: {opp['contact']}
Products/Services: {', '.join(opp['products']) if opp['products'] else 'Custom solution'}
Value: ${opp['value']:,.2f}
Expected Close: {opp['expected_close'] or 'TBD'}

Include:
1. Executive Summary
2. Problem Statement
3. Proposed Solution
4. Pricing
5. Timeline
6. Terms and Conditions

Make it professional and compelling."""

        proposal = await self.think(prompt, system=self.SALES_SYSTEM_PROMPT)
        
        opp["history"].append({
            "action": "proposal_generated",
            "template": template,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return {
            "opportunity_id": opportunity_id,
            "proposal": proposal,
            "template": template,
        }
    
    async def _tool_update_pipeline(
        self,
        opportunity_id: str,
        stage: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Update opportunity pipeline stage."""
        valid_stages = [
            "proposal", "negotiation", "verbal_commit",
            "contract_sent", "closed_won", "closed_lost",
        ]
        
        if stage not in valid_stages:
            return {"error": f"Invalid stage: {stage}. Valid stages: {valid_stages}"}
        
        if opportunity_id not in self._opportunities:
            return {"error": f"Opportunity not found: {opportunity_id}"}
        
        opp = self._opportunities[opportunity_id]
        old_stage = opp["stage"]
        opp["stage"] = stage
        opp["history"].append({
            "action": "stage_change",
            "from": old_stage,
            "to": stage,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        self.log("pipeline_updated", {
            "opportunity_id": opportunity_id,
            "old_stage": old_stage,
            "new_stage": stage,
        })
        
        return {
            "opportunity_id": opportunity_id,
            "old_stage": old_stage,
            "new_stage": stage,
            "notes": notes,
        }
    
    # === Task Handlers ===
    
    async def process_message(self, message) -> Optional[Any]:
        """Process an incoming message."""
        from ..protocol.acp import MessageType
        
        if message.type == MessageType.TASK_REQUEST:
            return await self._handle_task_request(message)
        elif message.type == MessageType.QUERY:
            return await self._handle_query(message)
        
        return None
    
    async def perform_task(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a sales task."""
        if task_type == "create_lead":
            # Map 'name' to 'lead_name' if provided
            if "name" in payload and "lead_name" not in payload:
                payload["lead_name"] = payload.pop("name")
            return await self._tool_create_lead(**payload)
        elif task_type == "qualify_lead":
            return await self._tool_qualify_lead(**payload)
        elif task_type == "create_opportunity":
            return await self._tool_create_opportunity(**payload)
        elif task_type == "generate_proposal":
            return await self._tool_generate_proposal(**payload)
        elif task_type == "update_pipeline":
            return await self._tool_update_pipeline(**payload)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _handle_task_request(self, message) -> Optional[Any]:
        """Handle a task request."""
        from ..protocol.acp import MessageType
        
        task_type = message.subject
        supported = ["create_lead", "qualify_lead", "create_opportunity",
                     "generate_proposal", "update_pipeline"]
        
        if task_type not in supported:
            self.bus.reject_task(message, f"Unsupported task: {task_type}")
            return None
        
        self.bus.accept_task(message)
        result = await self.perform_task(task_type, message.body)
        self.bus.complete_task(message, result)
        return result
    
    async def _handle_query(self, message) -> Optional[Any]:
        """Handle a query about sales."""
        response = await self.think(
            f"Answer this sales question: {message.subject}",
            system=self.SALES_SYSTEM_PROMPT,
        )
        self.bus.respond(message, response)
        return {"answer": response}


def create_sales_agent(**kwargs) -> SalesAgent:
    """Create a sales agent."""
    return SalesAgent(**kwargs)