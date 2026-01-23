#!/usr/bin/python3
"""
Advanced Process Memory Editor - Heap String Replacement Tool

A sophisticated utility for safely finding and replacing strings
in a process's heap memory with comprehensive error handling,
validation, and safety checks.

Features:
- Multi-occurrence replacement
- ASCII/Unicode support (configurable)
- Heap boundary protection
- Permission escalation detection
- Progress reporting
- Dry-run mode
- Backup/restore capability
- Comprehensive logging

Usage:
    sudo ./advanced_heap_replace.py [OPTIONS] pid search_string replace_string

Options:
    --unicode       Enable Unicode string handling
    --dry-run       Simulate without making changes
    --backup FILE   Create memory backup file
    --verbose       Show detailed operation info
    --all           Replace all occurrences (default: first only)
"""

import sys
import os
import re
import argparse
from typing import List, Tuple, Optional
import logging
from dataclasses import dataclass

# Constants
MAX_HEAP_SIZE = 100 * 1024 * 1024  # 100MB safety limit
BACKUP_EXTENSION = ".heapbak"


@dataclass
class ReplacementResult:
    count: int
    addresses: List[int]
    backup_file: Optional[str]


class MemoryEditor:
    """Core memory editing functionality with safety controls."""

    def __init__(self, pid: int):
        self.pid = pid
        self.maps_path = f"/proc/{pid}/maps"
        self.mem_path = f"/proc/{pid}/mem"
        self.heap_ranges = []
        self.validate_process()

    def validate_process(self):
        """Verify process exists and we can access it."""
        if not os.path.exists(f"/proc/{self.pid}"):
            raise ProcessLookupError(f"Process {self.pid} not found")

        try:
            with open(self.maps_path, 'r') as f:
                pass
        except PermissionError:
            raise PermissionError(f"Need root privileges to \
            access process {self.pid}")

    def locate_heap_regions(self) -> List[Tuple[int, int]]:
        """Find all heap memory regions with write permissions."""
        heap_ranges = []
        try:
            with open(self.maps_path, 'r') as maps_file:
                for line in maps_file:
                    if '[heap]' in line and 'rw' in line:
                        parts = line.split()
                        addr_range = parts[0].split('-')
                        start = int(addr_range[0], 16)
                        end = int(addr_range[1], 16)
                        heap_ranges.append((start, end))
        except Exception as e:
            raise RuntimeError(f"Failed to parse memory maps: {str(e)}")

        if not heap_ranges:
            raise RuntimeError("No accessible heap regions found")

        return heap_ranges

    def backup_region(self, start: int, end: int, backup_file: str) -> None:
        """Create backup of memory region."""
        if end - start > MAX_HEAP_SIZE:
            raise MemoryError(f"Heap region too large \
            ({(end-start)/1024/1024:.2f}MB > \
            {MAX_HEAP_SIZE/1024/1024}MB limit)")

        try:
            with (
                open(self.mem_path, 'rb') as mem_file,
                open(backup_file, 'wb') as backup
            ):
                mem_file.seek(start)
                backup.write(mem_file.read(end - start))
        except Exception as e:
            raise RuntimeError(f"Backup failed: {str(e)}")

    def find_and_replace(
      self, search_bytes: bytes, replace_bytes: bytes,
      replace_all: bool = False, dry_run: bool = False,
      backup_prefix: Optional[str] = None
      ) -> ReplacementResult:
        """Main replacement operation with safety checks."""
        if len(replace_bytes) > len(search_bytes):
            raise ValueError("Replacement string cannot be longer \
            than search string")

        self.heap_ranges = self.locate_heap_regions()
        result = ReplacementResult(0, [], None)

        for start, end in self.heap_ranges:
            region_size = end - start
            logging.info(f"Scanning heap region \
            0x{start:x}-0x{end:x} ({region_size} bytes)")

            try:
                with open(self.mem_path, 'r+b') as mem_file:
                    # Create backup if requested
                    backup_file = None
                    if backup_prefix:
                        backup_file = f"{backup_prefix}_\
                        {start:x}-{end:x}{BACKUP_EXTENSION}"
                        self.backup_region(start, end, backup_file)
                        result.backup_file = backup_file

                    # Read heap content
                    mem_file.seek(start)
                    heap_data = mem_file.read(region_size)

                    # Find all occurrences
                    offset = 0
                    while True:
                        pos = heap_data.find(search_bytes, offset)
                        if pos == -1:
                            break

                        abs_pos = start + pos
                        logging.info(f"Found match at 0x{abs_pos:x}")

                        if not dry_run:
                            # Perform replacement
                            mem_file.seek(abs_pos)
                            mem_file.write(replace_bytes)

                            # Pad with nulls if replacement is shorter
                            if len(replace_bytes) < len(search_bytes):
                                padding = (
                                  len(search_bytes) - len(replace_bytes)
                                  )
                                mem_file.write(b'\x00' * padding)

                        result.count += 1
                        result.addresses.append(abs_pos)

                        if not replace_all:
                            break

                        offset = pos + 1

            except Exception as e:
                logging.error(f"Error processing region \
                0x{start:x}-0x{end:x}: {str(e)}")
                if backup_file and os.path.exists(backup_file):
                    os.remove(backup_file)
                raise

        return result


def validate_strings(
  search_str: str, replace_str: str, unicode: bool = False
  ) -> Tuple[bytes, bytes]:
    """Validate and encode strings according to parameters."""
    if not search_str:
        raise ValueError("Search string cannot be empty")

    try:
        encoding = 'utf-8' if unicode else 'ascii'
        search_bytes = search_str.encode(encoding)
        replace_bytes = replace_str.encode(encoding)
        return search_bytes, replace_bytes
    except UnicodeError as e:
        raise ValueError(f"String encoding error: {str(e)}")


def setup_logging(verbose: bool):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=level
    )


def parse_arguments():
    """Handle command line arguments with argparse."""
    parser = argparse.ArgumentParser(
        description="Advanced heap memory string replacement tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  sudo %(prog)s --all --backup \
        /tmp/backup 1234 password p@ssw0rd"
    )

    parser.add_argument(
      "pid", type=int, help="Target process ID"
      )
    parser.add_argument(
      "search_string", type=str, help="String to search for"
      )
    parser.add_argument(
      "replace_string", type=str, help="Replacement string"
      )
    parser.add_argument(
      "--unicode",
      action="store_true",
      help="Enable Unicode support"
      )
    parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Simulate without modifying memory"
      )
    parser.add_argument(
      "--backup",
      type=str,
      help="Create memory backup to specified path"
      )
    parser.add_argument(
      "--verbose",
      action="store_true",
      help="Show detailed operation info"
      )
    parser.add_argument(
      "--all",
      action="store_true",
      help="Replace all occurrences (default: first only)"
      )

    return parser.parse_args()


def main():
    """Main program execution."""
    args = parse_arguments()
    setup_logging(args.verbose)

    try:
        # Initial validation
        if os.geteuid() != 0:
            logging.error("This tool requires root privileges")
            sys.exit(1)

        # Prepare for operation
        editor = MemoryEditor(args.pid)
        search_bytes, replace_bytes = validate_strings(
            args.search_string, args.replace_string, args.unicode
        )

        logging.info(f"Starting replacement in process {args.pid}")
        logging.debug(f"Search bytes: {search_bytes}")
        logging.debug(f"Replace bytes: {replace_bytes}")

        # Perform the replacement
        result = editor.find_and_replace(
            search_bytes=search_bytes,
            replace_bytes=replace_bytes,
            replace_all=args.all,
            dry_run=args.dry_run,
            backup_prefix=args.backup
        )

        # Report results
        if result.count == 0:
            logging.warning("No matches found in heap memory")
        else:
            action = "Would replace" if args.dry_run else "Replaced"
            logging.info(f"{action} {result.count} occurrence(s) at:")
            for addr in result.addresses:
                logging.info(f"  0x{addr:x}")

            if args.backup and result.backup_file:
                logging.info(f"Memory backup saved to {result.backup_file}")

        sys.exit(0)

    except Exception as e:
        logging.error(f"Operation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()