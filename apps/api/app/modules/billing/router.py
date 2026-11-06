"""India-capable billing via Razorpay Orders + payment webhooks."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models import AuditEvent, Subscription, User
from app.services.analytics import track

router = APIRouter(prefix="/billing", tags=["billing"])

PLAN_AMOUNTS_PAISE = {
    "plus": 79900,
    "pro": 149900,
}


class CheckoutIn(BaseModel):
    plan_id: str = "plus"


@router.get("/plans")
def plans() -> dict[str, Any]:
    settings = get_settings()
    configured = bool(settings.razorpay_key_id and settings.razorpay_key_secret)
    return {
        "currency": "INR",
        "provider": "razorpay",
        "configured": configured,
        "plans": [
            {"id": "free", "name": "Free", "price_inr": 0, "features": ["1 skill path", "Limited AI"]},
            {"id": "plus", "name": "Plus", "price_inr": 799, "features": ["Multiple paths", "Higher AI quota"]},
            {"id": "pro", "name": "Pro", "price_inr": 1499, "features": ["Voice + sandbox", "Exports", "Higher quotas"]},
        ],
        "note": (
            "Razorpay checkout is live when RAZORPAY_KEY_ID/SECRET are set."
            if configured
            else "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to enable live checkout."
        ),
    }


def _create_razorpay_order(*, amount_paise: int, receipt: str, notes: dict[str, str]) -> dict[str, Any]:
    settings = get_settings()
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            "https://api.razorpay.com/v2/orders" if False else "https://api.razorpay.com/v1/orders",
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret),
            json={
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt[:40],
                "notes": notes,
            },
        )
    if resp.status_code >= 400:
        raise AppError("razorpay_error", f"Razorpay order failed: {resp.text[:300]}", 502)
    return resp.json()


@router.post("/checkout")
def checkout(
    payload: CheckoutIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise AppError(
            "payments_unconfigured",
            "Razorpay keys are not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.",
            503,
        )
    if payload.plan_id not in PLAN_AMOUNTS_PAISE:
        raise AppError("invalid_plan", "Unknown plan_id", 400)

    amount = PLAN_AMOUNTS_PAISE[payload.plan_id]
    order = _create_razorpay_order(
        amount_paise=amount,
        receipt=f"mt_{user.id.hex[:12]}",
        notes={"user_id": str(user.id), "plan_id": payload.plan_id},
    )
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not sub:
        sub = Subscription(user_id=user.id, provider="razorpay", status="created", plan_id=payload.plan_id)
        db.add(sub)
    else:
        sub.provider = "razorpay"
        sub.status = "checkout_started"
        sub.plan_id = payload.plan_id
    sub.provider_subscription_id = order.get("id")
    track(db, user_id=user.id, event_name="checkout_started", properties={"plan_id": payload.plan_id, "order_id": order.get("id")})
    db.commit()
    return {
        "provider": "razorpay",
        "key_id": settings.razorpay_key_id,
        "order_id": order.get("id"),
        "amount_paise": amount,
        "currency": "INR",
        "plan_id": payload.plan_id,
    }


def _activate_plan(db: Session, *, user_id: str, plan_id: str, payment_id: str | None, order_id: str | None) -> None:
    from uuid import UUID

    try:
        uid = UUID(user_id)
    except (ValueError, TypeError):
        return
    user = db.get(User, uid)
    if not user:
        return
    user.plan = plan_id if plan_id in {"plus", "pro"} else "plus"
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not sub:
        sub = Subscription(user_id=user.id, provider="razorpay", plan_id=user.plan)
        db.add(sub)
    sub.provider = "razorpay"
    sub.status = "active"
    sub.plan_id = user.plan
    sub.provider_subscription_id = order_id or sub.provider_subscription_id
    sub.provider_customer_id = payment_id
    sub.current_period_end = datetime.now(UTC) + timedelta(days=30)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="subscription_activated",
            target_type="subscription",
            target_id=str(sub.id),
            metadata_json={"plan_id": user.plan, "payment_id": payment_id, "order_id": order_id},
        )
    )


@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")
    if settings.razorpay_webhook_secret:
        expected = hmac.new(settings.razorpay_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise AppError("invalid_signature", "Invalid webhook signature", 400)

    try:
        event = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AppError("invalid_payload", "Invalid JSON body", 400) from exc

    event_name = event.get("event") or ""
    payload = event.get("payload") or {}

    if event_name in {"payment.captured", "order.paid"}:
        payment = (payload.get("payment") or {}).get("entity") or {}
        order = (payload.get("order") or {}).get("entity") or payment
        notes = payment.get("notes") or order.get("notes") or {}
        user_id = notes.get("user_id")
        plan_id = notes.get("plan_id") or "plus"
        if user_id:
            _activate_plan(
                db,
                user_id=str(user_id),
                plan_id=str(plan_id),
                payment_id=payment.get("id"),
                order_id=order.get("id") or payment.get("order_id"),
            )
            db.commit()
    elif event_name in {"subscription.cancelled", "payment.failed"}:
        # Soft-fail: leave plan until period end; mark subscription status.
        payment = (payload.get("payment") or {}).get("entity") or {}
        notes = payment.get("notes") or {}
        if notes.get("user_id"):
            from uuid import UUID

            try:
                uid = UUID(str(notes["user_id"]))
            except (ValueError, TypeError):
                uid = None
            if uid:
                sub = db.scalar(select(Subscription).where(Subscription.user_id == uid))
                if sub and event_name == "subscription.cancelled":
                    sub.status = "cancelled"
                    db.commit()

    return {"status": "accepted"}


@router.get("/entitlements")
def entitlements(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    sub = db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    return {
        "plan": user.plan,
        "subscription_status": sub.status if sub else "none",
        "provider": sub.provider if sub else "none",
        "current_period_end": sub.current_period_end.isoformat() if sub and sub.current_period_end else None,
    }
