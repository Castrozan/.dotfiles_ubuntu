import pytest

from hook_module_loader import import_hyphenated_hook_module

herdr_agent_session_report_handler = import_hyphenated_hook_module(
    "herdr_agent_session_report_handler"
)


@pytest.fixture(autouse=True)
def without_inherited_codex_thread_identifier(monkeypatch):
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)


def test_codex_reports_the_resumable_identifier_from_its_rollout(tmp_path):
    transcript_path = tmp_path / "rollout.jsonl"
    transcript_path.write_text(
        '{"type":"session_meta","payload":{"id":"thread-456"}}\n',
        encoding="utf-8",
    )

    request_parameters = (
        herdr_agent_session_report_handler.build_report_agent_session_parameters(
            {
                "hook_event_name": "SessionStart",
                "session_id": "turn-123",
                "transcript_path": str(transcript_path),
            },
            "codex",
        )
    )

    assert request_parameters["agent_session_id"] == "thread-456"


def test_codex_rejects_an_invalid_rollout(tmp_path):
    transcript_path = tmp_path / "rollout.jsonl"
    transcript_path.write_text("not-json\n", encoding="utf-8")

    request_parameters = (
        herdr_agent_session_report_handler.build_report_agent_session_parameters(
            {
                "hook_event_name": "SessionStart",
                "session_id": "turn-123",
                "transcript_path": str(transcript_path),
            },
            "codex",
        )
    )

    assert request_parameters is None


def test_codex_rejects_a_rollout_whose_first_record_is_not_an_object(tmp_path):
    transcript_path = tmp_path / "rollout.jsonl"
    transcript_path.write_text("[]\n", encoding="utf-8")

    request_parameters = (
        herdr_agent_session_report_handler.build_report_agent_session_parameters(
            {
                "hook_event_name": "SessionStart",
                "session_id": "turn-123",
                "transcript_path": str(transcript_path),
            },
            "codex",
        )
    )

    assert request_parameters is None


def test_codex_rejects_a_helper_without_a_persisted_transcript():
    request_parameters = (
        herdr_agent_session_report_handler.build_report_agent_session_parameters(
            {
                "hook_event_name": "SessionStart",
                "session_id": "01a0840b-752f-7d60-b58d-7fe21ffa3761",
            },
            "codex",
        )
    )

    assert request_parameters is None


def test_codex_rejects_a_session_that_differs_from_the_inherited_thread(
    tmp_path, monkeypatch
):
    transcript_path = tmp_path / "rollout.jsonl"
    transcript_path.write_text(
        '{"type":"session_meta","payload":{"id":"helper-456"}}\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("CODEX_THREAD_ID", "interactive-123")

    request_parameters = (
        herdr_agent_session_report_handler.build_report_agent_session_parameters(
            {
                "hook_event_name": "SessionStart",
                "session_id": "helper-456",
                "transcript_path": str(transcript_path),
            },
            "codex",
        )
    )

    assert request_parameters is None
