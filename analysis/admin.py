from django.contrib import admin

from analysis.models import NewsHeadline, NewsReleaseData


class NewsHeadLineAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "measurement")
    search_fields = ("title", )
    fields = ("definition", )
    ordering = ("title", )


class NewsReleaseDataAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "value_actual",
                    "value_previous", "value_forecast", "impact")
    search_fields = ("date", )
    fields = ("value_actual", "value_previous", "value_forecast", "impact")
    ordering = ("date", )

    def title(self, obj):
        return obj.headline.title


admin.site.register(NewsHeadline)
admin.site.register(NewsReleaseData)
