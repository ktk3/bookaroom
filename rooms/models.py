from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.IntegerField()
    description = models.CharField(max_length=140,default='')

    def __unicode__(self):
        return "{} {}".format(self.name, self.capacity)
    
    def free_slots(self):
        return FreeSlot.objects.filter(room=self)

class FreeSlot(models.Model):
    room = models.ForeignKey(Room)
    date = models.DateField()
    begin_time = models.TimeField()
    end_time = models.TimeField()
 
    def __unicode__(self):
        return "{} {} {}-{}".format(self.room.name, self.date, self.begin_time, self.end_time)
