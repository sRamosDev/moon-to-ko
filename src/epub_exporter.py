import os

class EpubExporter:
    @staticmethod
    def export(extractor, output_dir: str, progress_cb=None) -> int:
        books_dir = os.path.join(output_dir, "books")
        os.makedirs(books_dir, exist_ok=True)
        epub_paths = [
            p for p in extractor.get_all_original_paths() if p.lower().endswith(".epub")
        ]

        from tqdm import tqdm
        
        extracted_count = 0
        total_epubs = len(epub_paths)
        
        # If GUI progress callback provided, skip tqdm to avoid terminal spam
        iterator = epub_paths if progress_cb else tqdm(epub_paths, desc="Extracting EPUBs", unit="file")
        
<<<<<<< HEAD
        for epub_path in iterator:
            basename = os.path.basename(epub_path)
            out_book = os.path.join(books_dir, basename)

            try:
                extractor.extract_file_to(epub_path, out_book)
                extracted_count += 1
                if progress_cb:
                    progress_cb(extracted_count, total_epubs)
            except Exception:
                # Handle case where file might not exist or other issues
                pass
=======
        with zipfile.ZipFile(extractor.mrpro_path, "r") as zf:
            for epub_path in iterator:
                content = extractor.get_file_content(epub_path, zf=zf)
                if content:
                    basename = os.path.basename(epub_path)
                    out_book = os.path.join(books_dir, basename)
                    with open(out_book, "wb") as f:
                        f.write(content)
                    extracted_count += 1
                    if progress_cb:
                        progress_cb(extracted_count, total_epubs)
>>>>>>> cd0d06e (⚡ Optimize epub extraction by opening zip file once)
                
        return extracted_count
