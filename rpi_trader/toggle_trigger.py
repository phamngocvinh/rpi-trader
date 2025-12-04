import os

# Control file name (consistent with main_app.py)
TRIGGER_FILE = "trigger.txt"

def toggle_trigger_file():
    """
    Toggles the content of the trigger.txt file between '0' and '1'.
    '0': Entry mode (Search for opportunities)
    '1': Management mode (Close/Trailing Stop)
    """
    new_state = "1" # Default to '1' if current state cannot be read
    current_state = ""
    
    try:
        # 1. Read current state
        if os.path.exists(TRIGGER_FILE):
            with open(TRIGGER_FILE, "r") as f:
                current_state = f.read().strip()
        else:
            # If the file does not exist, assume default state '0'
            print(f"File {TRIGGER_FILE} not found. Creating with default state '0'.")
            current_state = "0"

        # 2. Determine new state
        if current_state == "1":
            # If currently '1' (Management), switch to '0' (Entry)
            new_state = "0"
            mode_desc = "Opportunity Search (Mode 0)"
        else:
            # If currently '0' (Entry) or empty/error, switch to '1' (Management)
            new_state = "1"
            mode_desc = "Order Management (Mode 1)"

        # 3. Write new state to file
        with open(TRIGGER_FILE, "w") as f:
            f.write(new_state)

        print("-" * 40)
        print(f"✅ STATUS UPDATED SUCCESSFULLY!")
        print(f"New Status: {new_state} ({mode_desc})")
        print(f"Note: Main App will read the new status in the next 15-minute cycle.")
        print("-" * 40)

    except Exception as e:
        print(f"❌ Error toggling trigger file: {e}")

if __name__ == "__main__":
    toggle_trigger_file()