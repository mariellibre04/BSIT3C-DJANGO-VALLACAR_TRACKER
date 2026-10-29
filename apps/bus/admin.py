from django.contrib import admin

from .models import (
    Bus,
    BusNextStopLog,
    BusTerminalTap,
    Route,
    RouteStop,
    Terminal,
)


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'plate_number', 'capacity', 'route', 'current_location', 'movement_status', 'movement_reason', 'status')
    search_fields = ('bus_number', 'plate_number', 'route', 'current_location', 'movement_reason')
    list_filter = ('status', 'movement_status')


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'province', 'is_owned_terminal', 'is_major_stop')
    search_fields = ('name', 'code', 'city', 'province', 'aliases')
    list_filter = ('is_owned_terminal', 'is_major_stop', 'province')


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 0
    ordering = ('sequence',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'destination', 'validation_status', 'validated_at')
    search_fields = ('name', 'aliases', 'source', 'origin__name', 'destination__name')
    list_filter = ('validation_status',)
    inlines = [RouteStopInline]


@admin.register(BusNextStopLog)
class BusNextStopLogAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'current_station', 'next_stop', 'eta_minutes', 'eta_at', 'logged_at')
    search_fields = ('bus__bus_number', 'route__name', 'current_station__name', 'next_stop__name')
    list_filter = ('route',)
    readonly_fields = ('logged_at',)


@admin.register(BusTerminalTap)
class BusTerminalTapAdmin(admin.ModelAdmin):
    list_display = ('bus', 'terminal_name', 'tapped_at', 'left_at')
    search_fields = ('bus__bus_number', 'terminal_name')
    list_filter = ('terminal_name',)
