#!/usr/bin/env python
"""Run a demo workflow for a specific ticket.

Usage:
    python scripts/demo.py              # Runs CD-1002 (refund approval)
    python scripts/demo.py --ticket CD-1005  # Runs CD-1005 (escalation)
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("LLM_PROVIDER", "fake")
os.environ.setdefault("VECTOR_STORE", "memory")
os.environ.setdefault("USE_FAKE_REDIS", "true")
os.environ.setdefault("CHECKPOINT_DB_PATH", ":memory:")

from app.services.workflow_service import WorkflowService
from app.repositories.ticket_repository import TicketRepository
from app.core.database import get_session_factory


async def run_demo(ticket_display_id: str) -> None:
    """Run demo workflow for a ticket."""
    print(f"\n{'='*60}")
    print(f"DEMO: Running workflow for {ticket_display_id}")
    print(f"{'='*60}\n")

    session_factory = get_session_factory()
    async with session_factory() as session:
        ticket_repo = TicketRepository(session)
        workflow_service = WorkflowService(session)

        # Find ticket by display ID (e.g., CD-1002)
        ticket = await ticket_repo.get_by_display_id(ticket_display_id)
        if not ticket:
            print(f"Ticket {ticket_display_id} not found!")
            return

        print(f"Ticket: {ticket.id} - {ticket.subject}")
        print(f"Status: {ticket.status}")
        print(f"Customer: {ticket.customer_id}")
        print()

        # Start workflow
        print("Starting workflow...")
        workflow_id = await workflow_service.create_run(ticket.id)
        print(f"Workflow ID: {workflow_id}")
        print(f"Status: running")
        print()

        # Poll for completion
        max_polls = 60
        for i in range(max_polls):
            await asyncio.sleep(2)
            state = await workflow_service.get_workflow_state(workflow_id)
            if not state:
                print("Workflow state not found")
                break

            print(f"  Node: {state.get('current_node', 'unknown')}")
            print(f"  Completed: {state.get('completed_nodes', [])}")

            if state.get("status") == "completed":
                print("\nWorkflow completed!")
                print(f"Summary: {state.get('summary')}")
                print(f"Memory updated: {state.get('memory_updated')}")
                break
            elif state.get("status") == "paused":
                print("\nWorkflow paused - waiting for approval")
                approval_id = state.get("approval_request_id")
                print(f"Approval request: {approval_id}")
                print("\nTo approve, run:")
                print(f"  # In another terminal or API call:")
                print(f"  POST /api/v1/approvals/{approval_id}/approve")
                break
            elif state.get("status") == "failed":
                print(f"\nWorkflow failed: {state.get('error')}")
                break
        else:
            print("\nTimeout waiting for workflow")


def main():
    parser = argparse.ArgumentParser(description="Run CloudDesk demo workflow")
    parser.add_argument("--ticket", default="CD-1002", help="Ticket display ID (default: CD-1002)")
    args = parser.parse_args()

    asyncio.run(run_demo(args.ticket))


if __name__ == "__main__":
    main()