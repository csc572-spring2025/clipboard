# ClipBoard
*The one-stop shop for everything copy-paste.*
Developed by CSC572: The Open Source Movement, Spring 2024-2025

## Brief Description
ClipBoard records everything copied to the system clipboard and aims to intelligently organize it into categories like code snippets, quotes, math equations, URLs, or plain text. Users can search past entries via tags, date, or keywords, making it easy to find what they copied days or weeks ago.

UI Display:
![Example](userinterface.png)

### Instructions to download for users
Dependencies:
- pyperclip
- PyQt5

Install dependencies with:

###  ```pip install -r requirements.txt```

Open application using

### ```python backgroundapp.py```

### Potential Contribution
- Add a "delete" button to remove a specific entry
- Generate tags for each entry based on the content
- Special shortcut for non-tracking copy-paste (cmd+shift+c)

### Known issues

- Copy button doesn't switch to Copied when completed
- Blocks of copy-paste history are super large and clog up the window too much (should be condensed)
- Categorization logic doesn't work well

### Licenses        

MIT License
