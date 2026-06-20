from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps, UnidentifiedImageError

from apps.common.storage import file_key, file_url, media_url_for_key


VARIANT_WIDTHS = (320, 480, 768, 1024, 1440, 1920)
WEBP_QUALITY = 78
JPEG_QUALITY = 82


@dataclass(frozen=True)
class VariantResult:
    source_key: str
    variant_key: str
    width: int
    height: int
    format: str
    byte_size: int


def ensure_image_variants(file_field, *, force: bool = False) -> list[VariantResult]:
    source_key = file_key(file_field)
    if not source_key:
        return []

    try:
        with file_field.storage.open(source_key, "rb") as handle:
            image = Image.open(handle)
            image.load()
    except (FileNotFoundError, UnidentifiedImageError, OSError):
        return []

    image = ImageOps.exif_transpose(image)
    source_width, source_height = image.size
    if source_width <= 0 or source_height <= 0:
        return []

    target_widths = sorted({min(width, source_width) for width in VARIANT_WIDTHS})
    has_alpha = _has_alpha(image)
    results: list[VariantResult] = []

    for target_width in target_widths:
        target_height = round(source_height * (target_width / source_width))
        resized = image if target_width == source_width else image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        results.append(_write_variant(source_key, resized, target_width, target_height, "webp", force=force))
        if not has_alpha:
            results.append(_write_variant(source_key, resized, target_width, target_height, "jpeg", force=force))

    return results


def image_variant_set(file_field) -> dict:
    source_key = file_key(file_field)
    fallback_url = file_url(file_field)
    if not source_key:
        return {"webp": [], "jpeg": [], "fallback_url": fallback_url, "fallback_key": None}

    from apps.content.models import ImageVariant

    variants = ImageVariant.objects.filter(source_key=source_key).order_by("format", "width")
    grouped = {"webp": [], "jpeg": []}
    for variant in variants:
        grouped.setdefault(variant.format, []).append(
            {
                "url": media_url_for_key(variant.variant_key),
                "key": variant.variant_key,
                "width": variant.width,
                "height": variant.height,
                "format": variant.format,
                "byte_size": variant.byte_size,
            }
        )

    return {
        "webp": grouped.get("webp", []),
        "jpeg": grouped.get("jpeg", []),
        "fallback_url": fallback_url,
        "fallback_key": source_key,
    }


def _write_variant(source_key: str, image: Image.Image, width: int, height: int, image_format: str, *, force: bool) -> VariantResult:
    from apps.content.models import ImageVariant

    ext = "jpg" if image_format == "jpeg" else "webp"
    variant_key = _variant_key(source_key, width, ext)

    existing = ImageVariant.objects.filter(source_key=source_key, width=width, format=image_format).first()
    if existing and not force and default_storage.exists(existing.variant_key):
        return VariantResult(
            source_key=existing.source_key,
            variant_key=existing.variant_key,
            width=existing.width,
            height=existing.height,
            format=existing.format,
            byte_size=existing.byte_size,
        )

    output = BytesIO()
    if image_format == "jpeg":
        encoded = image.convert("RGB")
        encoded.save(output, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    else:
        encoded = image.convert("RGBA" if _has_alpha(image) else "RGB")
        encoded.save(output, format="WEBP", quality=WEBP_QUALITY, method=6)
    data = output.getvalue()

    if default_storage.exists(variant_key):
        default_storage.delete(variant_key)
    content = ContentFile(data)
    content.content_type = "image/jpeg" if image_format == "jpeg" else "image/webp"
    saved_key = default_storage.save(variant_key, content)
    ImageVariant.objects.update_or_create(
        source_key=source_key,
        width=width,
        format=image_format,
        defaults={"variant_key": saved_key, "height": height, "byte_size": len(data)},
    )
    return VariantResult(source_key=source_key, variant_key=saved_key, width=width, height=height, format=image_format, byte_size=len(data))


def _variant_key(source_key: str, width: int, ext: str) -> str:
    root = source_key.strip("/")
    return f"variants/{root}/w{width}.{ext}"


def _has_alpha(image: Image.Image) -> bool:
    if image.mode in {"RGBA", "LA"}:
        return True
    return image.mode == "P" and "transparency" in image.info
