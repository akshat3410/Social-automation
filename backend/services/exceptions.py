class SocialEngineError(Exception):
    pass

class NotFoundError(SocialEngineError):
    pass

class UnauthorizedError(SocialEngineError):
    pass

class DuplicateContentError(SocialEngineError):
    pass

class QualityGateFailedError(SocialEngineError):
    pass

class PublishingError(SocialEngineError):
    pass

class ProviderError(SocialEngineError):
    pass

class RateLimitError(SocialEngineError):
    pass
