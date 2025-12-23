from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from mopidy import backend

from mopidy_orfradio.client import ORFClient
from mopidy_orfradio.library import InvalidORFUriError
from mopidy_orfradio.types import ORFArchiveItemUri, ORFLiveUri, ORFUri

if TYPE_CHECKING:
    from mopidy.audio import AudioProxy
    from mopidy.types import Uri

    from mopidy_orfradio.backend import ORFBackend

logger = logging.getLogger(__name__)


class ORFPlaybackProvider(backend.PlaybackProvider):
    backend: ORFBackend
    client: ORFClient

    def __init__(
        self,
        audio: AudioProxy,
        backend: ORFBackend,
        client: ORFClient | None = None,
    ):
        super().__init__(audio, backend)
        self.client = client or ORFClient(backend=self.backend)

    @override
    def translate_uri(self, uri: Uri) -> Uri | None:
        try:
            orf_uri = ORFUri.parse(uri)
        except InvalidORFUriError:
            return None

        match orf_uri:
            case ORFLiveUri():
                return self.client.get_live_url(
                    station=orf_uri.station,
                )
            case ORFArchiveItemUri():
                return self.client.get_item_url(
                    station=orf_uri.station,
                    day=orf_uri.day,
                    show_id=orf_uri.show_id,
                    item_id=orf_uri.item_id,
                    loopstream_slug=orf_uri.loopstream_slug,
                )
            case _:
                return None
