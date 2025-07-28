from gettsim import GERMANY_ROOT


def test_germany_root():
    if not GERMANY_ROOT.is_dir():
        raise NotADirectoryError
