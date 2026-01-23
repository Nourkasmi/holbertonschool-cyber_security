#!/usr/bin/env python3
"""
read_write_heap.py
Finds a string in the heap of a running process and replaces it.

Usage: read_write_heap.py pid search_string replace_string
"""

import sys

def print_usage_and_exit():
    """Prints usage error and exits."""
    print("Usage: read_write_heap.py pid search_string replace_string")
    sys.exit(1)

def main():
    """Main function to search and replace a string in the heap of a process."""
    if len(sys.argv) != 4:
        print_usage_and_exit()

    pid = sys.argv[1]
    search = sys.argv[2].encode()
    replace = sys.argv[3].encode()

    if len(search) != len(replace):
        print("Error: search and replace strings must have the same length.")
        sys.exit(1)

    maps_path = f"/proc/{pid}/maps"
    mem_path = f"/proc/{pid}/mem"

    try:
        with open(maps_path, "r") as maps_file:
            for line in maps_file:
                if "[heap]" in line:
                    start, end = [int(x, 16) for x in line.split(" ")[0].split("-")]
                    break
            else:
                print("Heap not found.")
                sys.exit(1)

        with open(mem_path, "rb+") as mem_file:
            mem_file.seek(start)
            heap_data = mem_file.read(end - start)

            offset = heap_data.find(search)
            if offset == -1:
                print("String not found in heap.")
                sys.exit(0)

            abs_addr = start + offset
            print(f"[*] Found '{search.decode()}' at {hex(abs_addr)}")

            mem_file.seek(abs_addr)
            mem_file.write(replace)
            print(f"[*] Replaced with '{replace.decode()}' successfully.")

    except FileNotFoundError:
        print(f"Error: process {pid} not found.")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Try running as root.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
