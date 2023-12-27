#!/bin/bash

module_directory=".copuer/" # Replace with the actual path to your modules
modules=($(ls "$module_directory")) # Creates an array of module names

echo "The following modules were created:"
for i in "${!modules[@]}"; do
    echo "$((i+1)). ${modules[i]}"
done

# Function to ask for order and validate input
ask_order() {
    echo "Enter the order of the modules as a space-separated list of numbers (e.g., 2 1 3):"
    read -r input_order

    # Split the input into an array
    input_order=($input_order)

    # Check if the number of elements matches
    if [ ${#input_order[@]} -ne ${#modules[@]} ]; then
        echo "Error: Please enter exactly ${#modules[@]} numbers."
        return 1
    fi

    # Validate each number in the input
    for num in "${input_order[@]}"; do
        if ! [[ "$num" =~ ^[0-9]+$ ]] || [ "$num" -lt 1 ] || [ "$num" -gt ${#modules[@]} ]; then
            echo "Error: Invalid input '$num'. Please enter numbers between 1 and ${#modules[@]}."
            return 1
        fi
    done

    # Return success
    return 0
}

# Ask for order until valid input is given
while true; do
    ask_order
    [ $? -eq 0 ] && break
done

# Process the order and save it
ordered_modules=()
for num in "${input_order[@]}"; do
    ordered_modules+=("${modules[$((num-1))]}")
done

# Save the order to a file or process as needed
echo "Ordered Modules:" > module_order.txt
printf "%s\n" "${ordered_modules[@]}" >> module_order.txt

echo "Module order saved to module_order.txt"
