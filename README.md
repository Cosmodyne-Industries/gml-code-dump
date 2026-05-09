# gml-code-dump
My first python scripts / workflow. This is very rudimentary, manual RAG system designed for use with GameMaker. The purpose is to streamline AI collaboration and reduce token usage / context bloat, whilst keeping the user fully in-the-loop, by creating a summarised index of all of the objects/scripts in your project to share with your LLM of choice. The LLM can then decide which events it needs to see in full and request this from the user. 

## Contents

A) dump_create.py - reads all of the code from every object/script in the game folder, clean it up into a readable format, and dump into a single game_dump.txt file. If a game_dump.txt file already exists in the folder, it will also tag every object/script that has changed since the script was last run. 

B) index_create.py - reads the game_dump.txt file and makes an API call (currently Anthropic - Haiku. But feel free to change to your preferred model) to generate a concise summary of every object/script (including a list of any dependencies). This will ignore any obejcts/scripts that have not been flagged as "changed". To get around context and token per minute limits, the game_dump.txt is broken into max 80k token chuncks, and 61 second pause is forced between each chunk. Therefore, when running for the first time you may want to leave it running in the background as it can take a while! Any subsequent refreshes will be much quicker, as Haiku will only summarise and append the objects/scripts that have changed since it was last run. 

C) extract.py - input the name of a specific object / script and it will copy the full, tidied-up code to clipboard, allowing you to quickly paste into the LLM chat. 

## Set-up and configuration:

Step 1: download and save all .py and (optional but reccomend) .bat files into the root folder of your game project e.g. C:\Users\John\GameMakerProjects\my-platformer-v1

Step 2: set up your Anthropic API key in your machine's environment variables. On windows, search "environment variables" in your taskbar -> click "new" -> name it "ANTHROPIC_API_KEY" -> enter the full API key as the value. If you don't have an API kley, you can get one from https://platform.claude.com/

Step 3: run the dump_create.py in Command Prompt or Powershell (or more quickly by double clicking on the refresh_dump.bat file if you downloaded it). 

Step 4: run the index_create.py (or use the refresh_index.bat file). If its the first time, this can take over 10 minutes. 

## Using the workflow

Once you have run both scripts for the first time you wil find two new files in the game project folder: game_index.txt and game_dump.txt.

game_index.txt is designed to be shared directly with your chosen LLM at the beginning of the conversation. This will give the LLM the full context of your game, and a decent understanding of what objects do and how they interact with eachother. Instruct the LLM that if it needs to see the full code for any object in order to respond to a query, it should respond with the full name of the object (e.g. obj_player_character), or list of objects. 

You can then run the extract.py script (or double click the extract.bat file), and copy the full object name into the CLI. The script will then find the relevant code from the game_dump.txt file and copy it to clipboard ready to be pasted back into the conversation. 

## Dependencies: Python, GameMaker (obviously)
