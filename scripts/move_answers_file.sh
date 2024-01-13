#!/bin/bash

if [ -n "$1" ]; then
    module_directory_name=$1

    if [ -f ".copier-answers.yml" ]; then
        mv .copier-answers.yml "${module_directory_name}/.config.yaml"
    else
        echo "No answers file found to rename."
    fi

fi

# TODO: find out why when re-running from existing moduel config, this file re-appears
# rm -f .config.yaml