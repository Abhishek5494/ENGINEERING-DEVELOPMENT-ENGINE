"""Ingestion target: a validated product URL (T-0402).

No network. `parse_target` only validates and normalises a caller-supplied
URL so the rest of the CIE can rely on a well-formed target.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from urllib.parse import urlsplit

_ALLOWED_SCHEMES = ("http", "https")


class TargetError(Exception):
    """Raised when a supplied URL is not a usable ingestion target."""


@dataclass(frozen=True)
class Target:
    """A validated product URL split into its components."""

    url: str
    scheme: str
    host: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def parse_target(url: object) -> Target:
    """Validate and normalise a product URL.

    Requires an absolute http/https URL with a host. The host is
    lowercased and a leading ``www.`` is stripped; the original (stripped)
    URL is preserved verbatim.
    """
    if not isinstance(url, str) or not url.strip():
        raise TargetError("target URL must be a non-empty string")
    candidate = url.strip()
    parts = urlsplit(candidate)
    scheme = parts.scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise TargetError(f"unsupported URL scheme: {parts.scheme!r}")
    host = (parts.hostname or "").lower()
    if not host:
        raise TargetError("target URL has no host")
    if host.startswith("www."):
        host = host[4:]
    return Target(url=candidate, scheme=scheme, host=host, path=parts.path)


__all__ = ["Target", "TargetError", "parse_target"]