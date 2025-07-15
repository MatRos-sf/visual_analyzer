import ast
import mimetypes
import re
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from warnings import warn

import piexif
from PIL import Image

from analyzer_core.exceptions import NotSupported

PATTERN_VA_DESCRIPTION_RE = r"va\|({.*})\|"
SUPPORTED_EXTENSION = ["jpg", "jpeg"]


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"


def extract_info_type(path: str | Path) -> Tuple[MediaType, str]:
    """
    Return (media_type, extension) for the given path.
    Raises:
        NotSupported:   If the MIME type cannot be determined
    """
    path = Path(path)
    mine_type, _ = mimetypes.guess_type(path)
    if mine_type is None:
        raise NotSupported(f"File {path} is not supported (unknow MIME type).")
    _type, extension = mine_type.split("/")
    return MediaType(_type), extension


class AbstractMetadata(ABC):
    """
    Abstract class for metadata manager. This class should have 'media_path' and 'pattern_to_match' attributes
    """

    media_path: Path
    pattern_to_match: re.Pattern

    def encode_description(self, raw_description: bytes, faces_info: dict) -> None:
        raise NotImplementedError()

    def decode_description(self):
        raise NotImplementedError()


class MetaDataManager(AbstractMetadata):
    def __init__(
        self, media_path: Path, pattern_to_match: re.Pattern = PATTERN_VA_DESCRIPTION_RE
    ):
        self.media_path = media_path
        self.pattern_to_match = pattern_to_match

    def encode_description(self, raw_description: bytes, faces_info: dict) -> None:
        image = Image.open(self.media_path)
        exif_dict = piexif.load(image.info.get("exif", b""))
        exif_dict["0th"][
            piexif.ImageIFD.ImageDescription
        ] = self.create_new_description(raw_description, faces_info)

        exif_bytes = piexif.dump(exif_dict)
        image.save(self.media_path, exif=exif_bytes)

    def decode_description(self) -> bytes:
        image = Image.open(self.media_path)
        exif_dict = piexif.load(image.info.get("exif", {}))
        exif_dict = exif_dict.get("0th", {}).get(piexif.ImageIFD.ImageDescription, b"")
        return exif_dict

    def extract_faces_info(self, raw_description: bytes) -> dict:
        """
        Extract faces info from 'raw_description' based on 'pattern_to_match'.
        'pattern_to_match' must include group section to extract face info.
        """
        match_pattern = re.search(
            self.pattern_to_match, raw_description.decode("utf-8")
        )
        if not match_pattern:
            return {}

        return ast.literal_eval(match_pattern.group(1))

    def create_new_description(self, raw_description: bytes, faces_info: dict) -> bytes:
        raw_description: str = raw_description.decode("utf-8")
        new_metadata_patch = f"va|{str(faces_info)}|"
        match_pattern = re.search(self.pattern_to_match, raw_description)
        if not match_pattern:
            return raw_description.encode("utf-8")
        return raw_description.replace(
            match_pattern.group(0), new_metadata_patch
        ).encode("utf-8")


class Media:
    def __init__(
        self, original_path: Path, metadata_manager: AbstractMetadata = MetaDataManager
    ):
        self.original_path = original_path
        self.metadata_manager = metadata_manager(original_path)
        self.faces: Optional[dict] = None
        self.raw_description: Optional[bytes] = None

        media_type, extend = extract_info_type(original_path)
        self.media_type = media_type
        self.media_extension = extend

    def load_metadata(self) -> None:
        """
        Set 'raw_description' and 'faces' attributes
        """
        self.raw_description = self.metadata_manager.decode_description()
        self.faces = self.metadata_manager.extract_faces_info(self.raw_description)

    def save_metadata(self):
        if not self.faces:
            return

        self.metadata_manager.encode_description(self.raw_description, self.faces)


class MediaCollection:
    def __init__(self, media: List[Media]):
        self.photos = []
        self.videos = []
        self.unsupported_media = []

        self.__set_attributes(media)

    def __set_attributes(self, media: List[Media]):
        for media in media:
            if (
                media.media_type not in [MediaType.IMAGE, MediaType.VIDEO]
                or media.media_extension not in SUPPORTED_EXTENSION
            ):
                warn(f"Media {media.original_path} is not supported.")
                continue

            if media.media_type == MediaType.IMAGE:
                self.photos.append(media)
            elif media.media_type == MediaType.VIDEO:
                self.videos.append(media)

    @classmethod
    def from_path_list(cls, path_list: List[Path]):
        media_collection = []
        unsupported_media = []
        for path in path_list:
            try:
                media_collection.append(Media(path))
            except NotSupported as e:
                warn("Media not supported: " + str(e))
                unsupported_media.append(path)
            except ValueError as e:
                warn(str(e))
                unsupported_media.append(path)
        mc = cls(media_collection)
        mc.unsupported_media += unsupported_media
        return mc
