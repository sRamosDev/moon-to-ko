# TEAM_001: Main CLI orchestrator for the migration
import argparse
import tempfile
import os
import sys

from src.mrpro_extractor import MrproExtractor
from src.db_mapper import DbMapper
from src.koreader_exporter import KOReaderExporter


def main():
    parser = argparse.ArgumentParser(
        description="Moon+ Reader Pro to KOReader migration tool"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to the .mrpro backup file"
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to the output directory where KOReader files will be generated",
    )
    parser.add_argument(
        "--extract-epubs",
        action="store_true",
        help="Extract all EPUB files from the backup into the output directory",
    )
    parser.add_argument(
        "--extract-replacements",
        action="store_true",
        help="Extract and translate Moon+ Reader text replacement rules",
    )
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Starting migration from {input_file} to {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "mrbooks.db")

        # 1. Extract DB
        print("Extracting Moon+ Reader database...")
        try:
            extractor = MrproExtractor(input_file)
            extractor.extract_db_to(db_path)
            print("Database extracted successfully.")
        except Exception as e:
            print(f"Error during extraction: {e}")
            sys.exit(1)

        # 2. Map DB
        print("Parsing reading statistics and metadata...")
        mapper = DbMapper(db_path)
        books = mapper.get_books()
        stats = mapper.get_statistics()
        progresses = mapper.get_read_progresses()

        print(
            f"Found {len(books)} books, {len(stats)} stat records, and {len(progresses)} reading progresses."
        )

        # Optional Extractions
        if args.extract_epubs:
            print("Extracting EPUB files...")
            from src.epub_exporter import EpubExporter

            count = EpubExporter.export(extractor, output_dir)
            print(f"Extracted {count} EPUB files.")

        book_rules_map = {}
        if args.extract_replacements:
            print("Parsing text replacement rules...")
            from src.replacements_exporter import ReplacementsExporter

            global_count = ReplacementsExporter.export_global_rules(
                extractor, output_dir
            )
            if global_count > 0:
                print(f"Exported global replacements ({global_count} rules).")

            book_rules_map = ReplacementsExporter.extract_book_rules(extractor)
            print(
                f"Exported book-specific replacements for {len(book_rules_map)} books."
            )

        # 3. Export to KOReader
        print("Generating KOReader statistics.sqlite and .sdr sidecars...")
        exporter = KOReaderExporter(output_dir)
        exporter.export_statistics(books, stats)
        exporter.export_sdr_folders(progresses, book_rules_map=book_rules_map)

    print(f"Migration complete! Files saved to {output_dir}")
    print("Copy the generated `statistics.sqlite3` to your KOReader settings folder.")
    print(
        "Copy the generated `.sdr` folders next to your actual book files on your e-reader."
    )


if __name__ == "__main__":
    main()
