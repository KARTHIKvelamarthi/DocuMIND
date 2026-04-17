import os

# Extensions to include
INCLUDE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".json", ".md"
}

# Folders to skip (important to avoid junk)
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"
}

OUTPUT_FILE = "full_project.txt"


def should_include_file(file_name):
    _, ext = os.path.splitext(file_name)
    return ext.lower() in INCLUDE_EXTENSIONS


def is_excluded_dir(dirname):
    return dirname in EXCLUDE_DIRS


def dump_project(root_dir):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Remove excluded dirs in-place (important)
            dirnames[:] = [d for d in dirnames if not is_excluded_dir(d)]

            for file in filenames:
                if should_include_file(file):
                    full_path = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(full_path, root_dir)

                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f"FILE: {rel_path}\n")
                    outfile.write(f"{'='*80}\n\n")

                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            outfile.write(content)
                            outfile.write("\n\n")
                    except Exception as e:
                        outfile.write(f"[ERROR READING FILE: {e}]\n\n")


if __name__ == "__main__":
    root_directory = os.getcwd()
    dump_project(root_directory)
    print(f"✅ Done! Output written to {OUTPUT_FILE}")