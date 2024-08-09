# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

# Show current git branch in prompt
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

if [ "$color_prompt" = yes ]; then
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\[\033[01;32m\] \u\[\033[00m\]\[\033[01;34m\] \W\[\033[00m\]\[\033[01;1;38;2;253;200;169m\]\$(parse_git_branch)\[\033[00m\]\$ "
else
    PS1="\u@\h:\w\$(parse_git_branch)\$ "
fi

unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@: \W\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Open tmux on startup
#if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
  #exec tmux
#fi

# Enable case-insensitive tab completion
# If ~/.inputrc doesn't exist yet: First include the original /etc/inputrc
# so it won't get overriden
if [ ! -a ~/.inputrc ]; then echo '$include /etc/inputrc' > ~/.inputrc; fi

# Add shell-option to ~/.inputrc to enable case-insensitive tab completion
echo 'set completion-ignore-case On' >> ~/.inputrc

# BEGIN EVN VARIABLES
# asdf
. "$HOME/.asdf/asdf.sh"
. "$HOME/.asdf/completions/asdf.bash"

# NVM variables
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Pyenv variables
export PYENV_ROOT=/home/lucas.zanoni/.pyenv
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
export PATH="$HOME/.pyenv/bin:$PATH"

export PATH=$PATH:~/.local/bin
export OBSIDIAN_HOME="$HOME/Documents/obsidianVault"
# flatpak
export XDG_DATA_DIRS=/var/lib/flatpak/exports/share:/home/lucas.zanoni/.local/share/flatpak/exports/share:$XDG_DATA_DIRS

# pnpm
export PNPM_HOME="/home/lucas.zanoni/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
# sdkman
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
# END ENV VARIABLES

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.
# TODO: source aliases from a file
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# BEGIN ALIASES
# aliases Betha
alias k="kubectl"
alias standalone="cd /opt/wildfly-aplicacoes/standalone/configuration"
export FLY_HOME=/home/lucas.zanoni/betha-fly
alias fly-java6='sdk use java 1.6.0_45-fly; sdk use maven 3.2.3-fly'
alias fly-jboss='/home/lucas.zanoni/betha-fly/tools/jboss-5.1.0.GA/bin/run.sh -c betha'
alias wildfly='cd /opt/wildfly-aplicacoes/bin; ./standalone.sh'
alias fly-java6='sdk use java 1.6.0_45-fly; sdk use maven 3.2.3-fly'
alias jboss='/home/lucas.zanoni/betha-fly/tools/jboss-5.1.0.GA/bin/run.sh -c betha'alias killport='sh /home/lucas.zanoni/.local/bin/killport'
alias vt_prod='aws sso login --profile eks-plataforma-production'
alias vt_test='aws sso login --profile eks-plataforma-test'
alias studio3t="cd ~/studio3t && ./Studio-3T .sh"

# aliases personal
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias code="code . -n"
alias lc="ls -a --color=never"
alias oo="cd $OBSIDIAN_HOME && nvim ."
alias studio3t="cd ~/studio3t && ./Studio-3T .sh"
alias nvim="$HOME/nvim.appimage"
alias bashrc="nvim ~/.bashrc"
alias dotfiles="cd ~/.dotfiles_ubuntu && nvim ."
alias source-bash="source ~/.bashrc"
alias obsidian="flatpak run md.obsidian.Obsidian >/dev/null 2>&1 &"
alias t="tmux"
alias todo="cd $HOME/Documents/obsidianVault && nvim TODO.md"
alias scripts="cd $HOME/repo/scripts && nvim ."
alias g="lazygit"
alias d="lazydocker"

# flatpak
export XDG_DATA_DIRS=/var/lib/flatpak/exports/share:/home/lucas.zanoni/.local/share/flatpak/exports/share:$XDG_DATA_DIRS

# pnpm
export PNPM_HOME="/home/lucas.zanoni/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
# pnpm end

# Source git completions
if [ -f /usr/share/bash-completion/completions ]; then
    . /usr/share/bash-completion/completions/git
fi

# Set autocomplete for terraform
complete -C /usr/bin/terraform terraform

# Source bash env config
if [ -f ~/.bash_env_variables ]; then
    . ~/.bash_env_variables
fi

# Add brew to PATH
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# TODO: lucas.zanoni doesen't exist on other sistems
# Files sourced by dotfiles at /home/lucas.zanoni/.dotfiles_ubuntu
. /home/lucas.zanoni/.dotfiles_ubuntu/shell/configs/case_insensitive_completion.sh
# Files sourced by dotfiles at /home/lucas.zanoni/.dotfiles_ubuntu
. /home/lucas.zanoni/.dotfiles_ubuntu/shell/configs/git_aliases.sh