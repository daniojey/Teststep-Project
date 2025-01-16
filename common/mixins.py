from django.core.cache import cache


class CacheMixin:
    def set_get_cache(self, query, cache_name, chache_time):
        data = cache.get(cache_name)

        if not data:
            data = query
            # print(f"Создание кэша {data}")
            cache.set(cache_name, data, chache_time)

        # print(f"Кэш получен {data}")
        return data