# New phone checklist (Fold 7 -> Fold 8 Ultra)

The parts `install.sh` cannot do - Android settings, accounts, apps.

## 1. Security first
- [ ] Screen lock (PIN/pattern), then fingerprint / face
- [ ] Samsung account + Google account sign-in; Find My Mobile on
- [ ] Re-enroll biometrics for apps that use them (banking, password manager, Google Pay)
- [ ] Authenticator app: confirm codes were transferred **before** wiping the old phone

## 2. Log in everywhere (prove access on the new phone)
- [ ] Google (Gmail, Drive, Docs), Samsung, Microsoft
- [ ] GitHub (`gh auth login` in Termux - the installer offers it)
- [ ] Claude (app + `cl` in Termux)
- [ ] Banking / finance, social, messaging (WhatsApp/Signal need re-verification)
- [ ] Anything on 2FA tied to the old device - move it, then remove the old device

## 3. Google Docs
- [ ] Open the doc started for the new setup; confirm offline access is on for key docs

## 4. Poweramp
- [ ] Reinstall / restore license (Play Store account must match)
- [ ] Restore settings: Poweramp > Settings > Backup/Restore (or the backup zip)
- [ ] Re-add music folders / rescan library; check equalizer, skin, output device, gapless/crossfade

## 5. Termux (this repo)
- [ ] Install Termux from F-Droid (or GitHub releases), plus Termux:API if wanted
- [ ] `pkg update -y && pkg upgrade -y && pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/etothex23/WMR/main/install.sh | bash`
- [ ] Add the printed SSH public key at https://github.com/settings/ssh/new
- [ ] Type `cl` in a folder, sign in to Claude Code
- [ ] Android: Settings > Apps > Termux > Battery > Unrestricted (so long jobs aren't killed)
