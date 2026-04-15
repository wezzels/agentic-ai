"""
QA Agent - Quality assurance and testing
==========================================

Specialized agent for:
- Test generation
- Test execution and validation
- Bug detection
- Code quality analysis
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .base import BaseAgent, AgentStatus, Permission, Tool


class TestType(str, Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class TestResult:
    """Result of a test run."""
    test_id: str
    test_type: TestType
    passed: bool
    duration_ms: float
    message: str
    details: Optional[Dict[str, Any]] = None


class QAAgent(BaseAgent):
    """
    QA agent for quality assurance and testing.
    
    Specialized in:
    - Generating test cases
    - Running and validating tests
    - Detecting bugs and issues
    - Code quality analysis
    - Coverage analysis
    
    Model: llama3.1:8b (general purpose)
    Permission: READ_ONLY (can read code, write tests)
    """
    
    agent_type = "qa"
    
    # System prompt for QA tasks
    QA_SYSTEM_PROMPT = """You are a meticulous QA engineer agent. Your responsibilities:

1. Design comprehensive test suites that catch edge cases
2. Write clear, maintainable test code
3. Verify test coverage meets requirements
4. Identify potential bugs and vulnerabilities
5. Ensure code meets quality standards
6. Document test cases and expected behaviors

When writing tests:
- Test happy paths and error paths
- Include boundary conditions
- Test with invalid inputs
- Mock external dependencies
- Ensure tests are deterministic
- Use descriptive test names
- Add assertions for all important behaviors

When analyzing code:
- Look for potential null/undefined errors
- Check for resource leaks
- Verify error handling
- Identify security vulnerabilities
- Consider thread safety issues
- Look for performance bottlenecks"""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        project_path: Optional[str] = None,
        **kwargs
    ):
        # QA has read-only permissions for code, but can write tests
        if "permission" not in kwargs:
            kwargs["permission"] = Permission.READ_ONLY
        
        super().__init__(
            agent_id=agent_id,
            name=name or "QAAgent",
            **kwargs
        )
        
        self.project_path = Path(project_path) if project_path else None
        self._test_results: List[TestResult] = []
        self._register_qa_tools()
    
    def _register_qa_tools(self):
        """Register QA-specific tools."""
        
        self.register_tool(Tool(
            name="generate_tests",
            description="Generate test cases for code",
            func=self._tool_generate_tests,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File to generate tests for"},
                    "test_type": {"type": "string", "enum": ["unit", "integration", "e2e"]},
                    "coverage_target": {"type": "number", "description": "Target coverage percentage"},
                },
                "required": ["path"],
            },
            requires_permission=Permission.READ_ONLY,
        ))
        
        self.register_tool(Tool(
            name="run_tests",
            description="Run tests and collect results",
            func=self._tool_run_tests,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Test file or directory"},
                    "failfast": {"type": "boolean", "description": "Stop on first failure"},
                    "verbose": {"type": "boolean", "description": "Verbose output"},
                },
                "required": [],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="analyze_coverage",
            description="Analyze test coverage",
            func=self._tool_analyze_coverage,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to analyze"},
                    "min_coverage": {"type": "number", "description": "Minimum required coverage"},
                },
                "required": [],
            },
            requires_permission=Permission.READ_ONLY,
        ))
        
        self.register_tool(Tool(
            name="find_bugs",
            description="Find potential bugs in code",
            func=self._tool_find_bugs,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File to analyze"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                },
                "required": ["path"],
            },
            requires_permission=Permission.READ_ONLY,
        ))
        
        self.register_tool(Tool(
            name="check_quality",
            description="Check code quality metrics",
            func=self._tool_check_quality,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File or directory to check"},
                    "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to check"},
                },
                "required": ["path"],
            },
            requires_permission=Permission.READ_ONLY,
        ))
    
    # === Tool Implementations ===
    
    async def _tool_generate_tests(
        self,
        path: str,
        test_type: str = "unit",
        coverage_target: float = 80.0,
    ) -> Dict[str, Any]:
        """Generate test cases for a file."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        file_path = self.project_path / path
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        try:
            code = file_path.read_text()
            
            prompt = f"""Generate {test_type} tests for this code with {coverage_target}% coverage target:

```python
{code[:6000]}
```

Requirements:
1. Test all public methods/functions
2. Include edge cases and boundary conditions
3. Test error handling paths
4. Use appropriate mocking for dependencies
5. Include descriptive test names and docstrings
6. Target {coverage_target}% code coverage

Provide complete, runnable pytest test code."""

            tests = await self.think(prompt, system=self.QA_SYSTEM_PROMPT)
            
            self.log("tests_generated", {"path": path, "type": test_type})
            
            return {
                "path": path,
                "test_type": test_type,
                "coverage_target": coverage_target,
                "tests": tests,
                "suggested_file": f"test_{file_path.name}",
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_run_tests(
        self,
        path: Optional[str] = None,
        failfast: bool = False,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """Run tests and collect results."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        test_path = self.project_path / path if path else self.project_path / "tests"
        
        cmd = ["python", "-m", "pytest", str(test_path)]
        if verbose:
            cmd.append("-v")
        if failfast:
            cmd.append("-x")
        cmd.extend(["--tb=short", "-q"])
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.project_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            # Parse results
            output = stdout.decode() if stdout else ""
            errors = stderr.decode() if stderr else ""
            
            # Extract test counts
            passed = output.count("PASSED")
            failed = output.count("FAILED")
            skipped = output.count("SKIPPED")
            
            result = {
                "returncode": proc.returncode,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "output": output,
                "errors": errors,
            }
            
            self.log("tests_run", result)
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_analyze_coverage(
        self,
        path: Optional[str] = None,
        min_coverage: float = 80.0,
    ) -> Dict[str, Any]:
        """Analyze test coverage."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        analyze_path = self.project_path / path if path else self.project_path
        
        cmd = [
            "python", "-m", "pytest",
            str(analyze_path),
            "--cov", str(analyze_path),
            "--cov-report=term-missing",
            "--cov-fail-under", str(min_coverage),
            "-q",
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.project_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            output = stdout.decode() if stdout else ""
            
            # Parse coverage percentage
            coverage = 0.0
            for line in output.splitlines():
                if "TOTAL" in line and "%" in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith("%"):
                            try:
                                coverage = float(part.rstrip("%"))
                            except ValueError:
                                pass
            
            return {
                "returncode": proc.returncode,
                "coverage": coverage,
                "min_coverage": min_coverage,
                "meets_target": coverage >= min_coverage,
                "output": output,
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_find_bugs(
        self,
        path: str,
        severity: str = "medium",
    ) -> Dict[str, Any]:
        """Find potential bugs in code."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        file_path = self.project_path / path
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        try:
            code = file_path.read_text()
            
            prompt = f"""Analyze this code for potential bugs. Focus on {severity} severity issues.

```python
{code[:6000]}
```

Look for:
1. Null/undefined errors
2. Off-by-one errors
3. Resource leaks
4. Race conditions
5. Type errors
6. Logic errors
7. Security vulnerabilities
8. Performance issues

For each bug found, provide:
- Line number
- Bug type
- Description
- Severity (critical/high/medium/low)
- Suggested fix"""

            analysis = await self.think(prompt, system=self.QA_SYSTEM_PROMPT)
            
            bugs = []
            # Parse structured bugs from analysis
            
            return {
                "path": path,
                "severity_filter": severity,
                "bugs": bugs,
                "analysis": analysis,
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_check_quality(
        self,
        path: str,
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Check code quality metrics."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        file_path = self.project_path / path
        
        if not file_path.exists():
            return {"error": f"Path not found: {path}"}
        
        metrics = metrics or ["complexity", "maintainability", "documentation", "duplication"]
        
        try:
            if file_path.is_file():
                code = file_path.read_text()
                lines = code.splitlines()
                
                # Simple metrics calculation
                total_lines = len(lines)
                code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith("#"))
                comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
                blank_lines = total_lines - code_lines - comment_lines
                
                # Functions/classes count
                functions = sum(1 for l in lines if l.strip().startswith("def "))
                classes = sum(1 for l in lines if l.strip().startswith("class "))
                
                # Average function length (rough)
                avg_func_length = code_lines / max(functions, 1)
                
                # Documentation ratio
                doc_ratio = (comment_lines / code_lines * 100) if code_lines > 0 else 0
                
                results = {
                    "path": path,
                    "metrics": {
                        "total_lines": total_lines,
                        "code_lines": code_lines,
                        "comment_lines": comment_lines,
                        "blank_lines": blank_lines,
                        "functions": functions,
                        "classes": classes,
                        "avg_function_length": round(avg_func_length, 1),
                        "documentation_ratio": round(doc_ratio, 1),
                    },
                    "quality_score": self._calculate_quality_score(
                        doc_ratio, avg_func_length, functions
                    ),
                }
            else:
                results = {"error": "Directory analysis not implemented"}
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_quality_score(
        self,
        doc_ratio: float,
        avg_func_length: float,
        num_functions: int,
    ) -> Dict[str, Any]:
        """Calculate overall quality score."""
        # Documentation score (0-100)
        doc_score = min(100, doc_ratio * 2) if doc_ratio > 0 else 0
        
        # Function size score (prefer smaller functions)
        size_score = max(0, 100 - (avg_func_length - 20) * 2) if avg_func_length > 20 else 100
        
        # Complexity score (fewer functions = less complexity)
        complexity_score = max(0, 100 - num_functions) if num_functions < 100 else 0
        
        overall = (doc_score + size_score + complexity_score) / 3
        
        return {
            "overall": round(overall, 1),
            "documentation": round(doc_score, 1),
            "function_size": round(size_score, 1),
            "complexity": round(complexity_score, 1),
        }
    
    # === Message and Task Handlers ===
    
    async def process_message(self, message) -> Optional[Any]:
        """Process an incoming message."""
        from ..protocol.acp import MessageType
        
        self.log("message_received", {"from": message.sender, "type": message.type.value})
        
        if message.type == MessageType.TASK_REQUEST:
            return await self._handle_task_request(message)
        elif message.type == MessageType.QUERY:
            return await self._handle_query(message)
        
        return None
    
    async def perform_task(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a specific QA task."""
        self.log("task_started", {"task_type": task_type})
        
        if task_type == "generate_tests":
            return await self._task_generate_tests(payload)
        elif task_type == "run_tests":
            return await self._task_run_tests_task(payload)
        elif task_type == "analyze_coverage":
            return await self._task_analyze_coverage_task(payload)
        elif task_type == "find_bugs":
            return await self._task_find_bugs(payload)
        elif task_type == "validate":
            return await self._task_validate(payload)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    # === Task Implementations ===
    
    async def _task_generate_tests(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tests for code."""
        path = payload.get("path", "")
        test_type = payload.get("test_type", "unit")
        
        return await self._tool_generate_tests(path, test_type)
    
    async def _task_run_tests_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests and report results."""
        path = payload.get("path")
        
        result = await self._tool_run_tests(path)
        
        # Store test result
        test_result = TestResult(
            test_id=f"test_{len(self._test_results)}",
            test_type=TestType.UNIT,
            passed=result.get("failed", 1) == 0,
            duration_ms=0,  # Would parse from output
            message=result.get("output", ""),
            details=result,
        )
        self._test_results.append(test_result)
        
        return result
    
    async def _task_analyze_coverage_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test coverage."""
        path = payload.get("path")
        min_coverage = payload.get("min_coverage", 80.0)
        
        return await self._tool_analyze_coverage(path, min_coverage)
    
    async def _task_find_bugs(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Find bugs in code."""
        path = payload.get("path", "")
        severity = payload.get("severity", "medium")
        
        return await self._tool_find_bugs(path, severity)
    
    async def _task_validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code against requirements."""
        code = payload.get("code", "")
        requirements = payload.get("requirements", [])
        
        prompt = f"""Validate this code against the following requirements:

Requirements:
{chr(10).join(f'- {r}' for r in requirements)}

Code:
```
{code[:5000]}
```

For each requirement:
1. Check if it is satisfied
2. If not, explain why
3. Suggest fixes if needed

Provide a clear pass/fail assessment."""

        validation = await self.think(prompt, system=self.QA_SYSTEM_PROMPT)
        
        return {
            "status": "validated",
            "validation": validation,
            "requirements": requirements,
        }
    
    async def _handle_task_request(self, message) -> Optional[Any]:
        """Handle a task request message."""
        from ..protocol.acp import ACPMessage, MessageType
        
        task_type = message.subject
        payload = message.body
        
        supported_tasks = ["generate_tests", "run_tests", "analyze_coverage", "find_bugs", "validate"]
        
        if task_type not in supported_tasks:
            self.bus.reject_task(message, f"Unsupported task type: {task_type}")
            return None
        
        self.bus.accept_task(message)
        result = await self.perform_task(task_type, payload)
        self.bus.complete_task(message, result)
        
        return result
    
    async def _handle_query(self, message) -> Optional[Any]:
        """Handle a query message."""
        from ..protocol.acp import ACPMessage, MessageType
        
        question = message.subject
        
        response = await self.think(
            f"Answer this question about testing/quality: {question}",
            system=self.QA_SYSTEM_PROMPT,
        )
        
        self.bus.respond(message, response)
        return {"answer": response}


# Convenience function
def create_qa_agent(
    project_path: str,
    agent_id: Optional[str] = None,
    **kwargs
) -> QAAgent:
    """Create a QA agent for a project."""
    return QAAgent(
        agent_id=agent_id,
        project_path=project_path,
        **kwargs
    )