local M = {}
local documents = {}

local function show_message(buffer, message)
  vim.bo[buffer].modifiable = true
  vim.api.nvim_buf_set_lines(buffer, 0, -1, false, vim.split(message, "\n", { plain = true }))
  vim.bo[buffer].modifiable = false
  vim.bo[buffer].modified = false
end

local function show_page(buffer, page)
  local document = documents[buffer]
  if not document or not document.page_count then
    return
  end
  if page < 1 or page > document.page_count then
    vim.notify("PDF page must be between 1 and " .. document.page_count, vim.log.levels.WARN)
    return
  end
  if document.placement then
    if not document.placement.img:ready() and not document.placement.img:failed() then
      vim.notify("PDF page is still rendering", vim.log.levels.INFO)
      return
    end
    document.placement:close()
  end
  document.page = page
  show_message(buffer, "")
  document.placement = Snacks.image.placement.new(buffer, document.path .. "#page=" .. page, {
    conceal = true,
    auto_resize = true,
  })
  vim.notify(string.format("PDF page %d/%d · :PdfPage +1 / -1", page, document.page_count))
end

local function close_document(buffer)
  local document = documents[buffer]
  documents[buffer] = nil
  if not document then
    return
  end
  if document.process then
    document.process:kill(15)
  end
  if document.placement then
    document.placement:close()
  end
end

local function open_document(buffer)
  close_document(buffer)
  local document = { path = vim.api.nvim_buf_get_name(buffer), page = 1 }
  documents[buffer] = document
  vim.bo[buffer].buftype = "nowrite"
  vim.bo[buffer].swapfile = false
  vim.bo[buffer].filetype = "image"
  show_message(buffer, "Loading PDF…")
  for _, executable in ipairs({ "pdfinfo", "magick", "gs" }) do
    if vim.fn.executable(executable) ~= 1 then
      show_message(buffer, "PDF viewer requires " .. executable .. ". Rebuild the Neovim configuration.")
      return
    end
  end
  Snacks.image.terminal.detect(function()
    if documents[buffer] ~= document then
      return
    end
    if not Snacks.image.supports_terminal() then
      show_message(buffer, "PDF images require a terminal with Kitty graphics support. See :checkhealth snacks.")
      return
    end
    document.process = vim.system(
      { "pdfinfo", document.path },
      { text = true, timeout = 10000, env = { LC_ALL = "C" } },
      vim.schedule_wrap(function(result)
        if documents[buffer] ~= document then
          return
        end
        document.process = nil
        local page_count = tonumber((result.stdout or ""):match("Pages:%s+(%d+)"))
        if result.code ~= 0 or not page_count or page_count < 1 then
          show_message(buffer, "Unable to open PDF:\n" .. (result.stderr or "Invalid page count"))
          return
        end
        document.page_count = page_count
        show_page(buffer, 1)
      end)
    )
  end)
  vim.api.nvim_buf_create_user_command(buffer, "PdfPage", function(command)
    if not document.page_count then
      vim.notify("PDF is not ready", vim.log.levels.WARN)
      return
    end
    if command.args == "" then
      vim.notify(string.format("PDF page %d/%d", document.page, document.page_count))
      return
    end
    if not command.args:match("^[+-]?%d+$") then
      vim.notify("Use :PdfPage <number>, +<count>, or -<count>", vim.log.levels.WARN)
      return
    end
    local page = tonumber(command.args)
    if command.args:match("^[+-]") then
      page = document.page + page
    end
    show_page(buffer, page)
  end, { nargs = "?", desc = "Show a PDF page or move by a signed page count" })
end

function M.setup()
  local group = vim.api.nvim_create_augroup("PdfViewer", { clear = true })
  vim.api.nvim_create_autocmd("BufReadCmd", {
    group = group,
    pattern = "*.[pP][dD][fF]",
    callback = function(event)
      open_document(event.buf)
    end,
  })
  vim.api.nvim_create_autocmd({ "BufDelete", "BufWipeout" }, {
    group = group,
    callback = function(event)
      close_document(event.buf)
    end,
  })
end

return M
