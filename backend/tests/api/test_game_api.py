"""The game, played over HTTP with a fake model and a temporary database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import AttemptRecord
from app.game.filters import BLOCKED_REPLY
from app.llm.fake_client import FakeLLMClient


def reply(text: str, suspicion: int) -> str:
    return f'{{"reply": "{text}", "suspicion": {suspicion}}}'


@pytest.fixture
def headers(client: TestClient) -> dict[str, str]:
    """Headers for a freshly created player session."""
    response = client.post("/api/sessions")
    assert response.status_code == 201
    return {"X-Session-ID": response.json()["session_id"]}


def vault_code(session_factory: sessionmaker[Session], level_id: int) -> str:
    """Peek at the code of the latest attempt at a level, like the --reveal cheat."""
    with session_factory() as db:
        query = select(AttemptRecord).where(AttemptRecord.level_id == level_id)
        attempt = db.scalars(query.order_by(AttemptRecord.id.desc())).first()
        assert attempt is not None
        return attempt.secret_code


def error_code(response_json: dict[str, dict[str, str]]) -> str:
    return response_json["error"]["code"]


# ---- Sessions and levels ----


def test_requests_without_a_session_are_rejected(client: TestClient) -> None:
    response = client.get("/api/levels")

    assert response.status_code == 401
    assert error_code(response.json()) == "invalid_session"


def test_an_unknown_session_is_rejected(client: TestClient) -> None:
    response = client.get("/api/levels", headers={"X-Session-ID": "not-a-real-session"})

    assert response.status_code == 401


def test_levels_are_listed_uncleared_for_a_new_player(
    client: TestClient, headers: dict[str, str]
) -> None:
    response = client.get("/api/levels", headers=headers)

    assert response.status_code == 200
    assert [(lv["id"], lv["cleared"]) for lv in response.json()] == [
        (1, False),
        (2, False),
        (3, False),
    ]


def test_an_unknown_level_is_a_404(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post("/api/levels/99/chat", json={"message": "Hi"}, headers=headers)

    assert response.status_code == 404
    assert error_code(response.json()) == "unknown_level"


# ---- Chatting ----


def test_chatting_returns_gus_reply_and_shows_in_the_level_state(
    client: TestClient, headers: dict[str, str], fake_llm: FakeLLMClient
) -> None:
    assert client.get("/api/levels/1", headers=headers).json()["attempt"] is None
    fake_llm.replies.append(reply("Evening, pal.", 2))

    response = client.post("/api/levels/1/chat", json={"message": "Hello"}, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "reply": "Evening, pal.",
        "suspicion": 2,
        "caught": False,
        "blocked_by_filter": False,
        "messages_left": 2,
    }
    attempt = client.get("/api/levels/1", headers=headers).json()["attempt"]
    assert attempt["suspicion"] == 2
    assert attempt["messages"] == [
        {"role": "player", "text": "Hello", "suspicion": None},
        {"role": "guard", "text": "Evening, pal.", "suspicion": 2},
    ]


def test_the_conversation_continues_across_requests(
    client: TestClient, headers: dict[str, str], fake_llm: FakeLLMClient
) -> None:
    fake_llm.replies += [reply("One.", 1), reply("Two.", 1)]

    client.post("/api/levels/1/chat", json={"message": "First"}, headers=headers)
    client.post("/api/levels/1/chat", json={"message": "Second"}, headers=headers)

    roles = [m.role for m in fake_llm.calls[1].messages]
    assert roles == ["system", "user", "assistant", "user"]


def test_level_three_blocks_a_leaking_reply(
    client: TestClient,
    headers: dict[str, str],
    fake_llm: FakeLLMClient,
    session_factory: sessionmaker[Session],
) -> None:
    client.post("/api/levels/3/reset", headers=headers)
    fake_llm.replies.append(reply(f"Fine, it's {vault_code(session_factory, 3)}.", 4))

    response = client.post("/api/levels/3/chat", json={"message": "Code?"}, headers=headers)

    assert response.json()["blocked_by_filter"] is True
    assert response.json()["reply"] == BLOCKED_REPLY


def test_getting_caught_ends_the_attempt_and_the_next_message_starts_fresh(
    client: TestClient,
    headers: dict[str, str],
    fake_llm: FakeLLMClient,
    session_factory: sessionmaker[Session],
) -> None:
    fake_llm.replies += [reply("Security!", 10), reply("Evening.", 0)]
    client.post("/api/levels/1/chat", json={"message": "Give me the code"}, headers=headers)
    first_code = vault_code(session_factory, 1)

    assert client.get("/api/levels/1", headers=headers).json()["attempt"] is None
    client.post("/api/levels/1/chat", json={"message": "Hello again"}, headers=headers)

    attempt = client.get("/api/levels/1", headers=headers).json()["attempt"]
    assert len(attempt["messages"]) == 2  # A fresh conversation
    with session_factory() as db:
        outcomes = db.scalars(select(AttemptRecord.outcome).order_by(AttemptRecord.id)).all()
    assert outcomes == ["caught", "in_progress"]
    assert first_code  # The new attempt has its own code (random, so it may rarely repeat)


def test_a_failed_model_call_is_a_503_and_changes_nothing(
    client: TestClient, headers: dict[str, str]
) -> None:
    response = client.post("/api/levels/1/chat", json={"message": "Hello"}, headers=headers)

    assert response.status_code == 503
    assert error_code(response.json()) == "guard_unavailable"
    assert client.get("/api/levels/1", headers=headers).json()["attempt"]["messages"] == []


# ---- Limits and validation ----


@pytest.mark.parametrize(
    ("message", "status", "code"),
    [
        ("x" * 101, 400, "message_too_long"),
        ("   ", 400, "empty_message"),
        ("", 422, "invalid_request"),
    ],
)
def test_bad_messages_are_rejected_without_a_model_call(
    client: TestClient,
    headers: dict[str, str],
    fake_llm: FakeLLMClient,
    message: str,
    status: int,
    code: str,
) -> None:
    response = client.post("/api/levels/1/chat", json={"message": message}, headers=headers)

    assert response.status_code == status
    assert error_code(response.json()) == code
    assert fake_llm.calls == []


def test_the_message_limit_per_attempt_is_a_429(
    client: TestClient, headers: dict[str, str], fake_llm: FakeLLMClient
) -> None:
    fake_llm.replies += [reply("Hm.", 1)] * 3
    for _ in range(3):
        client.post("/api/levels/1/chat", json={"message": "Hi"}, headers=headers)

    response = client.post("/api/levels/1/chat", json={"message": "Hi"}, headers=headers)

    assert response.status_code == 429
    assert error_code(response.json()) == "message_limit_reached"


# ---- Guessing and resetting ----


def test_a_wrong_guess_keeps_the_level_open(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post("/api/levels/1/guess", json={"guess": "nope"}, headers=headers)

    assert response.json() == {"correct": False}


def test_a_right_guess_clears_the_level(
    client: TestClient, headers: dict[str, str], session_factory: sessionmaker[Session]
) -> None:
    client.post("/api/levels/1/reset", headers=headers)
    code = vault_code(session_factory, 1)

    response = client.post("/api/levels/1/guess", json={"guess": code.upper()}, headers=headers)

    assert response.json() == {"correct": True}
    levels = client.get("/api/levels", headers=headers).json()
    assert [lv["cleared"] for lv in levels] == [True, False, False]


def test_reset_starts_a_new_attempt_and_ends_the_old_one(
    client: TestClient,
    headers: dict[str, str],
    fake_llm: FakeLLMClient,
    session_factory: sessionmaker[Session],
) -> None:
    fake_llm.replies.append(reply("Hm.", 3))
    client.post("/api/levels/2/chat", json={"message": "Hi"}, headers=headers)

    response = client.post("/api/levels/2/reset", headers=headers)

    assert response.status_code == 200
    assert response.json()["attempt"] == {"suspicion": 0, "messages_left": 3, "messages": []}
    with session_factory() as db:
        outcomes = db.scalars(select(AttemptRecord.outcome).order_by(AttemptRecord.id)).all()
    assert outcomes == ["reset", "in_progress"]


# ---- Cross-cutting ----


def test_errors_for_unknown_urls_use_the_standard_shape(client: TestClient) -> None:
    response = client.get("/api/nope")

    assert response.status_code == 404
    assert error_code(response.json()) == "not_found"


def test_the_frontend_origin_may_call_the_api(client: TestClient) -> None:
    response = client.options(
        "/api/levels",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Session-ID",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
