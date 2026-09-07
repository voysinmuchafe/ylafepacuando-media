import sys
from pathlib import Path, PurePosixPath

from PIL import Image

JPEG_QUALITY = 95
JPEG_SUBSAMPLING = 0


def transport_path_for(master_path: Path) -> Path:
    raw = master_path.as_posix()
    pure = PurePosixPath(raw)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError("PNG master path inválido.")
    if len(pure.parts) != 2 or pure.parts[0] != "published":
        raise ValueError("El PNG master debe estar directamente bajo published/.")
    if pure.suffix.lower() != ".png":
        raise ValueError("El master debe ser PNG.")
    return Path("transport") / f"{pure.stem}.jpg"


def _assert_opaque(image: Image.Image) -> None:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        alpha = image.convert("RGBA").getchannel("A")
        minimum, maximum = alpha.getextrema()
        if minimum < 255 or maximum < 255:
            raise ValueError(
                "El PNG contiene transparencia y no se puede aplanar silenciosamente."
            )


def convert_png_to_jpeg(master_path: Path, transport_path: Path) -> Path:
    with Image.open(master_path) as image:
        if image.format != "PNG":
            raise ValueError("El master debe ser un PNG válido.")
        _assert_opaque(image)
        rgb = image.convert("RGB")
        transport_path.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(
            transport_path,
            format="JPEG",
            quality=JPEG_QUALITY,
            subsampling=JPEG_SUBSAMPLING,
            optimize=False,
            progressive=False,
        )
    return transport_path


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Uso: prepare_transport.py published/<archivo>.png [...]")
    for raw_path in sys.argv[1:]:
        master = Path(raw_path)
        transport = transport_path_for(master)
        convert_png_to_jpeg(master, transport)
        print(f"Prepared {transport.as_posix()}")


if __name__ == "__main__":
    main()
