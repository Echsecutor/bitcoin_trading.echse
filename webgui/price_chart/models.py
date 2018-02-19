from django.db import models


class Trade(models.Model):
    """
    This represents a trade of
    amount curIn |-> rate * amount curOut
    traded on platform source with platform specific id source_id
    curIn and out are the ticker symbols, such as btc, eth, ...
    """
    source = models.CharField(max_length=64)
    source_id = models.PositiveIntegerField()
    curIn = models.CharField(max_length=6)
    curOut = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=28, decimal_places=18)
    rate = models.DecimalField(max_digits=28, decimal_places=18)
    date = models.DateTimeField()
