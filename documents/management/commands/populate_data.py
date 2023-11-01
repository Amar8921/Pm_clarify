from django.core.management.base import BaseCommand
from documents.models import DocumentDefinition

class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **kwargs):
        data = [
            (1, "Identity Document (ID)", ["Permanent Account Number Card", "Name", "Father's Name"]),
        ]
        
        for id, name, details in data:
            DocumentDefinition.objects.update_or_create(pk=id, defaults={'name': name, 'details': details})
        
        self.stdout.write(self.style.SUCCESS('Data populated successfully'))
