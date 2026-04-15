"""
Inference Server - Ollama API Client for Agentic AI
====================================================

Provides LLM inference via Ollama running on miner (10.0.0.117).
Supports multiple models for different agent tasks.
"""

import httpx
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass
import json


@dataclass
class ModelInfo:
    """Information about an available model."""
    name: str
    size: int
    parameter_size: str
    quantization: str
    family: str


class InferenceServer:
    """
    Ollama inference server client.
    
    Connects to Ollama running on miner (10.0.0.117:11434).
    Provides model management and inference for agents.
    """
    
    # Default model assignments for different agent types
    DEFAULT_MODELS = {
        "developer": "qwen3-coder:latest",      # Code generation
        "qa": "llama3.1:8b",                     # Test generation
        "lead": "gemma3:12b",                    # Coordination, planning
        "sysadmin": "llama3.1:8b",               # Infrastructure ops
        "finance": "gemma3:12b",                 # Reporting, analysis
        "sales": "gemma3:12b",                   # CRM, communication
        "designer": "gemma3:12b",                # UI/UX suggestions
        "writer": "llama3.1:8b",                 # Documentation
        "pm": "gemma3:12b",                      # Sprint management
    }
    
    # Fallback models (smaller/faster)
    FALLBACK_MODELS = {
        "developer": "llama3.1:8b",
        "default": "llama3.1:8b",
    }
    
    def __init__(
        self,
        host: str = "10.0.0.117",
        port: int = 11434,
        timeout: float = 120.0,
    ):
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None
        self._available_models: List[ModelInfo] = []
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client
    
    def health_check(self) -> bool:
        """Check if Ollama server is responding."""
        try:
            client = self._get_client()
            response = client.get(f"{self.base_url}/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[ModelInfo]:
        """Get list of available models."""
        try:
            client = self._get_client()
            response = client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = []
            data = response.json()
            for model in data.get("models", []):
                details = model.get("details", {})
                models.append(ModelInfo(
                    name=model["name"],
                    size=model.get("size", 0),
                    parameter_size=details.get("parameter_size", "unknown"),
                    quantization=details.get("quantization_level", "unknown"),
                    family=details.get("family", "unknown"),
                ))
            
            self._available_models = models
            return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def get_model_for_agent(self, agent_type: str) -> str:
        """Get the appropriate model for an agent type."""
        # Check if preferred model exists
        preferred = self.DEFAULT_MODELS.get(agent_type, "llama3.1:8b")
        
        available_names = [m.name for m in self._available_models]
        if preferred in available_names:
            return preferred
        
        # Try fallback
        fallback = self.FALLBACK_MODELS.get(agent_type, self.FALLBACK_MODELS["default"])
        if fallback in available_names:
            return fallback
        
        # Last resort: first available model
        if self._available_models:
            return self._available_models[0].name
        
        return "llama3.1:8b"  # Default fallback
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        agent_type: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> str:
        """
        Generate a completion from the model.
        
        Args:
            prompt: The input prompt
            model: Model name (auto-selected if None)
            system: System prompt
            agent_type: Agent type for auto model selection
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Generated text
        """
        # Auto-select model if not specified
        if model is None:
            if agent_type:
                model = self.get_model_for_agent(agent_type)
            else:
                model = "llama3.1:8b"
        
        client = self._get_client()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            if stream:
                return self._generate_stream(client, payload)
            else:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            print(f"Generation error: {e}")
            return f"Error: {str(e)}"
    
    def _generate_stream(
        self,
        client: httpx.Client,
        payload: Dict[str, Any],
    ) -> Generator[str, None, None]:
        """Stream generation response."""
        try:
            with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
            ) as response:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
        except Exception as e:
            yield f"Stream error: {str(e)}"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        agent_type: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Chat-style completion with message history.
        
        Args:
            messages: List of {"role": "user|assistant|system", "content": "..."}
            model: Model name (auto-selected if None)
            agent_type: Agent type for auto model selection
            temperature: Sampling temperature
        
        Returns:
            Generated response
        """
        if model is None:
            if agent_type:
                model = self.get_model_for_agent(agent_type)
            else:
                model = "llama3.1:8b"
        
        client = self._get_client()
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        try:
            response = client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            print(f"Chat error: {e}")
            return f"Error: {str(e)}"
    
    def embed(
        self,
        text: str,
        model: str = "nomic-embed-text:latest",
    ) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            model: Embedding model
        
        Returns:
            Embedding vector
        """
        client = self._get_client()
        
        try:
            response = client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text},
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
        except Exception as e:
            print(f"Embedding error: {e}")
            return []
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton instance for easy access
_inference_server: Optional[InferenceServer] = None


def get_inference_server(
    host: str = "10.0.0.117",
    port: int = 11434,
) -> InferenceServer:
    """Get or create the inference server singleton."""
    global _inference_server
    if _inference_server is None:
        _inference_server = InferenceServer(host=host, port=port)
        _inference_server.list_models()  # Cache available models
    return _inference_server