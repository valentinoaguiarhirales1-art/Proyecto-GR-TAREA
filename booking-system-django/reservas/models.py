import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Resource(models.Model):
    name = models.CharField('nombre', max_length=100)
    description = models.TextField('descripción', blank=True)
    capacity = models.PositiveIntegerField('capacidad', default=1)
    icon = models.CharField('emoji', max_length=4, default='🏟️')
    slot_minutes = models.PositiveIntegerField('duración del turno (min)', default=60)
    is_active = models.BooleanField('activo', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Availability(models.Model):
    WEEKDAYS = [(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
                (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField('día', choices=WEEKDAYS)
    start_time = models.TimeField('apertura')
    end_time = models.TimeField('cierre')

    class Meta:
        ordering = ['resource', 'weekday', 'start_time']
        verbose_name_plural = 'availabilities'

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('La apertura debe ser anterior al cierre.')

    def __str__(self):
        return f'{self.resource} - {self.get_weekday_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}'


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmada'
        CANCELLED = 'cancelled', 'Cancelada'

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)
    notes = models.CharField('notas', max_length=200, blank=True)
    recurrence_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start']

    def __str__(self):
        return f'{self.resource} {self.start:%d/%m/%Y %H:%M}'

    @classmethod
    def overlapping(cls, resource, start, end, exclude_pk=None):
        qs = cls.objects.filter(resource=resource, status=cls.Status.CONFIRMED,
                                start__lt=end, end__gt=start)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs

    def clean(self):
        if self.start and self.end:
            if self.start >= self.end:
                raise ValidationError('El fin debe ser posterior al inicio.')
            if self.status == self.Status.CONFIRMED and \
                    Booking.overlapping(self.resource, self.start, self.end, self.pk).exists():
                raise ValidationError('Ya existe una reserva que se solapa con este horario.')


def new_recurrence_id():
    return uuid.uuid4()
