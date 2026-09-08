from hook_module_loader import import_hyphenated_hook_module

herdr_agent_session_report_handler = import_hyphenated_hook_module(
    "herdr_agent_session_report_handler"
)


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


def test_codex_falls_back_to_the_hook_identifier_for_an_invalid_rollout(tmp_path):
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

    assert request_parameters["agent_session_id"] == "turn-123"


def test_codex_falls_back_when_the_rollout_record_is_not_an_object(tmp_path):
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

    assert request_parameters["agent_session_id"] == "turn-123"
