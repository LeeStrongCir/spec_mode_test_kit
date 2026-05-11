import uuid

import pytest

from app.services.lecs_lifecycle_service import (
    LOCKED_STATES,
    STATE_TRANSITIONS,
    validate_transition,
)


def test_validate_normal_shutdown():
    ok, next_state = validate_transition("normal", "shutdown")
    assert ok is True
    assert next_state == "shutting_down"


def test_validate_normal_start_blocked():
    ok, next_state = validate_transition("normal", "start")
    assert ok is False
    assert next_state is None


def test_validate_stopped_start():
    ok, next_state = validate_transition("stopped", "start")
    assert ok is True
    assert next_state == "starting"


def test_validate_stopped_delete():
    ok, next_state = validate_transition("stopped", "delete")
    assert ok is True
    assert next_state == "deleting"


def test_validate_failed_start():
    ok, next_state = validate_transition("failed", "start")
    assert ok is True
    assert next_state == "starting"


def test_validate_failed_delete():
    ok, next_state = validate_transition("failed", "delete")
    assert ok is True
    assert next_state == "deleting"


def test_validate_creating_locked():
    for op in ["shutdown", "start", "delete"]:
        ok, _ = validate_transition("creating", op)
        assert ok is False


def test_validate_deleting_locked():
    for op in ["shutdown", "start", "delete"]:
        ok, _ = validate_transition("deleting", op)
        assert ok is False


def test_validate_shutting_down_locked():
    ok, _ = validate_transition("shutting_down", "start")
    assert ok is False


def test_validate_starting_locked():
    ok, _ = validate_transition("starting", "shutdown")
    assert ok is False


def test_validate_unknown_state():
    ok, _ = validate_transition("unknown_state", "shutdown")
    assert ok is False


def test_state_transitions_matrix():
    assert STATE_TRANSITIONS["normal"]["shutdown"] == "shutting_down"
    assert STATE_TRANSITIONS["stopped"]["start"] == "starting"
    assert STATE_TRANSITIONS["stopped"]["delete"] == "deleting"
    assert STATE_TRANSITIONS["failed"]["start"] == "starting"
    assert STATE_TRANSITIONS["failed"]["delete"] == "deleting"


def test_locked_states_completeness():
    assert "creating" in LOCKED_STATES
    assert "shutting_down" in LOCKED_STATES
    assert "starting" in LOCKED_STATES
    assert "deleting" in LOCKED_STATES
