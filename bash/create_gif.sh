#!/bin/bash

# Show the current Directory
echo -e "\033[1;33mCurrent directory: $(pwd)\033[0m"

# Ask for the directory path
read -p $'\033[1;35mEnter the directory path where the files are located: \033[0m' dir_path

# If the user leaves it blank, use the current directory
if [[ -z "$dir_path" ]]; then
  dir_path="."
fi

# Check if the directory exists
if [[ ! -d "$dir_path" ]]; then
  echo -e "\033[1;31mDirectory not found. Please enter a valid directory.\033[0m"
  exit 1
fi

# Ask for the file extension (without the dot)
#read -p $'\033[1;35mEnter the image type (e.g., jpg, png): \033[0m' extension

# Prompt user to choose a file type
echo -e "\033[1;35mChoose the file type:\033[0m"
echo -e "\033[1;35m  1. jpg\033[0m"
echo -e "\033[1;35m  2. png\033[0m"
# Read the user's choice
read -p $'\033[1;35mEnter the number corresponding to your choice: ' choice

# Set the 'extension' variable based on the choice
case $choice in
  1)
    extension="jpg"
    ;;
  2)
    extension="png"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

# Ask for delay
# Loop until valid input is provided
while true; do
    # Prompt the user for input
    read -p "Enter a number between 1 and 1000: " delay

    # Check if the input is a valid number between 1 and 1000
    if [[ "$delay" =~ ^[0-9]+$ ]] && [ "$delay" -ge 1 ] && [ "$delay" -le 1000 ]; then
        echo "You entered: $delay"
        break
    else
        echo "Invalid input. Please enter a number between 1 and 1000."
    fi
done

# Ask for the prefix for renaming
read -p $'\033[1;35mEnter the name of the GIF: \033[0m' gif_name

# Initialize a counter for numbering
#counter=1

# Change to the specified directory
cd "$dir_path" || exit

# Loop through all files with the specified extension in the directory
if command -v magick >/dev/null 2>&1; then im=magick; else im=convert; fi
shopt -s nullglob
files=(*."$extension")
if [ ${#files[@]} -eq 0 ]; then echo "No .$extension files found in $(pwd)"; exit 1; fi
"$im" -delay "$delay" -loop 0 "${files[@]}" "$gif_name.gif" && \
  echo -e "\033[1;36mCreated $gif_name.gif from ${#files[@]} .$extension files.\033[0m"


