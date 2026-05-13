from pathlib import Path
import re
import img2pdf
import pikepdf


def create_pdf(
    image_paths: list[Path],
    output_pdf: Path,
    strip_pattern: str = "",
) -> None:
    image_paths = [Path(p) for p in image_paths]

    if not image_paths:
        raise ValueError("No image paths provided.")

    def folio_label(path: Path) -> str:
        label = path.stem
        if strip_pattern:
            label = re.sub(strip_pattern, "", label)
        return label

    # img2pdf embeds JPEG/JPEG2000 losslessly where possible.
    # It does not resample or recompress images.
    pdf_bytes = img2pdf.convert([str(p) for p in image_paths])

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    tmp_pdf = output_pdf.with_suffix(".tmp.pdf")
    tmp_pdf.write_bytes(pdf_bytes)

    pdf = pikepdf.Pdf.open(tmp_pdf)

    if len(pdf.pages) != len(image_paths):
        raise RuntimeError(
            f"Expected {len(image_paths)} pages, got {len(pdf.pages)}."
        )

    with pdf.open_outline() as outline:
        outline.root.clear()

        for page_index, image_path in enumerate(image_paths):
            label = folio_label(image_path)
            print(label)
            outline.root.append(
                pikepdf.OutlineItem(label, page_index)
            )

    pdf.save(output_pdf)
    tmp_pdf.unlink()