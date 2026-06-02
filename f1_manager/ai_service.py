"""LLM integration with fallback generation and caching."""

from __future__ import annotations

import hashlib
import json
import os
import random
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List


class AIService:
    def __init__(self, cache_path: str = ".ai_cache.json", provider: str | None = None, model: str | None = None):
        self.cache_file = Path(cache_path)
        self.cache: Dict[str, str] = {}
        self._load_cache()
        self.provider = provider or self._resolve_provider()
        self.model = model or self._resolve_model()

    def _resolve_provider(self) -> str:
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        return "fallback"

    def _resolve_model(self) -> str:
        if self.provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        if self.provider == "anthropic":
            return os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
        return "procedural-sim"

    def generate(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 220) -> str:
        cache_key = self._cache_key(prompt, temperature, max_tokens)
        if cache_key in self.cache:
            return self.cache[cache_key]

        if self.provider == "openai":
            response = self._call_openai(prompt, temperature, max_tokens)
        elif self.provider == "anthropic":
            response = self._call_anthropic(prompt, temperature, max_tokens)
        else:
            response = self._fallback_response(prompt)

        self.cache[cache_key] = response
        self._persist_cache()
        return response

    def generate_batch(self, prompts: Iterable[str]) -> List[str]:
        return [self.generate(prompt) for prompt in prompts]

    def _cache_key(self, prompt: str, temperature: float, max_tokens: int) -> str:
        payload = f"{self.provider}|{self.model}|{temperature}|{max_tokens}|{prompt}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _load_cache(self) -> None:
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def _persist_cache(self) -> None:
        self.cache_file.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")

    def _fallback_response(self, prompt: str) -> str:
        snippets = [
            "Pressure rises after mixed telemetry and tense debriefs.",
            "A pragmatic compromise keeps morale stable for now.",
            "Sponsor expectations increase as public interest grows.",
            "Technical staff disagree on setup but align under deadline.",
            "Driver confidence shifts after strategic calls under safety-car risk.",
        ]
        seed = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        selected = rng.sample(snippets, k=2)
        return " ".join(selected)

    def _call_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._fallback_response(prompt)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You generate realistic, grounded F1 management scenarios."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
            return self._fallback_response(prompt)

    def _call_anthropic(self, prompt: str, temperature: float, max_tokens: int) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return self._fallback_response(prompt)

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": "You generate realistic, grounded F1 management scenarios.",
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["content"][0]["text"].strip()
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
            return self._fallback_response(prompt)
