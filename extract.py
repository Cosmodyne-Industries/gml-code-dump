import argparse
import pyperclip

source_file = r".\game_dump.txt"

def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def find_block(text, name):
    blocks = text.split('\n\n###############')
    for block in blocks:
        if f"OBJECT: {name}" in block or f"SCRIPT: {name}" in block:
            return block
    return None

def is_script(block):
    return "SCRIPT:" in block

def find_event(block, event_name):
    sub_blocks = block.split('\n\n---------------')
    for sub in sub_blocks:
        if f"EVENT: {event_name}" in sub:
            return sub
    return None

def main():
    parser = argparse.ArgumentParser(description='Search code dump and copy to clipboard')
    parser.add_argument('requests', nargs='+', help='One or more name:event pairs, e.g. obj_player:Create_0 scr_my_script')
    parser.add_argument('--file', default=source_file, help='Path to game_dump.txt')
    args = parser.parse_args()

    text = load_file(args.file)
    results = []

    for req in args.requests:
        # Split on colon to separate name and optional event
        parts = req.split(':')
        name = parts[0]
        event = parts[1] if len(parts) > 1 else None

        block = find_block(text, name)

        if not block:
            print(f"Not found: '{name}'")
            continue

        if is_script(block):
            results.append(block)
            print(f"Found script: '{name}'")
        else:
            if event is None:
                print(f"'{name}' is an object — provide an event. Usage: obj_name:Event_0")
                continue
            result = find_event(block, event)
            if result:
                results.append(result)
                print(f"Found: '{name}:{event}'")
            else:
                print(f"Event '{event}' not found in '{name}'")

    if results:
        combined = '\n\n'.join(results)
        pyperclip.copy(combined)
        print(f"\nCopied {len(results)} block(s) to clipboard ({len(combined)} chars)")

if __name__ == '__main__':
    main()