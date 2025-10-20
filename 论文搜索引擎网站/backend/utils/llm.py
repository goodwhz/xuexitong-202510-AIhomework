import os
from typing import Optional, List

from dotenv import load_dotenv

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
except Exception:  # pragma: no cover
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    pipeline = None  # type: ignore
    torch = None  # type: ignore


load_dotenv()


class LocalQwenLLM:
    """Minimal local Qwen wrapper using transformers pipeline.

    If transformers/torch are unavailable, it degrades to a simple echo.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> None:
        self.model_path = model_path or os.getenv("LLM_MODEL_PATH", "Qwen/Qwen2-1.5B-Instruct")
        self.device = device or os.getenv("LLM_DEVICE", "cuda" if (torch and torch.cuda.is_available()) else "cpu")
        self.max_tokens = int(max_tokens or os.getenv("LLM_MAX_TOKENS", "512"))
        self.temperature = float(temperature or os.getenv("LLM_TEMPERATURE", "0.3"))
        self._pipe: Optional[object] = None

    def _ensure_pipeline(self) -> None:
        if self._pipe is not None:
            return
        if pipeline is None or AutoTokenizer is None or AutoModelForCausalLM is None:
            self._pipe = None
            return
        self._pipe = pipeline(
            "text-generation",
            model=self.model_path,
            tokenizer=self.model_path,
            torch_dtype=(torch.float16 if self.device.startswith("cuda") else None),
            device_map="auto" if self.device.startswith("cuda") else None,
        )

    def generate(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        self._ensure_pipeline()
        if self._pipe is None:
            text = f"[Local Qwen unavailable] Echo: {prompt[:2000]}"
            return text

        params = {
            "max_new_tokens": self.max_tokens,
            "temperature": self.temperature,
            "do_sample": True,
            "eos_token_id": None,
        }
        out = self._pipe(prompt, **params)
        if isinstance(out, list) and len(out) > 0 and "generated_text" in out[0]:
            text = out[0]["generated_text"][len(prompt):].strip()
        else:
            text = str(out)
        if stop:
            for s in stop:
                idx = text.find(s)
                if idx != -1:
                    text = text[:idx]
                    break
        return text


