import sys

def ex(msg, _ex=True):
    sys.stderr.write(f"Error: {msg}")
    if _ex:
        sys.exit(1)

def get_arg(index, args):
    return None if index >= len(args) else args[index]
