from django.test import TestCase
from rooms.models import *
from datetime import date, time
from django.core.exceptions import ValidationError

class ModelsConstructorsTests(TestCase):
    def setUp(self):
        #populate database with simple data
        Room(name="TestRoom", capacity=20).save()

    def test_Room_constructor(self):
        count = Room.objects.all().count()
        Room(name="TestRoom2", capacity=1).save()
        self.assertEqual(Room.objects.all().count(), count + 1)
        tr = Room(name="TestRoom3", capacity=0)
        self.assertRaises(ValidationError, tr.save)
        self.assertEqual(Room.objects.all().count(), count + 1)
        Room.objects.create(name="lion", capacity=2)
        self.assertEqual(Room.objects.all().count(), count + 2)

    def test_TimeSlot_constructor(self):
        count = TimeSlot.objects.all().count()
        room1 = Room.objects.get(name="TestRoom")
        fs1 = TimeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 03, 01), end_time = time(12,00,01))
        fs1.save()
        self.assertEquals(fs1.begin_time.second, 0)
        self.assertEquals(fs1.begin_time.minute, 0)
        self.assertEquals(fs1.end_time.second, 0) 
        self.assertEquals(fs1.end_time.minute, 15) 
        fs2 = TimeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 53, 01), end_time = time(12,45,01))
        self.assertRaises(ValidationError, fs2.save)
        fs2.date = fs2.date.replace(day=11)
        fs2.save()
        self.assertEquals(fs2.begin_time, time(9, 45, 00))
        self.assertEquals(fs2.end_time, time(13, 00, 00))
        fs3 = TimeSlot(room = room1, date = date(2014, 07, 11), begin_time = time(9, 30, 00), end_time = time(12,00,00))
        self.assertRaises(ValidationError, fs3.save)
        fs3.date = fs3.date.replace(day=12)
        fs3.save() 
        self.assertEquals(fs3.begin_time, time(9, 30, 00))
        self.assertEquals(fs3.end_time, time(12, 00, 00))
        self.assertEquals(TimeSlot.objects.all().count(), count + 3)

class BookTimeSlotTests(TestCase):
    def setUp(self):
        #populate database with simple data
        room1 = Room(name="TestRoom", capacity=20)
        room1.save()
        TimeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 00, 00), end_time = time(17,00,00)).save()

    def test_book_incorrect_input_arguments(self):
        ts = TimeSlot.objects.get(room=Room.objects.get(name="TestRoom"))
        self.assertRaises(ValidationError, ts.book, time(12), time(11))
        self.assertRaises(ValidationError, ts.book, time(12), time(12))
        self.assertRaises(ValidationError, ts.book, time(8), time(12))
        self.assertRaises(ValidationError, ts.book, time(6), time(8))
        self.assertRaises(ValidationError, ts.book, time(16), time(18))
        self.assertRaises(ValidationError, ts.book, time(17,30), time(18))

    def test_book_full_slot(self):
        ts = TimeSlot.objects.get(room=Room.objects.get(name="TestRoom"))
        count = TimeSlot.objects.all().count()
        ts.book(time(9), time(17))
        self.assertEquals(TimeSlot.objects.all().count(), count - 1)

    def test_book_to_end(self):
        ts = TimeSlot.objects.filter(room=Room.objects.get(name="TestRoom"))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        ts0.book(time(12), time(17))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        self.assertEquals(ts0.begin_time, time(9))
        self.assertEquals(ts0.end_time, time(12))

    def test_book_from_beginning(self):
        ts = TimeSlot.objects.filter(room=Room.objects.get(name="TestRoom"))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        ts0.book(time(9), time(12))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        self.assertEquals(ts0.begin_time, time(12))
        self.assertEquals(ts0.end_time, time(17))

    def test_book_in_middle(self):
        ts = TimeSlot.objects.filter(room=Room.objects.get(name="TestRoom"))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        ts0.book(time(12), time(13,30))
        self.assertEquals(ts.count(), 2)
        ts0 = ts[0]
        self.assertEquals(ts0.begin_time, time(9))
        self.assertEquals(ts0.end_time, time(12))
        ts1 = ts[1]
        self.assertEquals(ts1.begin_time, time(13,30))
        self.assertEquals(ts1.end_time, time(17))