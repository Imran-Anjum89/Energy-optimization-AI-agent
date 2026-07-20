"""
LLM Client
Thin wrapper around the Anthropic API so agents don't need to know the
SDK's call signature. Used by InsightAgent for the pipeline's one
genuinely non-deterministic reasoning step.
"""

from backend.config import config
from services.logger import setup_logger

logger = setup_logger("LLMClient")


class LLMClient:
    """
    Minimal wrapper: generate(prompt) -> str.

    Reads the API key from Config (which reads it from the environment),
    never hardcoded. If no key is configured, is_available() returns
    False so callers can degrade gracefully instead of crashing the
    pipeline.
    """

    def __init__(self, model: str = None, max_tokens: int = None):
        self._model_override = model
        self.max_tokens = max_tokens or config.INSIGHT_MAX_TOKENS
        self._client = None
        self._client_key = None

        if not config.ANTHROPIC_API_KEY:
            logger.info(
                "ANTHROPIC_API_KEY not set - InsightAgent will use its "
                "deterministic fallback instead of LLM reasoning."
            )

    @property
    def model(self) -> str:
        return self._model_override or config.INSIGHT_MODEL

    @property
    def client(self):
        current_key = config.ANTHROPIC_API_KEY
        if current_key != self._client_key:
            self._client_key = current_key
            if current_key:
                try:
                    import anthropic
                    self._client = anthropic.Anthropic(api_key=current_key)
                    logger.info("Anthropic client initialized/updated successfully.")
                except ImportError:
                    logger.warning(
                        "anthropic package not installed - run "
                        "'pip install anthropic' to enable InsightAgent's LLM reasoning."
                    )
                    self._client = None
                except Exception as exc:
                    logger.error(f"Failed to initialize Anthropic client: {exc}")
                    self._client = None
            else:
                self._client = None
        return self._client

    def is_available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str, system: str = None) -> str:
        """
        Returns plain text from the model. Raises RuntimeError if the
        client isn't configured - callers should check is_available()
        first, or catch the exception to fall back gracefully.
        """
        active_client = self.client
        if not active_client:
            raise RuntimeError(
                "LLM client not configured: set ANTHROPIC_API_KEY to enable "
                "the InsightAgent's reasoning step."
            )

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        try:
            response = active_client.messages.create(**kwargs)
            return "".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
        except Exception as exc:
            logger.error(f"LLM call failed: {exc}")
            raise
