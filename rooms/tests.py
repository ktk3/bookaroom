from django.test import TestCase
from rooms.models import *
from datetime import date, time
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class ModelsConstructorsTests(TestCase):
    def setUp(self):
        #populate database with simple data
        Room(name="TestRoom", capacity=20).save()
        User.objects.create_user(username='DummyUser', email='', password='x')

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
        fs1 = TimeSlot(room = room1, date = date(2014, 07, 10), 
            begin_time = time(9, 03, 01), end_time = time(12,00,01))
        fs1.save()
        self.assertEquals(fs1.begin_time.second, 0)
        self.assertEquals(fs1.begin_time.minute, 15)
        self.assertEquals(fs1.end_time.second, 0) 
        self.assertEquals(fs1.end_time.minute, 0) 
        fs2 = TimeSlot(room = room1, date = date(2014, 07, 10), 
            begin_time = time(9, 53, 01), end_time = time(12,45,01))
        self.assertRaises(ValidationError, fs2.save)
        fs2.date = fs2.date.replace(day=11)
        fs2.save()
        self.assertEquals(fs2.begin_time, time(10))
        self.assertEquals(fs2.end_time, time(12, 45))
        fs3 = TimeSlot(room = room1, date = date(2014, 07, 11), 
            begin_time = time(9, 30, 00), end_time = time(12,00,00))
        self.assertRaises(ValidationError, fs3.save)
        fs3.date = fs3.date.replace(day=12)
        fs3.save() 
        self.assertEquals(fs3.begin_time, time(9, 30, 00))
        self.assertEquals(fs3.end_time, time(12, 00, 00))
        self.assertEquals(TimeSlot.objects.all().count(), count + 3)

    def test_BookedTimeSlot_constructor(self):
        user = User.objects.get(username='DummyUser')
        count = BookedTimeSlot.objects.all().count()
        room1 = Room.objects.get(name="TestRoom")
        fs1 = BookedTimeSlot(user=user, room = room1, date = date(2014, 07, 10), begin_time = time(9, 03, 01), end_time = time(12,00,01))
        fs1.save()
        self.assertEquals(fs1.begin_time.second, 0)
        self.assertEquals(fs1.begin_time.minute, 0)
        self.assertEquals(fs1.end_time.second, 0) 
        self.assertEquals(fs1.end_time.minute, 15) 
        fs2 = BookedTimeSlot(user=user, room = room1, date = date(2014, 07, 10), begin_time = time(9, 53, 01), end_time = time(12,45,01))
        self.assertRaises(ValidationError, fs2.save)
        fs2.date = fs2.date.replace(day=11)
        fs2.save()
        self.assertEquals(fs2.begin_time, time(9, 45, 00))
        self.assertEquals(fs2.end_time, time(13, 00, 00))
        fs3 = BookedTimeSlot(user=user, room = room1, date = date(2014, 07, 11), begin_time = time(9, 30, 00), end_time = time(12,00,00))
        self.assertRaises(ValidationError, fs3.save)
        fs3.date = fs3.date.replace(day=12)
        fs3.save() 
        self.assertEquals(fs3.begin_time, time(9, 30, 00))
        self.assertEquals(fs3.end_time, time(12, 00, 00))
        self.assertEquals(BookedTimeSlot.objects.all().count(), count + 3)

    def test_TimeSlot_BookedTimeSlot_validation(self):
        user = User.objects.get(username='DummyUser')
        count_fs = TimeSlot.objects.all().count()
        count_bs = BookedTimeSlot.objects.all().count()
        room = Room.objects.get(name="TestRoom")
        date1 = date(2014, 07, 10)
        fs1 = TimeSlot(room = room, date = date1, begin_time = time(9), end_time = time(12))
        fs1.save()
        fs2 = BookedTimeSlot(user=user, room = room, date = date1, begin_time = time(9), end_time = time(11))
        self.assertRaises(ValidationError, fs2.save)
        fs2.begin_time = fs2.begin_time.replace(hour=13)
        fs2.end_time = fs2.end_time.replace(hour=14)
        fs2.save()
        fs3 = TimeSlot(room = room, date = date1, begin_time = time(13), end_time = time(15))
        self.assertRaises(ValidationError, fs3.save)
        fs3.begin_time = fs3.begin_time.replace(hour=14)
        fs3.save()

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

class BookFunctionsTests(TestCase):
    def setUp(self):
        #populate database with simple data
        room1 = Room(name="TestRoom", capacity=20)
        room1.save()
        TimeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9, 00, 00), end_time = time(17,00,00)).save()
        User.objects.create_user(username='DummyUser', email='', password='x')

    def test_book_new_slot_simple(self):
        user = User.objects.get(username='DummyUser')
        count_bs = BookedTimeSlot.objects.all().count()
        count_fs = TimeSlot.objects.all().count()
        ts = TimeSlot.objects.filter(room=Room.objects.get(name="TestRoom"))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        begin = time(9)
        end = time(11)
        bs = book_new_slot(ts0, user, begin, end)
        self.assertEquals(BookedTimeSlot.objects.all().count(), count_bs + 1)
        self.assertEquals(TimeSlot.objects.all().count(), count_fs)
        ts0 = ts[0]
        self.assertEquals(ts0.begin_time, time(11))
        self.assertEquals(ts0.end_time, time(17))
        bts = BookedTimeSlot.objects.filter(user=user)
        self.assertEquals(bts.count(), 1)
        bts0 = bts[0]
        self.assertEquals(bts0.begin_time, time(9))
        self.assertEquals(bts0.end_time, time(11))
        self.assertEquals(bs, bts0)

    def test_book_new_slot_middle(self):
        user = User.objects.get(username='DummyUser')
        count_bs = BookedTimeSlot.objects.all().count()
        count_fs = TimeSlot.objects.all().count()
        begin1 = time(10)
        end1 = time(11)
        begin2 = time(14)
        end2 = time(16)
        ts = TimeSlot.objects.filter(room=Room.objects.get(name="TestRoom"))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        bs1 = book_new_slot(ts0, user, begin1, end1)
        self.assertEquals(ts.count(), 2)
        ts0 = ts.get(begin_time=end1)
        bs2 = book_new_slot(ts0, user, begin2, end2)
        self.assertEquals(TimeSlot.objects.all().count(), count_fs + 2)  
        ts0 = ts.get(end_time=begin1)
        self.assertEquals(ts0.begin_time, time(9))
        ts1 = ts.get(begin_time=end1)
        self.assertEquals(ts1.end_time, begin2)
        ts2 = ts.get(begin_time=end2)
        self.assertEquals(ts2.end_time, time(17))
        bts = BookedTimeSlot.objects.filter(user=user)
        self.assertEquals(bts.count(), 2)
        bts0 = bts[0]
        self.assertEquals(bts0.begin_time, begin1)
        self.assertEquals(bts0.end_time, end1)
        bts1 = bts[1]
        self.assertEquals(bts1.begin_time, begin2)
        self.assertEquals(bts1.end_time, end2)
        self.assertEquals(bs1, bts0)
        self.assertEquals(bs2, bts1)

class JointAdjacentSlotsTests(TestCase):
    def setUp(self):
        room1 = Room(name="TestRoom", capacity=20)
        room1.save()
        User.objects.create_user(username='DummyUser', email='', password='x')

    def test_join_with_previous_TimeSlot(self):
        room = Room.objects.get(name="TestRoom")
        ts0 = TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(9), end_time = time(12))
        count = TimeSlot.objects.filter(room=room).count()
        ts1 = TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(12), end_time = time(14))
        self.assertEquals(TimeSlot.objects.filter(room=room).count(), count)
        self.assertEquals(ts1.begin_time, time(9))
        self.assertEquals(ts1.end_time, time(14))

    def test_join_with_next_TimeSlot(self):
        room = Room.objects.get(name="TestRoom")
        ts0 = TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(14), end_time = time(16))
        count = TimeSlot.objects.filter(room=room).count()
        ts1 = TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(12), end_time = time(14))
        self.assertEquals(TimeSlot.objects.filter(room=room).count(), count)
        self.assertEquals(ts1.begin_time, time(12))
        self.assertEquals(ts1.end_time, time(16))

    def test_join_with_prev_and_next(self):
        room = Room.objects.get(name="TestRoom")
        TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(14), end_time = time(16))
        TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(9), end_time = time(12))
        count = TimeSlot.objects.filter(room=room).count()
        ts1 = TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(12), end_time = time(14))
        self.assertEquals(TimeSlot.objects.filter(room=room).count(), count - 1)
        self.assertEquals(ts1.begin_time, time(9))
        self.assertEquals(ts1.end_time, time(16))

    def test_book_and_unbook(self):
        user = User.objects.get(username='DummyUser')
        room = Room.objects.get(name="TestRoom")
        ts =TimeSlot.objects.create(room = room, date = date(2014, 07, 10), 
            begin_time = time(9), end_time = time(16))
        count = TimeSlot.objects.filter(room=room).count()
        bs = book_new_slot(ts, user, time(11), time(13))
        self.assertEquals(TimeSlot.objects.filter(room=room).count(), count + 1)
        bs.unbook()
        self.assertEquals(TimeSlot.objects.filter(room=room).count(), count)
        ts1 = TimeSlot.objects.filter(room=room, date = date(2014, 07, 10))
        self.assertEquals(ts1.count(), 1)
        self.assertEquals(ts1[0].begin_time, time(9))
        self.assertEquals(ts1[0].end_time, time(16))

class MoreBookTests(TestCase):
    def setUp(self):
        #populate database with simple data
        room1 = Room(name="TestRoom", capacity=20)
        room1.save()
        TimeSlot(room = room1, date = date(2014, 07, 10), begin_time = time(9), end_time = time(17)).save()
        User.objects.create_user(username='DummyUser', email='', password='x')

    def test_book_unbook_many(self):
        user = User.objects.get(username='DummyUser')
        count_bs = BookedTimeSlot.objects.all().count()
        count_fs = TimeSlot.objects.all().count()
        ts = TimeSlot.objects.filter(room=Room.objects.get(name="TestRoom"))
        self.assertEquals(ts.count(), 1)
        ts0 = ts[0]
        begin1 = time(12)
        end1 = time(13)
        begin2 = time(15)
        end2 = time(16)
        begin3 = time(13)
        end3 = time(14,10   )
        bs = book_new_slot(ts0, user, begin1, end1)
        self.assertEquals(BookedTimeSlot.objects.all().count(), count_bs + 1)
        self.assertEquals(TimeSlot.objects.all().count(), count_fs + 1)
        ts0 = ts[0]
        self.assertEquals(ts0.begin_time, time(9))
        self.assertEquals(ts0.end_time, begin1)
        bts = BookedTimeSlot.objects.filter(user=user)
        self.assertEquals(bts.count(), 1)
        bts0 = bts[0]
        bs.unbook()
        self.assertEquals(BookedTimeSlot.objects.all().count(), count_bs)
        self.assertEquals(TimeSlot.objects.all().count(), count_fs)
        ts0 = ts[0]
        self.assertEquals(ts0.begin_time, time(9))
        self.assertEquals(ts0.end_time, time(17))
        bs1 = book_new_slot(ts0, user, begin1, end1)
        ts0 = ts.get(begin_time=end1)
        bs2 = book_new_slot(ts0, user, begin2, end2)
        self.assertEquals(TimeSlot.objects.all().count(), count_fs + 2)
        ts0 = ts.get(end_time=begin2)
        bs3 = book_new_slot(ts0, user, begin3, end3)

