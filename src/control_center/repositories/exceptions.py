"""Safe repository exceptions that never include credentials."""


class RepositoryError(RuntimeError):
    """Base class for persistence failures safe to show at the app boundary."""


class RepositoryConfigurationError(RepositoryError):
    """Required repository configuration is missing or invalid."""


class RepositoryUnavailableError(RepositoryError):
    """The configured persistence provider could not complete an operation."""

