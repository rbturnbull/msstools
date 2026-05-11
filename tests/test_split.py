from pathlib import Path
from PIL import Image
from typer.testing import CliRunner
from msstools.main import app

runner = CliRunner()


def create_test_image(path: Path, width=200, height=100, color=(255, 0, 0)):
    img = Image.new("RGB", (width, height), color=color)
    img.save(path)
    return path


def test_split_images_ltr(tmp_path):
    img1 = create_test_image(tmp_path / "page1.jpg")
    img2 = create_test_image(tmp_path / "page2.jpg", color=(0, 255, 0))

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "output"),
            str(img1),
            str(img2),
            "--overlap",
            "20",
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    files = list(tmp_path.glob("output-*"))
    assert len(files) == 4  # 2 pages → 2 verso and 2 recto
    for file in files:
        with Image.open(file) as img:
            assert img.height == 100
            assert img.width > 100  # overlap included


def test_split_images_rtl(tmp_path):
    img = create_test_image(tmp_path / "page.jpg", color=(0, 0, 255))

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "out"),
            str(img),
            "--rtl",
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    v_path = tmp_path / "out-f0v.jpg"
    r_path = tmp_path / "out-f1r.jpg"
    assert v_path.exists()
    assert r_path.exists()


def test_split_images_rtl_no_recto_verso(tmp_path):
    img = create_test_image(tmp_path / "page.jpg", color=(0, 0, 255))

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "out"),
            str(img),
            str(img),
            "--margin-left",
            "10",
            "--rtl",
            "--no-recto-verso",
        ],
    )
    assert result.exit_code == 0

    for i in range(0, 4):
        path = tmp_path / f"out-f{i}.jpg"
        assert path.exists()


def test_split_images_rtl_start155(tmp_path):
    img = create_test_image(tmp_path / "page.jpg", color=(0, 0, 255))

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "out"),
            str(img),
            "--rtl",
            "--start",
            "155",
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    v_path = tmp_path / "out-f155v.jpg"
    r_path = tmp_path / "out-f156r.jpg"
    assert v_path.exists()
    assert r_path.exists()


def test_split_images_zero_pads_page_numbers(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i)) for i in range(10)
    ]

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "out"),
            *[str(image) for image in images],
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "out-f00v.jpg").exists()
    assert (tmp_path / "out-f01r.jpg").exists()
    assert (tmp_path / "out-f09v.jpg").exists()
    assert (tmp_path / "out-f10r.jpg").exists()


def test_split_images_skip(tmp_path):
    img1 = create_test_image(tmp_path / "skip1.jpg", color=(123, 123, 123))
    img2 = create_test_image(tmp_path / "split1.jpg", color=(234, 234, 234))

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "book"),
            str(img1),
            str(img2),
            "--skip",
            "1",
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    # First image should be copied directly
    assert (tmp_path / "book--0.jpg").exists()
    # Second image should be split into verso and recto
    assert (tmp_path / "book-f0v.jpg").exists()
    assert (tmp_path / "book-f1r.jpg").exists()


def test_split_images_skip_does_not_advance_start_with_padding(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(13)
    ]

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "book"),
            *[str(image) for image in images],
            "--skip",
            "3",
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "book--00.jpg").exists()
    assert (tmp_path / "book--01.jpg").exists()
    assert (tmp_path / "book--02.jpg").exists()
    assert (tmp_path / "book-f00v.jpg").exists()
    assert (tmp_path / "book-f01r.jpg").exists()


def test_split_images_duplicate_folio_labels(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(4)
    ]

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "book"),
            *[str(image) for image in images],
            "--start",
            "44",
            "--duplicates",
            "46",
            "--recto-verso",
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "book-f46rA.jpg").exists()
    assert (tmp_path / "book-f46vA.jpg").exists()
    assert (tmp_path / "book-f46rB.jpg").exists()
    assert (tmp_path / "book-f46vB.jpg").exists()
    assert (tmp_path / "book-f47r.jpg").exists()


def test_split_images_force_overwrite(tmp_path):
    img = create_test_image(tmp_path / "original.jpg", color=(10, 10, 10))
    out_prefix = tmp_path / "scan"

    # First run
    runner.invoke(
        app,
        [
            "split-images",
            str(out_prefix),
            str(img),
            "--recto-verso",
        ],
    )
    v_path = tmp_path / "scan-f0v.jpg"
    r_path = tmp_path / "scan-f1r.jpg"
    assert v_path.exists()

    # Overwrite with different color
    create_test_image(img, color=(99, 99, 99))
    runner.invoke(
        app,
        [
            "split-images",
            str(out_prefix),
            str(img),
            "--recto-verso",
            "--force",
        ],
    )
    with Image.open(v_path) as im:
        assert im.getpixel((0, 0)) == (99, 99, 99)
