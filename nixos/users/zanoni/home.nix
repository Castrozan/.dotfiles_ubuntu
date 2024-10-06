{pkgs, ...}: {
  ##################################################################################################################
  #
  # All Zanoni's Home Manager Configuration
  #
  ##################################################################################################################

  imports = [
    ../../home/core.nix

    # ../../home/fcitx5
    ../../home/i3
    ../../home/programs
    # ../../home/rofi
    # ../../home/shell
  ];

  programs.git = {
    userName = "Castrozan";
    userEmail = "castro.lucas290@gmail.com";
  };
}
