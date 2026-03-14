# TEAM_001: Exports EPUB files directly from the .mrpro archive matching original structure.
import os
import sys


class EpubExporter:
    @staticmethod
    def export(extractor, output_dir: str) -> int:
        books_dir = os.path.join(output_dir, "books")
        os.makedirs(books_dir, exist_ok=True)
        epub_paths = [
            p for p in extractor.get_all_original_paths() if p.lower().endswith(".epub")
        ]

        import zipfile
        from tqdm import tqdm
        
        extracted_count = 0
        for epub_path in tqdm(epub_paths, desc="Extracting EPUBs", unit="file"):
            content = extractor.get_file_content(epub_path)
            if content:
                basename = os.path.basename(epub_path)
                out_book = os.path.join(books_dir, basename)
                with open(out_book, "wb") as f:
                    f.write(content)
                extracted_count += 1
                
        return extracted_count
