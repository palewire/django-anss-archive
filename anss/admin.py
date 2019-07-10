from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from .models import Feed, FeedEarthquake


@admin.register(FeedEarthquake)
class FeedEarthquakeAdmin(GeoModelAdmin):
    point_zoom = 5
    list_display = (
        "usgs_id",
        "title",
        "get_time_datetime",
        "get_updated_datetime",
        "feed",
    )
    readonly_fields = (
        "feed",
        "url",
        "detail",
        'usgs_id',
        'title',
        'net',
        'sources',
        'code',
        'ids',
        'type',
        'mag',
        'magType',
        'mmi',
        'felt',
        'cdi',
        'tsunami',
        'sig',
        'alert',
        'place',
        'depth',
        'get_time_datetime',
        'time',
        'tz',
        'updated',
        'nst',
        'dmin',
        'gap',
        'rms',
        'status',
        'types',
    )
    list_filter = (
        "alert",
        "status",
        "tsunami",
        "magType",
        "type"
    )
    search_fields = ("usgs_id", "title", "ids")
    fieldsets = (
        (
            'Identifiers',
            {
                'fields': (
                    'usgs_id',
                    'title',
                    'net',
                    'sources',
                    'code',
                    'ids'
                )
            }
        ),
        (
            'Where?',
            {
                'fields': (
                    'place',
                    'point',
                    'depth'
                ),
                'description': 'Where the event happened'
            }
        ),
        (
            'When',
            {
                'fields': (
                    'get_time_datetime',
                    'time',
                    'tz'
                ),
                'description': 'When the event happened'
            }
        ),
        (
            'What?',
            {
                'fields': (
                    'type',
                    'mag',
                    'magType',
                    'mmi',
                    'felt',
                    'cdi',
                    'tsunami',
                    'sig',
                    'alert'
                ),
                'description': 'The size of the event'
            }
        ),
        (
            'Reference',
            {
                'fields': (
                    'feed',
                    'url',
                    'detail'
                ),
                'description': "Where the data came from"
            }
        ),
        (
            'Review',
            {
                'fields': (
                    'updated',
                    'nst',
                    'dmin',
                    'gap',
                    'rms',
                    'status',
                    'types',
                ),
                'description': "More about how the data were calculated"
            }
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, *args):
        return False


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = (
        "archived_datetime",
        "format",
        "type",
        "timeframe",
        "get_generated_datetime",
        "api",
        "count",
        "status",
        "get_lag"
    )
    list_filter = ("format", "type", "timeframe", "api", "status")
    date_hierarchy = "archived_datetime"
    fieldsets = (
        (
            'The feed',
            {
                'fields': (
                    'title',
                    'url',
                    'api',
                    'format',
                    'type',
                    'timeframe'
                )
            }
        ),
        (
            'The metadata',
            {
                'fields': (
                    'get_generated_datetime',
                    'generated',
                    'count',
                    'status',
                )
            }
        ),
        (
            'The archive',
            {
                'fields': (
                    'archived_datetime',
                    'get_lag',
                    'content',
                )
            }
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, *args):
        return False

    def has_change_permission(self, *args):
        return False
