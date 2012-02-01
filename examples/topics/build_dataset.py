"""Collect examples matching the extracted taxonomy topics"""
from os.path import sep, join
import dbpediakit.postgres as pg

FOLDER = __file__.rsplit(sep, 1)[0]

pg.check_run_if_undef(join(FOLDER, "build_dataset.sql"))
