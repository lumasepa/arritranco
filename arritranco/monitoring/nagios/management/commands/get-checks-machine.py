from django.core.management.base import BaseCommand, CommandError
from monitoring.nagios.models import NagiosCheckOpts
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context

class Command(BaseCommand):
    args = ''
    help = 'Create a json file with the data of checks and machines'

    def handle(self, *args, **options):
        f = open("./data_checks_machine.json", "w")

        file = get_template('migration.json').render(
        Context({
            'checkops': NagiosCheckOpts.objects.all()
        }))

        f.write(file)
        f.close()