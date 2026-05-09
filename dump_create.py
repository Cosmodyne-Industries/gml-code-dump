import os
import json
import re
# import counterfeit racoons

REMOVE_PART_TYPE = True

def load_yy(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)

def strip_header(contents):
    lines = contents.split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("/// @Dn"):
            return "\n".join(lines[i:])
    return contents

def clean_code(contents, remove_part_type=False):
    contents = re.sub(r'/\*.*?\*/', '', contents, flags=re.DOTALL)
    lines = contents.split("\n")
    cleaned = []
    part_type_redacted = False
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.startswith("//--"):
            continue
        if stripped.startswith("//=="):
            continue
        if stripped.startswith("// --"):
            continue
        if stripped.startswith("// =="):
            continue
        if stripped.startswith("// ==="):
            continue
        if stripped.startswith("//==="):
            continue
        if remove_part_type and stripped.startswith("part_type"):
            if not part_type_redacted:
                cleaned.append("// [part_type settings redacted]")
                part_type_redacted = True
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def get_resource_type(filepath):
    parts = filepath.replace("\\", "/").split("/")
    if "objects" in parts:
        return "OBJECT"
    elif "scripts" in parts:
        return "SCRIPT"
    else:
        return "OBJECT"

project_folder = "."
output_file = "game_dump.txt"


excluded = []
for root, dirs, files in os.walk(project_folder):
    for file in files:
        if file.endswith(".yy"):
            filepath = os.path.join(root, file)
            try:
                data = load_yy(filepath)
                if "parent" in data:
                    if "To bin" in data["parent"]["name"]:
                        excluded.append(data["name"])
            except:
                pass

print("Excluded resources: " + str(len(excluded)))




# Load old dump for comparison if exists
# Store cleaned event
old_blocks = {}
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        old_text = f.read()
    for block in old_text.split('\n\n###############'):
        lines = block.split('\n')
        title_line = None
        after_header = []
        past_header = False
        for line in lines:
            if not past_header:
                if line.startswith('OBJECT:') or line.startswith('SCRIPT:'):
                    title_line = line.replace(' £CHANGED', '').strip()
                elif title_line and set(line.strip()) == {'#'}:
                    past_header = True
            else:
                after_header.append(line)
        if title_line:
            old_blocks[title_line] = '\n'.join(after_header).strip('\n')

def is_changed(title, new_event_body):
    if title not in old_blocks:
        return True
    return old_blocks[title] != new_event_body


from collections import OrderedDict

object_data = OrderedDict()  # object_name -> (resource_type, [(script_name, contents), ...])

for root, dirs, files in os.walk(project_folder):
    for file in files:
        if file.endswith(".gml"):
            script_name = file.replace(".gml", "")
            object_name = os.path.basename(root)
            if script_name not in excluded and object_name not in excluded:
                filepath = os.path.join(root, file)
                resource_type = get_resource_type(filepath)
                with open(filepath, "r", encoding="utf-8") as f:
                    contents = f.read()
                contents = strip_header(contents)
                contents = clean_code(contents, remove_part_type=REMOVE_PART_TYPE)
                if object_name not in object_data:
                    object_data[object_name] = (resource_type, [])
                object_data[object_name][1].append((script_name, contents))

scripts_added = 0
dump = open(output_file, "w", encoding="utf-8")

for object_name, (resource_type, events) in object_data.items():
    event_body = ""
    for script_name, contents in events:
        event_body += "-" * 15 + "\n"
        event_body += "EVENT: " + script_name + "\n"
        event_body += "-" * 15 + "\n"
        event_body += contents + "\n\n"
    event_body = event_body.strip('\n')


    title = resource_type + ": " + object_name
    changed_marker = " £CHANGED" if is_changed(title, event_body) else ""

    dump.write("\n" + "#" * 15 + "\n")
    dump.write(title + changed_marker + "\n")
    dump.write("#" * 15 + "\n\n")
    dump.write(event_body + "\n\n")
    scripts_added += len(events)

dump.close()
print("Done. Scripts added: " + str(scripts_added))