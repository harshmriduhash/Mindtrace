"""India-capable billing via Razorpay (optional keys). Stripe intentionally not used."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import AppError
from sqlalchemy import select

from app.db.session import get_db
from app.models import Subscription, User
from app.services.analytics import track

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutIn(BaseModel):
    plan_id: str = "plus"


@router.get("/plans")
def plans() -> dict[str, Any]:
    return {
        "currency": "INR",
        "provider": "razorpay",
        "plans": [
            {"id": "free", "name": "Free", "price_inr": 0, "features": ["1 skill path", "Limited AI"]},
            {"id": "plus", "name": "Plus", "price_inr": 799, "features": ["Multiple paths", "Higher AI quota"]},
        ],
        "note": "Stripe is not used (not operating in India). Set RAZORPAY_KEY_ID/SECRET to enable checkout.",
    }


@router.post("/checkout")
def checkout(
    payload: CheckoutIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise AppError(
            "payments_unconfigured",
            "Razorpay keys are not configured. Billing UI is ready; add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.",
            503,
        )
    # Stub order object — integrate Razorpay Orders API when keys are live.
    order_id = f"order_stub_{user.id.hex[:10]}_{payload.plan_id}"
    track(db, user_id=user.id, event_name="checkout_started", properties={"plan_id": payload.plan_id})
    db.commit()
    return {
        "provider": "razorpay",
        "key_id": settings.razorpay_key_id,
        "order_id": order_id,
        "amount_paise": 79900 if payload.plan_id == "plus" else 0,
        "currency": "INR",
        "plan_id": payload.plan_id,
    }


@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")
    if settings.razorpay_webhook_secret:
        expected = hmac.new(
            settings.razorpay_webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise AppError("invalid_signature", "Invalid webhook signature", 400)
    # Entitlement updates would parse event + set Subscription here.
    return {"status": "accepted"}


@router.get("/entitlements")
def entitlements(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    return {
        "plan": user.plan,
        "subscription_status": sub.status if sub else "none",
        "provider": sub.provider if sub else "none",
    }
