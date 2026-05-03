import os


def fix_docstrings():
    # Get all project Python files (excluding venv)
    py_files = []
    for root, dirs, files in os.walk("."):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    print(f"Found {len(py_files)} Python files to check")

    # The corrupted pattern is: """ (7 chars)
    # We need to replace it with: """ (3 chars)
    corrupted = b'"""'
    correct = b'"""'

    fixed_count = 0

    for f in py_files:
        with open(f, "rb") as fh:
            content = fh.read()

        if corrupted in content:
            new_content = content.replace(corrupted, correct)

            with open(f, "wb") as fh:
                fh.write(new_content)

            fixed_count += 1
            print(f"Fixed: {f}")

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    fix_docstrings()
