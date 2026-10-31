from datetime import date, datetime, timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Booking, Resource
from .services import BookingError, cancel_booking, create_bookings, day_slots


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label='Email (para notificaciones)')

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        messages.success(request, '¡Bienvenid@! Tu cuenta está lista 🎉')
        return redirect('recursos')
    return render(request, 'registration/register.html', {'form': form})


def resource_list(request):
    return render(request, 'reservas/resource_list.html',
                  {'resources': Resource.objects.filter(is_active=True)})


def _parse_day(value):
    try:
        return date.fromisoformat(value) if value else timezone.localdate()
    except ValueError:
        raise Http404('Fecha inválida')


def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk, is_active=True)
    return render(request, 'reservas/resource_detail.html', {
        'resource': resource, 'today': timezone.localdate(),
        'availabilities': resource.availabilities.all()})


def slots_api(request, pk):
    resource = get_object_or_404(Resource, pk=pk, is_active=True)
    day = _parse_day(request.GET.get('date'))
    data = []
    for s in day_slots(resource, day):
        b = s['booking']
        data.append({
            'start': s['start'].isoformat(), 'end': s['end'].isoformat(),
            'label': f"{timezone.localtime(s['start']):%H:%M} - {timezone.localtime(s['end']):%H:%M}",
            'state': 'mine' if b and request.user.is_authenticated and b.user_id == request.user.id else s['state'],
        })
    return JsonResponse({'date': day.isoformat(), 'slots': data})


def month_api(request, pk):
    """Ocupación por día para pintar el calendario mensual."""
    resource = get_object_or_404(Resource, pk=pk, is_active=True)
    try:
        year, month = int(request.GET['year']), int(request.GET['month'])
        first = date(year, month, 1)
    except (KeyError, ValueError):
        raise Http404
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    days = {}
    for i in range((nxt - first).days):
        d = first + timedelta(days=i)
        slots = day_slots(resource, d)
        free = sum(1 for s in slots if s['state'] == 'free')
        days[d.isoformat()] = {'total': len(slots), 'free': free}
    return JsonResponse({'days': days})


@login_required
@require_POST
def book(request, pk):
    resource = get_object_or_404(Resource, pk=pk, is_active=True)
    try:
        tz = timezone.get_current_timezone()
        start = datetime.fromisoformat(request.POST['start'])
        end = datetime.fromisoformat(request.POST['end'])
        start = start if timezone.is_aware(start) else timezone.make_aware(start, tz)
        end = end if timezone.is_aware(end) else timezone.make_aware(end, tz)
        repeat = int(request.POST.get('repeat_weeks') or 0)
        created = create_bookings(request.user, resource, start, end, repeat,
                                  request.POST.get('notes', '')[:200])
    except (KeyError, ValueError):
        msg = 'Datos de reserva inválidos.'
        ok = False
    except BookingError as e:
        msg, ok = str(e), False
    else:
        msg, ok = f'✅ {len(created)} reserva(s) confirmada(s).', True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': ok, 'message': msg}, status=200 if ok else 400)
    (messages.success if ok else messages.error)(request, msg)
    return redirect('mis_reservas') if ok else redirect('recurso', pk=pk)


@login_required
def my_bookings(request):
    now = timezone.now()
    qs = Booking.objects.filter(user=request.user).select_related('resource')
    return render(request, 'reservas/my_bookings.html', {
        'upcoming': qs.filter(end__gte=now, status=Booking.Status.CONFIRMED),
        'past': qs.exclude(end__gte=now, status=Booking.Status.CONFIRMED).order_by('-start')[:30]})


@login_required
@require_POST
def cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user_id != request.user.id and not request.user.is_staff:
        raise Http404
    n = cancel_booking(booking, whole_series=request.POST.get('series') == '1')
    messages.success(request, f'Se cancelaron {n} reserva(s).')
    nxt = request.POST.get('next')
    if not nxt or not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        nxt = 'mis_reservas'
    return redirect(nxt)


staff_required = user_passes_test(lambda u: u.is_staff, login_url='login')


@staff_required
def dashboard(request):
    now = timezone.now()
    bookings = Booking.objects.select_related('resource', 'user')
    resource_id = request.GET.get('resource')
    if resource_id and resource_id.isdigit():
        bookings = bookings.filter(resource_id=resource_id)
    stats =  [{'resource': r, 'upcoming': r.bookings.filter(status='confirmed', start__gte=now).count()}
             for r in Resource.objects.all()]
    return render(request, 'reservas/dashboard.html', {
        'upcoming': bookings.filter(status='confirmed', end__gte=now)[:50],
        'stats': stats, 'resources': Resource.objects.all(),
        'total_users': Booking.objects.values('user').distinct().count(),
        'cancelled': Booking.objects.filter(status='cancelled').count(),
        'selected': resource_id})
