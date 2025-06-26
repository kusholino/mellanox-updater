import argparse
import sys
import csv

def apply_replacements_from_file(input_file, output_file, replacements_text_file):
    """
    Reads an input file, performs multiple find-and-replace operations
    based on a text file, and writes the result to a new output file.

    The replacements file should have one find,replace pair per line,
    separated by a comma. Example: string_to_find,string_to_replace

    Args:
        input_file (str): The path to the source file.
        output_file (str): The path for the new file that will be created.
        replacements_text_file (str): Path to the text file with replacement pairs.
    """
    try:
        # Open the input file for reading
        with open(input_file, 'r', encoding='utf-8') as file:
            file_contents = file.read()

        # Open and read the replacements file
        with open(replacements_text_file, 'r', encoding='utf-8') as config_file:
            # Use the csv module to correctly handle the comma separator
            reader = csv.reader(config_file)
            new_contents = file_contents
            for row in reader:
                # Skip empty lines or lines that don't have exactly 2 values
                if len(row) == 2:
                    find_str, replace_str = row
                    new_contents = new_contents.replace(find_str, replace_str)

        # Open the output file for writing
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(new_contents)

        print(f"Successfully updated file and saved to '{output_file}'")

    except FileNotFoundError as e:
        print(f"Error: The file '{e.filename}' was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find and replace text in a file using a replacements text file and save to a new file."
    )
    parser.add_argument(
        '--input-file',
        required=True,
        help="Path to the input file."
    )
    parser.add_argument(
        '--output-file',
        required=True,
        help="Path to the new output file."
    )
    parser.add_argument(
        '--replacements-file',
        required=True,
        help="Path to the text file containing find,replace pairs on each line."
    )

    args = parser.parse_args()

    apply_replacements_from_file(args.input_file, args.output_file, args.replacements_file)