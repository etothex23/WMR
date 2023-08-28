# @watermelonrobot
# balls.sackman@watermelonrobot.com
#
# This theme is based on the oh-my-zsh theme: jonathan
# https://github.com/championswimmer/oh-my-zsh/blob/master/themes/jonathan.zsh-theme
# This theme is in development and may not display properly
# you can change the top bar length by changing the theme_precmd

# THEME_PRECMD---------------------------------------------
function theme_precmd {
  local TERMWIDTH=$(( COLUMNS - ${ZLE_RPROMPT_INDENT:-1} ))

  PR_FILLBAR=""
  PR_PWDLEN=""

  local promptsize=${#${(%):---(( ⚆_⚆)---(%n@%m:%l)---(☉_☉ )---()---}}
  local rubypromptsize=${#${(%)$(ruby_prompt_info)}}
  local pwdsize=${#${(%):-%~}}

  # Truncate the path if it's too long.
  if (( promptsize + rubypromptsize + pwdsize > TERMWIDTH )); then
    (( PR_PWDLEN = TERMWIDTH - promptsize ))
  elif [[ "${langinfo[CODESET]}" = UTF-8 ]]; then
    PR_FILLBAR="\${(l:$(( TERMWIDTH - (promptsize + rubypromptsize + pwdsize) ))::${PR_HBAR}:)}"
  else
    PR_FILLBAR="${PR_SHIFT_IN}\${(l:$(( TERMWIDTH - (promptsize + rubypromptsize + pwdsize) ))::${altchar[q]:--}:)}${PR_SHIFT_OUT}"
  fi
}

# THEME_PREEXEC--------------------------------
# 
function theme_preexec {
  setopt local_options extended_glob
  if [[ "$TERM" = "screen" ]]; then
    local CMD=${1[(wr)^(*=*|sudo|-*)]}
    echo -n "\ek$CMD\e\\"
  fi
}

# THEME_SPLASH---------------------------------
# 
function theme_splash {
  clear
  printf "%s\n"
  printf "%9s*%s\n"
  printf "%5s*-{o 0}-* $(pwd) SuK aWn dEeZ Nutzzz%s\n"
  printf "%10s__%6s_%1s_%2s_%1s__%1s_____%1s_%2s_%1s___%1s___%1s___%1s___%1s_________%s\n"
  printf "%10s\%1s\%4s/%1s|%2s\%2s/%2s|%1s(%2s)%1s|/%2s__%2s\%2s0%2s|/%5s\%1s__%3s___|%s\n"
  printf "%11s\%1s\/\/%1s/|%3s\/%3s|%2s__%2s\|%1s|__|%1s|%4s<%3s0%1s.%1s0>%1s|%2s|%s\n"
  printf "%12s\_/\_/%1s|_%1s|%2s|%1s_|__|%1s\__\______/__0__|\_____/%2s|__|%s\n"
  printf "%s\n"
  # echo df -h -T apfs /System/Volumes/Data
  # echo du -sk -I *Library* * | awk '{ printf "[%-40s %15f]\n", $2, $1 }' 
}
# attempted formater


# AUTOLOAD
# Loading functions----------------------------
autoload -U add-zsh-hook
add-zsh-hook precmd  theme_precmd
add-zsh-hook preexec theme_preexec

# Set the prompt
# setop prompt_subst is used top tell zsh to switch it up
# Need this so the prompt will work.
setopt prompt_subst

# See if we can use colors.
autoload zsh/terminfo
for color in RED GREEN YELLOW BLUE MAGENTA CYAN WHITE GREY; do
  typeset -g PR_$color="%{$terminfo[bold]$fg[${(L)color}]%}"
  typeset -g PR_LIGHT_$color="%{$fg[${(L)color}]%}"
done
PR_NO_COLOUR="%{$terminfo[sgr0]%}"

# Modify Git prompt
ZSH_THEME_GIT_PROMPT_PREFIX=" on %{$fg[green]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_DIRTY=""
ZSH_THEME_GIT_PROMPT_CLEAN=""

ZSH_THEME_GIT_PROMPT_ADDED="%{$fg[green]%} %{%G✚%}"
ZSH_THEME_GIT_PROMPT_MODIFIED="%{$fg[blue]%} %{%G✹%}"
ZSH_THEME_GIT_PROMPT_DELETED="%{$fg[red]%} %{%G✖%}"
ZSH_THEME_GIT_PROMPT_RENAMED="%{$fg[magenta]%} %{%G➜%}"
ZSH_THEME_GIT_PROMPT_UNMERGED="%{$fg[yellow]%} %{%G═%}"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%{$fg[cyan]%} %{%G✭%}"

# Use extended characters to look nicer if supported.
if [[ "${langinfo[CODESET]}" = UTF-8 ]]; then
  PR_SET_CHARSET=""
  PR_HBAR="─"
  PR_ULCORNER="┌"
  PR_VBAR="|"
  PR_LLCORNER="└"
  PR_LRCORNER="9"
  PR_URCORNER="6"
else
  typeset -g -A altchar
  set -A altchar ${(s..)terminfo[acsc]}
  # Some stuff to help us draw nice lines
  PR_SET_CHARSET="%{$terminfo[enacs]%}"
  PR_SHIFT_IN="%{$terminfo[smacs]%}"
  PR_SHIFT_OUT="%{$terminfo[rmacs]%}"
  PR_HBAR="${PR_SHIFT_IN}${altchar[q]:--}${PR_SHIFT_OUT}"
  PR_ULCORNER="${PR_SHIFT_IN}${altchar[l]:--}${PR_SHIFT_OUT}"
  PR_LLCORNER="${PR_SHIFT_IN}${altchar[m]:--}${PR_SHIFT_OUT}"
  PR_VBAR="${PR_SHIFT_IN}${altchar[m]:--}${PR_SHIFT_OUT}"
  PR_LRCORNER="${PR_SHIFT_IN}${altchar[j]:--}${PR_SHIFT_OUT}"
  PR_URCORNER="${PR_SHIFT_IN}${altchar[k]:--}${PR_SHIFT_OUT}"
fi

# Decide if we need to set titlebar text.
case $TERM in
  xterm*)
    PR_TITLEBAR=$'%{\e]0;%(!.-=*[ROOT]*=- | .)%n@%m:%~ | ${COLUMNS}x${LINES} | %y\a%}'
    ;;
  screen)
    PR_TITLEBAR=$'%{\e_screen \005 (\005t) | %(!.-=[ROOT]=- | .)%n@%m:%~ | ${COLUMNS}x${LINES} | %y\e\\%}'
    ;;
  *)
    PR_TITLEBAR=""
    ;;
esac

# Decide whether to set a screen title
if [[ "$TERM" = "screen" ]]; then
  PR_STITLE=$'%{\ekzsh\e\\%}'
else
  PR_STITLE=""
fi

FFACES=("( ⚆_⚆)" "(☉_☉ )" "( ◕‿◕)" "(◕‿◕ )" "(⇀‿‿↼)" "(≖‿‿≖)" "(◕‿‿◕)" "(-__-)" "(°▃▃°)" "(⌐■_■)" "(•‿‿•)" "(ᵔ◡◡ᵔ)" "(^‿‿^)" "(☼‿‿☼)" "(≖__≖)" "(✜‿‿✜)" "(ب__ب)" "(╥☁╥ )" "(-_-')" "(♥‿‿♥)" "(☓‿‿☓)" "(#__#)" "(1__0)" "(1__1)" "(0__1)")

PR_RFACE=${FFACES[RANDOM%9]}
PR_LFACE=${FFACES[RANDOM%10]}
PR_LTFACE=${FFACES[RANDOM%10]}
PR_ROOT=${FFACES[RANDOM%13]}
PR_MYPWD=$(pwd)
PR_ARM="=<"

PROMPT='${PR_SET_CHARSET}${PR_STITLE}${(e)PR_TITLEBAR}\
${PR_GREEN}${PR_ULCORNER}${PR_HBAR}${PR_GREEN}(${PR_YELLOW}${PR_LTFACE}${PR_LIGHT_RED}[$(pwd)]\
${PR_GREEN})%${PR_PWDLEN}<...<%${PR_ROOT}%<<\
$(ruby_prompt_info)${PR_GREEN}${PR_HBAR}${PR_HBAR}${(e)PR_FILLBAR}${PR_HBAR}\
${PR_YELLOW}%D{%a,%b%d %H:%M:%S}${PR_MAGENTA}${PR_RFACE}\
${PR_GREEN})${PR_GREEN}${PR_HBAR}${PR_URCORNER}\

${PR_GREEN}${PR_VBAR}\

${PR_GREEN}${PR_LLCORNER}${PR_HBAR}${PR_BLUE}(\
${PR_MAGENTA}${PR_LFACE}${PR_ARM}../${$(pwd)##*/}\
${PR_LIGHT_BLUE}%{$reset_color%}$(git_prompt_info)$(git_prompt_status)${PR_BLUE})${PR_GREEN}${PR_HBAR}\
${PR_HBAR}\
>${PR_NO_COLOUR} '

# display exitcode on the right when > 0
return_code="%(?..%{$fg[red]%}%? ↵ %{$reset_color%})"
RPROMPT=' $return_code${PR_CYAN}${PR_HBAR}${PR_BLUE}${PR_HBAR}\
(${PR_BLUE})${PR_CYAN}${PR_LRCORNER}${PR_NO_COLOUR}'

PS2='${PR_BLUE}${PR_HBAR}\
${PR_HBAR}(\
${PR_LIGHT_GREEN}%_${PR_BLUE})${PR_HBAR}\
${PR_CYAN}${PR_HBAR}${PR_NO_COLOUR} '

theme_splash