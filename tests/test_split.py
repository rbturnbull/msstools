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
        ],
    )
    assert result.exit_code == 0

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

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "out"),
            str(img),
            "--rtl",
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "out-0.jpg").exists()
    assert (tmp_path / "out-1.jpg").exists()


def test_split_images_zero_pads_output_indexes(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(10)
    ]

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "out"),
            *[str(image) for image in images],
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "out-00.jpg").exists()
    assert (tmp_path / "out-01.jpg").exists()
    assert (tmp_path / "out-18.jpg").exists()
    assert (tmp_path / "out-19.jpg").exists()


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
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "book-0.jpg").exists()
    assert (tmp_path / "book-1.jpg").exists()
    assert (tmp_path / "book-2.jpg").exists()


def test_split_images_recto_anchor(tmp_path):
    images = [
        create_test_image(tmp_path / f"page{i}.jpg", color=(i, i, i))
        for i in range(3)
    ]

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "book"),
            *[str(image) for image in images],
            "--recto",
            "page1.jpg=49",
        ],
    )
    assert result.exit_code == 0

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

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "book"),
            *[str(image) for image in images],
            "--skip",
            "3",
            "--recto",
            "page3.jpg=49",
        ],
    )
    assert result.exit_code == 0

    assert (tmp_path / "book-0.jpg").exists()
    assert (tmp_path / "book-1.jpg").exists()
    assert (tmp_path / "book-2.jpg").exists()
    assert (tmp_path / "book-3.jpg").exists()
    assert (tmp_path / "book-4-49r.jpg").exists()
    assert (tmp_path / "book-5-49v.jpg").exists()
    assert (tmp_path / "book-6-50r.jpg").exists()


def test_split_images_force_overwrite(tmp_path):
    img = create_test_image(tmp_path / "original.jpg", color=(10, 10, 10))
    out_prefix = tmp_path / "scan"

    runner.invoke(
        app,
        [
            "split-images",
            str(out_prefix),
            str(img),
        ],
    )
    v_path = tmp_path / "scan-0.jpg"
    assert v_path.exists()

    create_test_image(img, color=(99, 99, 99))
    runner.invoke(
        app,
        [
            "split-images",
            str(out_prefix),
            str(img),
            "--force",
        ],
    )
    with Image.open(v_path) as im:
        assert im.getpixel((0, 0)) == (99, 99, 99)
