from django.core.exceptions import ValidationError
from rooms.models import *

def validate_dummy_slot(slot_id):
    print slot_id
    slot = TimeSlot.objects.get(id=slot_id)
    print slot
    slots = TimeSlot.objects.filter(room=slot.room, date=slot.date)
    print slots
    #if value % 2 != 0:
    #    raise ValidationError(u'%s is not an even number' % value)

def validate_free_slot(slot):
	free_slots = slot.room.free_slots.all
	print free_slots

def validate_create_free_slot(slot):
	for s in TimeSlot.objects.filter(room=slot.room, date=slot.date):
		if (s.begin_time <= slot.begin_time and s.end_time > slot.begin_time) \
		or (s.begin_time >= slot.begin_time and s.end_time < slot.end_time):
			raise ValidationError('Collision with another free slot')
