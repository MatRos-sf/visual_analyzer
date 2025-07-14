import ast
import re
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import List, Optional

import piexif
from PIL import Image

PATTERN_VA_DESCRIPTION = r"va\|({.*})\|"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"


class AbstractMetadata(ABC):
    def __init__(self, media_path: Path):
        self.media_path = media_path

    def encode_description(self, src_path: Path) -> None:
        raise NotImplementedError()

    def decode_description(self):
        raise NotImplementedError()


class MetaDataManager:
    def __init__(
        self, media_path: Path, pattern_to_match: re.Pattern = PATTERN_VA_DESCRIPTION
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
    def __init__(self, original_path: Path, metadata_manager: AbstractMetadata):
        self.original_path = original_path
        self.metadata_manager = metadata_manager(original_path)
        self.faces: Optional[dict] = None
        self.raw_description: Optional[bytes] = None

    def load_metadata(self) -> None:
        """
        Set 'raw_description' and 'facec' attributes
        """
        self.raw_description = self.metadata_manager.decode_description()
        self.faces = self.metadata_manager.extract_faces_info(self.raw_description)

    def save_metadata(self):
        pass


class MediaCollection:
    def __init__(self, media: List[Media]):
        self.__set_atributes(media)

    def __set_atributes(self, media: List[Media]):
        self.photos = []
        self.videos = []
        self.unsupported_media = []

        for media in media:
            if media.media_type == MediaType.IMAGE:
                self.photos.append(media)
            elif media.media_type == MediaType.VIDEO:
                self.videos.append(media)
            else:
                self.unsupported_media.append(media)
