import os

from auth import _extract_roles


def test_extract_roles_supports_audience_roles_claim(monkeypatch):
    monkeypatch.setenv("AUTH0_DOMAIN", "tenant.example.com")
    monkeypatch.setenv("AUTH0_API_AUDIENCE", "audience")

    payload = {
        "audience/roles": ["admin", "customer"],
    }

    assert _extract_roles(payload) == ["admin", "customer"]


def test_extract_roles_prefers_standard_roles_claim(monkeypatch):
    monkeypatch.setenv("AUTH0_DOMAIN", "tenant.example.com")
    monkeypatch.setenv("AUTH0_API_AUDIENCE", "audience")

    payload = {
        "roles": ["customer"],
        "audience/roles": ["admin"],
    }

    assert _extract_roles(payload) == ["customer"]
