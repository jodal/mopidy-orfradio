import logging
from typing import ClassVar, cast

import pykka
from mopidy import backend
from mopidy import config as config_lib
from mopidy.audio import AudioProxy
from mopidy.types import UriScheme

from mopidy_orfradio.library import ORFLibraryProvider
from mopidy_orfradio.playback import ORFPlaybackProvider

logger = logging.getLogger(__name__)


class ORFBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes: ClassVar[list[UriScheme]] = [UriScheme("orfradio")]
    config: config_lib.ConfigDict

    def __init__(
        self,
        config: config_lib.Config,
        audio: AudioProxy,
    ) -> None:
        super().__init__()

        self.config = cast("config_lib.ConfigDict", config)

        self.library = ORFLibraryProvider(backend=self)
        self.playback = ORFPlaybackProvider(audio=audio, backend=self)
