"""
Finance Agent - Financial analysis and reporting
================================================

Specialized agent for:
- Financial analysis
- Budget tracking
- Invoice management
- Financial reporting
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

from .base import BaseAgent, AgentStatus, Permission, Tool


class TransactionType(str, Enum):
    """Financial transaction types."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    REFUND = "refund"


class FinanceAgent(BaseAgent):
    """
    Finance agent for financial analysis and reporting.
    
    Specialized in:
    - Budget management and tracking
    - Invoice and expense management
    - Financial analysis and forecasting
    - Report generation
    
    Model: gemma3:12b (analysis-focused)
    Permission: STANDARD (financial data access)
    """
    
    agent_type = "finance"
    
    FINANCE_SYSTEM_PROMPT = """You are a professional finance agent. Your responsibilities:

1. Track income and expenses accurately
2. Generate financial reports and forecasts
3. Manage budgets and alert on variances
4. Process invoices and payments
5. Ensure compliance with financial policies
6. Provide actionable financial insights

When analyzing finances:
- Be accurate and thorough
- Highlight trends and anomalies
- Provide context for numbers
- Suggest cost-saving opportunities
- Flag potential issues early
- Maintain confidentiality

When generating reports:
- Use clear, professional language
- Include key metrics and KPIs
- Provide actionable recommendations
- Format for readability"""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ):
        if "permission" not in kwargs:
            kwargs["permission"] = Permission.STANDARD
        
        super().__init__(
            agent_id=agent_id,
            name=name or "FinanceAgent",
            **kwargs
        )
        
        self._transactions: List[Dict] = []
        self._budgets: Dict[str, Dict] = {}
        self._invoices: Dict[str, Dict] = {}
        self._register_finance_tools()
    
    def _register_finance_tools(self):
        """Register finance-specific tools."""
        
        self.register_tool(Tool(
            name="record_transaction",
            description="Record a financial transaction",
            func=self._tool_record_transaction,
            parameters={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["income", "expense", "transfer", "refund"]},
                    "amount": {"type": "number"},
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "date": {"type": "string"},
                    "project_id": {"type": "string"},
                },
                "required": ["type", "amount", "category", "description"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="create_budget",
            description="Create or update a budget",
            func=self._tool_create_budget,
            parameters={
                "type": "object",
                "properties": {
                    "budget_name": {"type": "string"},
                    "categories": {"type": "object"},
                    "period": {"type": "string"},
                },
                "required": ["budget_name", "categories"],
            },
            requires_permission=Permission.ELEVATED,
        ))
        
        self.register_tool(Tool(
            name="analyze_spending",
            description="Analyze spending patterns",
            func=self._tool_analyze_spending,
            parameters={
                "type": "object",
                "properties": {
                    "period": {"type": "string"},
                    "category": {"type": "string"},
                    "project_id": {"type": "string"},
                },
                "required": [],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="create_invoice",
            description="Create an invoice",
            func=self._tool_create_invoice,
            parameters={
                "type": "object",
                "properties": {
                    "client": {"type": "string"},
                    "items": {"type": "array"},
                    "due_date": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["client", "items"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="generate_report",
            description="Generate a financial report",
            func=self._tool_generate_report,
            parameters={
                "type": "object",
                "properties": {
                    "report_type": {"type": "string", "enum": ["pnl", "cashflow", "budget_variance", "summary"]},
                    "period": {"type": "string"},
                    "format": {"type": "string", "enum": ["text", "json", "markdown"]},
                },
                "required": ["report_type"],
            },
            requires_permission=Permission.STANDARD,
        ))
    
    # === Tool Implementations ===
    
    async def _tool_record_transaction(
        self,
        type: str,
        amount: float,
        category: str,
        description: str,
        date: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record a financial transaction."""
        import uuid
        
        transaction = {
            "id": str(uuid.uuid4())[:8],
            "type": TransactionType(type),
            "amount": amount,
            "category": category,
            "description": description,
            "date": date or datetime.utcnow().isoformat(),
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._transactions.append(transaction)
        
        self.log("transaction_recorded", {
            "transaction_id": transaction["id"],
            "type": type,
            "amount": amount,
            "category": category,
        })
        
        return {
            "status": "recorded",
            "transaction_id": transaction["id"],
            "transaction": {k: str(v) if isinstance(v, TransactionType) else v 
                          for k, v in transaction.items()},
        }
    
    async def _tool_create_budget(
        self,
        budget_name: str,
        categories: Dict[str, float],
        period: str = "monthly",
    ) -> Dict[str, Any]:
        """Create or update a budget."""
        import uuid
        
        budget_id = str(uuid.uuid4())[:8]
        
        budget = {
            "id": budget_id,
            "name": budget_name,
            "categories": categories,
            "period": period,
            "total": sum(categories.values()),
            "created_at": datetime.utcnow().isoformat(),
            "actuals": {cat: 0.0 for cat in categories},
        }
        
        self._budgets[budget_name] = budget
        
        self.log("budget_created", {"budget_id": budget_id, "name": budget_name, "total": budget["total"]})
        
        return {
            "status": "created",
            "budget_id": budget_id,
            "budget": budget,
        }
    
    async def _tool_analyze_spending(
        self,
        period: Optional[str] = None,
        category: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze spending patterns."""
        # Filter transactions
        filtered = self._transactions.copy()
        
        if category:
            filtered = [t for t in filtered if t["category"] == category]
        
        if project_id:
            filtered = [t for t in filtered if t.get("project_id") == project_id]
        
        # Calculate totals by category
        by_category = {}
        for t in filtered:
            cat = t["category"]
            if cat not in by_category:
                by_category[cat] = {"income": 0, "expense": 0}
            
            if t["type"] == TransactionType.INCOME:
                by_category[cat]["income"] += t["amount"]
            elif t["type"] == TransactionType.EXPENSE:
                by_category[cat]["expense"] += t["amount"]
        
        # Calculate totals
        total_income = sum(t["amount"] for t in filtered if t["type"] == TransactionType.INCOME)
        total_expense = sum(t["amount"] for t in filtered if t["type"] == TransactionType.EXPENSE)
        net = total_income - total_expense
        
        # Top categories by expense
        top_expenses = sorted(
            [(cat, data["expense"]) for cat, data in by_category.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        
        return {
            "period": period,
            "total_transactions": len(filtered),
            "total_income": total_income,
            "total_expense": total_expense,
            "net": net,
            "by_category": by_category,
            "top_expenses": top_expenses,
        }
    
    async def _tool_create_invoice(
        self,
        client: str,
        items: List[Dict[str, Any]],
        due_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an invoice."""
        import uuid
        
        invoice_id = str(uuid.uuid4())[:8].upper()
        invoice_num = f"INV-{datetime.utcnow().strftime('%Y%m')}-{invoice_id}"
        
        # Calculate totals
        subtotal = sum(item.get("quantity", 1) * item.get("price", 0) for item in items)
        
        invoice = {
            "id": invoice_id,
            "invoice_number": invoice_num,
            "client": client,
            "items": items,
            "subtotal": subtotal,
            "total": subtotal,  # Could add tax
            "due_date": due_date,
            "notes": notes,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._invoices[invoice_id] = invoice
        
        self.log("invoice_created", {"invoice_id": invoice_id, "client": client, "total": subtotal})
        
        return {
            "status": "created",
            "invoice_id": invoice_id,
            "invoice_number": invoice_num,
            "invoice": invoice,
        }
    
    async def _tool_generate_report(
        self,
        report_type: str,
        period: Optional[str] = None,
        format: str = "markdown",
    ) -> Dict[str, Any]:
        """Generate a financial report."""
        
        # Get data for report
        analysis = await self._tool_analyze_spending()
        
        if report_type == "pnl":
            report_content = await self._generate_pnl_report(analysis, format)
        elif report_type == "cashflow":
            report_content = await self._generate_cashflow_report(analysis, format)
        elif report_type == "budget_variance":
            report_content = await self._generate_budget_variance_report(format)
        else:
            report_content = await self._generate_summary_report(analysis, format)
        
        return {
            "report_type": report_type,
            "period": period,
            "format": format,
            "content": report_content,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def _generate_pnl_report(self, analysis: Dict, format: str) -> str:
        """Generate profit and loss report."""
        if format == "json":
            return json.dumps(analysis, indent=2)
        
        return f"""# Profit & Loss Report

## Summary

| Metric | Amount |
|--------|--------|
| Total Income | ${analysis['total_income']:,.2f} |
| Total Expenses | ${analysis['total_expense']:,.2f} |
| **Net Profit/Loss** | **${analysis['net']:,.2f}** |

## Expenses by Category

| Category | Amount |
|-----------|--------|
{chr(10).join(f"| {cat} | ${amt:,.2f} |" for cat, amt in analysis['top_expenses'])}

## Analysis

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
    
    async def _generate_cashflow_report(self, analysis: Dict, format: str) -> str:
        """Generate cash flow report."""
        if format == "json":
            return json.dumps(analysis, indent=2)
        
        return f"""# Cash Flow Report

## Cash Flow Summary

- **Inflows**: ${analysis['total_income']:,.2f}
- **Outflows**: ${analysis['total_expense']:,.2f}
- **Net Cash Flow**: ${analysis['net']:,.2f}

## Transaction Count: {analysis['total_transactions']}

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
    
    async def _generate_budget_variance_report(self, format: str) -> str:
        """Generate budget variance report."""
        variances = []
        
        for name, budget in self._budgets.items():
            for category, allocated in budget["categories"].items():
                actual = budget["actuals"].get(category, 0.0)
                variance = allocated - actual
                variance_pct = (variance / allocated * 100) if allocated > 0 else 0
                
                variances.append({
                    "budget": name,
                    "category": category,
                    "allocated": allocated,
                    "actual": actual,
                    "variance": variance,
                    "variance_pct": variance_pct,
                })
        
        if format == "json":
            return json.dumps(variances, indent=2)
        
        lines = ["# Budget Variance Report\n"]
        lines.append("| Budget | Category | Allocated | Actual | Variance | % |")
        lines.append("|--------|-----------|-----------|--------|----------|---|")
        
        for v in variances:
            status = "✓" if v["variance"] >= 0 else "⚠"
            lines.append(f"| {v['budget']} | {v['category']} | ${v['allocated']:,.2f} | ${v['actual']:,.2f} | ${v['variance']:,.2f} | {v['variance_pct']:.1f}% {status} |")
        
        return "\n".join(lines)
    
    async def _generate_summary_report(self, analysis: Dict, format: str) -> str:
        """Generate summary report."""
        if format == "json":
            return json.dumps(analysis, indent=2)
        
        return f"""# Financial Summary

## Overview

- **Income**: ${analysis['total_income']:,.2f}
- **Expenses**: ${analysis['total_expense']:,.2f}
- **Net**: ${analysis['net']:,.2f}

## Top Expense Categories

{chr(10).join(f"- {cat}: ${amt:,.2f}" for cat, amt in analysis['top_expenses'])}

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
    
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
        """Perform a finance task."""
        if task_type == "record_transaction":
            return await self._tool_record_transaction(**payload)
        elif task_type == "create_budget":
            # Map 'name' to 'budget_name' if provided
            if "name" in payload and "budget_name" not in payload:
                payload["budget_name"] = payload.pop("name")
            return await self._tool_create_budget(**payload)
        elif task_type == "analyze_spending":
            return await self._tool_analyze_spending(**payload)
        elif task_type == "create_invoice":
            return await self._tool_create_invoice(**payload)
        elif task_type == "generate_report":
            return await self._tool_generate_report(**payload)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _handle_task_request(self, message) -> Optional[Any]:
        """Handle a task request."""
        from ..protocol.acp import MessageType
        
        task_type = message.subject
        supported = ["record_transaction", "create_budget", "analyze_spending",
                     "create_invoice", "generate_report"]
        
        if task_type not in supported:
            self.bus.reject_task(message, f"Unsupported task: {task_type}")
            return None
        
        self.bus.accept_task(message)
        result = await self.perform_task(task_type, message.body)
        self.bus.complete_task(message, result)
        return result
    
    async def _handle_query(self, message) -> Optional[Any]:
        """Handle a finance query."""
        response = await self.think(
            f"Answer this finance question: {message.subject}",
            system=self.FINANCE_SYSTEM_PROMPT,
        )
        self.bus.respond(message, response)
        return {"answer": response}


def create_finance_agent(**kwargs) -> FinanceAgent:
    """Create a finance agent."""
    return FinanceAgent(**kwargs)