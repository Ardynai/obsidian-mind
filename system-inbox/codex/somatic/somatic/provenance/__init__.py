"""Content-addressed provenance helpers (stdlib). P2P distribution stays disabled."""

from .cas import address_record, hash_payload, verify_file, verify_record

__all__ = ["address_record", "hash_payload", "verify_file", "verify_record"]
