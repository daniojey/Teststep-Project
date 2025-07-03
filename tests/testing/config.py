from dataclasses import dataclass
from typing import Optional

@dataclass
class TestConfig:
    """Глобальный конфиг для фабрики и тестов"""
    all_tests: int = 4
    test_reviews: bool = False
    test_results: bool = False
    random_data: bool = True


    # TODO Доп параметры пока не рабочие 
    test_mode: str = 'development'
    debug_mode: bool = False
    custom_seed: Optional[int] = None



DEFAULT_CONFIG = TestConfig()


PRODUCTION_CONFIG = TestConfig(
    all_tests=50,
    test_reviews=False,
    test_results=True,
    random_data=True,
    test_mode="production",
    debug_mode=False
)

STAGING_CONFIG = TestConfig(
    all_tests=25,
    test_reviews=True,
    test_results=True,
    random_data=False,
    test_mode="staging",
    debug_mode=True
)

СURRENT_CONFIG = DEFAULT_CONFIG