import os
import time
import anthropic

REFRESH_MODE = True

client = anthropic.Anthropic()
DRY_RUN = False
input_file = r".\game_dump.txt"
output_file = r".\game_index.txt"
MAX_OBJECTS_PER_CHUNK = 25
MAX_CHARS_PER_CHUNK = 80000

SYSTEM = """You are a technical indexer for a GameMaker Studio 2 project written in GML.
Your output must be machine-readable and strictly consistent in format.
Every entry must follow this exact structure with no deviations:

OBJECT: [name]
Summary: [one sentence — role and purpose]
Dependencies: [comma-separated list of objects/scripts this relies on, or 'none']
Dependents: [comma-separated list of objects/scripts that rely on this, or 'none']

SCRIPT: [name]
Summary: [one sentence — role and purpose]
Dependencies: [comma-separated list of objects/scripts this relies on, or 'none']
Dependents: [comma-separated list of objects/scripts that rely on this, or 'none']

Rules:
- One blank line between entries, nothing else
- No markdown, no bullet points, no extra commentary
- Every object and script in the code dump must have an entry
- Base dependencies and dependents on the actual code, not just naming conventions
- Do not stop until every entry in this chunk is complete"""

message_template = """Below is part {chunk_num} of {total_chunks} of a full code dump for a top-down space game written in GML.
Read the entire chunk before writing any entries.
Index every object and script in this chunk. Do not stop until all entries are complete.\n\n"""

# standard functions ----------------------------

def read_dump(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def split_dump(contents, max_objects, max_chars):
    separator = "\n###############"
    entries = [e for e in contents.split(separator) if e.strip()]
    chunks = []
    current_chunk = []
    current_size = 0
    for entry in entries:
        if (len(current_chunk) >= max_objects or
            current_size + len(entry) > max_chars):
            if current_chunk:
                chunks.append(separator.join(current_chunk))
            current_chunk = [entry]
            current_size = len(entry)
        else:
            current_chunk.append(entry)
            current_size += len(entry)
    if current_chunk:
        chunks.append(separator.join(current_chunk))
    return chunks

def count_objects(chunk):
    separator = "\n###############"
    return len([e for e in chunk.split(separator) if e.strip()])

def stream_chunk(chunk, chunk_num, total_chunks, output_path, mode):
    prompt = message_template.format(
        chunk_num=chunk_num,
        total_chunks=total_chunks
    ) + chunk
    print(f"\nChunk {chunk_num}/{total_chunks} — {len(chunk)} characters, approx {len(chunk)//4} tokens...")
    with open(output_path, mode, encoding="utf-8") as f:
        with client.messages.stream(
            model="claude-haiku-4-5",
            system=SYSTEM,
            max_tokens=32000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                f.write(text)
        f.write('\n\n')
    print(f"\nChunk {chunk_num} complete. Output tokens used: {stream.get_final_message().usage.output_tokens}")

# refresh functions ----------------------------------

def get_changed_blocks(dump):
    """Return only blocks with £CHANGED and strip £ from header"""
    changed = []
    for block in dump.split('\n\n###############'):
        if '£CHANGED' in block:
            cleaned = block.replace(' £CHANGED', '')
            changed.append(cleaned)
    return changed

def delete_from_index(index_path, titles):
    """check if any changed titles match index - only keep ones that don't"""
    if not os.path.exists(index_path):
        return
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = content.split('\n\n')
    kept = []
    for entry in entries:
        first_line = entry.split('\n')[0]
        if first_line.strip() not in titles:           
            kept.append(entry)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(kept))  

def run_refresh(dump, index_path):
    changed_blocks = get_changed_blocks(dump)
    if not changed_blocks:
        print("No changes detected — index is up to date.")
        return
    
    titles = []
    for block in changed_blocks:
        for line in block.strip().split('\n'):
            if line.startswith('OBJECT:') or line.startswith('SCRIPT:'):
                titles.append(line.strip())  
                break
    
    print(f"{len(changed_blocks)} changed blocks found: {titles}")
    delete_from_index(index_path, titles)
    
    # reuse existing chunking and streaming — just on changed blocks only
    changed_dump = '\n\n###############'.join(changed_blocks)
    chunks = split_dump(changed_dump, MAX_OBJECTS_PER_CHUNK, MAX_CHARS_PER_CHUNK)
    for i, chunk in enumerate(chunks):
        stream_chunk(chunk, i + 1, len(chunks), index_path, "a")
        if i < len(chunks) - 1:
            print("\nWaiting 61 seconds...")
            time.sleep(61)

game_dump = read_dump(input_file)


run_refresh(game_dump, output_file)

print(f"\nIndex compiled in {output_file}")