# WMR (watermelonrobot)
wmr settings and configs and apps - one script to set up a fresh device.

## Quick start

**Fresh Termux** (install Termux from F-Droid or GitHub, not the Play Store):

```bash
pkg update -y && pkg upgrade -y && pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/etothex23/WMR/main/install.sh | bash
```

**Already cloned** (Ubuntu / Debian / Raspberry Pi OS / proot / macOS):

```bash
git clone https://github.com/etothex23/WMR.git ~/WMR && ~/WMR/install.sh
```

It asks a handful of questions (stage on/off, git name/email, SSH key, `gh auth login`).
`./install.sh --yes` takes every default and asks nothing.
Safe to re-run any time - it only fixes what's missing and updates what's there.

## What it does (stages)

| stage    | what |
|----------|------|
| `base`   | update packages; git, curl, zsh, openssh, python, imagemagick, ffmpeg, jq, gh, ... |
| `repo`   | clone/update this repo to `~/WMR` |
| `zsh`    | oh-my-zsh, plugins (autosuggestions, syntax-highlighting, autocomplete), the `watermelonrobot` theme, `~/.zshrc` edits, aliases, default shell |
| `python` | python deps for `python/` (`requirements.txt`; heavy ones are opt-in on Termux) |
| `git`    | `user.name`/`user.email`, ed25519 SSH key (prints the public key), optional `gh auth login` |
| `claude` | Termux: proot-distro **Ubuntu** + the same installer inside it + **Claude Code**. Linux/mac: Claude Code directly |

```bash
./install.sh --only zsh          # just one stage (or: zsh,git)
./install.sh --skip claude       # everything except one
./install.sh --dry-run           # print, don't do
WMR_GIT_NAME="Me" WMR_GIT_EMAIL="me@example.com" ./install.sh --yes   # fully unattended
```

After install:

* `meow`, `rnf`, `gifit`, `noice` - the helper scripts in `bash/` (also on `PATH`)
* `wmr-update` - pull the latest WMR; `updootit` - update the system packages
* Termux: `ubu` opens a shell in Ubuntu; `cl` runs **Claude Code in Ubuntu on the folder you are standing in**
  (first run prints a login URL - open it in the phone browser)

## Layout

```
install.sh                  the bootstrap (curl | bash friendly)
watermelonrobot.zsh-theme   zsh theme
config/wmr.zsh              aliases/PATH sourced from ~/.zshrc (edit once, git pull everywhere)
config/aliases-mac.zsh      macOS-only aliases
bash/                       create_gif.sh  kitty-cat.sh  noice.sh  rename_files.sh  ascii-cats.txt
python/                     all the python scripts (see requirements*.txt)
docs/NEW-PHONE-CHECKLIST.md the non-scriptable half of a phone migration
custom-terminal             old zsh-only script, now a shim that calls install.sh --only zsh
```

### Python notes
* `requirements.txt` light deps; `requirements-heavy.txt` pandas/yfinance/google-generativeai;
  `requirements-pc.txt` mediapipe/opencv (desktop only); `requirements-pi.txt` Raspberry Pi hardware libs.
* `python/pyTracking/get_models.sh` downloads the MediaPipe `.task` models (kept out of git).
* tkinter GUIs (quotes, Market Sentinel) need a desktop; they won't open on Termux.
* Not included on purpose: virtualenvs, `.idea/`, and two big generated images
  (`newquotes/newquote/images/quote_image.png`, `nature-image/nature.jpg`).
* Scripts with API keys (`quotes*.py`, `GAISDK/agent-request.py`) contain placeholders only - keep real keys out of git.

---

Plank: the dock app
1. I am making a plank editor - gui
2. The commands are available but I like the app and wanted to contribute
