class HedabotError(Exception):
    """Base error for hedabot."""
    pass


class VoiceError(HedabotError):
    def __init__(self, message: str, guild_id: str | None = None):
        super().__init__(message)
        self.guild_id = guild_id


class AlreadyConnectedError(VoiceError):
    pass


class NotConnectedError(VoiceError):
    pass


class ConnectionInProgressError(VoiceError):
    pass


class ConnectionFailedError(VoiceError):
    pass
