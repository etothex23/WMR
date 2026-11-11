#!/usr/bin/env bash
# =============================================================================
# WMR bootstrap  -  one script to set up a fresh Termux / Ubuntu / Debian / mac
#
#   Termux (fresh install):
#     pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/etothex23/WMR/main/install.sh | bash
#
#   Already cloned:
#     ./install.sh            # ask a few questions
#     ./install.sh --yes      # no questions, take every default
#
# Safe to re-run: every stage checks what is already there and only fixes the
# gaps (clones become pulls, config edits are marker-guarded).
# =============================================================================
set -uo pipefail

WMR_REPO="${WMR_REPO:-https://github.com/etothex23/WMR.git}"
WMR_RAW="${WMR_RAW:-https://raw.githubusercontent.com/etothex23/WMR/main}"
WMR_HOME="${WMR_HOME:-$HOME/WMR}"
UBUNTU_ALIAS="${UBUNTU_ALIAS:-ubuntu}"          # proot-distro distro name

ALL_STAGES="base repo zsh python git claude"
ASSUME_YES=0
DRY_RUN=0
INNER=0                                          # running inside proot ubuntu
ONLY=""
SKIP=""
FAILED=()

# ---------- output helpers ---------------------------------------------------
if [ -t 1 ]; then
  C_B=$'\033[1;34m'; C_G=$'\033[1;32m'; C_Y=$'\033[1;33m'; C_R=$'\033[1;31m'; C_0=$'\033[0m'
else
  C_B=""; C_G=""; C_Y=""; C_R=""; C_0=""
fi
say()   { printf '%s==>%s %s\n' "$C_B" "$C_0" "$*"; }
ok()    { printf '%s ok%s  %s\n' "$C_G" "$C_0" "$*"; }
warn()  { printf '%s !!%s  %s\n' "$C_Y" "$C_0" "$*" >&2; }
err()   { printf '%s ERR%s %s\n' "$C_R" "$C_0" "$*" >&2; }
have()  { command -v "$1" >/dev/null 2>&1; }

usage() {
  cat <<EOF
WMR installer

Usage: install.sh [options]
  -y, --yes          Never ask; take defaults (git identity is skipped unless
                     WMR_GIT_NAME / WMR_GIT_EMAIL are set)
  --only a,b         Run only these stages
  --skip a,b         Skip these stages
  --dry-run          Print what would run, change nothing
  -h, --help         This text

Stages (in order): $ALL_STAGES
  base    update packages, install git curl zsh python imagemagick ...
  repo    clone/update $WMR_REPO into \$WMR_HOME (default ~/WMR)
  zsh     oh-my-zsh + plugins + watermelonrobot theme + aliases + default shell
  python  python deps for the scripts in python/
  git     git name/email, SSH key, optional 'gh auth login'
  claude  Termux: proot-distro Ubuntu + Claude Code inside it
          Linux/mac: Node + Claude Code directly

Environment: WMR_GIT_NAME, WMR_GIT_EMAIL, WMR_HOME, WMR_REPO, WMR_PLUGINS
EOF
}

# ---------- argument parsing -------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    -y|--yes)   ASSUME_YES=1 ;;
    --only)     ONLY="${2:-}"; shift ;;
    --skip)     SKIP="${2:-}"; shift ;;
    --dry-run)  DRY_RUN=1 ;;
    --inner)    INNER=1 ;;       # internal: invoked inside proot Ubuntu
    -h|--help)  usage; exit 0 ;;
    *)          err "unknown option: $1"; usage; exit 2 ;;
  esac
  shift
done

# ---------- environment detection -------------------------------------------
detect_env() {
  if [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *com.termux* ]]; then
    ENV_KIND=termux
  elif [ "$(uname -s)" = "Darwin" ]; then
    ENV_KIND=mac
  elif have apt-get; then
    ENV_KIND=debian      # Ubuntu / Debian / proot Ubuntu / Raspberry Pi OS
  else
    ENV_KIND=unsupported
  fi

  SUDO=""
  if [ "$ENV_KIND" = debian ] && [ "$(id -u)" -ne 0 ]; then
    if have sudo; then SUDO="sudo"; else
      err "not root and sudo is missing - re-run as root or install sudo"; exit 1
    fi
  fi
}

# Run a command, or just print it under --dry-run.
run() {
  if [ "$DRY_RUN" -eq 1 ]; then printf '   [dry-run] %s\n' "$*"; return 0; fi
  "$@"
}

# ---------- prompting (works under `curl | bash` by reading /dev/tty) -------
TTY_OK=0
if [ "$ASSUME_YES" -eq 0 ] && [ -r /dev/tty ] && ( : </dev/tty ) 2>/dev/null; then TTY_OK=1; fi

# ask "question" "default"   -> echoes answer
ask() {
  local q="$1" def="${2:-}" ans=""
  if [ "$TTY_OK" -eq 1 ]; then
    if [ -n "$def" ]; then printf '%s [%s]: ' "$q" "$def" >/dev/tty; else printf '%s: ' "$q" >/dev/tty; fi
    IFS= read -r ans </dev/tty || ans=""
  fi
  printf '%s' "${ans:-$def}"
}
# confirm "question" Y|N   -> returns 0 for yes
confirm() {
  local q="$1" def="${2:-Y}" ans
  if [ "$TTY_OK" -eq 0 ]; then [ "$def" = Y ]; return; fi
  ans="$(ask "$q (y/n)" "$(printf '%s' "$def" | tr 'A-Z' 'a-z')")"
  case "$ans" in [Yy]*) return 0 ;; *) return 1 ;; esac
}

stage_enabled() {
  local s="$1"
  if [ -n "$ONLY" ]; then case ",$ONLY," in *",$s,"*) return 0 ;; *) return 1 ;; esac; fi
  case ",$SKIP," in *",$s,"*) return 1 ;; esac
  return 0
}

# ---------- package helpers --------------------------------------------------
PKG_UPDATED=0
pkg_update() {
  [ "$PKG_UPDATED" -eq 1 ] && return 0
  case "$ENV_KIND" in
    termux)
      run pkg update -y || warn "pkg update failed (try: termux-change-repo)"
      run env DEBIAN_FRONTEND=noninteractive apt-get -y \
          -o Dpkg::Options::=--force-confold upgrade || warn "apt upgrade had problems" ;;
    debian)
      run $SUDO env DEBIAN_FRONTEND=noninteractive apt-get update -y || warn "apt update failed" ;;
    mac)
      have brew && run brew update ;;
  esac
  PKG_UPDATED=1
}

# pkg_install <termux-names> -- <debian-names> -- <brew-names>
pkg_install() {
  # -e: install each package separately so one missing package can't sink the rest
  if [ "${1:-}" = "-e" ]; then
    shift
    local each=() cur=t a
    for a in "$@"; do
      if [ "$a" = "--" ]; then case "$cur" in t) cur=d ;; d) cur=b ;; esac; continue; fi
      case "$ENV_KIND:$cur" in termux:t|debian:d|mac:b) each+=("$a") ;; esac
    done
    for a in ${each[@]+"${each[@]}"}; do
      case "$ENV_KIND" in
        termux) run pkg install -y "$a" >/dev/null 2>&1 && ok "$a" || warn "skipped (not available): $a" ;;
        debian) run $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y "$a" >/dev/null 2>&1 && ok "$a" || warn "skipped (not available): $a" ;;
        mac)    have brew && { run brew install "$a" >/dev/null 2>&1 && ok "$a" || warn "skipped: $a"; } ;;
      esac
    done
    return 0
  fi
  local t=() d=() b=() cur=t a
  for a in "$@"; do
    if [ "$a" = "--" ]; then
      case "$cur" in t) cur=d ;; d) cur=b ;; esac; continue
    fi
    case "$cur" in t) t+=("$a") ;; d) d+=("$a") ;; b) b+=("$a") ;; esac
  done
  case "$ENV_KIND" in
    termux) [ ${#t[@]} -gt 0 ] && { run pkg install -y "${t[@]}" || warn "some Termux packages failed: ${t[*]}"; } ;;
    debian) [ ${#d[@]} -gt 0 ] && { run $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y "${d[@]}" \
                                      || warn "some apt packages failed: ${d[*]}"; } ;;
    mac)    if have brew; then [ ${#b[@]} -gt 0 ] && { run brew install "${b[@]}" || warn "some brew packages failed: ${b[*]}"; }
            else warn "Homebrew not found - install it from https://brew.sh then re-run"; fi ;;
  esac
}

# git_sync <url> <dest> [clone-args...]   clone, or fast-forward pull if present
git_sync() {
  local url="$1" dest="$2"; shift 2
  if [ -d "$dest/.git" ]; then
    run git -C "$dest" pull --ff-only --quiet || warn "could not update $dest (local changes?)"
  else
    run mkdir -p "$(dirname "$dest")"
    run git clone --quiet "$@" "$url" "$dest" || { warn "clone failed: $url"; return 1; }
  fi
}

# Append a block to a file once, identified by a marker line.
append_once() {
  local file="$1" marker="$2" body="$3"
  touch "$file" 2>/dev/null || true
  if grep -qF "$marker" "$file" 2>/dev/null; then return 0; fi
  [ "$DRY_RUN" -eq 1 ] && { printf '   [dry-run] append %s block to %s\n' "$marker" "$file"; return 0; }
  printf '\n%s\n%s\n' "$marker" "$body" >> "$file"
}

# Replace the first line matching an ERE with a new line.  If nothing matches,
# insert it just before the `source ...oh-my-zsh.sh` line (so it still takes
# effect), or append when there is no such line.
# set_line <file> <ERE> <new line>
set_line() {
  local file="$1" re="$2" new="$3" tmp line replaced=0
  [ "$DRY_RUN" -eq 1 ] && { printf '   [dry-run] set %s in %s\n' "$new" "$file"; return 0; }
  touch "$file"
  tmp="$(mktemp)"
  if grep -Eq "$re" "$file"; then
    while IFS= read -r line || [ -n "$line" ]; do
      if [ "$replaced" -eq 0 ] && [[ $line =~ $re ]]; then printf '%s\n' "$new"; replaced=1
      else printf '%s\n' "$line"; fi
    done < "$file" > "$tmp"
  else
    local src='^[[:space:]]*source[[:space:]].*oh-my-zsh\.sh'
    while IFS= read -r line || [ -n "$line" ]; do
      if [ "$replaced" -eq 0 ] && [[ $line =~ $src ]]; then printf '%s\n' "$new"; replaced=1; fi
      printf '%s\n' "$line"
    done < "$file" > "$tmp"
    [ "$replaced" -eq 0 ] && printf '%s\n' "$new" >> "$tmp"
  fi
  cat "$tmp" > "$file"; rm -f "$tmp"
}

# ---------- stage: base ------------------------------------------------------
stage_base() {
  say "Base packages"
  pkg_update
  # essentials: all together (fast); optional extras: one by one so a missing package can't break the rest
  pkg_install git curl zsh openssh python ncurses-utils \
    -- git curl zsh openssh-client python3 python3-pip python3-venv ncurses-bin ca-certificates \
    -- git curl zsh python
  pkg_install -e wget jq nano imagemagick ffmpeg gh \
    -- wget jq nano imagemagick ffmpeg \
    -- wget jq imagemagick ffmpeg gh
  if [ "$ENV_KIND" = termux ] && [ "$INNER" -eq 0 ] && confirm "Grant Termux access to shared storage (termux-setup-storage)?" Y; then
    run termux-setup-storage || true
  fi
}

# ---------- stage: repo ------------------------------------------------------
ensure_repo() {
  have git || { err "git is not installed - run the 'base' stage first"; return 1; }
  git_sync "$WMR_REPO" "$WMR_HOME"
}
stage_repo() { say "WMR repo -> $WMR_HOME"; ensure_repo && ok "repo ready"; }

# ---------- stage: zsh -------------------------------------------------------
stage_zsh() {
  say "zsh + oh-my-zsh + watermelonrobot theme"
  have zsh || pkg_install zsh -- zsh -- zsh
  have zsh || { err "zsh is not available"; return 1; }
  have git && have curl || { err "git and curl are required (run the base stage)"; return 1; }

  [ -f "$WMR_HOME/config/wmr.zsh" ] || ensure_repo || warn "repo unavailable: aliases/theme will be fetched without it"
  # Always under $HOME: an inherited $ZSH from another session must not redirect us.
  local omz="$HOME/.oh-my-zsh"
  if [ -d "$omz" ]; then
    ok "oh-my-zsh already installed"
  else
    # --unattended: don't start zsh / chsh;  --keep-zshrc: leave an existing .zshrc alone
    local installer; installer="$(mktemp)"
    if run curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -o "$installer"; then
      [ "$DRY_RUN" -eq 1 ] || ZSH="$omz" RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh "$installer" --unattended || warn "oh-my-zsh installer reported a problem"
    else
      warn "could not download the oh-my-zsh installer"
    fi
    rm -f "$installer"
  fi
  [ -d "$omz" ] || [ "$DRY_RUN" -eq 1 ] || { err "oh-my-zsh is missing; cannot continue zsh stage"; return 1; }

  # .zshrc must exist (KEEP_ZSHRC / earlier failures can leave it missing)
  if [ ! -f "$HOME/.zshrc" ] && [ "$DRY_RUN" -eq 0 ]; then
    if [ -f "$omz/templates/zshrc.zsh-template" ]; then
      sed "s|^export ZSH=.*|export ZSH=\"$omz\"|" "$omz/templates/zshrc.zsh-template" > "$HOME/.zshrc"
    else
      printf 'export ZSH="%s"\nZSH_THEME="robbyrussell"\nplugins=(git)\nsource $ZSH/oh-my-zsh.sh\n' "$omz" > "$HOME/.zshrc"
    fi
  fi

  local custom="$omz/custom"
  git_sync https://github.com/zsh-users/zsh-autosuggestions.git      "$custom/plugins/zsh-autosuggestions"      --depth 1
  git_sync https://github.com/zsh-users/zsh-syntax-highlighting.git   "$custom/plugins/zsh-syntax-highlighting"  --depth 1
  git_sync https://github.com/marlonrichert/zsh-autocomplete.git      "$custom/plugins/zsh-autocomplete"         --depth 1

  # Theme: prefer the checked-out repo copy (always in sync), else download.
  run mkdir -p "$custom/themes"
  if [ -f "$WMR_HOME/watermelonrobot.zsh-theme" ]; then
    run cp "$WMR_HOME/watermelonrobot.zsh-theme" "$custom/themes/watermelonrobot.zsh-theme"
  else
    run curl -fsSL "$WMR_RAW/watermelonrobot.zsh-theme" -o "$custom/themes/watermelonrobot.zsh-theme" \
      || warn "could not fetch the theme"
  fi

  # .zshrc edits. zsh-autocomplete first, zsh-syntax-highlighting last (their docs).
  local plugins="${WMR_PLUGINS:-git zsh-autocomplete zsh-autosuggestions zsh-syntax-highlighting}"
  set_line "$HOME/.zshrc" '^[[:space:]]*ZSH_THEME=' 'ZSH_THEME="watermelonrobot"'
  set_line "$HOME/.zshrc" '^[[:space:]]*plugins=\(.*\)[[:space:]]*$' "plugins=($plugins)"
  append_once "$HOME/.zshrc" "# >>> WMR >>>" \
"export WMR_HOME=\"$WMR_HOME\"
[ -f \"\$WMR_HOME/config/wmr.zsh\" ] && source \"\$WMR_HOME/config/wmr.zsh\"
# <<< WMR <<<"
  ok ".zshrc configured (theme + plugins + WMR aliases)"

  # Default shell
  if [ "$ENV_KIND" = termux ]; then
    run chsh -s zsh || warn "chsh failed; run 'chsh -s zsh' manually"
  elif [ "$ENV_KIND" = debian ]; then
    local zpath; zpath="$(command -v zsh)"
    if [ "$DRY_RUN" -eq 0 ] && { chsh -s "$zpath" 2>/dev/null || $SUDO chsh -s "$zpath" "$(id -un)" 2>/dev/null; }; then
      ok "default shell -> zsh"
    else
      # chsh often can't work in proot; fall back to exec-ing zsh from bash
      append_once "$HOME/.bashrc" "# >>> WMR zsh >>>" \
'if [ -t 1 ] && [ -z "${ZSH_VERSION:-}" ] && command -v zsh >/dev/null 2>&1; then exec zsh; fi
# <<< WMR zsh <<<'
      ok "bash will hand off to zsh (chsh unavailable here)"
    fi
  fi
}

# ---------- stage: python ----------------------------------------------------
pip_install() {
  # Newer distros mark the system python "externally managed" (PEP 668).
  run python3 -m pip install -q "$@" 2>/dev/null \
    || run python3 -m pip install -q --break-system-packages "$@" \
    || return 1
}
stage_python() {
  say "Python dependencies"
  case "$ENV_KIND" in
    termux)
      pkg_install -e python-numpy python-pillow python-pandas -- -- ;;
    debian)
      pkg_install -e -- python3-numpy python3-pil python3-pandas -- ;;
    mac)
      warn "mac: skipping auto pip install. Use:  python3 -m pip install -r $WMR_HOME/python/requirements.txt"
      return 0 ;;
  esac
  have python3 || { warn "python3 not found"; return 1; }
  local req="$WMR_HOME/python/requirements.txt" heavy="$WMR_HOME/python/requirements-heavy.txt"
  [ -f "$req" ] || ensure_repo
  if [ -f "$req" ]; then
    pip_install -r "$req" && ok "installed python/requirements.txt" || warn "some pip packages failed (see output above)"
  else
    warn "$req not found (repo stage skipped?)"
  fi
  # pandas / yfinance / google-generativeai: fine on Linux wheels, but on Termux they may compile for ages.
  if [ -f "$heavy" ]; then
    local want=Y; [ "$ENV_KIND" = termux ] && want=N
    if confirm "Install heavy deps (yfinance/pandas, google-generativeai)? $( [ "$ENV_KIND" = termux ] && echo 'Can compile for a long time on Termux.')" "$want"; then
      pip_install -r "$heavy" && ok "installed python/requirements-heavy.txt" || warn "heavy deps failed (on Termux try: pkg install python-pandas)"
    else
      say "skipped heavy deps - later: python3 -m pip install -r $heavy"
    fi
  fi
  say "Not installed automatically: python/requirements-pc.txt (mediapipe/opencv, desktop only)"
  say "                             python/requirements-pi.txt (Raspberry Pi GPIO/Adafruit libs)"
}

# ---------- stage: git / ssh -------------------------------------------------
stage_git() {
  say "git identity + SSH key"
  have git || { err "git missing"; return 1; }
  local name="${WMR_GIT_NAME:-$(git config --global user.name 2>/dev/null || true)}"
  local email="${WMR_GIT_EMAIL:-$(git config --global user.email 2>/dev/null || true)}"
  [ -z "$name" ]  && name="$(ask  'git user.name (blank to skip)' '')"
  [ -z "$email" ] && email="$(ask 'git user.email (blank to skip)' '')"
  export WMR_GIT_NAME="$name" WMR_GIT_EMAIL="$email"
  [ -n "$name" ]  && run git config --global user.name  "$name"
  [ -n "$email" ] && run git config --global user.email "$email"
  run git config --global init.defaultBranch main
  run git config --global pull.ff only

  [ "$INNER" -eq 1 ] && return 0     # key + gh login live on the Termux side
  if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
    if confirm "Generate an SSH key (ed25519) for GitHub?" Y; then
      run mkdir -p "$HOME/.ssh"; run chmod 700 "$HOME/.ssh"
      local comment="${email:-$(id -un)@$(hostname 2>/dev/null || echo device)}"
      if [ "$TTY_OK" -eq 1 ]; then run ssh-keygen -t ed25519 -C "$comment" -f "$HOME/.ssh/id_ed25519"
      else run ssh-keygen -t ed25519 -N "" -C "$comment" -f "$HOME/.ssh/id_ed25519"; fi
    fi
  else
    ok "SSH key already exists"
  fi
  if [ -f "$HOME/.ssh/id_ed25519.pub" ]; then
    say "Public key (add at https://github.com/settings/ssh/new):"
    cat "$HOME/.ssh/id_ed25519.pub"
  fi

  if have gh && ! gh auth status >/dev/null 2>&1 && [ "$TTY_OK" -eq 1 ]; then
    if confirm "Log in to GitHub with 'gh auth login' now?" Y; then
      gh auth login && gh auth setup-git
    fi
  fi
}

# ---------- stage: claude ----------------------------------------------------
# Inside Ubuntu (or any Linux/mac with node): install Claude Code.
claude_install_local() {
  if have claude; then ok "claude already installed: $(claude --version 2>/dev/null || echo '?')"; return 0; fi
  say "Installing Claude Code (native installer, npm fallback)"
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '   [dry-run] curl -fsSL https://claude.ai/install.sh | bash   (fallback: npm i -g @anthropic-ai/claude-code)\n'
    return 0
  fi
  local inst; inst="$(mktemp)"
  if curl -fsSL https://claude.ai/install.sh -o "$inst" && [ -s "$inst" ] && bash "$inst"; then
    export PATH="$HOME/.local/bin:$PATH"
    if have claude; then ok "claude installed"; rm -f "$inst"; return 0; fi
  fi
  rm -f "$inst"
  warn "native installer did not produce 'claude'; falling back to npm"
  if ! have npm; then
    case "$ENV_KIND" in
      debian) $SUDO sh -c 'curl -fsSL https://deb.nodesource.com/setup_22.x | bash -' && pkg_install -- nodejs -- ;;
      mac)    pkg_install -- -- node ;;
    esac
  fi
  have npm || { err "npm unavailable; install Node, then: npm i -g @anthropic-ai/claude-code"; return 1; }
  $SUDO npm install -g @anthropic-ai/claude-code && ok "claude installed via npm"
}

stage_claude() {
  if [ "$ENV_KIND" = termux ]; then
    say "Claude Code via proot-distro $UBUNTU_ALIAS"
    pkg_install proot-distro -- --
    have proot-distro || { err "proot-distro missing"; return 1; }
    local rootfs="${PREFIX:-/data/data/com.termux/files/usr}/var/lib/proot-distro/installed-rootfs/$UBUNTU_ALIAS"
    if [ -d "$rootfs" ]; then ok "$UBUNTU_ALIAS rootfs already installed"
    else run proot-distro install "$UBUNTU_ALIAS" || { err "proot-distro install failed"; return 1; }; fi
    ensure_repo || true
    # Re-run this same installer inside Ubuntu, with the repo bind-mounted so no extra download is needed.
    run proot-distro login "$UBUNTU_ALIAS" --shared-tmp --bind "$WMR_HOME:/root/WMR" -- \
      env WMR_HOME=/root/WMR WMR_GIT_NAME="${WMR_GIT_NAME:-}" WMR_GIT_EMAIL="${WMR_GIT_EMAIL:-}" \
      bash /root/WMR/install.sh --yes --inner --only base,zsh,python,git,claude \
      || { err "install inside Ubuntu failed - retry with: proot-distro login $UBUNTU_ALIAS"; return 1; }
    ok "Ubuntu ready.  'ubu' = shell in Ubuntu,  'cl' = Claude Code on the current directory"
    say "First run: type  cl  and sign in (it prints a URL; open it in the phone browser)"
  else
    claude_install_local
  fi
}

# ---------- main -------------------------------------------------------------
main() {
  detect_env
  [ "$ENV_KIND" = unsupported ] && { err "unsupported system (need Termux, Debian/Ubuntu, or macOS)"; exit 1; }
  [ "$DRY_RUN" -eq 1 ] && warn "DRY RUN - nothing will be changed"
  say "WMR installer  [env: $ENV_KIND$( [ "$INNER" -eq 1 ] && echo ', inside proot')]  home: $HOME"

  # If we are being run from a checkout, prefer it over ~/WMR.
  local here; here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
  if [ -n "$here" ] && [ -f "$here/watermelonrobot.zsh-theme" ] && [ "$here" != "$WMR_HOME" ] && [ ! -d "$WMR_HOME/.git" ]; then
    WMR_HOME="$here"; ok "using checkout at $WMR_HOME"
  fi

  local s fn
  for s in $ALL_STAGES; do
    stage_enabled "$s" || { say "skip: $s"; continue; }
    # Offer a choice per stage on a terminal; defaults to yes.
    if [ "$TTY_OK" -eq 1 ] && [ -z "$ONLY" ] && ! confirm "Run stage '$s'?" Y; then say "skip: $s"; continue; fi
    # In the proot, 'claude' means "install it here".
    fn="stage_$s"
    if ! "$fn"; then FAILED+=("$s"); fi
  done

  echo
  if [ ${#FAILED[@]} -gt 0 ]; then
    warn "finished with problems in: ${FAILED[*]}   (re-run: ./install.sh --only ${FAILED[0]})"
  else
    ok "all done"
  fi
  [ "$INNER" -eq 0 ] && say "Open a new session (or run:  exec zsh ) to load the new shell."
  return 0
}

# In inner mode the 'claude' stage must install locally, not nest another proot.
if [ "$INNER" -eq 1 ]; then
  stage_claude() { claude_install_local; }
fi

main "$@"
