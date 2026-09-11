import json

import pytest


def test_closing_aborts_work_and_stale_callbacks_cannot_reopen_a_document(
    run_headless_lua, pdf_viewer_prelude
):
    result = run_headless_lua(
        "pdf_close.lua",
        pdf_viewer_prelude
        + """
        vim.cmd.edit(document_path)
        vim.cmd("edit!")
        assert(killed_processes == 1)
        complete_metadata(1)
        assert(#conversions == 0)
        complete_metadata(2)
        vim.api.nvim_buf_delete(0, { force = true })
        assert(aborted_conversions == 1)
        complete_conversion(1)
        assert(#placements == 0 and #conversions == 1)
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_failed_page_does_not_prevent_scrolling_to_other_pages(
    run_headless_lua, pdf_viewer_prelude
):
    result = run_headless_lua(
        "pdf_page_failure.lua",
        pdf_viewer_prelude
        + """
        vim.cmd.edit(document_path)
        complete_metadata(1)
        complete_conversion(1, "conversion failed")
        assert(vim.api.nvim_buf_line_count(0) > 100)
        vim.cmd("normal! G")
        refresh()
        assert(conversions[2].options.src == document_path .. "#page=3")
        complete_conversion(2)
        assert(#placements == 1)
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "failure_setup, completion, expected_message",
    [
        ("terminal_supported = false", "", "Kitty graphics"),
        (
            'vim.fn.executable = function(name) return name == "gs" and 0 or 1 end',
            "",
            "requires gs",
        ),
        ("", 'complete_metadata(1, "", 1, "Incorrect password")', "Incorrect password"),
        ("", 'complete_metadata(1, "Pages: 2")', "Invalid PDF page dimensions"),
    ],
)
def test_pdf_failures_preserve_the_source_and_show_the_reason(
    run_headless_lua, pdf_viewer_prelude, failure_setup, completion, expected_message
):
    result = run_headless_lua(
        "pdf_failure.lua",
        pdf_viewer_prelude
        + f"""
        {failure_setup}
        vim.cmd.edit(document_path)
        {completion}
        assert(#conversions == 0)
        local content = table.concat(vim.api.nvim_buf_get_lines(0, 0, -1, false), "\\n")
        assert(content:find({json.dumps(expected_message)}, 1, true), content)
        assert(not vim.bo.modifiable and vim.bo.buftype == "nowrite")
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_text_buffers_and_native_keys_keep_their_behavior(
    run_headless_lua, pdf_viewer_prelude
):
    result = run_headless_lua(
        "pdf_scope.lua",
        pdf_viewer_prelude
        + """
        local text_path = document_path .. ".txt"
        vim.fn.writefile({ "ordinary text" }, text_path)
        vim.cmd.edit(text_path)
        assert(vim.bo.buftype == "" and vim.bo.modifiable and not vim.bo.readonly)
        assert(#metadata_requests == 0)
        vim.cmd.edit(document_path)
        complete_metadata(1)
        for _, key in ipairs({ "j", "k", "G", "gg", "<C-f>", "<C-b>", "<C-d>", "<ScrollWheelDown>" }) do
          assert(vim.fn.maparg(key, "n") == "", key .. " was shadowed")
        end
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr
