import os
import sys

import fuzzers
import packaging
import pytest

from PIL import Image, features

if sys.platform.startswith("win32"):
    pytest.skip("Fuzzer is linux only", allow_module_level=True)
if features.check("libjpeg_turbo"):
    version = packaging.version.parse(features.version("libjpeg_turbo"))
    if version.major == 2 and version.minor == 0:
        pytestmark = pytest.mark.valgrind_known_error(
            reason="Known failing with libjpeg_turbo 2.0"
        )


@pytest.mark.parametrize(
    "path",
    [
        os.path.join(dirname, path)
        for dirname, subdirs, files in os.walk("Tests/images")
        for path in files
        if os.path.isfile(os.path.join(dirname, path))
    ],
)
def test_fuzz_images(path):
    fuzzers.enable_decompressionbomb_error()
    try:
        with open(path, "rb") as f:
            fuzzers.fuzz_image(f.read())
            assert True
    except (
        OSError,
        SyntaxError,
        MemoryError,
        ValueError,
        NotImplementedError,
        OverflowError,
    ):
        # Known exceptions that are through from Pillow
        assert True
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        Image.UnidentifiedImageError,
    ):
        # Known Image.* exceptions
        assert True
    finally:
        fuzzers.disable_decompressionbomb_error()


@pytest.mark.parametrize(
    "path",
    [
        os.path.join(dirname, path)
        for dirname, subdirs, files in os.walk("Tests/fonts")
        for path in files
        if os.path.isfile(os.path.join(dirname, path))
    ],
)
def test_fuzz_fonts(path):
    if not path:
        return
    with open(path, "rb") as f:
        try:
            fuzzers.fuzz_font(f.read())
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            pass
        assert True
