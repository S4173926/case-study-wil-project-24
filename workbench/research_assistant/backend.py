"""Apple MLX adapter with immutable revision logging and explicit stop metadata."""
from __future__ import annotations
import json
import platform
import threading
import time
from dataclasses import dataclass, asdict
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

MODEL = "mlx-community/Qwen2.5-3B-Instruct-4bit"

@dataclass
class Completion:
    text: str
    finish_reason: str
    prompt_tokens: int = 0
    generation_tokens: int = 0
    seconds: float = 0
    def to_dict(self): return asdict(self)


class MLXBackend:
    def __init__(self, root: Path = ROOT, repo: str = MODEL, context_limit: int = 8192):
        self.root, self.repo, self.context_limit = root, repo, context_limit
        self.model = self.tokenizer = None
        self.info = {"backend":"mlx", "model":repo,"revision":"not_loaded", "temperature":0.0}
        self._lock = threading.Lock()

    def _load(self):
        if self.model is not None: return
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            raise RuntimeError("MLX inference requires native ARM64 Python on an Apple Silicon Mac. Deterministic source-linked composition works here.")
        from huggingface_hub import snapshot_download
        from mlx_lm import load
        lockfile=self.root / "results/model_revision.json"
        revision=None
        reference=self.root / "config/model_reference.json"
        if reference.exists():
            baseline=json.loads(reference.read_text(encoding="utf-8"))
            if baseline.get("model")==self.repo:revision=baseline.get("revision")
        if lockfile.exists():
            record=json.loads(lockfile.read_text(encoding="utf-8"))
            if record.get("model")!=self.repo: raise RuntimeError("Model revision file belongs to a different model; use a separate results folder.")
            revision=record["revision"]
        # Hugging Face cache is reused. Once resolved, future loads request the exact revision.
        try:
            snapshot=Path(snapshot_download(self.repo, revision=revision, local_files_only=True))
        except Exception:
            snapshot=Path(snapshot_download(self.repo, revision=revision))
        commit=snapshot.name
        if len(commit)!=40 or any(c not in "0123456789abcdef" for c in commit):
            raise RuntimeError("Could not establish immutable model snapshot revision")
        self.model, self.tokenizer=load(str(snapshot))
        self.info.update({"revision":commit,"context_limit":self.context_limit})
        for package in ("mlx","mlx-lm","huggingface-hub"):
            try: self.info[package]=version(package)
            except PackageNotFoundError: self.info[package]="unknown"
        lockfile.parent.mkdir(parents=True,exist_ok=True)
        tmp=lockfile.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.info,indent=2), encoding="utf-8"); tmp.replace(lockfile)

    def count_tokens(self, messages: list[dict]) -> int:
        with self._lock:
            self._load()
            text=self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            return len(self.tokenizer.encode(text))

    def complete(self, messages: list[dict], max_tokens: int=1200) -> Completion:
        with self._lock:
            self._load()
            from mlx_lm import stream_generate
            from mlx_lm.sample_utils import make_sampler
            text=self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
            prompt=self.tokenizer.encode(text)
            if len(prompt)+max_tokens>self.context_limit:
                raise RuntimeError(f"Input budget exceeded ({len(prompt)}+{max_tokens}>{self.context_limit}); no source text was silently truncated")
            parts=[]; last=None; start=time.perf_counter()
            for response in stream_generate(self.model,self.tokenizer,prompt=prompt,max_tokens=max_tokens,
                                            sampler=make_sampler(temp=0.0)):
                parts.append(response.text); last=response
            if last is None: return Completion("","empty",seconds=time.perf_counter()-start)
            stop=getattr(last,"finish_reason",None)
            if stop not in {"stop","length"}: stop="unknown"
            return Completion("".join(parts),stop,int(getattr(last,"prompt_tokens",len(prompt))),
                              int(getattr(last,"generation_tokens",0)),time.perf_counter()-start)
