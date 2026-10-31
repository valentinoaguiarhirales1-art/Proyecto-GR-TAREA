from django.core.management.base import BaseCommand

from reservas.models import Availability, Resource


class Command(BaseCommand):
    help = 'Crea recursos de ejemplo con su horario semanal'

    def handle(self, *args, **options):
        demo = [
            ('Pista de pádel 1', '🎾', 'Pista cubierta con iluminación LED.', 4, 60),
            ('Pista de fútbol sala', '⚽', 'Césped artificial, vestuarios incluidos.', 10, 60),
            ('Sala de reuniones A', '💼', 'Proyector, pizarra y WiFi.', 8, 30),
        ]
        for name, icon, desc, cap, slot in demo:
            r, created = Resource.objects.get_or_create(
                name=name, defaults=dict(icon=icon, description=desc, capacity=cap, slot_minutes=slot))
            if created:
                for wd in range(7):
                    end = '22:00' if wd < 5 else '20:00'
                    Availability.objects.create(resource=r, weekday=wd, start_time='09:00', end_time=end)
        self.stdout.write(self.style.SUCCESS('Datos de ejemplo listos'))
