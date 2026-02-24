"""Tests for Stripe integration: webhook, checkout, portal."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Create a TestClient with mocked pipeline and rate limiter."""
    with (
        patch("api.main.SkillVectorPipeline") as MockPipeline,
        patch("api.main.RateLimiter") as MockLimiter,
    ):
        mock_pipeline = MagicMock()
        MockPipeline.return_value = mock_pipeline
        mock_limiter = MagicMock()
        mock_limiter.check.return_value = (True, "ok")
        MockLimiter.return_value = mock_limiter

        from api.main import app
        import api.main as api_mod

        api_mod.pipeline = mock_pipeline
        api_mod.rate_limiter = mock_limiter

        with TestClient(app) as c:
            yield c


# ── Webhook: checkout.session.completed ──────────────────────────────────────


@patch("api.stripe_routes.UserRepository")
@patch("api.stripe_routes.stripe.Webhook.construct_event")
def test_webhook_checkout_completed(mock_construct, MockRepo, client):
    """Webhook should activate Pro on checkout.session.completed."""
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_abc",
                "subscription": "sub_123",
                "metadata": {"skillvector_user_id": "user-1"},
            }
        },
    }
    mock_repo = MockRepo.return_value

    resp = client.post(
        "/stripe/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={"stripe-signature": "t=123,v1=abc"},
    )
    assert resp.status_code == 200
    mock_repo.update_plan.assert_called_once_with(
        "user-1",
        plan_tier="pro",
        stripe_customer_id="cus_abc",
        stripe_subscription_id="sub_123",
    )


# ── Webhook: customer.subscription.deleted ───────────────────────────────────


@patch("api.stripe_routes.UserRepository")
@patch("api.stripe_routes.stripe.Webhook.construct_event")
def test_webhook_subscription_deleted(mock_construct, MockRepo, client):
    """Webhook should downgrade to free on subscription.deleted."""
    mock_construct.return_value = {
        "type": "customer.subscription.deleted",
        "data": {"object": {"customer": "cus_abc"}},
    }
    mock_repo = MockRepo.return_value
    mock_repo.get_user_by_stripe_customer.return_value = {"id": "user-1", "email": "a@b.com"}

    resp = client.post(
        "/stripe/webhook",
        content=b'{"type": "customer.subscription.deleted"}',
        headers={"stripe-signature": "t=123,v1=abc"},
    )
    assert resp.status_code == 200
    mock_repo.update_plan.assert_called_once_with("user-1", plan_tier="free")


# ── Webhook: invalid signature ───────────────────────────────────────────────


@patch("api.stripe_routes.stripe.Webhook.construct_event")
def test_webhook_invalid_signature(mock_construct, client):
    """Webhook should return 400 on invalid signature."""
    import stripe

    mock_construct.side_effect = stripe.SignatureVerificationError("bad sig", "sig_header")

    resp = client.post(
        "/stripe/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={"stripe-signature": "invalid"},
    )
    assert resp.status_code == 400
    assert "signature" in resp.json()["error"].lower()


# ── Create checkout: requires auth ───────────────────────────────────────────


def test_create_checkout_requires_auth(client):
    """create-checkout should return 401 without auth token."""
    resp = client.post("/stripe/create-checkout")
    assert resp.status_code == 401


# ── Create checkout: rejects already-pro ─────────────────────────────────────


@patch("api.stripe_routes.get_current_user")
def test_create_checkout_rejects_pro(mock_user, client):
    """create-checkout should reject users already on Pro."""
    mock_user.return_value = {
        "id": "user-1",
        "email": "pro@example.com",
        "plan_tier": "pro",
        "stripe_customer_id": "cus_abc",
    }

    resp = client.post("/stripe/create-checkout")
    assert resp.status_code == 400
    assert "Already" in resp.json()["error"]


# ── Portal: requires stripe_customer_id ──────────────────────────────────────


@patch("api.stripe_routes.get_current_user")
def test_portal_requires_stripe_customer(mock_user, client):
    """Portal should return 400 if user has no stripe_customer_id."""
    mock_user.return_value = {
        "id": "user-1",
        "email": "free@example.com",
        "plan_tier": "free",
        "stripe_customer_id": None,
    }

    resp = client.get("/stripe/portal")
    assert resp.status_code == 400
    assert "subscription" in resp.json()["error"].lower()
