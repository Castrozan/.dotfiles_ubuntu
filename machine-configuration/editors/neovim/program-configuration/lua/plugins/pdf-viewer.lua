return {
  {
    "folke/snacks.nvim",
    opts = {
      image = {
        enabled = true,
        formats = {},
        doc = { enabled = false },
        math = { enabled = false },
        convert = {
          magick = {
            pdf = require("config.pdf_document_view").conversion_arguments,
          },
        },
      },
    },
    init = function()
      require("config.pdf_viewer").setup()
    end,
  },
}
