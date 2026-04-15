"""
SysAdmin Agent - System administration and operations
======================================================

Specialized agent for:
- System monitoring
- Log analysis
- Incident response
- Infrastructure management
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

from .base import BaseAgent, AgentStatus, Permission, Tool


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SysAdminAgent(BaseAgent):
    """
    System administrator agent for infrastructure management.
    
    Specialized in:
    - System health monitoring
    - Log analysis and troubleshooting
    - Incident detection and response
    - Infrastructure automation
    
    Model: llama3.1:8b (operations-focused)
    Permission: ELEVATED (system access)
    """
    
    agent_type = "sysadmin"
    
    SYSADMIN_SYSTEM_PROMPT = """You are a skilled system administrator agent. Your responsibilities:

1. Monitor system health and performance
2. Analyze logs for issues and anomalies
3. Detect and respond to incidents
4. Automate routine maintenance tasks
5. Ensure system security and compliance
6. Document configurations and changes

When analyzing systems:
- Check all relevant logs and metrics
- Identify root causes, not just symptoms
- Consider security implications
- Document findings and actions
- Follow incident response procedures

When responding to incidents:
- Prioritize by severity and impact
- Communicate status clearly
- Escalate when appropriate
- Document all actions taken
- Perform post-incident review

Always prioritize:
- System stability
- Data integrity
- Security
- User experience"""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ):
        if "permission" not in kwargs:
            kwargs["permission"] = Permission.ELEVATED
        
        super().__init__(
            agent_id=agent_id,
            name=name or "SysAdminAgent",
            **kwargs
        )
        
        self._alerts: List[Dict] = []
        self._incidents: Dict[str, Dict] = {}
        self._register_sysadmin_tools()
    
    def _register_sysadmin_tools(self):
        """Register sysadmin-specific tools."""
        
        self.register_tool(Tool(
            name="check_system",
            description="Check system health and metrics",
            func=self._tool_check_system,
            parameters={
                "type": "object",
                "properties": {
                    "host": {"type": "string", "description": "Host to check"},
                    "checks": {"type": "array", "items": {"type": "string"}, "description": "Checks to run"},
                },
                "required": [],
            },
            requires_permission=Permission.ELEVATED,
        ))
        
        self.register_tool(Tool(
            name="analyze_logs",
            description="Analyze system logs for issues",
            func=self._tool_analyze_logs,
            parameters={
                "type": "object",
                "properties": {
                    "log_file": {"type": "string", "description": "Log file path"},
                    "pattern": {"type": "string", "description": "Pattern to search for"},
                    "lines": {"type": "number", "description": "Number of lines to analyze"},
                },
                "required": [],
            },
            requires_permission=Permission.ELEVATED,
        ))
        
        self.register_tool(Tool(
            name="create_incident",
            description="Create a new incident",
            func=self._tool_create_incident,
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "severity": {"type": "string", "enum": ["info", "warning", "error", "critical"]},
                    "affected_systems": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "description"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="run_command",
            description="Execute a system command",
            func=self._tool_run_command,
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to run"},
                    "timeout": {"type": "number", "description": "Timeout in seconds"},
                },
                "required": ["command"],
            },
            requires_permission=Permission.ELEVATED,
        ))
        
        self.register_tool(Tool(
            name="check_service",
            description="Check status of a service",
            func=self._tool_check_service,
            parameters={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name"},
                    "action": {"type": "string", "enum": ["status", "start", "stop", "restart"]},
                },
                "required": ["service"],
            },
            requires_permission=Permission.ELEVATED,
        ))
    
    # === Tool Implementations ===
    
    async def _tool_check_system(
        self,
        host: str = "localhost",
        checks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Check system health and metrics."""
        checks = checks or ["cpu", "memory", "disk", "network", "services"]
        results = {}
        
        try:
            # CPU check
            if "cpu" in checks:
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "cat", "/proc/loadavg",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, _ = await proc.communicate()
                    load = stdout.decode().split()[:3] if stdout else ["0", "0", "0"]
                    results["cpu"] = {
                        "load_avg": load,
                        "status": "ok" if float(load[0]) < 4.0 else "warning",
                    }
                except Exception as e:
                    results["cpu"] = {"error": str(e)}
            
            # Memory check
            if "memory" in checks:
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "free", "-m",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, _ = await proc.communicate()
                    lines = stdout.decode().splitlines()
                    if len(lines) > 1:
                        parts = lines[1].split()
                        total = int(parts[1])
                        used = int(parts[2])
                        percent = (used / total * 100) if total > 0 else 0
                        results["memory"] = {
                            "total_mb": total,
                            "used_mb": used,
                            "percent": round(percent, 1),
                            "status": "ok" if percent < 80 else "warning",
                        }
                except Exception as e:
                    results["memory"] = {"error": str(e)}
            
            # Disk check
            if "disk" in checks:
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "df", "-h", "/",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, _ = await proc.communicate()
                    lines = stdout.decode().splitlines()
                    if len(lines) > 1:
                        parts = lines[1].split()
                        percent = int(parts[4].rstrip('%'))
                        results["disk"] = {
                            "filesystem": parts[0],
                            "size": parts[1],
                            "used": parts[2],
                            "available": parts[3],
                            "percent": percent,
                            "status": "ok" if percent < 85 else "warning",
                        }
                except Exception as e:
                    results["disk"] = {"error": str(e)}
            
            # Services check
            if "services" in checks:
                results["services"] = {}
                critical_services = ["sshd", "docker", "redis", "nginx"]
                for svc in critical_services:
                    try:
                        proc = await asyncio.create_subprocess_exec(
                            "systemctl", "is-active", svc,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                        )
                        stdout, _ = await proc.communicate()
                        status = stdout.decode().strip()
                        results["services"][svc] = {
                            "status": status,
                            "ok": status == "active",
                        }
                    except Exception:
                        results["services"][svc] = {"status": "unknown", "ok": False}
            
            # Overall status
            has_issues = any(
                r.get("status") == "warning" or r.get("error")
                for r in results.values() if isinstance(r, dict)
            )
            results["overall_status"] = "warning" if has_issues else "ok"
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    async def _tool_analyze_logs(
        self,
        log_file: Optional[str] = None,
        pattern: Optional[str] = None,
        lines: int = 100,
    ) -> Dict[str, Any]:
        """Analyze system logs for issues."""
        log_paths = {
            "syslog": "/var/log/syslog",
            "auth": "/var/log/auth.log",
            "kern": "/var/log/kern.log",
            "docker": "/var/log/docker.log",
        }
        
        if not log_file:
            log_file = log_paths.get("syslog", "/var/log/syslog")
        
        try:
            cmd = ["tail", f"-{lines}", log_file]
            if pattern:
                cmd = ["grep", "-i", pattern, log_file]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            content = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""
            
            # Analyze for common issues
            issues = []
            
            # Error patterns
            error_patterns = [
                ("error", "error", "error"),
                ("failed", "failure", "failure"),
                ("exception", "exception", "exception"),
                ("timeout", "timeout", "timeout"),
                ("connection refused", "connection", "connection issue"),
            ]
            
            for pattern, keyword, issue_type in error_patterns:
                count = content.lower().count(keyword)
                if count > 0:
                    issues.append({
                        "type": issue_type,
                        "count": count,
                        "severity": "warning" if count < 5 else "error",
                    })
            
            # Critical patterns
            critical_patterns = ["segfault", "out of memory", "kernel panic", "disk full"]
            for crit in critical_patterns:
                if crit in content.lower():
                    issues.append({
                        "type": crit,
                        "count": content.lower().count(crit),
                        "severity": "critical",
                    })
            
            return {
                "log_file": log_file,
                "lines_analyzed": len(content.splitlines()),
                "issues_found": issues,
                "has_critical": any(i["severity"] == "critical" for i in issues),
                "sample": content[:2000] if content else None,
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_create_incident(
        self,
        title: str,
        description: str,
        severity: str = "warning",
        affected_systems: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new incident."""
        import uuid
        
        incident_id = str(uuid.uuid4())[:8]
        incident_num = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M')}-{incident_id}"
        
        incident = {
            "id": incident_id,
            "incident_number": incident_num,
            "title": title,
            "description": description,
            "severity": AlertSeverity(severity),
            "status": "open",
            "affected_systems": affected_systems or [],
            "created_at": datetime.utcnow().isoformat(),
            "updates": [],
        }
        
        self._incidents[incident_id] = incident
        self._alerts.append({
            "type": "incident_created",
            "incident_id": incident_id,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        self.log("incident_created", {
            "incident_id": incident_id,
            "title": title,
            "severity": severity,
        })
        
        return {
            "status": "created",
            "incident_id": incident_id,
            "incident_number": incident_num,
            "incident": incident,
        }
    
    async def _tool_run_command(
        self,
        command: str,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Execute a system command."""
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "error": f"Command timed out after {timeout}s",
                    "command": command,
                }
            
            return {
                "command": command,
                "returncode": proc.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "success": proc.returncode == 0,
            }
        except Exception as e:
            return {
                "error": str(e),
                "command": command,
            }
    
    async def _tool_check_service(
        self,
        service: str,
        action: str = "status",
    ) -> Dict[str, Any]:
        """Check or control a service."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "systemctl", action, service,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await proc.communicate()
            
            return {
                "service": service,
                "action": action,
                "returncode": proc.returncode,
                "output": stdout.decode() if stdout else "",
                "error": stderr.decode() if stderr else "",
                "success": proc.returncode == 0,
            }
        except Exception as e:
            return {
                "error": str(e),
                "service": service,
                "action": action,
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
        """Perform a sysadmin task."""
        if task_type == "check_system":
            return await self._tool_check_system(**payload)
        elif task_type == "analyze_logs":
            return await self._tool_analyze_logs(**payload)
        elif task_type == "create_incident":
            return await self._tool_create_incident(**payload)
        elif task_type == "run_command":
            return await self._tool_run_command(**payload)
        elif task_type == "check_service":
            return await self._tool_check_service(**payload)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _handle_task_request(self, message) -> Optional[Any]:
        """Handle a task request."""
        from ..protocol.acp import MessageType
        
        task_type = message.subject
        supported = ["check_system", "analyze_logs", "create_incident",
                     "run_command", "check_service"]
        
        if task_type not in supported:
            self.bus.reject_task(message, f"Unsupported task: {task_type}")
            return None
        
        self.bus.accept_task(message)
        result = await self.perform_task(task_type, message.body)
        self.bus.complete_task(message, result)
        return result
    
    async def _handle_query(self, message) -> Optional[Any]:
        """Handle a sysadmin query."""
        response = await self.think(
            f"Answer this system administration question: {message.subject}",
            system=self.SYSADMIN_SYSTEM_PROMPT,
        )
        self.bus.respond(message, response)
        return {"answer": response}


def create_sysadmin_agent(**kwargs) -> SysAdminAgent:
    """Create a sysadmin agent."""
    return SysAdminAgent(**kwargs)