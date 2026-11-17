"""Shared grid coordinates, copper mass reference and CSV utilities."""

from csv import DictReader, DictWriter


TURNS = range(450, 1101, 25)
AREAS = tuple(10 + index * 0.5 for index in range(41))
COPPER_DENSITY = 8890  # kg/m³, NBS Handbook 100 §1.3.


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(DictReader(handle))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
