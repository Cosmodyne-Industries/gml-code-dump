import os
import json
import re

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

def get_resource_type(filepath):
    parts = filepath.replace("\\", "/").split("/")
    if "objects" in parts:
        return "OBJECT"
    elif "scripts" in parts:
        return "SCRIPT"
    else:
        return "OBJECT"  

project_folder = "."
output_file = r".\game_digest.txt"

# Get all .yy files and build an exclusion list -----------------------------

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

# Get all .gml files --------------------------------------
digest = open(output_file, "w", encoding="utf-8")
scripts_added = 0
current_object = ""

for root, dirs, files in os.walk(project_folder):
    for file in files:
        if file.endswith(".gml"):
            script_name = file.replace(".gml", "")
            object_name = os.path.basename(root)
            if script_name not in excluded and object_name not in excluded:
                filepath = os.path.join(root, file)
                resource_type = get_resource_type(filepath)
                f = open(filepath, "r", encoding="utf-8")
                contents = f.read()
                f.close()
                contents = strip_header(contents)
                if object_name != current_object:
                    current_object = object_name
                    digest.write("\n" + "#" * 50 + "\n")
                    digest.write(resource_type + ": " + object_name + "\n")
                    digest.write("#" * 50 + "\n\n")
                digest.write("-" * 30 + "\n")
                digest.write("EVENT: " + script_name + "\n")
                digest.write("-" * 30 + "\n")
                digest.write(contents + "\n\n")
                scripts_added = scripts_added + 1

digest.close()
print("Done. Scripts added: " + str(scripts_added))