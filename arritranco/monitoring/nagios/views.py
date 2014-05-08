from inventory.models import Machine, OperatingSystem, BalancedService
from backups.models import FileBackupTask, R1BackupTask, TSMBackupTask, BackupTask
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from helpers.processors import mco2dict, mco2dict_balanced
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
import os.path
import logging
logger = logging.getLogger(__name__)

from nsca import NSCA
from models import NagiosCheck, NagiosCheckOpts, NagiosNetworkParent, HUMAN_TO_NAGIOS
from scheduler.models import TaskStatus, TaskCheck
from templatetags.nagios_filters import nagios_safe

def hosts(request):
    '''
        Nagios hosts config file.
    '''
    template = 'nagios/hosts.cfg'

    context = {'machines': []}
    for m in BalancedService.objects.filter(up = True).order_by('fqdn'):
        i = m.machine.all()[0]
	context['machines'].append({
            'fqdn': m.fqdn,
            'service_ip': m.ip,
            'contact_groups': i.responsibles(),
            'parents': NagiosNetworkParent.get_parents_for_host(i),
        })
    for m in Machine.objects.filter(up = True).order_by('fqdn'):
        context['machines'].append({
            'fqdn': m.fqdn,
            'service_ip': m.get_service_ip(),
            'contact_groups': m.responsibles(),
            'parents': NagiosNetworkParent.get_parents_for_host(m),
        })
    if 'file' in request.GET:
        response = render_to_response(template, context, mimetype="text/plain")
        response['Content-Disposition'] = 'attachment; filename=%s' % request.GET['file'] 
    else:
        response = render_to_response(template, context, mimetype="text/plain")
    return response


def hosts_ext_info(request):
    '''
        Nagios extinfo config file
    '''
    l = []
    # FIXME:
    for os in OperatingSystem.objects.filter(type__name__in = ['Linux', 'Windows', 'Solaris']):
        running_machines = os.machine_set.filter(up = True)
        if running_machines.count():
            machines = []
            for m in running_machines:
# FIXME: We need to import ip's from the old tool to improve this a little bit.
#                if m.maquinared_set.filter(visible = True).count():
#                    machines.append(m)
                machines.append(m)
            if len(machines):
                l.append((os.logo, ",".join([m.fqdn for m in machines])))
    context = {"logo_machines": l }
    return render_to_response('nagios/host_ext_info.cfg', context, mimetype="text/plain")


def get_checks(request, name):
    '''
        Render all defined checks of "name" for all machines UP.
    '''
    template = 'nagios/' + name + '_checks.cfg'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/templates/'+ template

    if not os.path.isfile(file_path):
        template = 'nagios/default_checks.cfg'
	
    context = {}
    try:
        check = NagiosCheck.objects.get(slug = name)
    except ObjectDoesNotExist: 
        response = HttpResponse(u"Check %s does not exist" % name, content_type = "text/plain")
        response.status_code =  404
        return response

    servers = []
    for machine_check_options in check.all_machines(): 
        servers.append(mco2dict(machine_check_options))

    for m in BalancedService.objects.filter(up = True).order_by('fqdn'):
        m0 = m.machine.all()[0]
        for c in NagiosCheckOpts.objects.filter(machine=m0, check__name=check.name, balanced=True):
            servers.append(mco2dict_balanced(c,m))
 
    context['servers'] = servers
    context['check'] = check.name

    if 'file' in request.GET:
        filename = name + '_checks.cfg'
        response = render_to_response(template, context, mimetype="text/plain")
        response['Content-Disposition'] = 'attachment; filename=%s' % request.GET['file'] 
    else:
        response = render_to_response(template, context, mimetype="text/plain")

    return response


def backup_checks(request):
    '''
        Backup checks
    '''
    template = 'nagios/backup_checks.cfg'
    context = {
    'backup_file_tasks': FileBackupTask.objects.filter(machine__up=True).filter(active=True).order_by('machine__fqdn'),
    'r1soft_tasks': R1BackupTask.objects.filter(machine__up=True).filter(active=True).order_by('machine__fqdn'),
    'TSM_tasks': TSMBackupTask.objects.filter(machine__up=True).filter(active=True).order_by('machine__fqdn')}
    if 'file' in request.GET:
        response = render_to_response(template, context, mimetype="text/plain")
        response['Content-Disposition'] = 'attachment; filename=%s' % request.GET['file'] 
    else:
        response = render_to_response(template, context, mimetype="text/plain")
    return response

def refresh_nagios_status(request):
    logger.debug('Refreshing nagios status')
    nsca = NSCA()
    for bt in BackupTask.objects.filter(active = True, machine__up = True):
        try:
            tch = TaskCheck.objects.filter(task = bt).order_by('-task_time')[0]
        except IndexError:
            logger.debug('There is no TaskCheck for %s', bt)
            continue
        status = tch.get_status()
        if isinstance(status, TaskStatus):
            logger.debug('Last status for %s: %s is %s (%s)', bt, bt.description, status, status.check_time)
            logger.debug('Human to nagios de %s es %d' % (status.status,HUMAN_TO_NAGIOS[status.status]))
            nsca.add_custom_status(
                    bt.machine.fqdn,
                    nagios_safe(bt.description),
                    HUMAN_TO_NAGIOS[status.status],
                    status.comment
                )
    nsca.send()
    logger.debug('Nagios status updated for %s', bt)

    return HttpResponse("Nagios up to date")

def json_migration(request):
    template = 'nagios/migration.json'
    context = {
        'checkops': NagiosCheckOpts.objects.all()
    }
    NagiosCheckOpts.objects.all()[0].contact_groups.all()
    if 'file' in request.GET:
        response = render_to_response(template, context, mimetype="text/plain")
        response['Content-Disposition'] = 'attachment; filename=%s' % request.GET['file']
    else:
        response = render_to_response(template, context, mimetype="text/plain")
    return response
    pass