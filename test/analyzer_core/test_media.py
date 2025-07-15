from unittest.mock import patch

import piexif
import pytest
from PIL import Image

from analyzer_core.media import MetaDataManager

DESCRIPTION = "Test photo,va|{'face1', 'face2'}|End description"


@pytest.fixture
def image_with_metadata(tmp_path_factory):
    metadata_description = DESCRIPTION.encode("utf-8")
    image = Image.new("RGB", (100, 100), color="white")
    fn = tmp_path_factory.mktemp("data") / "img.jpg"

    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = metadata_description
    exif_bytes = piexif.dump(exif_dict)
    image.save(fn, format="JPEG", exif=exif_bytes)

    return fn


@pytest.mark.usefixtures("image_with_metadata")
class TestMetaDataManager:
    @pytest.mark.parametrize("new_faces_info", [{"test1", "test2"}, {}])
    def test_should_encode_description_with_new_meta(
        self, image_with_metadata, new_faces_info
    ):
        metadata_manager = MetaDataManager(image_with_metadata)
        metadata_manager.encode_description(DESCRIPTION.encode("utf-8"), new_faces_info)
        del metadata_manager

        new_meta_manager = MetaDataManager(image_with_metadata)
        assert new_meta_manager.decode_description() != DESCRIPTION.encode("utf-8")

    def test_should_decode_description(self, image_with_metadata):
        metadata_manager = MetaDataManager(image_with_metadata)
        assert metadata_manager.decode_description() == DESCRIPTION.encode("utf-8")

    def test_should_extract_faces_info(self, image_with_metadata):
        metadata_manager = MetaDataManager(image_with_metadata)
        assert metadata_manager.extract_faces_info(DESCRIPTION.encode("utf-8")) == {
            "face1",
            "face2",
        }

    @patch("re.search", return_value=None)
    def test_should_extract_face_info_when_no_metadata(self, image_with_metadata):
        metadata_manager = MetaDataManager(image_with_metadata)
        assert metadata_manager.extract_faces_info(DESCRIPTION.encode("utf-8")) == {}

    def test_should_create_new_description(self, image_with_metadata):
        new_faces_info = {"face3", "face4"}
        expected = DESCRIPTION.replace(
            "{'face1', 'face2'}", str(new_faces_info)
        ).encode("utf-8")
        metadata_manager = MetaDataManager(image_with_metadata)
        assert (
            metadata_manager.create_new_description(
                DESCRIPTION.encode("utf-8"), new_faces_info
            )
            == expected
        )

    @pytest.mark.parametrize(
        "raw_description",
        [b"va|['face1', 'face2']|", b"va{'face1', 'face2'}|", b"{'face1', 'face2'}"],
    )
    def test_should_not_create_new_description_when_not_match_pattern(
        self, image_with_metadata, raw_description
    ):
        new_face = {"test1"}

        metadata_manager = MetaDataManager(image_with_metadata)
        assert (
            metadata_manager.create_new_description(raw_description, new_face)
            == raw_description
        )
