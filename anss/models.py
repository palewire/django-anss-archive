from datetime import timedelta

from django.contrib.gis.db import models
from django.utils import timezone

from anss import parse_unix_datetime


class Feed(models.Model):
    """
    A raw feed archived from the USGS real time service.
    """

    # The feed
    archived_datetime = models.DateTimeField(
        help_text="The time the feed was pulled.", null=True
    )
    TYPE_CHOICES = (("m1", "Magnitude > 1.0"),)
    type = models.CharField(max_length=500, choices=TYPE_CHOICES)
    FORMAT_CHOICES = (("geojson", "GeoJSON"),)
    format = models.CharField(max_length=500, choices=FORMAT_CHOICES)
    TIMEFRAME_CHOICES = (("one-hour", "One hour"),)
    timeframe = models.CharField(max_length=500, choices=TIMEFRAME_CHOICES)
    content = models.FileField(verbose_name="archived GeoJSON")

    # The metadata in the feed
    generated = models.BigIntegerField(null=True, verbose_name="time generated (UNIX)")
    url = models.CharField(max_length=5000, blank=True, verbose_name="GeoJSON URL")
    title = models.CharField(max_length=5000, blank=True)
    api = models.CharField(max_length=5000, blank=True, verbose_name="API version")
    count = models.IntegerField(null=True, verbose_name="earthquake count")
    status = models.IntegerField(null=True, verbose_name="response status")

    class Meta:
        ordering = ("-archived_datetime",)
        get_latest_by = "archived_datetime"
        verbose_name = "Archived feed"

    def __str__(self):
        return f"{self.title} ({self.archived_datetime})"

    def get_absolute_url(self):
        return self.url

    def get_generated_datetime(self):
        """
        Returns the UNIX epoch time in the generated field as a UTC datetime object.
        """
        if not self.generated:
            return None
        return parse_unix_datetime(self.generated)

    get_generated_datetime.short_description = "time generated"

    def get_lag(self):
        """
        The difference between the time we pulled the feed and when USGS generated it.
        """
        if not self.generated or not self.archived_datetime:
            return None
        return self.archived_datetime - self.get_generated_datetime()

    get_lag.short_description = "lag"


class FeedEarthquake(models.Model):
    """
    An earthquake included in a raw USGS feed.

    Table includes every quake in every feed. Lots of duplicates.
    """

    # Link to other model
    feed = models.ForeignKey(
        "Feed", on_delete=models.CASCADE, verbose_name="archived source"
    )

    # Identifiers
    usgs_id = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="USGS ID",
        help_text="A composite identifier that combines the source network and the earthquake.",
    )
    net = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="network ID",
        help_text=(
            "The ID of a data contributor. "
            "Identifies the network considered to be the "
            "preferred source of information for this event."
        ),
    )
    sources = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="network sources",
        help_text="A comma-separated list of network contributors",
    )
    code = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="unique ID",
        help_text=(
            "An identifying code assigned by - and unique from - "
            "the corresponding source for the event."
        ),
    )
    ids = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="identifiers",
        help_text="A comma-separated list of event ids that are associated to an event.",
    )
    title = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="description",
        help_text="A summary of the event",
    )

    # What
    type = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="event type",
        help_text="Type of seismic event",
    )
    mag = models.FloatField(null=True, verbose_name="magnitude")
    magType = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="magnitude type",
        help_text=(
            "The method or algorithm used to calculate the "
            "preferred magnitude for the event."
        ),
    )
    mmi = models.FloatField(
        null=True,
        verbose_name="Maximum Modified Mercalli Intensity",
        help_text=(
            "The maximum estimated instrumental intensity for the event. "
            "Computed by ShakeMap. While typically reported as a roman numeral, "
            "for the purposes of this API, intensity is expected as the decimal "
            "equivalent of the roman numeral."
        ),
    )
    felt = models.IntegerField(
        null=True,
        verbose_name="how many felt it?",
        help_text="The total number of felt reports submitted to the DYFI? system",
    )
    cdi = models.FloatField(
        null=True,
        verbose_name="community decimal intensity",
        help_text=(
            "The maximum reported intensity for the event. Computed by DYFI. "
            "While typically reported as a roman numeral, for the purposes of this API, "
            "intensity is expected as the decimal equivalent of the roman numeral"
        ),
    )
    tsunami = models.IntegerField(
        null=True,
        verbose_name="tsunami warning",
        help_text=(
            "This flag is set to 1 for large events in oceanic regions and 0 otherwise. "
            "The existence or value of this flag does not indicate if a tsunami actually "
            "did or will exist."
        ),
    )
    sig = models.IntegerField(
        null=True,
        verbose_name="significance",
        help_text=(
            "A number describing how significant the event is. "
            "Larger numbers indicate a more significant event. "
            "This value is determined on a number of factors, including: "
            "magnitude, maximum MMI, felt reports, and estimated impact."
        ),
    )
    alert = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="alert level",
        help_text="The alert level from the PAGER earthquake impact scale",
    )

    # Where
    place = models.CharField(
        max_length=5000, blank=True, help_text="Description of the epicenter"
    )
    point = models.PointField(srid=4326, null=True, verbose_name="epicenter")
    depth = models.FloatField(null=True, help_text="Depth of the event in kilometers")

    # When
    time = models.BigIntegerField(
        null=True,
        verbose_name="occurred at (UNIX)",
        help_text=(
            "Time when the event occurred. "
            "Times are reported in milliseconds since the epoch."
        ),
    )
    tz = models.IntegerField(
        null=True,
        help_text="Timezone offset from UTC in minutes at the event epicenter",
    )

    # References
    url = models.CharField(max_length=5000, blank=True, verbose_name="Summary page")
    detail = models.CharField(max_length=5000, blank=True, verbose_name="GeoJSON")

    # Review
    updated = models.BigIntegerField(
        null=True,
        verbose_name="updated at (UNIX)",
        help_text=(
            "Time when the event was most recently updated. "
            "Times are reported in milliseconds since the epoch."
        ),
    )
    nst = models.IntegerField(
        null=True,
        verbose_name="seismic stations",
        help_text="The total number of seismic stations used to determine earthquake location",
    )
    dmin = models.FloatField(
        null=True,
        verbose_name="nearest seismic station",
        help_text=(
            "Horizontal distance from the epicenter to the nearest station (in degrees). "
            "1 degree is approximately 111.2 kilometers. In general, the smaller this number, "
            "the more reliable is the calculated depth of the earthquake."
        ),
    )
    gap = models.FloatField(
        null=True,
        verbose_name="largest azimuthal gap",
        help_text=(
            "The largest azimuthal gap between azimuthally adjacent stations (in degrees). "
            "In general, the smaller this number, the more reliable is the calculated horizontal "
            "position of the earthquake. Earthquake locations in which the azimuthal gap exceeds "
            "180 degrees typically have large location and depth uncertainties."
        ),
    )
    rms = models.FloatField(
        null=True,
        verbose_name="root mean squared",
        help_text=(
            "The root-mean-square (RMS) travel time residual, in sec, using all weights. "
            "This parameter provides a measure of the fit of the observed arrival times to "
            "the predicted arrival times for this location. Smaller numbers reflect a better "
            "fit of the data. The value is dependent on the accuracy of the velocity model "
            "used to compute the earthquake location, the quality weights assigned to the "
            "arrival time data, and the procedure used to locate the earthquake."
        ),
    )
    status = models.CharField(
        max_length=5000,
        blank=True,
        help_text=(
            "Indicates whether the event has been reviewed by a human. Status is either "
            "automatic or reviewed. Automatic events are directly posted by automatic "
            "processing systems and have not been verified or altered by a human. Reviewed "
            "events have been looked at by a human. The level of review can range from a "
            "quick validity check to a careful reanalysis of the event."
        ),
    )
    types = models.CharField(
        max_length=5000,
        blank=True,
        verbose_name="product types",
        help_text="A comma-separated list of product types associated to this event",
    )

    class Meta:
        ordering = ("-feed_id", "-time")
        get_latest_by = ("-feed_id", "-time")
        verbose_name = "Archived earthquake"

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return self.url

    def get_time_datetime(self):
        """
        Returns the UNIX epoch time in the time field as a UTC datetime object.
        """
        if not self.time:
            return None
        return parse_unix_datetime(self.time)

    get_time_datetime.short_description = "occurred at"

    def get_updated_datetime(self):
        """
        Returns the UNIX epoch time in the updated field as a UTC datetime object.
        """
        if not self.updated:
            return None
        return parse_unix_datetime(self.updated)

    get_updated_datetime.short_description = "updated at"

    def is_last_hour(self):
        """
        Returns whether an earthquake happened in the last hour.
        """
        return self.get_time_datetime() >= timezone.now() - timedelta(hours=1)
