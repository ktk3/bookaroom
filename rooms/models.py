from django.db import models
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField()
    description = models.CharField(max_length=140,default='')

    def __unicode__(self):
        return "{} {}".format(self.name, self.capacity)
    
    def free_slots(self):
        return TimeSlot.objects.filter(room=self)

    def clean(self):
        if self.capacity <= 0:
            raise ValidationError('Room capacity has to be > 0')

    def save (self, *args, **kwargs):
        self.clean()
        super(Room, self).save(*args, **kwargs)

class AbstractTimeSlot(models.Model):
    class Meta:
        abstract = True
    room = models.ForeignKey(Room)
    date = models.DateField()
    begin_time = models.TimeField()
    end_time = models.TimeField()
 
    def clean(self):
        if self.begin_time >= self.end_time:
            raise ValidationError('Incorrect timespan')
        slots_set = TimeSlot.objects.filter(room=self.room, date=self.date)
        slots_set = slots_set.exclude(begin_time__gte=self.end_time)
        slots_set = slots_set.exclude(end_time__lte=self.begin_time)
        if slots_set.count() > 0:
            raise ValidationError('Overlapping free slots')
        bs_set = BookedTimeSlot.objects.filter(room=self.room, date=self.date)
        bs_set = bs_set.exclude(begin_time__gte=self.end_time)
        bs_set = bs_set.exclude(end_time__lte=self.begin_time)
        if bs_set.count() > 0:
            raise ValidationError('Overlapping booked slots')

class TimeSlot(AbstractTimeSlot):

    def round_time(self, *args, **kwargs):
        self.end_time=self.end_time.replace(second=0)
        if self.end_time.minute < 15:
            self.end_time=self.end_time.replace(minute=0)
        else:
            if self.end_time.minute < 30:
                self.end_time=self.end_time.replace(minute=15)
            else: 
                if self.end_time.minute < 45:
                    self.end_time=self.end_time.replace(minute=30)
                else: 
                    self.end_time=self.end_time.replace(minute=45)
        if self.begin_time.second > 0: 
            if self.begin_time.minute == 59:
                self.begin_time=self.begin_time.replace(hour=self.begin_time.hour+1, minute=0, second=0)
            else:
                self.begin_time=self.begin_time.replace(minute=self.begin_time.minute+1, second=0)
        if self.begin_time.minute > 45:
            self.begin_time=self.begin_time.replace(hour=self.begin_time.hour+1, minute=0)
        else:
            if self.begin_time.minute > 30:
                self.begin_time=self.begin_time.replace(minute=45)
            else:
                if self.begin_time.minute > 15:
                    self.begin_time=self.begin_time.replace(minute=30)
                else:
                    if self.begin_time.minute > 0:
                        self.begin_time=self.begin_time.replace(minute=15)

 
    def __unicode__(self):
        return "{}: {} {} {}-{}".format(self.id, self.room.name, self.date, self.begin_time, self.end_time)

    def save(self, *args, **kwargs):
        self.round_time(*args, **kwargs)
        self.clean()
        #check if slot can be joined with adjacent slots
        prev_slot = TimeSlot.objects.filter(room=self.room, date=self.date,
            end_time=self.begin_time)
        if prev_slot:
            prev_slot[0].delete()
            self.begin_time = prev_slot[0].begin_time
        next_slot = TimeSlot.objects.filter(room=self.room, date=self.date,
            begin_time=self.end_time)
        if next_slot:
            next_slot[0].delete()
            self.end_time = next_slot[0].end_time
        super(TimeSlot, self).save(*args, **kwargs)

    def book(self, begin, end):
        #verify arguments
        if begin >= end :
            raise ValidationError('Incorrect timespan')
        if begin < self.begin_time or end > self.end_time:
            raise ValidationError('Time not within timeslot')
        self.delete()
        #check if there is time left in TimeSlot
        if begin > self.begin_time:
            TimeSlot.objects.create(room=self.room, date=self.date, begin_time=self.begin_time, end_time=begin)
        if end < self.end_time:
            TimeSlot.objects.create(room=self.room, date=self.date, begin_time=end, end_time=self.end_time)

class BookedTimeSlot(AbstractTimeSlot):

    def round_time(self, *args, **kwargs):
        self.begin_time=self.begin_time.replace(second=0)
        if self.begin_time.minute < 15:
            self.begin_time=self.begin_time.replace(minute=0)
        else:
            if self.begin_time.minute < 30:
                self.begin_time=self.begin_time.replace(minute=15)
            else: 
                if self.begin_time.minute < 45:
                    self.begin_time=self.begin_time.replace(minute=30)
                else: 
                    self.begin_time=self.begin_time.replace(minute=45)
        if self.end_time.second > 0: 
            if self.end_time.minute == 59:
                self.end_time=self.end_time.replace(hour=self.end_time.hour+1, minute=0, second=0)
            else:
                self.end_time=self.end_time.replace(minute=self.end_time.minute+1, second=0)
        if self.end_time.minute > 45:
            self.end_time=self.end_time.replace(hour=self.end_time.hour+1, minute=0)
        else:
            if self.end_time.minute > 30:
                self.end_time=self.end_time.replace(minute=45)
            else:
                if self.end_time.minute > 15:
                    self.end_time=self.end_time.replace(minute=30)
                else:
                    if self.end_time.minute > 0:
                        self.end_time=self.end_time.replace(minute=15)

    user = models.ForeignKey(User)
    def __unicode__(self):
        return "{}: {} {} {} {}-{}".format( self.id, self.user, self.room.name, self.date, self.begin_time, self.end_time)

    def save(self, *args, **kwargs):
        self.round_time(*args, **kwargs)
        self.clean()
        super(BookedTimeSlot, self).save(*args, **kwargs)

    def unbook(self):
        self.delete()
        #add as a new free slot
        TimeSlot(room=self.room, date=self.date, begin_time=self.begin_time,
            end_time=self.end_time).save()

def book_new_slot(slot, user, begin, end):
    slot.book(begin, end)
    bs = BookedTimeSlot.objects.create(room=slot.room, date=slot.date, 
        begin_time=begin, end_time=end, user=user)
    return bs