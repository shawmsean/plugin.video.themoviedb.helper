from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.items.directories.tmdb.lists_discover import ListDiscover
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS, DISCOVER_SORTBY_MOVIES, DISCOVER_SORTBY_TV
from jurialmunkey.ftools import cached_property
import xbmcgui


FILTER_CATEGORIES = [
    {'name': 'Movies', 'filter_value': 'movie_filter'},
    {'name': 'TV Shows', 'filter_value': 'tv_filter'},
]

FILTER_YEARS = [
    '', '2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019',
    '2020s', '2010s', '2000s', '90s', '80s', '70s', '60s', 'Earlier',
]

FILTER_SORTS = [
    {'name': 'Popularity', 'value': 'popularity.desc'},
    {'name': 'Rating', 'value': 'vote_average.desc'},
    {'name': 'Release Date', 'value': 'primary_release_date.desc'},
    {'name': 'Title', 'value': 'original_title.asc'},
]


def _add_filter_item(name, filter_value, tmdb_id=''):
    li = xbmcgui.ListItem(name if name else 'All', offscreen=True)
    li.setProperty('filter_value', filter_value)
    if tmdb_id:
        li.setProperty('filter_tmdb_id', str(tmdb_id))
    return ('', li, True)


class ListFilterCategories(ContainerDirectory):
    def get_items(self, **kwargs):
        xbmcgui.Window(10000).setProperty('filter_browse_plugin', 'plugin.video.themoviedb.helper')
        items = [_add_filter_item(c['name'], c['filter_value']) for c in FILTER_CATEGORIES]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterGenres(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        tmdb_type = 'movie' if cat_id == 'movie_filter' else 'tv'
        genres = self.query_database.get_genres(tmdb_type)
        items = [_add_filter_item(name, name, tmdb_id=gid) for name, gid in genres.items()]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterRegions(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        items = [_add_filter_item(r['name'], r['id']) for r in DISCOVER_REGIONS]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterYears(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        items = [_add_filter_item(y, y) for y in FILTER_YEARS]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterSorts(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        sorts = DISCOVER_SORTBY_MOVIES if cat_id == 'movie_filter' else DISCOVER_SORTBY_TV
        items = [_add_filter_item(s['name'], s['id']) for s in sorts]
        self.container_content = 'sources'
        self.kodi_db = None
        return items


class ListFilterPlatforms(ContainerDirectory):
    def get_items(self, cat_id='', **kwargs):
        tmdb_type = 'movie' if cat_id == 'movie_filter' else 'tv'
        watch_region = kwargs.get('watch_region', 'US')
        data = self.tmdb_api.get_response_json(
            'watch/providers', tmdb_type, params={'watch_region': watch_region}) or {}
        providers = data.get('results', [])
        items = [_add_filter_item(p.get('provider_name', ''), str(p.get('provider_id', '')), tmdb_id=p.get('provider_id', '')) for p in providers]
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