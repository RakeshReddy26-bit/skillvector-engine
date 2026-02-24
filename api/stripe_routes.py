"""Stripe payment endpoints for SkillVector Pro."""

import logging
import os

import stripe
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api.auth import get_current_user
from src.db.models import UserRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stripe", tags=["stripe"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.post("/create-checkout")
def create_checkout(request: Request):
    """Create a Stripe Checkout Session for Pro subscription."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated."})

    if user.get("plan_tier") == "pro":
        return JSONResponse(status_code=400, content={"error": "Already on Pro plan."})

    if not stripe.api_key:
        return JSONResponse(
            status_code=503, content={"error": "Payment service not configured."}
        )

    user_repo = UserRepository()
    try:
        # Create or reuse Stripe customer
        if user.get("stripe_customer_id"):
            customer_id = user["stripe_customer_id"]
        else:
            customer = stripe.Customer.create(
                email=user["email"],
                metadata={"skillvector_user_id": user["id"]},
            )
            customer_id = customer.id
            user_repo.update_plan(
                user["id"],
                plan_tier="free",
                stripe_customer_id=customer_id,
            )

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            success_url=f"{FRONTEND_URL}?upgrade=success",
            cancel_url=f"{FRONTEND_URL}?upgrade=cancelled",
            metadata={"skillvector_user_id": user["id"]},
        )

        return {"checkout_url": session.url}

    except stripe.StripeError as e:
        logger.error("Stripe checkout error: %s", e)
        return JSONResponse(status_code=500, content={"error": "Payment service error."})


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.SignatureVerificationError) as e:
        logger.warning("Stripe webhook verification failed: %s", e)
        return JSONResponse(status_code=400, content={"error": "Invalid signature."})

    user_repo = UserRepository()

    # Handle checkout completed — activate Pro
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        user_id = session.get("metadata", {}).get("skillvector_user_id")

        if user_id:
            user_repo.update_plan(
                user_id,
                plan_tier="pro",
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
            )
            logger.info("Activated Pro for user %s", user_id)

    # Handle subscription cancelled — downgrade to free
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        user = user_repo.get_user_by_stripe_customer(customer_id)
        if user:
            user_repo.update_plan(user["id"], plan_tier="free")
            logger.info("Downgraded user %s to free", user["id"])

    return {"status": "ok"}


@router.get("/portal")
def customer_portal(request: Request):
    """Create a Stripe Customer Portal session for managing subscription."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated."})

    if not user.get("stripe_customer_id"):
        return JSONResponse(status_code=400, content={"error": "No active subscription."})

    if not stripe.api_key:
        return JSONResponse(
            status_code=503, content={"error": "Payment service not configured."}
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=user["stripe_customer_id"],
            return_url=FRONTEND_URL,
        )
        return {"portal_url": session.url}

    except stripe.StripeError as e:
        logger.error("Stripe portal error: %s", e)
        return JSONResponse(status_code=500, content={"error": "Payment service error."})
