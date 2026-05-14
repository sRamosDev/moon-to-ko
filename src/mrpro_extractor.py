import zipfile
import typing
import shutil

class MrproExtractor:
    def __init__(self, mrpro_path: str):
        self.mrpro_path = mrpro_path
        self._name_map = None

    def _load_names_list(self):
        if self._name_map is not None:
            return

        self._name_map = {}
        with zipfile.ZipFile(self.mrpro_path, "r") as zf:
            names_list_path = "com.flyersoft.moonreaderp/_names.list"
            try:
                zf.getinfo(names_list_path)
            except KeyError:
                raise FileNotFoundError(
                    f"{names_list_path} not found in the backup archive."
                )

            with zf.open(names_list_path) as f:
                content = f.read().decode("utf-8")

            for idx, line in enumerate(content.splitlines()):
                cleaned_line = line.strip()
                if cleaned_line:
                    tag_filename = f"com.flyersoft.moonreaderp/{idx + 1}.tag"
                    self._name_map[cleaned_line] = tag_filename

    def _get_tag_filename(self, original_path: str) -> str:
        self._load_names_list()
        tag_filename = self._name_map.get(original_path)
        if not tag_filename:
            raise FileNotFoundError(
                f"Original path '{original_path}' not found in the backup mapping."
            )
        return tag_filename

    def get_file_content(self, original_path: str, zf: zipfile.ZipFile = None) -> bytes:
        """Extract the content of a file based on its original path."""
        tag_filename = self._get_tag_filename(original_path)

        def _read_from_zip(z: zipfile.ZipFile):
            try:
                with z.open(tag_filename) as f:
                    return f.read()
            except KeyError:
                raise FileNotFoundError(
                    f"Mapped tag file '{tag_filename}' not found in the backup archive."
                )

        if zf is not None:
            return _read_from_zip(zf)
            
        with zipfile.ZipFile(self.mrpro_path, "r") as mz:
            return _read_from_zip(mz)

    def get_all_original_paths(self) -> typing.List[str]:
        """Return a list of all original paths contained in the backup."""
        self._load_names_list()
        return list(self._name_map.keys())

    def extract_file_to(self, original_path: str, destination_path: str):
        """Extract a Specific file to a destination path."""
        tag_filename = self._get_tag_filename(original_path)
        with zipfile.ZipFile(self.mrpro_path, "r") as mz:
            try:
                with mz.open(tag_filename) as src, open(destination_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            except KeyError:
                raise FileNotFoundError(
                    f"Mapped tag file '{tag_filename}' not found in the backup archive."
                )

    def extract_db_to(self, destination_path: str):
        """Helper to specifically extract the mrbooks.db sqlite file."""
        self.extract_file_to(
            "com.flyersoft.moonreaderp/databases/mrbooks.db", destination_path
        )
