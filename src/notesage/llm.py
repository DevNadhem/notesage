import json
import urllib.error
import urllib.request

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"


class LLMError(Exception):
    """Raised when the language model cannot produce an answer."""


class OllamaClient:
    """Calls a local Ollama server. Uses only the standard library."""

    def __init__(self, model=DEFAULT_OLLAMA_MODEL, base_url=DEFAULT_OLLAMA_URL, timeout=120):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt):
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise LLMError(
                f"Could not reach Ollama at {self.base_url}. "
                "Is it running, and have you pulled the model?"
            ) from exc
        except (json.JSONDecodeError, TimeoutError) as exc:
            raise LLMError(f"Bad or slow response from Ollama: {exc}") from exc

        text = body.get("response", "").strip()
        if not text:
            raise LLMError("Ollama returned an empty answer")
        return text