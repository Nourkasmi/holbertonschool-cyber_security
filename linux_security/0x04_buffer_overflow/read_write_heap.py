#!/usr/bin/python3
"""read_write_heap.py - find and replace a string in the heap of a running process."""

import sys
import os


def print_usage_and_exit():
    """Print usage message and exit with code 1."""
    print("Usage: read_write_heap.py pid search_string replace_string")
    sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) != 4:
        print_usage_and_exit()

    pid = sys.argv[1]
    search = sys.argv[2].encode()
    replace = sys.argv[3].encode()

    if len(search) != len(replace):
        print("Error: search and replace strings must have the same length.")
        sys.exit(1)

    maps_path = "/proc/{}/maps".format(pid)
    mem_path = "/proc/{}/mem".format(pid)

    try:
        with open(maps_path, "r") as maps_file:
            for line in maps_file:
                if "[heap]" in line:
                    addr = line.split()[0]
                    start, end = [int(x, 16) for x in addr.split("-")]
                    break
            else:
                print("Heap not found.")
                sys.exit(1)

        with open(mem_path, "r+b") as mem_file:
            mem_file.seek(start)
            heap = mem_file.read(end - start)
            pos = heap.find(search)
            if pos == -1:
                print("String not found in heap.")
                sys.exit(0)
            mem_file.seek(start + pos)
            mem_file.write(replace)
            print("SUCCESS!")  # the only required stdout line

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
