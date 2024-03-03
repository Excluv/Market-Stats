from django.db import models


# Create your models here.
class AssetClass(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Asset classes"


class Product(models.Model):
    name = models.CharField(max_length=1000, null=True)
    symbol = models.CharField(max_length=30)
    alias = models.CharField(max_length=30, null=True)
    assetclass = models.ForeignKey(AssetClass, on_delete=models.PROTECT)


class PriceRecord(models.Model):
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
