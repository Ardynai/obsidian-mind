"""Local-only UI bridge: stdlib HTTP on 127.0.0.1 plus static assets.

This package never adds runtime dependencies. It reuses existing engine
functions and does not bypass consent, emergency, or framing gates.
"""

from .server import make_server, serve_ui

__all__ = ["make_server", "serve_ui"]
