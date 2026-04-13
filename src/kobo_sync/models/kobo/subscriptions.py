from datetime import datetime
from enum import Enum
from typing import Literal, Sequence
from uuid import UUID


class SubscriptionPrice:
    currency: str
    geo: str
    price: float
    tax_in: bool
    valid_from: datetime


class SubscriptionPhaseType(Enum):
    TRIAL = "Trial"
    ACTIVE = "Active"


class SubscriptionPhaseDuration:
    number: int
    unit: Literal["Days"]


class SubscriptionBillingInterval:
    interval_units: int
    interval_unit_type: Literal["Days"]


class SubscriptionBilling:
    initial_billing_date_offset: SubscriptionBillingInterval
    rebill_interval: SubscriptionBillingInterval


class SubscriptionPhase:
    order: int
    phase_type: str
    prices: Sequence[SubscriptionPrice]

    billing_specification: SubscriptionBilling
    duration: SubscriptionPhaseDuration


class SubscriptionTier:
    id: UUID
    description: str
    headline: str
    phases: Sequence[SubscriptionPhase]


class SubscriptionProduct:
    id: UUID
    cross_revision_id: UUID
    name: str
    tiers: Sequence[SubscriptionTier]
    activation_date: datetime
    is_pre_order: bool
