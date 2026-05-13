from pathlib import Path

import pytest
from PIL import Image

from msstools.split import split_images


def create_test_image(path: Path, width=200, height=100, color=(255, 0, 0)):
    img = Image.new("RGB", (width, height), color=color)
    img.save(path)
    return path


def create_margin_test_image(path: Path) -> Path:
    img = Image.new("RGB", (100, 20), (255, 0, 0))
    for x in range(10, 50):
        for y in range(20):
            img.putpixel((x, y), (0, 255, 0))
    for x in range(50, 90):
        for y in range(20):
            img.putpixel((x, y), (0, 0, 255))
    img.save(path)
    return path


def test_split_images_ltr(tmp_path):
    img1 = create_test_image(tmp_path / "page1.jpg")
    img2 = create_test_image(tmp_path / "page2.jpg", color=(0, 255, 0))

    split_images(tmp_path / "output", [img1, img2], overlap=20)

    files = list(tmp_path.glob("output-*"))
    assert len(files) == 4
    assert (tmp_path / "output-0.jpg").exists()
    assert (tmp_path / "output-1.jpg").exists()
    assert (tmp_path / "output-2.jpg").exists()
    assert (tmp_path / "output-3.jpg").exists()

    for file in files:
        with Image.open(file) as img:
            assert img.height == 100
            assert img.width > 100


def test_split_images_rtl(tmp_path):
    img = create_test_image(tmp_path / "page.jpg", color=(0, 0, 255))

    split_images(tmp_path / "out", [img], rtl=True)

    assert (tmp_path / "out-0.jpg").exists()
    assert (tmp_path / "out-1.jpg").exists()


def test_split_images_zero_pads_output_indexes(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(10)
    ]

    split_images(tmp_path / "out", images)

    assert (tmp_path / "out-00.jpg").exists()
    assert (tmp_path / "out-01.jpg").exists()
    assert (tmp_path / "out-18.jpg").exists()
    assert (tmp_path / "out-19.jpg").exists()


def test_split_images_skip(tmp_path):
    img1 = create_test_image(tmp_path / "skip1.jpg", color=(123, 123, 123))
    img2 = create_test_image(tmp_path / "split1.jpg", color=(234, 234, 234))

    split_images(tmp_path / "book", [img1, img2], skip=1)

    assert (tmp_path / "book-0.jpg").exists()
    assert (tmp_path / "book-1.jpg").exists()
    assert (tmp_path / "book-2.jpg").exists()


def test_split_images_recto_anchor(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(3)
    ]

    split_images(tmp_path / "book", images, recto=["page1.jpg=49"])

    assert (tmp_path / "book-0.jpg").exists()
    assert (tmp_path / "book-1.jpg").exists()
    assert (tmp_path / "book-2.jpg").exists()
    assert (tmp_path / "book-3-49r.jpg").exists()
    assert (tmp_path / "book-4-49v.jpg").exists()
    assert (tmp_path / "book-5-50r.jpg").exists()


def test_split_images_recto_anchor_with_padded_indexes(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(6)
    ]

    split_images(tmp_path / "book", images, skip=3, recto=["page3.jpg=49"])

    assert (tmp_path / "book-0.jpg").exists()
    assert (tmp_path / "book-1.jpg").exists()
    assert (tmp_path / "book-2.jpg").exists()
    assert (tmp_path / "book-3.jpg").exists()
    assert (tmp_path / "book-4-49r.jpg").exists()
    assert (tmp_path / "book-5-49v.jpg").exists()
    assert (tmp_path / "book-6-50r.jpg").exists()


def test_split_images_removes_margins_before_splitting(tmp_path):
    img = create_margin_test_image(tmp_path / "page.png")

    split_images(
        tmp_path / "out",
        [img],
        overlap=0,
        margin_left=10,
        margin_right=10,
    )

    with Image.open(tmp_path / "out-0.png") as verso_img:
        assert verso_img.size == (40, 20)
        assert verso_img.getpixel((0, 0)) == (0, 255, 0)
        assert verso_img.getpixel((39, 19)) == (0, 255, 0)

    with Image.open(tmp_path / "out-1.png") as recto_img:
        assert recto_img.size == (40, 20)
        assert recto_img.getpixel((0, 0)) == (0, 0, 255)
        assert recto_img.getpixel((39, 19)) == (0, 0, 255)


def test_split_images_rejects_invalid_recto_anchor(tmp_path):
    img = create_test_image(tmp_path / "page.jpg")

    with pytest.raises(
        ValueError,
        match="Invalid recto reference 'page.jpg'. Expected FILENAME=FOLIO.",
    ):
        split_images(tmp_path / "book", [img], recto=["page.jpg"])


def test_split_images_force_overwrite(tmp_path):
    img = create_test_image(tmp_path / "original.jpg", color=(10, 10, 10))
    out_prefix = tmp_path / "scan"

    split_images(out_prefix, [img])
    v_path = tmp_path / "scan-0.jpg"
    assert v_path.exists()

    create_test_image(img, color=(99, 99, 99))
    split_images(out_prefix, [img], force=True)

    with Image.open(v_path) as im:
        assert im.getpixel((0, 0)) == (99, 99, 99)
