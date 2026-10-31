from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Availability, Booking, Resource, new_recurrence_id


class BookingError(Exception):
    pass


def day_slots(resource, day):
    """Turnos del día con su estado: free / busy / mine-able / past."""
    tz = timezone.get_current_timezone()
    now = timezone.now()
    slots = []
    step = timedelta(minutes=resource.slot_minutes)
    bookings = list(Booking.objects.filter(
        resource=resource, status=Booking.Status.CONFIRMED,
        start__lt=timezone.make_aware(datetime.combine(day + timedelta(days=1), datetime.min.time()), tz),
        end__gt=timezone.make_aware(datetime.combine(day, datetime.min.time()), tz)))
    for av in resource.availabilities.filter(weekday=day.weekday()):
        cur = datetime.combine(day, av.start_time)
        close = datetime.combine(day, av.end_time)
        while cur + step <= close:
            s = timezone.make_aware(cur, tz)
            e = s + step
            taken = next((b for b in bookings if b.start < e and b.end > s), None)
            state = 'past' if s < now else ('busy' if taken else 'free')
            slots.append({'start': s, 'end': e, 'state': state, 'booking': taken})
            cur += step
    return slots


def is_within_availability(resource, start, end):
    ls, le = timezone.localtime(start), timezone.localtime(end)
    if ls.date() != le.date():
        return False
    return resource.availabilities.filter(
        weekday=ls.weekday(), start_time__lte=ls.time(), end_time__gte=le.time()).exists()


@transaction.atomic
def create_bookings(user, resource, start, end, repeat_weeks=0, notes=''):
    """Crea una reserva y, opcionalmente, repeticiones semanales. Todo o nada."""
    if not resource.is_active:
        raise BookingError('Este recurso no está disponible.')
    if start >= end:
        raise BookingError('El fin debe ser posterior al inicio.')
    if start < timezone.now():
        raise BookingError('No se puede reservar en el pasado.')
    repeat_weeks = max(0, min(int(repeat_weeks or 0), 12))
    rid = new_recurrence_id() if repeat_weeks else None
    # select_for_update serializa reservas concurrentes del mismo recurso
    Resource.objects.select_for_update().get(pk=resource.pk)
    created, errors = [], []
    for i in range(repeat_weeks + 1):
        # se suma sobre la hora local para respetar cambios de horario
        s = timezone.localtime(start).replace(tzinfo=None) + timedelta(weeks=i)
        e = timezone.localtime(end).replace(tzinfo=None) + timedelta(weeks=i)
        tz = timezone.get_current_timezone()
        s, e = timezone.make_aware(s, tz), timezone.make_aware(e, tz)
        label = timezone.localtime(s).strftime('%d/%m/%Y %H:%M')
        if not is_within_availability(resource, s, e):
            errors.append(f'{label}: fuera del horario disponible')
        elif Booking.overlapping(resource, s, e).exists():
            errors.append(f'{label}: ya está reservado')
        else:
            created.append(Booking(resource=resource, user=user, start=s, end=e,
                                   notes=notes, recurrence_id=rid))
    if errors:
        raise BookingError('No se pudo completar la reserva → ' + '; '.join(errors))
    Booking.objects.bulk_create(created)
    notify(user, f'Reserva confirmada: {resource.name}',
           f'Hola {user.username}, se han confirmado {len(created)} reserva(s) de {resource.name}.\n' +
           '\n'.join(timezone.localtime(b.start).strftime('- %d/%m/%Y %H:%M') for b in created))
    return created


def cancel_booking(booking, whole_series=False):
    qs = Booking.objects.filter(pk=booking.pk)
    if whole_series and booking.recurrence_id:
        qs = Booking.objects.filter(recurrence_id=booking.recurrence_id, start__gte=timezone.now())
    n = qs.filter(status=Booking.Status.CONFIRMED).update(status=Booking.Status.CANCELLED)
    notify(booking.user, f'Reserva cancelada: {booking.resource.name}',
           f'Se han cancelado {n} reserva(s) de {booking.resource.name}.')
    return n


def notify(user, subject, message):
    if user.email:
        send_mail(subject, message, None, [user.email], fail_silently=True)
