from __future__ import unicode_literals

from django.db import models


class VapitiVote(models.Model):
    VAPITI_TYPE_GOLD = "G"
    VAPITI_TYPE_SILVER_MALE = "M"
    VAPITI_TYPE_SILVER_FEMALE = "F"
    VAPITI_TYPES = [
        (VAPITI_TYPE_GOLD, "Gold"),
        (VAPITI_TYPE_SILVER_MALE, "Silver Male"),
        (VAPITI_TYPE_SILVER_FEMALE, "Silver Female"),
    ]

    user = models.ForeignKey("KTUser")
    year = models.PositiveIntegerField(default=0, blank=True, null=True)
    vapiti_round = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    vapiti_type = models.CharField(
        max_length=1, choices=VAPITI_TYPES, default=VAPITI_TYPE_GOLD
    )
    serial_number = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    film = models.ForeignKey("Film")
    artist = models.ForeignKey("Artist", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = [
            "user",
            "year",
            "vapiti_round",
            "vapiti_type",
            "serial_number",
        ]


class VapitiStat(models.Model):
    year = models.PositiveSmallIntegerField()
    vapiti_round = models.PositiveSmallIntegerField(blank=True, null=True)
    vapiti_type = models.CharField(max_length=1, choices=VapitiVote.VAPITI_TYPES)
    user_count = models.PositiveSmallIntegerField(blank=True, null=True)
    film_count = models.PositiveSmallIntegerField(blank=True, null=True)
    artist_count = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ["year", "vapiti_round", "vapiti_type"]
