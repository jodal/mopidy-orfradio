from __future__ import annotations

import datetime as dt
import logging
import re
from typing import TYPE_CHECKING, Any, override

from mopidy import backend
from mopidy.models import Album, Artist, Ref, Track

from mopidy_orfradio import TZ
from mopidy_orfradio.client import ORFClient
from mopidy_orfradio.stations import STATION_BY_SLUG, STATIONS
from mopidy_orfradio.types import (
    InvalidORFUriError,
    ORFArchiveDayUri,
    ORFArchiveItemUri,
    ORFArchiveShowUri,
    ORFLiveUri,
    ORFRootUri,
    ORFStationUri,
    ORFUri,
)

if TYPE_CHECKING:
    from mopidy.types import Uri

    from mopidy_orfradio.backend import ORFBackend

logger = logging.getLogger(__name__)


class ORFLibraryProvider(backend.LibraryProvider):
    backend: ORFBackend

    root_directory = Ref.directory(
        uri=ORFRootUri().uri,
        name="ORF Radio",
    )

    def __init__(
        self,
        backend: ORFBackend,
        client: ORFClient | None = None,
    ) -> None:
        super().__init__(backend)
        self.client = client or ORFClient(backend=self.backend)
        self.root = [
            Ref.directory(
                uri=station.as_station_uri().uri,
                name=station.name,
            )
            for station in STATIONS
            if station.slug in self.backend.config["orfradio"]["stations"]
        ]

    @override
    def browse(self, uri: Uri) -> list[Ref]:
        try:
            orf_uri = ORFUri.parse(uri)
        except InvalidORFUriError as e:
            logger.error(e)  # noqa: TRY400
            return []

        match orf_uri:
            case ORFRootUri():
                return self.root
            case ORFStationUri():
                return self._browse_station(orf_uri)
            case ORFArchiveDayUri():
                return self._browse_day(orf_uri)
            case ORFArchiveShowUri():
                return self._browse_show(orf_uri)
            case _:
                logger.warning(
                    "ORFLibraryProvider.browse called with URI "
                    f"that does not support browsing: {uri!r}"
                )
                return []

    def _browse_station(self, orf_uri: ORFStationUri) -> list[Ref]:
        station = STATION_BY_SLUG.get(orf_uri.station)
        if station is None:
            return []

        live = Ref.track(
            uri=ORFLiveUri(station=station.slug).uri,
            name=f"{station.name} Live",
        )
        if station.loopstream_slug is None:
            return [live]

        last_week = [
            dt.datetime.now(tz=TZ).date() - dt.timedelta(days=d) for d in range(8)
        ]
        archive = [
            Ref.directory(
                uri=orf_uri.as_archive_day_uri(day).uri,
                name=f"{day:%Y-%m-%d %A}",
            )
            for day in last_week
        ]
        return [live, *archive]

    def _get_track_title(
        self,
        item: dict[str, Any],
        *,
        afterhours: bool = False,
    ) -> str:
        time = item["time"]
        if afterhours and self.backend.config["orfradio"]["afterhours"]:
            time = re.sub(r"^0([0-4]:)", r"O\1", time)
        return "{}: {}".format(time, item["title"])

    def _browse_day(self, orf_uri: ORFArchiveDayUri) -> list[Ref]:
        return [
            Ref.directory(
                uri=orf_uri.as_archive_show_uri(show["id"]).uri,
                name=self._get_track_title(show, afterhours=True),
            )
            for show in self.client.get_day(
                station=orf_uri.station,
                day=orf_uri.day,
            )
        ]

    def _browse_show(self, orf_uri: ORFArchiveShowUri) -> list[Ref]:
        return [
            Ref.track(
                uri=orf_uri.as_archive_item_uri(item["id"]).uri,
                name=self._get_track_title(item),
            )
            for item in self.client.get_show(
                station=orf_uri.station,
                day=orf_uri.day,
                show_id=orf_uri.show_id,
            )
        ]

    @override
    def lookup(self, uri: Uri) -> list[Track]:  # noqa: PLR0911
        try:
            orf_uri = ORFUri.parse(uri)
        except InvalidORFUriError as e:
            logger.error(e)  # noqa: TRY400
            return []

        match orf_uri:
            case ORFLiveUri():
                return [Track(uri=orf_uri.uri, name="Live")]
            case ORFStationUri():
                return self._lookup_from_browse(self._browse_station(orf_uri))
            case ORFArchiveDayUri():
                return self._lookup_from_browse(self._browse_day(orf_uri))
            case ORFArchiveShowUri():
                return self._lookup_from_browse(self._browse_show(orf_uri))
            case ORFArchiveItemUri():
                return self._lookup_item(orf_uri)
            case _:
                logger.warning(
                    "ORFLibraryProvider.lookup called with URI "
                    f"that does not support lookup: {uri!r}"
                )
                return []

    def _lookup_from_browse(self, refs: list[Ref]) -> list[Track]:
        return [Track(uri=ref.uri, name=ref.name) for ref in refs]

    def _lookup_item(self, orf_uri: ORFArchiveItemUri) -> list[Track]:
        item = self.client.get_item(
            station=orf_uri.station,
            day=orf_uri.day,
            show_id=orf_uri.show_id,
            item_id=orf_uri.item_id,
        )
        return [
            Track(
                uri=orf_uri.uri,
                artists=frozenset([Artist(name=item["artist"])]),
                length=item["length"],
                album=Album(name=f"{item['show_long']} ({item['show_date']})"),
                genre=item["type"],
                name=item["title"],
            )
        ]

    @override
    def refresh(self, uri: Uri | None = None) -> None:
        self.client.refresh()
