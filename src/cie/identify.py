"""Exact-product identification from a page (T-0402, MASTER §8/§9).

Given an already-fetched page (HTML string) this extracts the product's
identity and maps it onto a `Component` record. It performs NO network
access: fetching is delegated to an injected acquirer. It never
fabricates values and never degrades to a generic search — an opaque page
raises `IdentificationError`.

Untrusted input is treated as data: `<script>` contents are ignored
except schema.org JSON-LD, which is parsed as JSON only (never executed).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Callable, Iterable, Protocol

from src.cie.model import UNKNOWN, Component, is_unknown
from src.cie.target import parse_target


class IdentificationError(Exception):
    """Raised when a page cannot yield an exact product identity."""


class Acquirer(Protocol):
    """A callable that returns the HTML for a URL (injected; no network)."""

    def __call__(self, url: str) -> str: ...


# --------------------------------------------------------------------------
# Page parsing
# --------------------------------------------------------------------------

_META_KEYS = (
    "og:title",
    "og:site_name",
    "og:url",
    "product:brand",
    "product:retailer",
    "product:price:amount",
    "product:price:currency",
)


class _PageParser(HTMLParser):
    """Collect title, product meta tags, canonical link and JSON-LD blobs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.jsonld: list[str] = []
        self._in_title = False
        self._title_parts: list[str] = []
        self._script_is_jsonld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "meta":
            key = (attributes.get("property") or attributes.get("name") or "").lower()
            content = attributes.get("content")
            if key in _META_KEYS and content is not None and key not in self.meta:
                self.meta[key] = content.strip()
        elif tag == "link":
            rel = attributes.get("rel", "").lower()
            href = attributes.get("href", "").strip()
            if "canonical" in rel.split() and href and self.canonical is None:
                self.canonical = href
        elif tag == "script":
            self._script_is_jsonld = "ld+json" in attributes.get("type", "").lower()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            text = "".join(self._title_parts).strip()
            if text and self.title is None:
                self.title = text
        elif tag == "script":
            self._script_is_jsonld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        elif self._script_is_jsonld:
            self.jsonld.append(data)


# --------------------------------------------------------------------------
# JSON-LD (schema.org) helpers
# --------------------------------------------------------------------------


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _name_of(value: Any) -> Any:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        name = value.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    if isinstance(value, list) and value:
        return _name_of(value[0])
    return UNKNOWN


def _find_products(node: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        node_type = node.get("@type")
        types = [node_type] if isinstance(node_type, str) else _as_list(node_type)
        if any(str(t).lower() == "product" for t in types):
            found.append(node)
        for value in node.values():
            found.extend(_find_products(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_find_products(item))
    return found


def _seller_of(offers: Any) -> Any:
    for offer in _as_list(offers):
        if isinstance(offer, dict):
            seller = offer.get("seller") or offer.get("offeredBy")
            name = _name_of(seller)
            if not is_unknown(name):
                return name
    return UNKNOWN


def _specs_of(products: Iterable[dict[str, Any]]) -> dict[str, Any]:
    specs: dict[str, Any] = {}
    for product in products:
        for prop in _as_list(product.get("additionalProperty")):
            if isinstance(prop, dict):
                key = prop.get("name") or prop.get("propertyID")
                value = prop.get("value")
                if isinstance(key, str) and key.strip() and value is not None:
                    specs.setdefault(key.strip(), value)
    return specs


def _first_product_json(url: str, html: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    parser = _PageParser()
    parser.feed(html)
    products: list[dict[str, Any]] = []
    for blob in parser.jsonld:
        try:
            data = json.loads(blob)
        except (ValueError, TypeError):
            continue
        products.extend(_find_products(data))
    meta = dict(parser.meta)
    meta["_title"] = parser.title or UNKNOWN
    meta["_canonical"] = parser.canonical or UNKNOWN
    return products, meta


# --------------------------------------------------------------------------
# Identification
# --------------------------------------------------------------------------


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@dataclass(frozen=True)
class Identification:
    """The exact-product identity extracted from a single page."""

    url: str
    host: str
    title: Any = UNKNOWN
    manufacturer: Any = UNKNOWN
    model: Any = UNKNOWN
    sku: Any = UNKNOWN
    part_number: Any = UNKNOWN
    seller: Any = UNKNOWN
    product_url: Any = UNKNOWN
    specifications: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"url": self.url, "host": self.host}
        for name in (
            "title",
            "manufacturer",
            "model",
            "sku",
            "part_number",
            "seller",
            "product_url",
        ):
            value = getattr(self, name)
            if not is_unknown(value):
                data[name] = value
        if self.specifications:
            data["specifications"] = dict(self.specifications)
        return data

    def component_id(self) -> str:
        key = self.model
        for candidate in (self.model, self.sku, self.part_number, self.title):
            if not is_unknown(candidate):
                key = candidate
                break
        if is_unknown(key):
            raise IdentificationError("cannot derive a component id without identity")
        slug = _slug(str(key))
        if not slug:
            raise IdentificationError("identity produced an empty component id")
        return f"{self.host}-{slug}" if self.host else slug

    def to_component(self, component_id: str | None = None) -> Component:
        fields: dict[str, Any] = {
            "id": component_id or self.component_id(),
            "source_urls": (self.url,),
        }
        mapping = {
            "name": self.title,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "part_number": self.part_number,
            "sku": self.sku,
        }
        for field_name, value in mapping.items():
            if not is_unknown(value):
                fields[field_name] = value
        if self.specifications:
            fields["specifications"] = dict(self.specifications)
        return Component(**fields)


def identify_page(url: str, html: str) -> Identification:
    """Identify an exact product from a page. Raises on an opaque page."""
    target = parse_target(url)
    if not isinstance(html, str) or not html.strip():
        raise IdentificationError("page content is empty")
    products, meta = _first_product_json(target.url, html)

    title = _name_of(products[0].get("name")) if products else UNKNOWN
    manufacturer = UNKNOWN
    model = UNKNOWN
    sku = UNKNOWN
    part_number = UNKNOWN
    seller = UNKNOWN

    for product in products:
        if is_unknown(manufacturer):
            manufacturer = _name_of(product.get("manufacturer")) or _name_of(
                product.get("brand")
            )
        if is_unknown(model):
            model = _name_of(product.get("model"))
        if is_unknown(sku):
            sku = _name_of(product.get("sku"))
        if is_unknown(part_number):
            part_number = _name_of(product.get("mpn"))
        if is_unknown(seller):
            seller = _seller_of(product.get("offers"))

    if is_unknown(title):
        title = meta.get("og:title", UNKNOWN)
    if is_unknown(title):
        title = meta["_title"]
    if is_unknown(manufacturer):
        manufacturer = meta.get("product:brand", UNKNOWN)
    if is_unknown(seller):
        seller = meta.get("product:retailer", UNKNOWN)

    product_url = meta.get("og:url", UNKNOWN)
    if is_unknown(product_url):
        product_url = meta["_canonical"]

    specifications = _specs_of(products)

    identification = Identification(
        url=target.url,
        host=target.host,
        title=title,
        manufacturer=manufacturer,
        model=model,
        sku=sku,
        part_number=part_number,
        seller=seller,
        product_url=product_url if not is_unknown(product_url) else target.url,
        specifications=specifications,
    )

    has_identity = any(
        not is_unknown(value)
        for value in (title, manufacturer, model, sku, part_number)
    )
    if not has_identity:
        raise IdentificationError(
            "no exact product identity found; refuse generic search (§8)"
        )
    return identification


def ingest(url: str, acquire: Callable[[str], str]) -> Identification:
    """Acquire a page via the injected acquirer, then identify it."""
    target = parse_target(url)
    html = acquire(target.url)
    return identify_page(target.url, html)


__all__ = [
    "Acquirer",
    "Identification",
    "IdentificationError",
    "identify_page",
    "ingest",
]