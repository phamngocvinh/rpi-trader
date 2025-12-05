import os
import sys

# Control file name (consistent with main_app.py)
TRIGGER_FILE = "trigger.txt"

def toggle_trigger_file():
    """
    Sets the content of the trigger.txt file to '0', '1', or '2' based on the command line argument.
    0: Entry Mode (No Trade, Search for opportunities)
    1: Management Mode (Active BUY Trade)
    2: Management Mode (Active SELL Trade)
    """
    
    # 1. Read command-line argument
    if len(sys.argv) < 2:
        print("❌ Error: Missing mode parameter. Usage: python toggle_trigger.py [0|1|2]")
        print("   0: Entry Mode (Default)")
        print("   1: Management Mode (BUY Order)")
        print("   2: Management Mode (SELL Order)")
        return
        
    new_state = sys.argv[1]
    if new_state not in ["0", "1", "2"]:
        print("❌ Error: Invalid mode parameter. Must be '0', '1', or '2'.")
        return

    # 2. Determine description
    mode_map = {
        "0": "Entry Mode (Search for opportunities)",
        "1": "Management Mode (Active BUY Order)",
        "2": "Management Mode (Active SELL Order)"
    }
    mode_desc = mode_map.get(new_state, "Unknown Mode")
    
    try:
        # 3. Write new state to file
        with open(TRIGGER_FILE, "w") as f:
            f.write(new_state)

        print("-" * 40)
        print(f"✅ STATUS UPDATED SUCCESSFULLY!")
        print(f"New Status: {new_state} ({mode_desc})")
        print(f"Note: The main application will read the new status in the next 15-minute cycle.")
        print("-" * 40)

    except Exception as e:
        print(f"❌ Error toggling trigger file: {e}")

if __name__ == "__main__":
    toggle_trigger_file()