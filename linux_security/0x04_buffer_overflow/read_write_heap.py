#!/usr/bin/python3
"""
advanced_heap_replace.py
--------------------------------------------------------
Advanced Process Memory Editor – Heap String Replacement Tool

Safely finds and replaces strings in a process's heap memory
with optional dry-run, backups, multi-occurrence replacement,
and detailed logging.

Usage:
    sudo ./advanced_heap_replace.py [OPTIONS] pid search_string replace_string

Options:
    --unicode       Enable Unicode string handling
    --dry-run       Simulate without making changes
    --backup FILE   Create memory backup file prefix
    --verbose       Show detailed operation info
    --all           Replace all occurrences (default: first only)
--------------------------------------------------------
"""

import os
import sys
import argparse
import logging
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
MAX_HEAP_SIZE = 100 * 1024 * 1024  # 100 MB safety limit
BACKUP_EXTENSION = ".heapbak"


# ---------------------------------------------------------------------
# Data structure to hold results
# ---------------------------------------------------------------------
@dataclass
class ReplacementResult:
    """Store replacement summary info."""
    count: int
    addresses: List[int]
    backup_file: Optional[str]


# ---------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------
class MemoryEditor:
    """Encapsulates heap parsing, searching, and safe editing."""

    def __init__(self, pid: int):
        self.pid = pid
        self.maps_path = f"/proc/{pid}/maps"
        self.mem_path = f"/proc/{pid}/mem"
        self.heap_ranges: List[Tuple[int, int]] = []
        self._validate_process()

    # -------------------------------------------------------------
    def _validate_process(self) -> None:
        """Check that the process exists and is readable."""
        if not os.path.exists(f"/proc/{self.pid}"):
            raise ProcessLookupError(f"Process {self.pid} not found.")
        try:
            with open(self.maps_path, "r"):
                pass
        except PermissionError:
            raise PermissionError(
                f"Need root privileges to access process {self.pid}"
            )

    # -------------------------------------------------------------
    def _locate_heap_regions(self) -> List[Tuple[int, int]]:
        """Return a list of (start, end) heap memory ranges."""
        ranges: List[Tuple[int, int]] = []
        with open(self.maps_path, "r") as maps:
            for line in maps:
                if "[heap]" in line and "rw" in line:
                    addr = line.split()[0]
                    start, end = [int(x, 16) for x in addr.split("-")]
                    ranges.append((start, end))
        if not ranges:
            raise RuntimeError("No accessible heap region found.")
        return ranges

    # -------------------------------------------------------------
    def _backup_region(self, start: int, end: int, file_name: str) -> None:
        """Create a binary backup of the heap segment."""
        size = end - start
        if size > MAX_HEAP_SIZE:
            raise MemoryError(
                f"Heap region too large "
                f"({size / 1024 / 1024:.2f} MB > {MAX_HEAP_SIZE / 1024 / 1024} MB)"
            )

        with open(self.mem_path, "rb") as mem, open(file_name, "wb") as backup:
            mem.seek(start)
            backup.write(mem.read(size))

    # -------------------------------------------------------------
    def find_and_replace(
        self,
        search_bytes: bytes,
        replace_bytes: bytes,
        replace_all: bool = False,
        dry_run: bool = False,
        backup_prefix: Optional[str] = None,
    ) -> ReplacementResult:
        """Main operation that performs the safe replacement."""
        if len(replace_bytes) > len(search_bytes):
            raise ValueError("Replacement string cannot be longer than search.")

        self.heap_ranges = self._locate_heap_regions()
        result = ReplacementResult(0, [], None)

        for start, end in self.heap_ranges:
            size = end - start
            logging.info(
                f"Scanning heap region 0x{start:x}-0x{end:x} ({size} bytes)"
            )

            backup_file = None
            if backup_prefix:
                backup_file = f"{backup_prefix}_{start:x}-{end:x}{BACKUP_EXTENSION}"
                self._backup_region(start, end, backup_file)
                result.backup_file = backup_file

            with open(self.mem_path, "r+b") as mem_file:
                mem_file.seek(start)
                heap_data = mem_file.read(size)

                offset = 0
                while True:
                    pos = heap_data.find(search_bytes, offset)
                    if pos == -1:
                        break

                    abs_pos = start + pos
                    logging.info(f"Found match at 0x{abs_pos:x}")

                    if not dry_run:
                        mem_file.seek(abs_pos)
                        mem_file.write(replace_bytes)
                        # Null-pad if replacement is shorter
                        padding = len(search_bytes) - len(replace_bytes)
                        if padding > 0:
                            mem_file.write(b"\x00" * padding)

                    result.count += 1
                    result.addresses.append(abs_pos)
                    if not replace_all:
                        break
                    offset = pos + 1

        return result


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------
def validate_strings(search_str: str, replace_str: str, unicode_mode: bool) -> Tuple[bytes, bytes]:
    """Validate and encode input strings."""
    if not search_str:
        raise ValueError("Search string cannot be empty.")
    encoding = "utf-8" if unicode_mode else "ascii"
    try:
        return search_str.encode(encoding), replace_str.encode(encoding)
    except UnicodeError as err:
        raise ValueError(f"Encoding error: {err}")


def setup_logging(verbose: bool) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=level
    )


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Advanced heap memory string replacement tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  sudo ./advanced_heap_replace.py --all --backup /tmp/heap "
            "1234 password p@ssw0rd"
        ),
    )

    parser.add_argument("pid", type=int, help="Target process ID")
    parser.add_argument("search_string", type=str, help="String to search for")
    parser.add_argument("replace_string", type=str, help="Replacement string")
    parser.add_argument("--unicode", action="store_true", help="Use UTF-8 encoding")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    parser.add_argument("--backup", type=str, help="Backup file prefix")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Replace all matches")
    return parser.parse_args()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    setup_logging(args.verbose)

    if os.geteuid() != 0:
        logging.error("This tool must be run as root.")
        sys.exit(1)

    try:
        editor = MemoryEditor(args.pid)
        search_b, replace_b = validate_strings(
            args.search_string, args.replace_string, args.unicode
        )

        logging.info(f"Starting replacement in PID {args.pid}")
        logging.debug(f"Search bytes: {search_b}")
        logging.debug(f"Replace bytes: {replace_b}")

        result = editor.find_and_replace(
            search_bytes=search_b,
            replace_bytes=replace_b,
            replace_all=args.all,
            dry_run=args.dry_run,
            backup_prefix=args.backup,
        )

        if result.count == 0:
            logging.warning("No matches found in heap.")
        else:
            action = "Would replace" if args.dry_run else "Replaced"
            logging.info(f"{action} {result.count} occurrence(s) at:")
            for addr in result.addresses:
                logging.info(f"  0x{addr:x}")
            if result.backup_file:
                logging.info(f"Backup saved to {result.backup_file}")

        sys.exit(0)

    except Exception as err:
        logging.error(f"Operation failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
