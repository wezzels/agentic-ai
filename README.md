# Agentic AI System

A multi-agent orchestration framework built on the Agent Communication Protocol (ACP) with Redis messaging, SQLite state persistence, and Ollama inference.

## Status: Phase 1-4 Complete ✅

| Phase | Status | Tests | Description |
|-------|--------|-------|-------------|
| Phase 1: Infrastructure | ✅ Complete | 17/17 | Inference, state, protocol, base agent |
| Phase 2: Developer + QA | ✅ Complete | 34/34 | Code implementation & quality assurance |
| Phase 3: Business Agents | ✅ Complete | 51/51 | Sales, Finance, SysAdmin |
| Phase 4: Lead Agent | ✅ Complete | 68/68 | Orchestration & workflow coordination |
| **Phase 5: Integration** | 🔄 In Progress | 68/68 | E2E tests & documentation |

## Quick Start

```bash
cd ~/stsgym-work/agentic_ai
source venv/bin/activate
python -m pytest tests/ -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agentic AI System                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Developer    │  │    QA       │  │   Sales     │         │
│  │  Agent      │  │   Agent     │  │   Agent     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                   ┌──────▼──────┐                           │
│                   │  Lead       │                           │
│                   │  Agent      │                           │
│                   │(Orchestrator)│                          │
│                   └──────┬──────┘                           │
│                          │                                  │
│         ┌────────────────┼────────────────┐                 │
│         │                │                │                 │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐         │
│  │  Finance    │  │  SysAdmin   │  │   Custom    │         │
│  │  Agent      │  │   Agent     │  │   Agents    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  ACP Bus    │  │ State Store │  │  Inference  │         │
│  │  (Redis)    │  │  (SQLite)   │  │  (Ollama)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Agent Types

### DeveloperAgent
- `implement(feature, specs)` - Write new code
- `review(pr_id)` - Code review with suggestions
- `fix_bug(issue_id, context)` - Debug and fix
- `write_tests(module, coverage_target)` - Generate tests
- `document(module)` - Create documentation

### QAAgent
- `generate_tests(module, requirements)` - Test generation
- `run_tests(suite_id)` - Execute test suites
- `analyze_coverage(report)` - Coverage analysis
- `find_bugs(codebase)` - Static analysis
- `validate(artifact)` - Quality validation

### SalesAgent
- `create_lead(name, company, contact)` - CRM entry
- `qualify_lead(lead_id, criteria)` - BANT scoring
- `create_opportunity(lead_id, value)` - Pipeline
- `generate_proposal(opportunity_id)` - Auto-proposals

### FinanceAgent
- `record_transaction(amount, type, category)` - Ledger
- `create_budget(period, allocations)` - Budget planning
- `analyze_spending(period)` - Financial analysis
- `generate_report(period, format)` - Reports

### SysAdminAgent
- `check_system(host)` - Health monitoring
- `analyze_logs(source, timeframe)` - Log analysis
- `create_incident(severity, description)` - Incident mgmt
- `run_command(host, command)` - Remote execution

### LeadAgent (Orchestrator)
- `create_workflow(name, tasks)` - Workflow definition
- `execute_workflow(workflow_id)` - Run workflows
- `delegate_task(agent_type, task)` - Task routing
- `monitor_workflows()` - Status tracking

## Project Structure

```
agentic_ai/
├── agents/
│   ├── base.py           # BaseAgent class, permissions, status
│   ├── developer.py      # DeveloperAgent implementation
│   ├── qa.py             # QAAgent implementation
│   ├── sales.py          # SalesAgent implementation
│   ├── finance.py        # FinanceAgent implementation
│   ├── sysadmin.py       # SysAdminAgent implementation
│   └── lead.py           # LeadAgent orchestrator
├── infrastructure/
│   ├── inference.py      # Ollama inference server
│   └── state.py          # SQLite + Redis state store
├── protocol/
│   └── acp.py            # Agent Communication Protocol
├── tests/
│   ├── test_infrastructure.py
│   ├── test_base_agent.py
│   ├── test_developer_qa.py
│   ├── test_phase3_agents.py
│   ├── test_lead_agent.py
│   └── test_integration.py
├── tools/                # Agent tools (optional extensions)
├── venv/                 # Python virtual environment
└── tests/                # Test suite (68 tests)
```

## Configuration

Model assignments (configurable per agent):

| Agent | Model | Purpose |
|-------|-------|---------|
| Developer | qwen3-coder | Code generation |
| QA | llama3.1:8b | Test analysis |
| Sales | gemma3:12b | CRM interactions |
| Finance | gemma3:12b | Financial reasoning |
| SysAdmin | llama3.1:8b | System operations |
| Lead | gemma3:12b | Orchestration |

## Testing

All tests pass: **68/68** ✅

```bash
# Run all tests
./venv/bin/python -m pytest tests/ -v

# Run specific phase
./venv/bin/python -m pytest tests/test_developer_qa.py -v

# Run with coverage
./venv/bin/python -m pytest tests/ --cov=agentic_ai
```

## License

Internal use - WezzelOS Project

## Contact

Wesley Robbins - wlrobbi@gmail.com
