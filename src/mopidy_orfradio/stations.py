from mopidy_orfradio.types import Station

STATIONS = [
    Station(slug="oe1", name="Ö1", loopstream_slug="oe1"),
    Station(slug="oe3", name="Ö3", loopstream_slug="oe3"),
    Station(slug="fm4", name="FM4", loopstream_slug="fm4"),
    Station(slug="campus", name="Ö1 Campus", loopstream_slug=None),
    Station(slug="bgl", name="Radio Burgenland", loopstream_slug="oe2b"),
    Station(slug="ktn", name="Radio Kärnten", loopstream_slug="oe2k"),
    Station(slug="noe", name="Radio Niederösterreich", loopstream_slug="oe2n"),
    Station(slug="ooe", name="Radio Oberösterreich", loopstream_slug="oe2o"),
    Station(slug="sbg", name="Radio Salzburg", loopstream_slug="oe2s"),
    Station(slug="stm", name="Radio Steiermark", loopstream_slug="oe2st"),
    Station(slug="tir", name="Radio Tirol", loopstream_slug="oe2t"),
    Station(slug="vbg", name="Radio Vorarlberg", loopstream_slug="oe2v"),
    Station(slug="wie", name="Radio Wien", loopstream_slug="oe2w"),
    Station(slug="slo", name="ORF Slovenski spored", loopstream_slug=None),
]
STATION_BY_SLUG = {station.slug: station for station in STATIONS}
