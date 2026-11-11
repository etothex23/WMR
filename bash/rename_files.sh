#!/bin/bash

# Show the current Directory
echo -e "\033[1;33mCurrent directory: $(pwd)\033[0m"

# Ask for the directory path
read -p $'\033[1;35mEnter path or blank for current dir: \033[0m' dir_path

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
read -p $'\033[1;35mEnter the file extension (e.g., jpg, txt): \033[0m' extension

# Ask for the prefix for renaming
read -p $'\033[1;35mEnter the prefix for renaming files: \033[0m' prefix

# Initialize a counter for numbering
counter=1

# Change to the specified directory
cd "$dir_path" || exit

# Loop through all files with the specified extension in the directory
for file in *."$extension"; do
    # Ensure we're only processing files
    if [[ -f "$file" ]]; then
        # Create the new file name using the prefix and counter, preserving the extension
        new_name="${prefix}_${counter}.${extension}"
        # Rename the file
        mv "$file" "$new_name"
        # Increment the counter
        ((counter++))
    fi
done

echo -e "\033[1;36mAll files with the .$extension extension renamed successfully.\033[0m"
