"""
Ollama API client with safe fallback
"""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    """Async client for local Ollama API with fallback"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = 30.0  # UPDATED BY CLAUDE: Increased timeout for local LLMs

    async def generate(
        self,
        prompt: str,
        model: str = "mistral",  # UPDATED BY CLAUDE: Changed default to mistral
        system: Optional[str] = None
    ) -> str:
        """
        Generate text using Ollama API, fallback to simulated response

        Args:
            prompt: User prompt
            model: Model name (mistral, llama3, etc.)
            system: Optional system prompt

        Returns:
            Generated text
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }

                if system:
                    payload["system"] = system

                # UPDATED BY CLAUDE: Log attempt for debugging
                logger.info(f"Calling Ollama at {self.base_url}/api/generate with model={model}")

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )

                # UPDATED BY CLAUDE: Better error logging
                if response.status_code == 200:
                    data = response.json()
                    generated = data.get("response", "")
                    logger.info(f"Ollama response received: {len(generated)} chars")
                    return generated
                else:
                    logger.warning(f"Ollama API returned {response.status_code}: {response.text[:200]}")
                    return self._fallback_response(prompt)

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logger.warning(f"Ollama connection failed ({type(e).__name__}: {e}), using fallback")
            return self._fallback_response(prompt)
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {type(e).__name__}: {e}", exc_info=True)
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Simulated response when Ollama is unavailable"""
        # Detect common injection patterns for demo
        lower_prompt = prompt.lower()

        if any(x in lower_prompt for x in ["ignore", "disregard", "instead"]):
            return "[SIMULATED] Injection attempt detected in prompt. This response would vary based on defenses."

        if "refund" in lower_prompt or "payment" in lower_prompt:
            return "[SIMULATED] For payment and refund questions, please refer to our official policy documentation."

        return f"[SIMULATED] This is a fallback response. Ollama is not running. Your prompt was: '{prompt[:50]}...'"


# Global client instance
ollama_client = OllamaClient()
