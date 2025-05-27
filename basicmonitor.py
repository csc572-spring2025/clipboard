'''A simple clipboard monitor that logs changes to the clipboard content with timestamps'''


import pyperclip
import time
import datetime
import os

# monitor clipboard for changes and log them with timestamps
def monitor_clipboard():
    print("Clipboard monitoring started. Press Ctrl+C to stop.")
    print("-" * 50)
    
    # create a logs directory if it doesn't exist
    if not os.path.exists("clipboard_logs"):
        os.makedirs("clipboard_logs")
    
    # initialize with current clipboard content
    previous_content = pyperclip.paste()
    log_file_path = os.path.join("clipboard_logs", f"clipboard_log_{datetime.datetime.now().strftime('%Y%m%d')}.txt")
    
    # track unique entries to avoid duplicates
    seen_entries = {previous_content}
    
    try:
        while True:
            # get current clipboard content
            current_content = pyperclip.paste()
            
            # check if content has changed and is not a duplicate
            if current_content != previous_content and current_content not in seen_entries:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # log to console
                print(f"\n[{timestamp}] New clipboard content:")
                print("-" * 50)
                print(current_content)
                print("-" * 50)
                
                # log to file
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n[{timestamp}]\n")
                    f.write("-" * 50 + "\n")
                    f.write(current_content + "\n")
                    f.write("-" * 50 + "\n")
                
                # update previous content and add to seen entries
                previous_content = current_content
                seen_entries.add(current_content)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nClipboard monitoring stopped.")


monitor_clipboard()