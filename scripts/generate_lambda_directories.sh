#!/bin/bash

# Check if lambda_names is provided
if [ -n "$1" ]; then
    lambda_names=$1
    lambda_list=(${lambda_names//,/ })

    for lambda_name in "${lambda_list[@]}"; do
        cp -rf ${module_directory_name}/lambda/functions/blueprint ${module_directory_name}/lambda/functions/${lambda_name// /}
    done
else
    echo "No lambda names provided."
fi