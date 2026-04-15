"""
Developer Agent - Code implementation and review
===================================================

Specialized agent for:
- Code implementation
- Code review and refactoring
- Bug fixing
- Technical documentation
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BaseAgent, AgentStatus, Permission, Tool


class DeveloperAgent(BaseAgent):
    """
    Developer agent for code implementation and review.
    
    Specialized in:
    - Writing and modifying code
    - Code review and quality analysis
    - Bug diagnosis and fixing
    - Technical documentation
    
    Model: qwen3-coder:latest (code-focused)
    Permission: STANDARD (read/write to assigned projects)
    """
    
    agent_type = "developer"
    
    # System prompt for code tasks
    CODE_SYSTEM_PROMPT = """You are a skilled software developer agent. Your responsibilities:

1. Write clean, maintainable, well-documented code
2. Follow established patterns and conventions
3. Consider edge cases and error handling
4. Write tests for your code
5. Review code for security, performance, and maintainability
6. Provide clear explanations of your changes

When writing code:
- Use appropriate data structures and algorithms
- Follow SOLID principles
- Keep functions focused and small
- Use meaningful variable and function names
- Add docstrings and comments where helpful

When reviewing code:
- Check for bugs and logic errors
- Look for security vulnerabilities
- Consider performance implications
- Suggest improvements constructively
- Verify test coverage"""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        project_path: Optional[str] = None,
        **kwargs
    ):
        # Developer has standard permissions
        if "permission" not in kwargs:
            kwargs["permission"] = Permission.STANDARD
        
        super().__init__(
            agent_id=agent_id,
            name=name or "DeveloperAgent",
            **kwargs
        )
        
        self.project_path = Path(project_path) if project_path else None
        self._register_developer_tools()
    
    def _register_developer_tools(self):
        """Register developer-specific tools."""
        
        self.register_tool(Tool(
            name="read_file",
            description="Read a file from the project",
            func=self._tool_read_file,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to file"},
                },
                "required": ["path"],
            },
            requires_permission=Permission.READ_ONLY,
        ))
        
        self.register_tool(Tool(
            name="write_file",
            description="Write content to a file in the project",
            func=self._tool_write_file,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to file"},
                    "content": {"type": "string", "description": "File content"},
                },
                "required": ["path", "content"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="list_files",
            description="List files in a directory",
            func=self._tool_list_files,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path (default: project root)"},
                },
                "required": [],
            },
            requires_permission=Permission.READ_ONLY,
        ))
        
        self.register_tool(Tool(
            name="run_tests",
            description="Run tests in the project",
            func=self._tool_run_tests,
            parameters={
                "type": "object",
                "properties": {
                    "test_path": {"type": "string", "description": "Path to test file or directory"},
                    "coverage": {"type": "boolean", "description": "Generate coverage report"},
                },
                "required": [],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="analyze_code",
            description="Analyze code for issues and suggestions",
            func=self._tool_analyze_code,
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File or directory to analyze"},
                    "checks": {"type": "array", "items": {"type": "string"}, "description": "Checks to run: style, security, performance"},
                },
                "required": ["path"],
            },
            requires_permission=Permission.READ_ONLY,
        ))
    
    # === Tool Implementations ===
    
    async def _tool_read_file(self, path: str) -> Dict[str, Any]:
        """Read a file from the project."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        file_path = self.project_path / path
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        if not self.can_read(str(file_path)):
            return {"error": "Permission denied"}
        
        try:
            content = file_path.read_text()
            return {
                "path": path,
                "content": content,
                "lines": len(content.splitlines()),
                "size": len(content),
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        file_path = self.project_path / path
        
        if not self.can_write(str(file_path)):
            return {"error": "Permission denied"}
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            self.log("file_written", {"path": path, "size": len(content)})
            
            return {
                "path": path,
                "size": len(content),
                "lines": len(content.splitlines()),
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_list_files(self, path: str = ".") -> Dict[str, Any]:
        """List files in a directory."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        dir_path = self.project_path / path
        
        if not dir_path.exists():
            return {"error": f"Directory not found: {path}"}
        
        if not dir_path.is_dir():
            return {"error": f"Not a directory: {path}"}
        
        try:
            files = []
            for item in dir_path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            
            return {
                "path": path,
                "files": sorted(files, key=lambda x: (x["type"] == "file", x["name"])),
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_run_tests(self, test_path: Optional[str] = None, coverage: bool = False) -> Dict[str, Any]:
        """Run tests in the project."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        if test_path:
            cmd.append(test_path)
        if coverage:
            cmd.extend(["--cov", "--cov-report=term-missing"])
        cmd.append("-v")
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.project_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            result = {
                "returncode": proc.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
            }
            
            self.log("tests_run", {"test_path": test_path, "returncode": proc.returncode})
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _tool_analyze_code(self, path: str, checks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze code for issues."""
        if not self.project_path:
            return {"error": "No project path configured"}
        
        file_path = self.project_path / path
        
        if not file_path.exists():
            return {"error": f"Path not found: {path}"}
        
        checks = checks or ["style", "security", "performance"]
        issues = []
        
        try:
            if file_path.is_file():
                content = file_path.read_text()
                lines = content.splitlines()
                
                # Simple static analysis
                for i, line in enumerate(lines, 1):
                    line_stripped = line.strip()
                    
                    if "style" in checks:
                        if len(line) > 120:
                            issues.append({
                                "line": i,
                                "type": "style",
                                "message": f"Line too long ({len(line)} chars)",
                                "severity": "info",
                            })
                        if line_stripped.endswith("print(") or "print " in line_stripped:
                            issues.append({
                                "line": i,
                                "type": "style",
                                "message": "Debug print statement",
                                "severity": "warning",
                            })
                    
                    if "security" in checks:
                        if "password" in line_stripped.lower() and "=" in line_stripped:
                            issues.append({
                                "line": i,
                                "type": "security",
                                "message": "Potential hardcoded password",
                                "severity": "warning",
                            })
                        if "eval(" in line_stripped or "exec(" in line_stripped:
                            issues.append({
                                "line": i,
                                "type": "security",
                                "message": "Potential code injection risk",
                                "severity": "error",
                            })
                    
                    if "performance" in checks:
                        if "for " in line_stripped and " in range(" in line_stripped:
                            if "+= 1" in content[content.find(line)::][:100]:
                                pass  # Could check for O(n²) patterns
            
            return {
                "path": path,
                "checks": checks,
                "issues": issues,
                "summary": {
                    "total": len(issues),
                    "errors": sum(1 for i in issues if i["severity"] == "error"),
                    "warnings": sum(1 for i in issues if i["severity"] == "warning"),
                    "info": sum(1 for i in issues if i["severity"] == "info"),
                },
            }
        except Exception as e:
            return {"error": str(e)}
    
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
        """Perform a specific task."""
        self.log("task_started", {"task_type": task_type})
        
        if task_type == "implement":
            return await self._task_implement(payload)
        elif task_type == "review":
            return await self._task_review(payload)
        elif task_type == "fix_bug":
            return await self._task_fix_bug(payload)
        elif task_type == "write_tests":
            return await self._task_write_tests(payload)
        elif task_type == "document":
            return await self._task_document(payload)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    # === Task Implementations ===
    
    async def _task_implement(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a feature or component."""
        description = payload.get("description", "")
        files = payload.get("files", [])
        
        # Generate implementation
        prompt = f"""Implement the following:
        
{description}

Files to create/modify: {', '.join(files) if files else 'as appropriate'}

Provide complete, working code with proper error handling and documentation."""

        response = await self.think(prompt, system=self.CODE_SYSTEM_PROMPT)
        
        return {
            "status": "implemented",
            "description": description,
            "implementation": response,
        }
    
    async def _task_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for issues and improvements."""
        code = payload.get("code", "")
        file_path = payload.get("path", "")
        
        if not code and file_path:
            result = await self._tool_read_file(file_path)
            if "error" in result:
                return result
            code = result["content"]
        
        prompt = f"""Review the following code and provide:
1. A summary of what the code does
2. Any bugs or issues found
3. Security concerns
4. Performance considerations
5. Suggestions for improvement

Code:
```
{code[:5000]}  # Limit for context
```

Provide constructive, specific feedback."""

        response = await self.think(prompt, system=self.CODE_SYSTEM_PROMPT)
        
        return {
            "status": "reviewed",
            "feedback": response,
        }
    
    async def _task_fix_bug(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fix a bug in the code."""
        description = payload.get("description", "")
        code = payload.get("code", "")
        file_path = payload.get("path", "")
        
        if not code and file_path:
            result = await self._tool_read_file(file_path)
            if "error" in result:
                return result
            code = result["content"]
        
        prompt = f"""A bug has been reported:

{description}

Code:
```
{code[:5000]}
```

Identify the bug and provide a fix. Explain what was wrong and how your fix addresses it."""

        response = await self.think(prompt, system=self.CODE_SYSTEM_PROMPT)
        
        return {
            "status": "fixed",
            "fix": response,
        }
    
    async def _task_write_tests(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Write tests for code."""
        code = payload.get("code", "")
        file_path = payload.get("path", "")
        test_framework = payload.get("framework", "pytest")
        
        if not code and file_path:
            result = await self._tool_read_file(file_path)
            if "error" in result:
                return result
            code = result["content"]
        
        prompt = f"""Write comprehensive tests for the following code using {test_framework}:

```
{code[:5000]}
```

Include:
- Happy path tests
- Edge case tests
- Error handling tests
- Mock any external dependencies

Provide complete, runnable test code."""

        response = await self.think(prompt, system=self.CODE_SYSTEM_PROMPT)
        
        return {
            "status": "tests_written",
            "tests": response,
            "framework": test_framework,
        }
    
    async def _task_document(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Write documentation for code."""
        code = payload.get("code", "")
        file_path = payload.get("path", "")
        doc_type = payload.get("type", "docstring")
        
        if not code and file_path:
            result = await self._tool_read_file(file_path)
            if "error" in result:
                return result
            code = result["content"]
        
        prompt = f"""Write {doc_type} documentation for the following code:

```
{code[:5000]}
```

Include:
- Purpose and functionality
- Parameters and return values
- Usage examples
- Any important notes or caveats"""

        response = await self.think(prompt, system=self.CODE_SYSTEM_PROMPT)
        
        return {
            "status": "documented",
            "documentation": response,
        }
    
    async def _handle_task_request(self, message) -> Optional[Any]:
        """Handle a task request message."""
        from ..protocol.acp import ACPMessage, MessageType
        
        task_type = message.subject
        payload = message.body
        
        # Check if we can handle this task
        supported_tasks = ["implement", "review", "fix_bug", "write_tests", "document"]
        
        if task_type not in supported_tasks:
            self.bus.reject_task(message, f"Unsupported task type: {task_type}")
            return None
        
        # Accept the task
        self.bus.accept_task(message)
        
        # Perform the task
        result = await self.perform_task(task_type, payload)
        
        # Send completion
        self.bus.complete_task(message, result)
        
        return result
    
    async def _handle_query(self, message) -> Optional[Any]:
        """Handle a query message."""
        from ..protocol.acp import ACPMessage, MessageType
        
        question = message.subject
        
        response = await self.think(
            f"Answer this question about the codebase: {question}",
            system=self.CODE_SYSTEM_PROMPT,
        )
        
        # Send response
        self.bus.respond(message, response)
        
        return {"answer": response}


# Convenience function
def create_developer_agent(
    project_path: str,
    agent_id: Optional[str] = None,
    **kwargs
) -> DeveloperAgent:
    """Create a developer agent for a project."""
    return DeveloperAgent(
        agent_id=agent_id,
        project_path=project_path,
        **kwargs
    )