"""
Backward-compatibility forwarder to app.config
"""

from app.config import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    get_config,
)

__all__ = [
    "Config",
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
    "get_config",
]
