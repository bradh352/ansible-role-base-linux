#!/bin/bash
# Print the user's current password hash from /etc/shadow, so the role can
# keep it when the password hasn't changed (see filter_plugins/password.py).
getent shadow "$1" | cut -d: -f2
