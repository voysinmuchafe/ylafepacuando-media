from pathlib import Path

import pytest
from PIL import Image

from scripts.prepare_transport import convert_png_to_jpeg, transport_path_for


def test_transport_path_maps_published_png_to_transport_jpg():
    assert transport_path_for(Path("published/003-si-me-debes-plata.png")) == Path(
        "transport/003-si-me-debes-plata.jpg"
    )


def test_transport_path_rejects_non_published_or_non_png_paths():
    for path in [
        Path("003.png"),
        Path("drafts/003.png"),
        Path("published/003.jpg"),
        Path("published/../secret.png"),
        Path("published/subdir/003.png"),
    ]:
        with pytest.raises(ValueError):
            transport_path_for(path)


def test_conversion_preserves_dimensions_and_outputs_rgb_jpeg(tmp_path):
    source = tmp_path / "published" / "piece.png"
    target = tmp_path / "transport" / "piece.jpg"
    source.parent.mkdir()
    Image.new("RGB", (1080, 1350), (240, 235, 220)).save(source)

    result = convert_png_to_jpeg(source, target)

    assert result == target
    with Image.open(target) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert image.size == (1080, 1350)


def test_conversion_rejects_any_non_opaque_alpha(tmp_path):
    source = tmp_path / "piece.png"
    target = tmp_path / "piece.jpg"
    image = Image.new("RGBA", (20, 20), (255, 255, 255, 255))
    image.putpixel((0, 0), (255, 255, 255, 254))
    image.save(source)

    with pytest.raises(ValueError, match="transparencia"):
        convert_png_to_jpeg(source, target)
    assert not target.exists()


def test_main_converts_each_supplied_master(monkeypatch, tmp_path):
    from scripts import prepare_transport

    source = tmp_path / "published" / "piece.png"
    source.parent.mkdir()
    Image.new("RGB", (10, 10), "white").save(source)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        ["prepare_transport.py", "published/piece.png"],
    )

    prepare_transport.main()

    assert (tmp_path / "transport" / "piece.jpg").exists()
