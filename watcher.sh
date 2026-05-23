#!/bin/bash

COMM_DIR="/data/data/com.termux/files/home/.backup_communication"
TRIGGER_FILE="$COMM_DIR/.backup_trigger"
STATUS_FILE="$COMM_DIR/backup_status.txt"

# Make sure the communication folder exists inside Termux home
mkdir -p "$COMM_DIR"

echo "=== Background Watcher Script Active [Option A: Quiet Duplicates] ==="

while true; do
    if [ -f "$TRIGGER_FILE" ]; then
        # 1. Safely pull out the cloud slot name
        SLOT=$(cat "$TRIGGER_FILE")
        
        if [ ! -z "$SLOT" ]; then
            # 2. Format the rclone remote profile syntax with a trailing colon
            REMOTE_TARGET=$(echo "${SLOT}:")
            
            echo "GUI Signal Intercepted! Initiating upload sequence for: $REMOTE_TARGET"
            
            # 3. Initialize the status file with a clean header
            echo -e "[BACKUP] Connecting to cloud profile...\n" > "$STATUS_FILE"
            
            # 4. Fire off rclone copy using --no-traverse
            # We redirect stderr to stdout (2>&1) so grep can scrub out duplicate lines immediately.
            rclone copy /storage/emulated/0/Documents "$REMOTE_TARGET" \
                --no-traverse \
                --progress \
                --stats 1s \
                --stats-one-line \
                2>&1 | grep --line-buffered -v -E "duplicate (file|directory) found" >> "$STATUS_FILE"
            
            # Capture rclone's exit status code via PIPESTATUS to catch rclone's exit, not grep's
            RCLONE_EXIT=${PIPESTATUS[0]}
            
            # 5. Check if the transfer succeeded or if it failed
            if [ $RCLONE_EXIT -eq 0 ]; then
                if grep -q "Transferred:[[:space:]]*[1-9]" "$STATUS_FILE" || grep -q "Checks:[[:space:]]*[1-9]" "$STATUS_FILE"; then
                    echo -e "\n[SUCCESS] Sync complete! New modifications uploaded.\nDONE" >> "$STATUS_FILE"
                else
                    echo -e "\n[SUCCESS] Cloud storage is already 100% identical and up to date!\nDONE" >> "$STATUS_FILE"
                fi
            else
                echo -e "\n[ERROR] Sync failed with exit code $RCLONE_EXIT\nDONE" >> "$STATUS_FILE"
            fi
        fi
        
        # 6. Clean up the trigger file so the loop resets safely
        rm "$TRIGGER_FILE"
    fi
    sleep 1
done

