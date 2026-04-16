# Agentic AI Dashboard

Real-time web dashboard for monitoring Agentic AI agents, experiments, and workflows.

## Features

- **Agent Overview**: Status, health, and activity across all 33+ agents
- **Chaos Monkey Dashboard**: Real-time experiment tracking, resiliency scores
- **Vendor Risk Dashboard**: Vendor tiers, assessments, findings heatmap
- **Audit Dashboard**: Control effectiveness, evidence tracking, findings
- **Cloud Security Dashboard**: Compliance scores, findings, policy violations
- **ML Ops Dashboard**: Model registry, experiment tracking, drift alerts

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State**: React Context + Hooks
- **API**: REST (Python backend)

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Dashboard Views

### 1. Overview Dashboard
- Agent health status
- Recent activity feed
- Quick stats across all agents

### 2. Chaos Monkey
- Experiment list with status badges
- Real-time experiment view
- Target management
- Resiliency score charts
- Safety constraints config

### 3. Vendor Risk
- Vendor tier breakdown (pie chart)
- Assessment status timeline
- Finding severity heatmap
- Alert timeline
- Continuous monitoring status

### 4. Audit
- Audit engagement status
- Control effectiveness (bar chart)
- Finding tracking by severity
- Evidence browser
- Workpaper status

### 5. Cloud Security
- Account inventory by cloud provider
- Finding summary (donut chart)
- Compliance score trends
- Policy violation list

### 6. ML Ops
- Model registry table
- Experiment tracking
- Deployment status
- Drift detection alerts

## API Integration

The dashboard connects to the Agentic AI Python backend via REST API.

```python
# Backend server (to be implemented)
python -m agentic_ai.server --host 0.0.0.0 --port 8000
```

## Screenshots

See `/dashboard/screenshots/` for mockups.

## Development

```bash
# Run tests
npm test

# Lint code
npm run lint

# Type check
npm run typecheck
```

## License

Apache 2.0
