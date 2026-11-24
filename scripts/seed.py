#!/usr/bin/env python
"""Seed the database with sample data for CloudDesk demo.

Idempotent: only runs when DEMO_MODE=true and there are no customers and no tickets.
Uses uuid5 of a key so reseeding cannot duplicate rows.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from uuid import UUID, uuid5, NAMESPACE_URL

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Set demo env before importing models
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/support.db")

from app.models.entities import (
    Profile, Customer, Subscription, Workspace, Product,
    Ticket, TicketMessage, SupportArticle, Incident,
    WorkflowRun, WorkflowEvent, ResolutionAction, ApprovalRequest,
    Escalation, CustomerMemory, AuditLog
)
from app.core.config import get_settings


# Namespace for deterministic UUIDs
DEMO_NS = UUID("00000000-0000-0000-0000-000000000000")


def uid(key: str) -> str:
    """Generate deterministic UUID from key."""
    return str(uuid5(DEMO_NS, key))


async def load_json(path: Path) -> list:
    """Load JSON file."""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_profiles(session: AsyncSession, data: list) -> None:
    """Seed user profiles."""
    for item in data:
        profile = Profile(
            id=uid(f"profile:{item['email']}"),
            email=item["email"],
            full_name=item.get("full_name", ""),
            role=item.get("role", "viewer"),
            is_active=item.get("is_active", True),
        )
        session.add(profile)
    await session.flush()


async def seed_customers(session: AsyncSession, data: list) -> None:
    """Seed customers."""
    for item in data:
        customer = Customer(
            id=uid(f"customer:{item['id']}"),
            name=item["name"],
            email=item["email"],
            plan=item["plan"],
            profile_id=uid(f"profile:{item['email']}"),
        )
        session.add(customer)
    await session.flush()


async def seed_subscriptions(session: AsyncSession, data: list) -> None:
    """Seed subscriptions."""
    for item in data:
        sub = Subscription(
            id=uid(f"subscription:{item['id']}"),
            customer_id=uid(f"customer:{item['customer_id']}"),
            plan=item["plan"],
            seats=item.get("seats", 1),
            status=item.get("status", "active"),
            renewal_at=item.get("renewal_at"),
        )
        session.add(sub)
    await session.flush()


async def seed_workspaces(session: AsyncSession, data: list) -> None:
    """Seed workspaces."""
    for item in data:
        ws = Workspace(
            id=uid(f"workspace:{item['id']}"),
            customer_id=uid(f"customer:{item['customer_id']}"),
            name=item["name"],
            storage_gb_used=item.get("storage_gb_used", 0),
            storage_gb_limit=item.get("storage_gb_limit", 10),
        )
        session.add(ws)
    await session.flush()


async def seed_products(session: AsyncSession, data: list) -> None:
    """Seed products."""
    for item in data:
        product = Product(
            id=uid(f"product:{item['id']}"),
            name=item["name"],
            description=item.get("description", ""),
            category=item.get("category", ""),
        )
        session.add(product)
    await session.flush()


async def seed_tickets(session: AsyncSession, data: list) -> None:
    """Seed tickets."""
    for item in data:
        ticket = Ticket(
            id=uid(f"ticket:{item['id']}"),
            subject=item["subject"],
            body=item["body"],
            channel=item["channel"],
            status=item.get("status", "new"),
            severity=item.get("severity"),
            category=item.get("category"),
            customer_id=uid(f"customer:{item['customer_id']}"),
            assignee_id=uid(f"profile:{item['assignee_email']}") if item.get("assignee_email") else None,
        )
        session.add(ticket)
    await session.flush()


async def seed_ticket_messages(session: AsyncSession, data: list) -> None:
    """Seed ticket messages."""
    for item in data:
        msg = TicketMessage(
            id=uid(f"message:{item['id']}"),
            ticket_id=uid(f"ticket:{item['ticket_id']}"),
            body=item["body"],
            author_id=uid(f"profile:{item['author_email']}") if item.get("author_email") else None,
            internal=item.get("internal", False),
        )
        session.add(msg)
    await session.flush()


async def seed_support_articles(session: AsyncSession, data: list) -> None:
    """Seed support articles."""
    for item in data:
        article = SupportArticle(
            id=uid(f"article:{item['id']}"),
            title=item["title"],
            category=item["category"],
            tags=item.get("tags", []),
            summary=item.get("summary", ""),
            content=item.get("content", ""),
        )
        session.add(article)
    await session.flush()


async def seed_incidents(session: AsyncSession, data: list) -> None:
    """Seed incidents."""
    for item in data:
        incident = Incident(
            id=uid(f"incident:{item['id']}"),
            title=item["title"],
            status=item.get("status", "investigating"),
            severity=item.get("severity", "medium"),
            affected_components=item.get("affected_components", []),
            started_at=item.get("started_at"),
            resolved_at=item.get("resolved_at"),
        )
        session.add(incident)
    await session.flush()


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    sample_dir = Path(settings.sample_data_dir)

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(Customer).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        result = await session.execute(select(Ticket).limit(1))
        if result.scalar_one_or_none():
            print("Database already has tickets. Skipping.")
            return

        print("Seeding database...")

        # Load all sample data
        profiles = await load_json(sample_dir / "profiles.json")
        customers = await load_json(sample_dir / "customers.json")
        subscriptions = await load_json(sample_dir / "subscriptions.json")
        workspaces = await load_json(sample_dir / "workspaces.json")
        products = await load_json(sample_dir / "products.json")
        tickets = await load_json(sample_dir / "tickets.json")
        ticket_messages = await load_json(sample_dir / "ticket_messages.json")
        support_articles = await load_json(sample_dir / "support_articles.json")
        incidents = await load_json(sample_dir / "incidents.json")

        # Seed in dependency order
        await seed_profiles(session, profiles)
        print(f"  Seeded {len(profiles)} profiles")

        await seed_customers(session, customers)
        print(f"  Seeded {len(customers)} customers")

        await seed_subscriptions(session, subscriptions)
        print(f"  Seeded {len(subscriptions)} subscriptions")

        await seed_workspaces(session, workspaces)
        print(f"  Seeded {len(workspaces)} workspaces")

        await seed_products(session, products)
        print(f"  Seeded {len(products)} products")

        await seed_tickets(session, tickets)
        print(f"  Seeded {len(tickets)} tickets")

        await seed_ticket_messages(session, ticket_messages)
        print(f"  Seeded {len(ticket_messages)} ticket messages")

        await seed_support_articles(session, support_articles)
        print(f"  Seeded {len(support_articles)} support articles")

        await seed_incidents(session, incidents)
        print(f"  Seeded {len(incidents)} incidents")

        await session.commit()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())