from django.contrib import admin

from .models import AssetClass, Product, PriceRecord


class AssetClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name", )
    ordering = ("id", )


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "symbol", "alias", "asset_class")
    search_fields = ("symbol", )
    ordering = ("id", )

    def asset_class(self, obj):
        return obj.assetclass.name


class PriceRecordAdmin(admin.ModelAdmin):
    list_display = ("symbol", "date", "open", "high", "low", "close")
    list_filter = ("date", )
    search_fields = ("date", )
    ordering = ("date", )
    fields = ("date", "open", "high", "low", "close")

    def symbol(self, obj):
        return obj.product.symbol


admin.site.register(AssetClass, AssetClassAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(PriceRecord, PriceRecordAdmin)
