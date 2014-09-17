from django.db import models
from datetime import datetime, date
from django.core.exceptions import ValidationError

class Room(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField()
    description = models.CharField(max_length=140,default='')

    def __unicode__(self):
        return "{} {}".format(self.name, self.capacity)
    
    def free_slots(self):
        return TimeSlot.objects.filter(room=self)

class TimeSlot(models.Model):
    room = models.ForeignKey(Room)
    date = models.DateField()
    begin_time = models.TimeField()
    end_time = models.TimeField()
 
    def __unicode__(self):
        return "{} {} {}-{}".format(self.room.name, self.date, self.begin_time, self.end_time)

    def save(self, *args, **kwargs):
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
        self.clean()
        super(TimeSlot, self).save(*args, **kwargs)

    def clean(self):
        if self.begin_time >= self.end_time:
            raise ValidationError('Incorrect timespan')
        slots_set = TimeSlot.objects.filter(room=self.room, date=self.date)
        slots_set = slots_set.exclude(begin_time__gte=self.end_time)
        slots_set = slots_set.exclude(end_time__lte=self.begin_time)
        if slots_set.count() > 0:
            raise ValidationError('Overlapping free slots')
