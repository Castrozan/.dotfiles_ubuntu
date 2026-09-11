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
            pdf = {
              "-density",
              144,
              "{src}[{page}]",
              "-background",
              "white",
              "-alpha",
              "remove",
              "-resize",
              "1920x1920>",
            },
          },
        },
      },
    },
    init = function()
      require("config.pdf_viewer").setup()
    end,
  },
}
