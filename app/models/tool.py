from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import Resize
from app.models.shed import Shed
import app.constants

class Tool(models.Model):
    class Meta:
        app_label = 'app'

    def toolPictureName(instance, filename):
        ext = filename.split('.')[-1]
        return 'toolpics/{}.{}'.format(instance.name, ext)

    name = models.CharField(max_length=25)
    picture = ProcessedImageField(processors=[Resize(500, 500)], format='JPEG', upload_to=toolPictureName)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=1, choices=app.constants.TOOL_STATUS)
    category = models.CharField(max_length=2, choices=app.constants.TOOL_CATEGORY)
    location = models.CharField(max_length=1, choices=app.constants.TOOL_LOCATION, blank=False, default='H')
    models.CharField()
    shed = models.ForeignKey(Shed, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    pickupArrangement = models.TextField(max_length=500)

    def __str__(self):
        return self.name

    # returns a query of reservations on the tool based on the reservation_status arg (A, O, AC, R, C, etc.)
    def get_reservations (self, reservation_status):
        reservations = self.reservation_set.filter(status = reservation_status)
        return reservations

    # Checks if tool has unresolved future reservations that prevent it from moving
    # Returns true if no unresolved future reservations on it, false otherwise
    def is_ready_to_move(self):
        # Keeps a count of all reservations that might be interfering with moving a tool.
        blockingReservations = 0

        # Checks tool for any active reservations
        activeReservations = self.get_reservations('AC')
        blockingReservations = blockingReservations + len(activeReservations)

        # Checks tool for approved future reservations
        approvedReservations = self.get_reservations('A')
        blockingReservations = blockingReservations + len(approvedReservations)

        # Add additional reservations that might block tool from moving here


        # Check the sum of the lengths of the reservation lists described above.
        # If sum is zero (no blocking reservations), return ready_to_move = True. Else, return ready_to_move = False
        if blockingReservations == 0:
            return True
        else:
            return False

    @property
    def address(self):
        if self.location == 'S':
            return self.shed.address
        return self.owner.address


class BlackoutDate(models.Model):
    class Meta:
        app_label = 'app'

    tool = models.ForeignKey(Tool)
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()