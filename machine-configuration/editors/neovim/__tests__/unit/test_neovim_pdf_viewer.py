import json

import pytest


@pytest.fixture
def pdf_viewer_prelude(neovim_lua_path, tmp_path):
    document_path = tmp_path / "report with 'quotes'.PDF"
    document_path.write_bytes(b"%PDF-1.7\noriginal bytes\n")
    return f"""
    local document_path = {json.dumps(str(document_path))}
    local rendered_pages, notifications, metadata_requests = {{}}, {{}}, {{}}
    local terminal_supported, rendering_ready = true, true
    local closed_placements, killed_processes = 0, 0
    vim.notify = function(message) table.insert(notifications, message) end
    vim.fn.executable = function() return 1 end
    vim.system = function(arguments, options, callback)
      table.insert(metadata_requests, {{ arguments = arguments, options = options, callback = callback }})
      return {{ kill = function() killed_processes = killed_processes + 1 end }}
    end
    Snacks = {{ image = {{
      terminal = {{ detect = function(callback) callback() end }},
      supports_terminal = function() return terminal_supported end,
      placement = {{ new = function(buffer, source, options)
        table.insert(rendered_pages, {{ buffer = buffer, source = source, options = options }})
        return {{
          close = function() closed_placements = closed_placements + 1 end,
          img = {{ ready = function() return rendering_ready end, failed = function() return false end }},
        }}
      end }},
    }} }}
    dofile({json.dumps(str(neovim_lua_path("config", "pdf_viewer.lua")))}).setup()
    local function complete_metadata(index, code, stdout, stderr)
      metadata_requests[index].callback({{ code = code or 0, stdout = stdout or "Pages: 3", stderr = stderr or "" }})
      vim.wait(100, function() return false end, 10)
    end
    """


def test_pdf_opening_navigation_and_writes_preserve_the_document(
    run_headless_lua, pdf_viewer_prelude
):
    result = run_headless_lua(
        "pdf_navigation.lua",
        pdf_viewer_prelude
        + """
        vim.cmd.edit(document_path)
        assert(#metadata_requests == 1 and #rendered_pages == 0)
        assert(metadata_requests[1].arguments[2] == document_path)
        assert(metadata_requests[1].options.timeout == 10000)
        complete_metadata(1)
        assert(#rendered_pages == 1 and rendered_pages[1].source == document_path .. "#page=1")
        vim.cmd("PdfPage +1")
        vim.cmd("PdfPage 3")
        vim.cmd("PdfPage -2")
        assert(#rendered_pages == 4 and rendered_pages[4].source == document_path .. "#page=1")
        assert(closed_placements == 3)
        for _, argument in ipairs({ "0", "4", "1.5", "abc", "-1" }) do
          vim.cmd("PdfPage " .. argument)
        end
        assert(#rendered_pages == 4, "invalid pages reached the renderer")
        assert(vim.bo.readonly and not vim.bo.modifiable and not vim.bo.swapfile)
        local written = pcall(vim.cmd, "write!")
        assert(not written, "the preview allowed overwriting the source PDF")
        assert(vim.fn.readfile(document_path)[2] == "original bytes")
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_navigation_does_not_queue_concurrent_page_conversions(
    run_headless_lua, pdf_viewer_prelude
):
    result = run_headless_lua(
        "pdf_render_bound.lua",
        pdf_viewer_prelude
        + """
        vim.cmd.edit(document_path)
        complete_metadata(1)
        rendering_ready = false
        for _ = 1, 100 do vim.cmd("PdfPage +1") end
        assert(#rendered_pages == 1 and closed_placements == 0)
        rendering_ready = true
        vim.cmd("PdfPage +1")
        assert(#rendered_pages == 2 and rendered_pages[2].source == document_path .. "#page=2")
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_closing_and_reopening_ignores_stale_metadata_and_releases_resources(
    run_headless_lua, pdf_viewer_prelude
):
    result = run_headless_lua(
        "pdf_lifecycle.lua",
        pdf_viewer_prelude
        + """
        vim.cmd.edit(document_path)
        local buffer = vim.api.nvim_get_current_buf()
        vim.cmd("edit!")
        assert(killed_processes == 1)
        complete_metadata(1)
        assert(#rendered_pages == 0)
        complete_metadata(2)
        assert(#rendered_pages == 1)
        vim.api.nvim_buf_delete(buffer, { force = true })
        assert(closed_placements == 1)
        vim.cmd.edit(document_path)
        vim.api.nvim_buf_delete(0, { force = true })
        assert(killed_processes == 2)
        complete_metadata(3)
        assert(#rendered_pages == 1)
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "failure_setup, completion, expected_message",
    [
        ("terminal_supported = false", "", "Kitty graphics support"),
        (
            'vim.fn.executable = function(name) return name == "gs" and 0 or 1 end',
            "",
            "requires gs",
        ),
        ("", 'complete_metadata(1, 1, "", "Incorrect password")', "Incorrect password"),
    ],
)
def test_pdf_failures_show_an_explanation_without_rendering(
    run_headless_lua, pdf_viewer_prelude, failure_setup, completion, expected_message
):
    result = run_headless_lua(
        "pdf_failure.lua",
        pdf_viewer_prelude
        + f"""
        {failure_setup}
        vim.cmd.edit(document_path)
        {completion}
        assert(#rendered_pages == 0)
        local content = table.concat(vim.api.nvim_buf_get_lines(0, 0, -1, false), "\\n")
        assert(content:find({json.dumps(expected_message)}, 1, true), content)
        assert(not vim.bo.modifiable and vim.bo.readonly)
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
        assert(vim.fn.exists(":PdfPage") == 0 and #metadata_requests == 0)
        vim.cmd.edit(document_path)
        complete_metadata(1)
        for _, key in ipairs({ "n", "p", "z", "q", "e", "<C-f>", "<C-b>" }) do
          assert(vim.fn.maparg(key, "n") == "", key .. " was shadowed")
        end
        vim.cmd("qa!")
        """,
    )
    assert result.returncode == 0, result.stdout + result.stderr
