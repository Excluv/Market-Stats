from django.db import models


class NewsHeadline(models.Model):
    title = models.CharField(max_length=255)
    region = models.CharField(max_length=10)
    measurement = models.CharField(max_length=10)
    definition = models.CharField(max_length=2000, null=True)

    def __str__(self):
        return self.title


class NewsReleaseData(models.Model):
    date = models.DateField()
    value_actual = models.FloatField(null=True)
    value_previous = models.FloatField(null=True)
    value_forecast = models.FloatField(null=True)
    impact = models.CharField(max_length=5)
    headline = models.ForeignKey(NewsHeadline, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "News release data"
