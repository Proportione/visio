"""LLM fusion layer.

The public release ships a deterministic stub. Production replaces
``visio.llm.stub.fuse`` with a Vertex AI / Anthropic / Ollama call. The
contract is the ``Recommendation`` dataclass returned by ``fuse``.
"""

from .stub import fuse, Recommendation

__all__ = ["fuse", "Recommendation"]
