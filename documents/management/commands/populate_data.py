from django.core.management.base import BaseCommand
from documents.models import DocumentDefinition

class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **kwargs):
        data = [
            (1, "PAN Card", ["Permanent Account Number Card", "Name", "Father's Name"]),
            (2, "Aadhar Card", ["Government", "India"]),
            (3, "Emirates ID Card", ["United", "Arab", "Emirates", "Identity"]),
            (4, "Qatar ID Card", ["State", "Of", "Qatar"]),
        ]
        
        for id, name, details in data:
            DocumentDefinition.objects.update_or_create(pk=id, defaults={'name': name, 'details': details})
        
        self.stdout.write(self.style.SUCCESS('Data populated successfully'))
