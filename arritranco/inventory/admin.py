# coding: utf-8
'''
Created on 25/03/2011

@author: esauro
'''

from django import forms
from models import Machine, PhysicalMachine, VirtualMachine, OperatingSystem, OperatingSystemType, Interface
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

# This is a little bit tricky, because nagios app is importing machine model as well, but works ;)
from monitoring.nagios.admin import NagiosMachineCheckOptsInline
import datetime

import logging

logger = logging.getLogger(__name__)

# Try to import the default name for service interface of a machine
try:
    from settings import DEFAULT_SVC_IFACE_NAME
except ImportError:
    DEFAULT_SVC_IFACE_NAME = None


class InterfacesInline(admin.TabularInline):
    model = Interface
    raw_id_fields = ('ip',)


class ManagementIPFilter(SimpleListFilter):
    title = (u'Management Ip')

    parameter_name = 'management ip'

    def lookups(self, request, model_admin):
        return (
            ("with ip", _(u'with ip')),
            ("without ip", _(u'without ip'))
        )

    def queryset(self, request, queryset):
        if self.value():
            machines = None
            if self.value() == "with ip":
                machines = queryset.exclude(server__management_ip=None)
            else:
                machines = queryset.filter(server__management_ip=None)
            return queryset.filter(id__in=machines)


class MachineAdmin(admin.ModelAdmin):
    list_display = ('fqdn', 'up', 'os', 'start_up', 'update_priority', 'epo_level', 'network_names')
    list_filter = ('up', 'os', 'update_priority', 'epo_level')
    date_hierarchy = 'start_up'
    search_fields = ('fqdn', 'os__name')
    inlines = [InterfacesInline, NagiosMachineCheckOptsInline, ]
    actions = ['copy_machine', 'update_machine']

    def save_related(self, request, form, formsets, change):
        """Control that interface called "DEFAULT_SVC_IFACE_NAME" e.g. "service" is asociated to de fqdn ip

        Take care! this only works under Django >= 1.4

        """
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
        # Our custom process starts here
        machine = form.instance
        if machine.up and not machine.get_service_iface():
            svc_iface = machine.build_service_interface()
            try:
                # Verify that an interface with the fqdn ip already exists, then rename it
                fqdn_iface = machine.interface_set.get(ip=svc_iface.ip)
            except ObjectDoesNotExist:
                fqdn_iface = None
            if machine.get_num_ifaces() == 0 or not fqdn_iface:
                # If there is no ifaces, or ther is some but no one with fqdn
                # ip addr, we create the default one
                machine.interface_set.add(svc_iface)
                messages.info(request, u'The iface %s has been created bounded to the fqdn of %s' % (
                    machine.get_service_iface(), machine))
            else:
                # There is an interface with fqdn ip addr, we rename it to DEFAULT_SVC_IFACE_NAME
                messages.info(request, _(u'The iface founded %s' % fqdn_iface))
                fqdn_iface.name = DEFAULT_SVC_IFACE_NAME
                logger.debug("Calling Interface Save method: %d - %s " % (fqdn_iface.id, fqdn_iface))
                fqdn_iface.save()
                messages.info(request, _(
                    u'The iface %s has been renamed to default service interface' % machine.get_service_iface()))

    class CopyMachineForm(forms.Form):
        fqdn = forms.CharField(max_length=255)
        description = forms.CharField(widget=forms.Textarea)
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    # First approach, this is a TODO
    def copy_machine(self, request, queryset):
        """Admin action to copy de basics of a machine."""
        form = None
        if 'apply' in request.POST:
            messages.info(request, _(u'The action has been applied'))
            return HttpResponseRedirect(request.get_full_path())
        if not form:  # first call render the form to ask for diferent parametters
            form = self.CopyMachineForm(initial=
                                        {
                                            '_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME),
                                            'fqdn': queryset[0].fqdn,
                                            'description': queryset[0].fqdn,
                                        }
            )
        return render_to_response('admin/copy_machine.html', {'machines': queryset,
                                                              'copy_form': form,
        }, context_instance=RequestContext(request))

    copy_machine.short_description = _(u'Copy from selected machine(TODO)')

    def update_machine(self, request, queryset):
        """ Admin action to set update date to now"""
        for machine in queryset:
            machine.up_to_date_date = datetime.date.today()
            machine.save()
        messages.info(request, _(u'%s machines has been updated' % (queryset.count())))

    update_machine.short_description = _(u'Machine up to date')


class PysicalMachineAdmin(MachineAdmin):
    list_display = ('fqdn', 'server_link', 'get_warranty_expires', 'up', 'os', 'start_up', 'update_priority', 'epo_level')
    list_filter = ('up', 'os', 'update_priority', 'epo_level', ManagementIPFilter)

    def server_link(self, obj):
        return "<a href=%s>%s<a/>" % (obj.get_server_admin_url(), str(obj.server))

    server_link.short_description = u'Server'
    server_link.allow_tags = True


class VirtualMachineAdmin(MachineAdmin):
    list_display = ('fqdn', 'hypervisor', 'up', 'os', 'start_up', 'update_priority', 'epo_level')
    list_filter = ('hypervisor', 'up', 'os', 'update_priority', 'epo_level')
    list_editable = ('hypervisor',)


class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('ip_addr', 'visible', 'machine', 'network')
    list_filter = ('visible', 'machine')


class OperatingSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', )
    list_filter = ('type', )





admin.site.register(PhysicalMachine, PysicalMachineAdmin)
admin.site.register(VirtualMachine, VirtualMachineAdmin)
admin.site.register(OperatingSystem, OperatingSystemAdmin)
admin.site.register(OperatingSystemType)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Machine, MachineAdmin)


