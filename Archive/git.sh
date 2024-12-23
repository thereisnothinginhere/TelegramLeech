#!/bin/bash

# Set Git user name and email
git config user.name "GitHub Actions"
git config user.email "actions@github.com"

# Add changes to the staging area
git add magnet_links.txt

# Commit the changes with a message
git commit -m "Updated"
