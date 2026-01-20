import datetime as dt
import unittest
from unittest.mock import Mock

from mopidy.models import Ref
from mopidy.types import Uri

from mopidy_orfradio import TZ
from mopidy_orfradio.library import ORFLibraryProvider
from mopidy_orfradio.types import (
    ORFArchiveDayUri,
    ORFArchiveShowUri,
    ORFLiveUri,
    ORFRootUri,
    ORFStationUri,
)


class ORFLibraryProviderTest(unittest.TestCase):
    def setUp(self):
        self.client_mock = Mock()
        self.client_mock.get_day = Mock(
            return_value=[
                {"id": "1", "time": "01:00", "title": "Item1"},
                {"id": "2", "time": "02:00", "title": "Item2"},
                {"id": "3", "time": "03:00", "title": "Item3"},
            ]
        )
        self.client_mock.get_show = Mock(
            return_value=[
                {"id": "1", "time": "01:00", "title": "Item1"},
                {"id": "2", "time": "02:00", "title": "Item2"},
                {"id": "3", "time": "03:00", "title": "Item3"},
            ]
        )
        self.client_mock.get_item = Mock(
            return_value={"id": "1", "time": "01:00", "title": "Item1"}
        )
        self.backend = Mock()
        self.backend.config = {
            "orfradio": {"stations": ["oe1", "fm4"], "afterhours": False}
        }

        self.library = ORFLibraryProvider(self.backend, client=self.client_mock)

    def test_browse_invalid_uri(self):
        uri = "foo:bar"
        result = self.library.browse(Uri(uri))
        assert result == []

    def test_browse_unbrowsable_uri(self):
        uri = ORFLiveUri(station="oe1").uri
        result = self.library.browse(uri)
        assert result == []

    def test_browse_root(self):
        uri = ORFRootUri().uri
        result = self.library.browse(uri)
        assert len(result) == 2

    def test_browse_station(self):
        uri = ORFStationUri(station="oe1").uri
        result = self.library.browse(uri)
        assert len(result) == 9
        assert result[0].type == Ref.TRACK
        assert result[0].uri == "orfradio:oe1/live"
        assert result[0].name == "Ö1 Live"
        assert result[1].type == Ref.DIRECTORY
        today = dt.datetime.now(tz=TZ).strftime("%Y%m%d")
        assert result[1].uri == f"orfradio:oe1/{today}"
        labeltext = dt.datetime.now(tz=TZ).strftime("%Y-%m-%d %A")
        assert result[1].name == labeltext

    def test_browse_archive_day(self):
        uri = ORFArchiveDayUri(
            station="oe1",
            day=dt.date(2014, 9, 14),
        ).uri
        result = self.library.browse(uri)
        self.client_mock.get_day.assert_called_once_with(
            station="oe1",
            day=dt.date(2014, 9, 14),
        )
        assert len(result) == 3
        assert result[0].type == Ref.DIRECTORY
        assert result[0].uri == "orfradio:oe1/20140914/1"
        assert result[0].name == "01:00: Item1"

    def test_lookup_invalid_uri(self):
        uri = Uri("foo:bar")
        result = self.library.lookup(uri)
        assert result == []

    def test_lookup_unlookable_uri(self):
        uri = ORFRootUri().uri
        result = self.library.lookup(uri)
        assert result == []

    def test_lookup_live(self):
        uri = ORFLiveUri(station="oe1").uri
        result = self.library.lookup(uri)
        assert len(result) == 1
        assert result[0].uri == uri
        assert result[0].name == "Live"

    def test_lookup_archive_day(self):
        uri = ORFArchiveDayUri(
            station="oe1",
            day=dt.date(2014, 9, 14),
        ).uri
        result = self.library.lookup(uri)
        self.client_mock.get_day.assert_called_once_with(
            station="oe1",
            day=dt.date(2014, 9, 14),
        )
        assert len(result) == 3
        assert result[0].uri == "orfradio:oe1/20140914/1"
        assert result[0].name == "01:00: Item1"

    def test_lookup_archive_show(self):
        uri = ORFArchiveShowUri(
            station="oe1",
            day=dt.date(2014, 9, 14),
            show_id="1234567",
        ).uri
        result = self.library.lookup(uri)
        self.client_mock.get_show.assert_called_once_with(
            station="oe1",
            day=dt.date(2014, 9, 14),
            show_id="1234567",
        )
        assert len(result) == 3
        # this test might be wrong:
        assert result[0].uri == "orfradio:oe1/20140914/1234567/1"
        assert result[0].name == "01:00: Item1"
