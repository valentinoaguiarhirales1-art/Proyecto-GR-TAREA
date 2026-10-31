from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Availability, Booking, Resource
from .services import BookingError, cancel_booking, create_bookings


class BookingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('ana', 'ana@x.com', 'pw12345678')
        self.other = get_user_model().objects.create_user('leo', password='pw12345678')
        self.res = Resource.objects.create(name='Pista', slot_minutes=60)
        for wd in range(7):
            Availability.objects.create(resource=self.res, weekday=wd, start_time='08:00', end_time='23:00')
        base = timezone.localtime() + timedelta(days=2)
        self.start = base.replace(hour=10, minute=0, second=0, microsecond=0)
        self.end = self.start + timedelta(hours=1)

    def test_creates_booking(self):
        self.assertEqual(len(create_bookings(self.user, self.res, self.start, self.end)), 1)

    def test_overlap_rejected(self):
        create_bookings(self.user, self.res, self.start, self.end)
        with self.assertRaises(BookingError):
            create_bookings(self.other, self.res, self.start + timedelta(minutes=30), self.end + timedelta(minutes=30))

    def test_adjacent_allowed(self):
        create_bookings(self.user, self.res, self.start, self.end)
        create_bookings(self.other, self.res, self.end, self.end + timedelta(hours=1))
        self.assertEqual(Booking.objects.count(), 2)

    def test_recurring_creates_series(self):
        created = create_bookings(self.user, self.res, self.start, self.end, repeat_weeks=3)
        self.assertEqual(len(created), 4)
        self.assertEqual(len({b.recurrence_id for b in created}), 1)

    def test_recurring_is_all_or_nothing(self):
        create_bookings(self.other, self.res, self.start + timedelta(weeks=2), self.end + timedelta(weeks=2))
        with self.assertRaises(BookingError):
            create_bookings(self.user, self.res, self.start, self.end, repeat_weeks=3)
        self.assertEqual(Booking.objects.count(), 1)

    def test_outside_hours_and_past_rejected(self):
        with self.assertRaises(BookingError):
            create_bookings(self.user, self.res, self.start.replace(hour=3), self.start.replace(hour=4))
        with self.assertRaises(BookingError):
            create_bookings(self.user, self.res, self.start - timedelta(days=10), self.end - timedelta(days=10))

    def test_cancel_series_frees_slots(self):
        first = create_bookings(self.user, self.res, self.start, self.end, repeat_weeks=2)[0]
        self.assertEqual(cancel_booking(first, whole_series=True), 3)
        create_bookings(self.other, self.res, self.start, self.end)

    def test_views(self):
        self.assertEqual(self.client.get(reverse('recursos')).status_code, 200)
        day = self.start.date().isoformat()
        r = self.client.get(reverse('slots', args=[self.res.pk]), {'date': day})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(len(r.json()['slots']) > 0)
        self.assertEqual(self.client.post(reverse('reservar', args=[self.res.pk])).status_code, 302)

    def test_only_owner_cancels_and_panel_is_staff_only(self):
        b = create_bookings(self.user, self.res, self.start, self.end)[0]
        self.client.login(username='leo', password='pw12345678')
        self.assertEqual(self.client.post(reverse('cancelar', args=[b.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('panel')).status_code, 302)
