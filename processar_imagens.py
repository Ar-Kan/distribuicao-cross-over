from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "imagens"
OUTPUT_DIR = ROOT / "saidas"
PROCESSED_DIR = OUTPUT_DIR / "imagens_processadas"
COMPARISON_DIR = OUTPUT_DIR / "comparacoes"


def apply_clahe_to_luminance(image_bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    lightness, channel_a, channel_b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_lightness = clahe.apply(lightness)
    enhanced_lab = cv2.merge((enhanced_lightness, channel_a, channel_b))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def unsharp_mask(image_bgr: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(image_bgr, (0, 0), sigmaX=1.1)
    return cv2.addWeighted(image_bgr, 1.55, blurred, -0.55, 0)


def preprocess_image(image_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    contrast = apply_clahe_to_luminance(image_bgr)
    denoised = cv2.bilateralFilter(contrast, d=7, sigmaColor=45, sigmaSpace=45)
    sharpened = unsharp_mask(denoised)

    gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

    return sharpened, gray


def make_comparison(original_bgr: np.ndarray, processed_bgr: np.ndarray) -> np.ndarray:
    original = original_bgr.copy()
    processed = processed_bgr.copy()

    label_height = 54
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 2

    def add_label(image: np.ndarray, label: str) -> np.ndarray:
        canvas = np.full(
            (image.shape[0] + label_height, image.shape[1], 3),
            fill_value=245,
            dtype=np.uint8,
        )
        canvas[label_height:, :] = image
        cv2.putText(
            canvas,
            label,
            (18, 36),
            font,
            font_scale,
            (35, 35, 35),
            thickness,
            cv2.LINE_AA,
        )
        return canvas

    return np.hstack(
        (
            add_label(original, "Original"),
            add_label(processed, "Processada"),
        )
    )


def process_all_images() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(INPUT_DIR.glob("*.jpeg"))
    if not image_paths:
        raise FileNotFoundError(f"Nenhuma imagem .jpeg encontrada em {INPUT_DIR}")

    for image_path in image_paths:
        image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image_bgr is None:
            raise ValueError(f"Não foi possível ler a imagem: {image_path}")

        processed_bgr, processed_gray = preprocess_image(image_bgr)
        output_stem = image_path.stem.replace(" ", "_")

        processed_path = PROCESSED_DIR / f"{output_stem}_processada.jpeg"
        gray_path = PROCESSED_DIR / f"{output_stem}_analitica_cinza.jpeg"
        comparison_path = COMPARISON_DIR / f"{output_stem}_antes_depois.jpeg"

        cv2.imwrite(str(processed_path), processed_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        cv2.imwrite(str(gray_path), processed_gray, [cv2.IMWRITE_JPEG_QUALITY, 95])

        comparison = make_comparison(image_bgr, processed_bgr)
        cv2.imwrite(str(comparison_path), comparison, [cv2.IMWRITE_JPEG_QUALITY, 95])


if __name__ == "__main__":
    process_all_images()
