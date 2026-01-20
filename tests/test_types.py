import datetime as dt

import pytest

from mopidy_orfradio.types import (
    ORFArchiveDayUri,
    ORFArchiveItemUri,
    ORFArchiveShowUri,
    ORFLiveUri,
    ORFRootUri,
    ORFStationUri,
    ORFUri,
)


@pytest.mark.parametrize(
    ("uri", "expected"),
    [
        (
            "orfradio:",
            ORFRootUri(),
        ),
        (
            "orfradio:oe1",
            ORFStationUri(station="oe1"),
        ),
        (
            "orfradio:oe1/live",
            ORFLiveUri(station="oe1"),
        ),
        (
            "orfradio:oe1/20140914",
            ORFArchiveDayUri(station="oe1", day=dt.date(2014, 9, 14)),
        ),
        (
            "orfradio:oe1/20140914/382176",
            ORFArchiveShowUri(
                station="oe1",
                day=dt.date(2014, 9, 14),
                show_id="382176",
            ),
        ),
        (
            "orfradio:oe1/20140914/382176/1633035600-1633039200",
            ORFArchiveItemUri(
                station="oe1",
                day=dt.date(2014, 9, 14),
                show_id="382176",
                item_id="1633035600-1633039200",
            ),
        ),
    ],
)
def test_orf_uri_parse(uri: str, expected: ORFUri):
    result = ORFUri.parse(uri)
    assert result == expected
    assert str(result) == uri
