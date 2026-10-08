"""
Minimal LLM client. No SDKs: urllib only, so it runs anywhere the translator runs.

Providers (pick with SEMAGRAM_PROVIDER or --provider):

  anthropic   Anthropic Messages API.      needs ANTHROPIC_API_KEY. model: SEMAGRAM_MODEL (default claude-sonnet-5-5)
  openai      any OpenAI-compatible server: Ollama (http://localhost:11434/v1), vLLM, llama.cpp,
              LM Studio, or OpenAI itself.  base url: SEMAGRAM_BASE_URL, key: SEMAGRAM_API_KEY (optional for local), model: SEMAGRAM_MODEL
  stub        offline; returns canned text. For testing the pipeline without a model.

Every provider exposes one call: complete(system, user) -> str.

The Anthropic path caches the system prompt and records token usage in
LLM.usage, so `synth` can report whether the cache is actually being read.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


class LLM:
    def __init__(self, provider: str | None = None, model: str | None = None,
                 base_url: str | None = None, temperature: float | None = None, max_tokens: int = 8192):
        self.provider = provider or os.environ.get("SEMAGRAM_PROVIDER", "anthropic")
        self.model = model or os.environ.get("SEMAGRAM_MODEL") or {
            "anthropic": "claude-sonnet-5-5", "openai": "llama3.1", "stub": "stub"}[self.provider]
        self.base_url = (base_url or os.environ.get("SEMAGRAM_BASE_URL", "http://localhost:11434/v1")).rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.calls = 0
        self.stub_responses: list[str] = []
        # token accounting, so a corpus run can show whether caching is working
        self.usage = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}

    # ------------------------------------------------------------ public
    def complete(self, system: str, user: str) -> str:
        self.calls += 1
        if self.provider == "stub":
            return self.stub_responses.pop(0) if self.stub_responses else "🔷"
        if self.provider == "anthropic":
            return self._anthropic(system, user)
        if self.provider == "openai":
            return self._openai(system, user)
        raise ValueError(f"unknown provider {self.provider!r}")

    # ------------------------------------------------------------ providers
    def _post(self, url: str, headers: dict, body: dict, retries: int = 3) -> dict:
        data = json.dumps(body).encode("utf-8")
        for attempt in range(retries):
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 529) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"{url} -> HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}") from None
        raise RuntimeError("unreachable")

    def _anthropic(self, system: str, user: str) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        # The system prompt is the whole grammar plus the dictionary (~5.3k
        # tokens) and is byte-identical across every call in a run, so it is
        # cached: reads cost 0.1x of input, writes 1.25x, break-even on call
        # two. Keep it first and leave the per-paragraph task in `messages`,
        # because caching is a prefix match.
        body = {"model": self.model, "max_tokens": self.max_tokens,
                "system": [{"type": "text", "text": system,
                            "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": user}]}
        # Current models reject a non-default temperature (400), so send it
        # only when a caller explicitly asks for one.
        if self.temperature is not None:
            body["temperature"] = self.temperature
        out = self._post("https://api.anthropic.com/v1/messages",
                         {"x-api-key": key, "anthropic-version": "2023-06-01"}, body)
        u = out.get("usage", {})
        self.usage["input"] += u.get("input_tokens", 0)
        self.usage["output"] += u.get("output_tokens", 0)
        self.usage["cache_read"] += u.get("cache_read_input_tokens", 0)
        self.usage["cache_write"] += u.get("cache_creation_input_tokens", 0)
        return "".join(b.get("text", "") for b in out.get("content", []))

    def _openai(self, system: str, user: str) -> str:
        headers = {}
        key = os.environ.get("SEMAGRAM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if key:
            headers["Authorization"] = f"Bearer {key}"
        body = {"model": self.model, "max_tokens": self.max_tokens,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if self.temperature is not None:
            body["temperature"] = self.temperature
        out = self._post(f"{self.base_url}/chat/completions", headers, body)
        return out["choices"][0]["message"]["content"]
