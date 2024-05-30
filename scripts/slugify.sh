#!/bin/bash

# Function to convert a string to a slug
slugify() {
  local input="$1"
  local slug
  
  # Convert to lowercase
  slug=$(echo "$input" | tr '[:upper:]' '[:lower:]')
  
  # Replace spaces with hyphens
  slug=$(echo "$slug" | tr ' ' '-')
  
  # Remove non-alphanumeric characters except hyphens
  slug=$(echo "$slug" | tr -cd '[:alnum:]-')
  
  echo "$slug"
}

# Call the function with the input argument
slugify "$1"
