from __future__ import annotations

import datetime as dt
import urllib.parse
from dataclasses import dataclass

from mopidy.types import Uri


@dataclass
class Station:
    slug: str
    name: str
    loopstream_slug: str | None

    def as_station_uri(self) -> ORFStationUri:
        return ORFStationUri(station=self.slug)


class InvalidORFUriError(TypeError):
    def __init__(self, uri: str):
        super().__init__(f"The URI is not a valid ORFLibraryUri: {uri!r}")


@dataclass
class ORFUri:
    @staticmethod
    def parse(uri: str) -> ORFUri:
        path = urllib.parse.urlsplit(uri).path
        path_parts = path.split("/", 4)

        match path_parts:
            case [""]:
                return ORFRootUri()
            case [station]:
                return ORFStationUri(
                    station=station,
                )
            case [station, "live"]:
                return ORFLiveUri(
                    station=station,
                )
            case [station, day]:
                return ORFArchiveDayUri(
                    station=station,
                    day=dt.datetime.strptime(day, "%Y%m%d").date(),  # noqa: DTZ007
                )
            case [station, day, show_id]:
                return ORFArchiveShowUri(
                    station=station,
                    day=dt.datetime.strptime(day, "%Y%m%d").date(),  # noqa: DTZ007
                    show_id=show_id,
                )
            case [station, day, show_id, item_id]:
                return ORFArchiveItemUri(
                    station=station,
                    day=dt.datetime.strptime(day, "%Y%m%d").date(),  # noqa: DTZ007
                    show_id=show_id,
                    item_id=item_id,
                )
            case _:
                raise InvalidORFUriError(uri)

    @property
    def uri(self) -> Uri:
        return Uri(str(self))


@dataclass
class ORFRootUri(ORFUri):
    def __str__(self) -> str:
        return "orfradio:"


@dataclass
class ORFStationUri(ORFUri):
    station: str

    def __str__(self) -> str:
        return f"orfradio:{self.station}"

    def as_archive_day_uri(self, day: dt.date) -> ORFArchiveDayUri:
        return ORFArchiveDayUri(
            station=self.station,
            day=day,
        )


@dataclass
class ORFLiveUri(ORFUri):
    station: str

    def __str__(self) -> str:
        return f"orfradio:{self.station}/live"


@dataclass
class ORFArchiveDayUri(ORFUri):
    station: str
    day: dt.date

    def __str__(self) -> str:
        return f"orfradio:{self.station}/{self.day:%Y%m%d}"

    def as_archive_show_uri(self, show_id: str) -> ORFArchiveShowUri:
        return ORFArchiveShowUri(
            station=self.station,
            day=self.day,
            show_id=show_id,
        )


@dataclass
class ORFArchiveShowUri(ORFUri):
    station: str
    day: dt.date
    show_id: str

    def __str__(self) -> str:
        return f"orfradio:{self.station}/{self.day:%Y%m%d}/{self.show_id}"

    def as_archive_item_uri(self, item_id: str) -> ORFArchiveItemUri:
        return ORFArchiveItemUri(
            station=self.station,
            day=self.day,
            show_id=self.show_id,
            item_id=item_id,
        )


@dataclass
class ORFArchiveItemUri(ORFUri):
    station: str
    day: dt.date
    show_id: str
    item_id: str

    def __str__(self) -> str:
        return (
            f"orfradio:{self.station}/{self.day:%Y%m%d}/{self.show_id}/{self.item_id}"
        )

    @property
    def loopstream_slug(self) -> str | None:
        from mopidy_orfradio.stations import STATION_BY_SLUG  # noqa: PLC0415

        station = STATION_BY_SLUG.get(self.station)
        if station is None:
            return None
        return station.loopstream_slug
