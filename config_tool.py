import argparse
import sys

def compare_files(file1_path, file2_path):
    """
    Compares two files line by line and prints the differences.
    """
    try:
        with open(file1_path, 'r') as f1:
            lines1 = set(line.strip() for line in f1)
        with open(file2_path, 'r') as f2:
            lines2 = set(line.strip() for line in f2)

        removed_lines = lines1 - lines2
        added_lines = lines2 - lines1

        if not removed_lines and not added_lines:
            print("Files are identical.")
            return

        for line in sorted(list(removed_lines)):
            print(f"[-] {line}")

        for line in sorted(list(added_lines)):
            print(f"[+] {line}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def search_file_contains(file_path, search_string):
    """
    Searches a file for lines that contain the search string.
    """
    found = False
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if search_string in line.strip():
                    print(f"[+] {line.strip()}")
                    found = True
        if not found:
            print(f"No line containing '{search_string}' found.")
            
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        sys.exit(1)

def main():
    """Handles command-line arguments and calls the appropriate function."""
    parser = argparse.ArgumentParser(
        description="A tool for comparing and searching switch configuration files."
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Sub-parser for the "compare" command
    parser_compare = subparsers.add_parser('compare', help='Compare two configuration files.')
    parser_compare.add_argument("file1", help="The original configuration file.")
    parser_compare.add_argument("file2", help="The new configuration file.")
    parser_compare.set_defaults(func=lambda args: compare_files(args.file1, args.file2))

    # Sub-parser for the "search" command
    parser_search = subparsers.add_parser('search', help='Search a file for lines containing a string.')
    parser_search.add_argument("file", help="The configuration file to search.")
    parser_search.add_argument("search_string", help="The string to search for.")
    parser_search.set_defaults(func=lambda args: search_file_contains(args.file, args.search_string))

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()