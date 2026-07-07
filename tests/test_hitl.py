"""Tests for HITL state machine."""

import time

from agent_harness.governance.hitl import HITLManager
from agent_harness.models import AgentAction


def test_create_request():
    h = HITLManager()
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    assert req.status == "pending"
    assert req.id is not None


def test_approve():
    h = HITLManager()
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    h.approve(req.id)
    assert req.status == "approved"


def test_deny():
    h = HITLManager()
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    h.deny(req.id)
    assert req.status == "denied"


def test_timeout():
    h = HITLManager(timeout=0)
    time.sleep(0.01)
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    assert h.check_timeout(req) is True
    assert req.status == "timed_out"
