# Django helpers
# Logging
import logging

# Files
import requests
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from anss.models import Feed, FeedEarthquake

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Archive the latest real-time earthquake notifications "
        "from the USGS's Advanced National Seismic System"
    )

    def set_options(self, *args, **options):
        self.now = timezone.now()
        self.url = (
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_hour.geojson"
        )
        self.feed = Feed.objects.create(
            archived_datetime=self.now,
            type="m1",
            format="geojson",
            timeframe="one-hour",
        )
        self.feedearthquake_model = self.get_feedearthquake_model()

    def handle(self, *args, **options):
        # Set options
        self.set_options(*args, **options)

        # Get the feed
        raw_feed = self.get_usgs_feed()

        # Check the response
        logger.debug(f"Response code: {raw_feed.status_code}")
        if not raw_feed.status_code == 200:
            msg = f"Request for {self.url} failed with code {raw_feed.status_code}"
            logger.error(msg)
            self.feed.status = raw_feed.status_code
            self.feed.save()
            raise CommandError(msg)

        # Save the file
        logger.debug("Archiving data")
        self.feed.content.save(
            self.get_file_path(), ContentFile(raw_feed.content), save=True
        )
        logger.debug(f"Archived at {self.feed.content.url}")

        # Read in the GeoJSON as a Python dictionary
        geojson = raw_feed.json()

        # Save the metadata to the database
        metadata = geojson["metadata"]
        logger.debug(f"Logging metadata {metadata}")
        self.feed.generated = metadata["generated"]
        self.feed.url = metadata["url"]
        self.feed.title = metadata["title"]
        self.feed.api = metadata["api"]
        self.feed.count = metadata["count"]
        self.feed.status = metadata["status"]
        self.feed.save()

        # Save each earthquake
        [self.create_feedearthquake(d) for d in geojson["features"]]

    def safestr(self, v):
        """
        Safely prepare a string value from the source data for the database.
        """
        return (v or "").strip()

    def get_feedearthquake_model(self):
        """
        Returns the model that will be used to save the FeedEarthquake data.
        """
        return FeedEarthquake

    def get_usgs_feed(self):
        """
        Returns a real-time feed from ANSS.
        """
        # Request the URL
        logger.debug(f"Requesting {self.url}")
        return requests.get(self.url)

    def get_file_path(self):
        """
        Returns the file path where the archived content will be saved in the MEDIA_ROOT
        """
        return f"anss/{self.feed.type}/{self.feed.format}/{self.feed.timeframe}/{self.feed.archived_datetime}.json"

    def create_feedearthquake(self, d):
        """
        Accepts a raw GeoJSON feature dictionary from the an ANSS real-time feed and creates a database record.
        """
        p = d["properties"]
        obj = self.feedearthquake_model(
            feed=self.feed,
            mag=p["mag"],
            place=self.safestr(p["place"]),
            time=p["time"],
            updated=p["updated"],
            tz=p["tz"],
            url=self.safestr(p["url"]),
            detail=self.safestr(p["detail"]),
            felt=p["felt"],
            cdi=p["cdi"],
            mmi=p["mmi"],
            alert=self.safestr(p["alert"]),
            status=p["status"],
            tsunami=p["tsunami"],
            sig=p["sig"],
            net=self.safestr(p["net"]),
            code=self.safestr(p["code"]),
            ids=self.safestr(p["ids"]),
            sources=self.safestr(p["sources"]),
            types=self.safestr(p["types"]),
            nst=p["nst"],
            dmin=p["dmin"],
            rms=p["rms"],
            gap=p["gap"],
            magType=self.safestr(p["magType"]),
            type=self.safestr(p["type"]),
            title=self.safestr(p["title"]),
            usgs_id=self.safestr(d["id"]),
        )
        lng, lat, depth = d["geometry"]["coordinates"]
        obj.point = Point(lng, lat)
        obj.depth = depth
        obj.save()
        logger.debug(f"Saved {obj}")
        return obj
