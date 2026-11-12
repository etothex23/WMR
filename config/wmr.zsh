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

# --- modern CLI tools (installed by the base stage) ---------------------------
# Debian/Ubuntu rename two of them; zsh-bat already handles batcat for `cat`.
command -v bat >/dev/null 2>&1 || { command -v batcat >/dev/null 2>&1 && alias bat=batcat; }
command -v fd  >/dev/null 2>&1 || { command -v fdfind >/dev/null 2>&1 && alias fd=fdfind; }
command -v eza >/dev/null 2>&1 && { alias ls='eza --group-directories-first'; alias ll='eza -l --git --group-directories-first'; alias la='eza -la --git --group-directories-first'; alias lt='eza --tree --level=2'; }
# zoxide: `z <part-of-dir>` jumps, `zi` picks interactively
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init zsh)"
# fzf: Ctrl+R history, Ctrl+T files, Alt+C cd.  `fzf --zsh` needs fzf >= 0.48; older apt builds ship a script.
if command -v fzf >/dev/null 2>&1; then
  if fzf --zsh >/dev/null 2>&1; then
    source <(fzf --zsh)
  else
    for f in /usr/share/doc/fzf/examples/key-bindings.zsh /usr/share/fzf/key-bindings.zsh; do
      [ -f "$f" ] && { source "$f"; break; }
    done
  fi
fi

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
  # cl [claude args]  - run Claude Code in Ubuntu, in the directory you are standing in.
  # Uses only documented proot-distro 5.x options (-w, -e, --bind); no nested shell quoting.
  cl() {
    proot-distro login ubuntu --shared-tmp --bind "$PWD:/root/work" -w /root/work \
      -e "PATH=/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" -- claude "$@"
  }
fi
