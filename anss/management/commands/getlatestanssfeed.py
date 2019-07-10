import logging
import requests
from django.utils import timezone
from django.contrib.gis.geos import Point
from anss.models import Feed, FeedEarthquake
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Pull the latest earthquakes feeds from the USGS"

    def safestr(self, v):
        """
        Safely prepare a string value to be saved to the database.
        """
        return v or ""

    def get_feedearthquake_model(self):
        """
        The model that will be used to save the FeedEarthquake data.
        """
        return FeedEarthquake

    def handle(self, *args, **options):
        # Get the feed
        now = timezone.now()
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.geojson"
        logger.debug(f"Requesting {url}")
        r = requests.get(url)

        # Check the response
        logger.debug(f"Response code: {r.status_code}")
        if not r.status_code == 200:
            logger.error(f"Request for {url} failed with code {r.status_code}")
            return

        # Archive it
        logger.debug("Archiving data")
        self.feed = Feed.objects.create(
            archived_datetime=now,
            type="m1",
            format="geojson",
            timeframe="one-hour",
        )

        # Save the file
        f = ContentFile(r.content)
        self.feed.content.save(
            f"usgs/{self.feed.type}/{self.feed.format}/{self.feed.timeframe}/{self.feed.archived_datetime}.json",
            f,
            save=True
        )
        logger.debug(f"Archived at {self.feed.content.url}")

        # Save the metadata in the field
        geojson = r.json()
        metadata = geojson['metadata']
        logger.debug(f"Logging metadata {metadata}")
        self.feed.generated = metadata['generated']
        self.feed.url = metadata['url']
        self.feed.title = metadata['title']
        self.feed.api = metadata['api']
        self.feed.count = metadata['count']
        self.feed.status = metadata['status']
        self.feed.save()

        # Save each earthquake
        [self.create_feedearthquake(d) for d in geojson['features']]

    def create_feedearthquake(self, d):
        """
        Accepts a raw GeoJSON feature dictionary from the an ANSS real-time feed and creates a database record.
        """
        p = d['properties']
        model = self.get_feedearthquake_model()
        e = model(
            feed=self.feed,
            mag=p['mag'],
            place=self.safestr(p['place']),
            time=p['time'],
            updated=p['updated'],
            tz=p['tz'],
            url=self.safestr(p['url']),
            detail=self.safestr(p['detail']),
            felt=p['felt'],
            cdi=p['cdi'],
            mmi=p['mmi'],
            alert=self.safestr(p['alert']),
            status=p['status'],
            tsunami=p['tsunami'],
            sig=p['sig'],
            net=self.safestr(p['net']),
            code=self.safestr(p['code']),
            ids=self.safestr(p['ids']),
            sources=self.safestr(p['sources']),
            types=self.safestr(p['types']),
            nst=p['nst'],
            dmin=p['dmin'],
            rms=p['rms'],
            gap=p['gap'],
            magType=self.safestr(p['magType']),
            type=self.safestr(p['type']),
            title=self.safestr(p['title']),
            usgs_id=self.safestr(d['id'])
        )
        lng, lat, depth = d['geometry']['coordinates']
        e.point = Point(lng, lat)
        e.depth = depth
        e.save()
        logger.debug(f"Saved {e}")
        return e
