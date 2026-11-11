#!/usr/bin/env bash

# Restore cursor on exit
trap 'tput cnorm; echo ""; exit 0' INT TERM EXIT

# Hide cursor and clear screen
tput civis
clear

# Animation frames
frame1="
     NOICE!
    \(•_•)
     (   (>
     /   \\
"

frame2="
     NOICE!
     (•_•)
     <)   )
     /   \\
"

frame3="
     NOICE!
    \(•_•)/
      (  )
      |  |
"

frame4="
     NOICE!
     (•_•)
     <)   )>
     /   \\
"

frames=("$frame1" "$frame2" "$frame3" "$frame4")

# Loop animation 3 times (or change to 'while true;' for infinite)
for _ in {1..3}; do
    for f in "${frames[@]}"; do
        tput cup 0 0
        echo -e "$f"
        sleep 0.2
    done
done
