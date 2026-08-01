from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.items.directories.tmdb.lists_discover import ListDiscover
from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ItemViews
from tmdbhelper.lib.addon.plugin import get_localized, get_language, ADDONPATH
from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS, DISCOVER_SORTBY_MOVIES, DISCOVER_SORTBY_TV
from jurialmunkey.ftools import cached_property


FILTER_CATEGORIES = {
    'en': [
        {'name': 'Movies', 'filter_value': 'movie_filter'},
        {'name': 'TV Shows', 'filter_value': 'tv_filter'},
    ],
    'zh': [
        {'name': '电影', 'filter_value': 'movie_filter'},
        {'name': '电视剧', 'filter_value': 'tv_filter'},
    ],
}

FILTER_YEARS = {
    'en': ['', '2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019',
           '2020s', '2010s', '2000s', '90s', '80s', '70s', '60s', 'Earlier'],
    'zh': ['', '2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019',
           '2020年代', '2010年代', '2000年代', '90年代', '80年代', '70年代', '60年代', '更早'],
}

_YEAR_VALUE_MAP = {
    '2020年代': '2020s', '2010年代': '2010s', '2000年代': '2000s',
    '90年代': '90s', '80年代': '80s', '70年代': '70s', '60年代': '60s',
    '更早': 'Earlier',
}

SORT_NAME_MAP = {
    'en': {},
    'zh': {
        'popularity.asc': '人气 升序', 'popularity.desc': '人气 降序',
        'vote_average.asc': '评分 升序', 'vote_average.desc': '评分 降序',
        'vote_count.asc': '评分数 升序', 'vote_count.desc': '评分数 降序',
        'primary_release_date.asc': '上映日期 升序', 'primary_release_date.desc': '上映日期 降序',
        'first_air_date.asc': '首播日期 升序', 'first_air_date.desc': '首播日期 降序',
        'original_title.asc': '片名 升序', 'original_title.desc': '片名 降序',
        'original_name.asc': '片名 升序', 'original_name.desc': '片名 降序',
        'title.asc': '标题 升序', 'title.desc': '标题 降序',
        'name.asc': '名称 升序', 'name.desc': '名称 降序',
        'revenue.asc': '票房 升序', 'revenue.desc': '票房 降序',
    },
}

REGION_NAME_MAP = {
    'zh': {
        'CN': '中国大陆', 'HK': '中国香港', 'TW': '中国台湾',
        'US': '美国', 'GB': '英国', 'JP': '日本', 'KR': '韩国',
        'FR': '法国', 'DE': '德国', 'ES': '西班牙', 'IT': '意大利',
        'IN': '印度', 'AU': '澳大利亚', 'CA': '加拿大', 'BR': '巴西',
        'RU': '俄罗斯', 'TH': '泰国', 'MX': '墨西哥', 'NL': '荷兰',
        'SE': '瑞典', 'PL': '波兰', 'DK': '丹麦', 'NO': '挪威',
        'FI': '芬兰', 'BE': '比利时', 'AT': '奥地利', 'CH': '瑞士',
        'PT': '葡萄牙', 'IE': '爱尔兰', 'NZ': '新西兰', 'SG': '新加坡',
        'MY': '马来西亚', 'PH': '菲律宾', 'ID': '印度尼西亚', 'TR': '土耳其',
        'SA': '沙特阿拉伯', 'AE': '阿联酋', 'IL': '以色列', 'ZA': '南非',
        'AR': '阿根廷', 'CO': '哥伦比亚', 'CL': '智利', 'PE': '秘鲁',
        'CZ': '捷克', 'HU': '匈牙利', 'RO': '罗马尼亚', 'GR': '希腊',
        'UA': '乌克兰', 'VN': '越南', 'PK': '巴基斯坦', 'BD': '孟加拉',
    },
}

_REGION_ORDER_ZH = ['CN', 'HK', 'TW', 'US', 'GB', 'JP', 'KR', 'FR', 'DE', 'ES', 'IT',
                     'IN', 'AU', 'CA', 'BR', 'RU', 'TH', 'MX', 'NL', 'SE', 'PL',
                     'DK', 'NO', 'FI', 'BE', 'AT', 'CH', 'PT', 'IE', 'NZ', 'SG']


def _get_lang_key():
    lang = get_language()
    return 'zh' if lang and lang.startswith('zh') else 'en'


class ItemFilter(ItemViews):
    item_icon_default = f'{ADDONPATH}/resources/icons/themoviedb/folder.png'
    item_mediatype = 'source'

    def __init__(self, name, filter_value, tmdb_id='', **kwargs):
        self.label = name if name else 'All'
        self.tmdb_id = tmdb_id or filter_value
        self.filter_value = filter_value

    @cached_property
    def infoproperties(self):
        return {'filter_value': self.filter_value}

    @cached_property
    def params(self):
        return {}


class ItemFilterCategory(ItemFilter):
    @cached_property
    def params(self):
        return {
            'info': 'filter_list',
            'cat_id': self.filter_value,
        }


class ListFilterCategories(ContainerDirectory):
    def get_items(self, **kwargs):
        lang = _get_lang_key()
        items = [ItemFilterCategory(c['name'], c['filter_value']).item for c in FILTER_CATEGORIES.get(lang, FILTER_CATEGORIES['en'])]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterGenres(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        tmdb_type = 'movie' if cat_id == 'movie_filter' else 'tv'
        genres = self.query_database.get_genres(tmdb_type)
        items = [ItemFilter(name, name, tmdb_id=gid).item for name, gid in genres.items()]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterRegions(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        lang = _get_lang_key()
        name_map = REGION_NAME_MAP.get(lang, {})
        if lang == 'zh':
            ordered_ids = _REGION_ORDER_ZH
            region_dict = {r['id']: r for r in DISCOVER_REGIONS}
            result = []
            for rid in ordered_ids:
                r = region_dict.get(rid)
                if r:
                    name = name_map.get(rid, r['name'])
                    result.append(ItemFilter(name, r['id']).item)
            items = result
        else:
            items = [ItemFilter(r['name'], r['id']).item for r in DISCOVER_REGIONS]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterYears(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        lang = _get_lang_key()
        years = FILTER_YEARS.get(lang, FILTER_YEARS['en'])
        items = []
        for y in years:
            fv = _YEAR_VALUE_MAP.get(y, y)
            items.append(ItemFilter(y, fv).item)
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterSorts(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        lang = _get_lang_key()
        sorts = DISCOVER_SORTBY_MOVIES if cat_id == 'movie_filter' else DISCOVER_SORTBY_TV
        name_map = SORT_NAME_MAP.get(lang, {})
        items = [ItemFilter(name_map.get(s['id'], s['name']), s['id']).item for s in sorts]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


COMMON_PROVIDERS = {
    'en': {'Netflix', 'Amazon Prime Video', 'Disney Plus', 'Apple TV Plus',
           'Hulu', 'HBO Max', 'Paramount Plus', 'Peacock', 'YouTube Premium',
           'Crunchyroll', 'Funimation', 'MUBI', 'Shudder', 'BritBox',
           'iQIYI', 'Tencent Video', 'Youku', 'Bilibili', 'Mango TV',
           'WeTV', 'VIU', 'Hotstar', 'JioCinema', 'Stan', 'Binge'},
    'zh': {'Netflix', 'Amazon Prime Video', 'Disney Plus', 'Apple TV Plus',
           'Hulu', 'HBO Max', 'Crunchyroll',
           '爱奇艺', '腾讯视频', '优酷', '哔哩哔哩', '芒果TV', '西瓜视频',
           '搜狐视频', '乐视', '咪咕视频', '华数TV', '百视通', 'CCTV'},
}


class ListFilterPlatforms(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        tmdb_type = 'movie' if cat_id == 'movie_filter' else 'tv'
        watch_region = kwargs.get('watch_region', 'US')
        data = self.tmdb_api.get_response_json(
            'watch/providers', tmdb_type, params={'watch_region': watch_region}) or {}
        providers = data.get('results', [])
        lang = _get_lang_key()
        allowed = COMMON_PROVIDERS.get(lang, COMMON_PROVIDERS['en'])
        if lang == 'zh':
            allowed = COMMON_PROVIDERS['en'] | COMMON_PROVIDERS['zh']
        providers = [p for p in providers if p.get('provider_name', '') in allowed]
        items = [ItemFilter(p.get('provider_name', ''), str(p.get('provider_id', '')), tmdb_id=p.get('provider_id', '')).item for p in providers]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterList(ListDiscover):
    def get_items(self, cat_id='', genre='', region='', year='', platform='', sort='popularity.desc', **kwargs):
        tmdb_type = 'movie' if cat_id == 'movie_filter' else 'tv'
        discover_params = {}
        if genre:
            genre_id = self.query_database.genres.get(genre)
            if genre_id:
                discover_params['with_genres'] = str(genre_id)
        if region:
            discover_params['with_origin_country'] = region
        if year:
            if tmdb_type == 'movie':
                if len(year) == 4 and year.isdigit():
                    discover_params['primary_release_year'] = year
                elif year.endswith('s'):
                    decade = year.rstrip('s')
                    if decade.isdigit():
                        dec_int = int(decade)
                        discover_params['primary_release_date.gte'] = f'{dec_int}-01-01'
                        discover_params['primary_release_date.lte'] = f'{dec_int + 9}-12-31'
                elif year == 'Earlier':
                    discover_params['primary_release_date.lte'] = '1959-12-31'
            else:
                if len(year) == 4 and year.isdigit():
                    discover_params['first_air_date_year'] = year
                elif year.endswith('s'):
                    decade = year.rstrip('s')
                    if decade.isdigit():
                        dec_int = int(decade)
                        discover_params['first_air_date.gte'] = f'{dec_int}-01-01'
                        discover_params['first_air_date.lte'] = f'{dec_int + 9}-12-31'
                elif year == 'Earlier':
                    discover_params['first_air_date.lte'] = '1959-12-31'
        if platform:
            discover_params['with_watch_providers'] = platform
            discover_params['watch_region'] = region if region else 'US'
        if sort:
            discover_params['sort_by'] = sort
        discover_params['with_id'] = 'True'
        return super().get_items(tmdb_type=tmdb_type, **discover_params)
