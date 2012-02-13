'''
Created on 23/12/2010

@author: esauro
'''
from django.contrib import admin
from models import Server, Rack, RackPlace, Chasis, BladeServer, HardDisk, RackServer

class HardDiskInline(admin.TabularInline):
    model = HardDisk
    extra = 2
    
class RackableAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'model_name', 'rack', 'buy_date', 'warranty_expires')
    date_hierarchy = 'buy_date'
    list_filter = ('model__manufacturer', 'rack__room__building' )

    def model_name(self, obj):
        return obj.model.name
    model_name.short_description = 'model'

class RackServerAdmin(RackableAdmin):
#    list_display = RackableAdmin.list_display + ('memory', 'processor_type', 'processor_clock', 'processor_number')
    list_display = ('memory', 'processor_type', 'processor_clock', 'processor_number')
    inlines = [HardDiskInline, ]  

class ServerAdmin(admin.ModelAdmin):
    list_display = ('memory', 'processor_type', 'processor_clock', 'processor_number')
    inlines = [HardDiskInline, ]  

class ServerAdmin2(admin.ModelAdmin):
    list_display = ('warranty_expires',)

admin.site.register(Server, ServerAdmin)
admin.site.register(RackServer, ServerAdmin2)
admin.site.register(Rack)
admin.site.register(RackPlace)
admin.site.register(Chasis)
admin.site.register(BladeServer)
