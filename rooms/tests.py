from django.test import TestCase
from rooms.models import *
from datetime import date, time

class ModelsConstructorsTests(TestCase):
    def setUp(self):
        #populate database with simple data
        Room(name="TestRoom", capacity=20).save()

    def test_Room_constructor(self):
        self.assertEqual(Room.objects.all().count(), 1)

    def test_FreeSlot_hour_conversions(self):
        room1 = Room.objects.get(name="TestRoom")
        fs1 = FreeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 03, 01), end_time = time(12,00,01))
        fs1.save()
        self.assertEquals(fs1.begin_time.second, 0)
        self.assertEquals(fs1.begin_time.minute, 0)
        self.assertEquals(fs1.end_time.second, 0) 
        self.assertEquals(fs1.end_time.minute, 15) 
        fs2 = FreeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 53, 01), end_time = time(12,45,01))
        fs2.save() 
        self.assertEquals(fs2.begin_time, time(9, 45, 00))
        self.assertEquals(fs2.end_time, time(13, 00, 00))
        fs3 = FreeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 30, 00), end_time = time(12,00,00))
        fs3.save() 
        self.assertEquals(fs3.begin_time, time(9, 30, 00))
        self.assertEquals(fs3.end_time, time(12, 00, 00))
