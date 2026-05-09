# gml-code-dump (version 2)
My first python script / workflow. This is very rudimentary, manual RAG system designed for use with GameMaker. The purpose is to streamline AI collaboration and reduce token usage & context bloat (whilst keeping the user fully in-the-loop) by creating a summarised index of all of the objects/scripts in your project to share with your LLM of choice. The LLM can then decide which events it needs to see in full and request this from the user.

## Contents
**A) dump_create.py** - reads all of the code from every object/script in the game folder, cleans it up into a readable format, and dumps into a single game_dump.txt file. If a game_dump.txt file already exists in the folder, it will also tag every object/script that has changed since the script was last run.

**B) index_create.py** - reads the game_dump.txt file and makes an API call (currently Anthropic - Haiku. But feel free to change to your preferred model) to generate a concise summary of every object/script (including a list of any dependencies). This will ignore any objects/scripts that have not been flagged as "changed". To get around context and token per minute limits, the game_dump.txt is broken into max 80,000 character chunks (roughly 20,000 tokens), and a 61 second pause is forced between each chunk. Therefore, when running for the first time you may want to leave it running in the background as it can take a while! Any subsequent refreshes will be much quicker, as Haiku will only summarise and append the objects/scripts that have changed since it was last run.

**C) extract.py** - input the name of a specific object/script and event and it will copy the full, tidied-up code to clipboard, allowing you to quickly paste into the LLM chat. See usage instructions below for the correct syntax.

## Dependencies
- Python 3.7 or higher
- GameMaker (obviously)
- Required Python packages — run this once before first use:
```
pip install anthropic pyperclip
```

## Set-up and configuration
**Step 1:** download and save all .py and (optional but recommended) .bat files into the root folder of your game project e.g. `C:\Users\John\GameMakerProjects\my-platformer-v1`

**Step 2:** set up your Anthropic API key in your machine's environment variables. On Windows, search "environment variables" in your taskbar -> click "new" -> name it `ANTHROPIC_API_KEY` -> enter the full API key as the value. If you don't have an API key, you can get one from https://platform.claude.com/

**Step 3:** run dump_create.py in Command Prompt or PowerShell (or more quickly by double clicking on the refresh_dump.bat file if you downloaded it). Note: the console window will stay open after running so you can read the output — this is intentional.

**Step 4:** run index_create.py (or use the refresh_index.bat file). If it's the first time, this can take over 10 minutes.

## Using the workflow
Once you have run both scripts for the first time you will find two new files in the game project folder: game_index.txt and game_dump.txt.

game_index.txt is designed to be shared directly with your chosen LLM at the beginning of the conversation. This will give the LLM a foundational understanding of what every object does and how they interact with each other. Inform the LLM that if it needs to see the full code for any object in order to respond to a query, it should respond with the object and event name in this format: `obj_name:Event_0` — or just the script name for scripts: `scr_my_script`.

You can then run extract.py using the following syntax:

```
python extract.py obj_name:Event_0
python extract.py scr_my_script
python extract.py obj_player:Create_0 obj_player:Step_0 scr_my_script
```

Separate multiple requests with spaces. The script will find the relevant code from game_dump.txt and copy it to clipboard ready to be pasted back into the conversation.

Alternatively, double-click extract.bat and enter your request(s) when prompted — the batch file handles the syntax for you.

