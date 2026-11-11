# WMR shell config - sourced from ~/.zshrc by install.sh (zsh stage).
# Edit here, `git pull` on every device.

: "${WMR_HOME:=$HOME/WMR}"

# bash/ helper scripts on PATH
[ -d "$WMR_HOME/bash" ] && export PATH="$WMR_HOME/bash:$PATH"
[ -d "$HOME/.local/bin" ] && export PATH="$HOME/.local/bin:$PATH"

# script shortcuts
alias gifit="$WMR_HOME/bash/create_gif.sh"
alias rnf="$WMR_HOME/bash/rename_files.sh"
alias meow="$WMR_HOME/bash/kitty-cat.sh"
alias noice="$WMR_HOME/bash/noice.sh"
alias wmr-update='git -C "$WMR_HOME" pull --ff-only && echo "WMR updated - run: exec zsh"'

case "$(uname -s)" in
  Darwin) [ -f "$WMR_HOME/config/aliases-mac.zsh" ] && source "$WMR_HOME/config/aliases-mac.zsh" ;;
  *)
    if [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *com.termux* ]]; then
      alias updootit='pkg update -y && pkg upgrade -y'
    else
      alias updootit='sudo apt update && sudo apt -y upgrade'
      [ "$(id -u)" -eq 0 ] && alias updootit='apt update && apt -y upgrade'
    fi
    ;;
esac

# Termux only: Ubuntu (proot-distro) + Claude Code living inside it
if command -v proot-distro >/dev/null 2>&1; then
  alias ubu='proot-distro login ubuntu --shared-tmp'
  # cl [claude args]  - run Claude Code in Ubuntu, in the directory you are standing in
  cl() {
    proot-distro login ubuntu --shared-tmp --bind "$PWD:/root/work" -- \
      bash -lc 'export PATH="$HOME/.local/bin:$PATH"; cd /root/work && exec claude "$@"' _ "$@"
  }
fi
