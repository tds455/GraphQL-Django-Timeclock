from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
import datetime
# Create your models here.

# Default Django user class is being used
class User(AbstractUser):
    pass

# Keeps a record of the duration and starting time of each shift
class TimeClock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)

    def returnhours(self):
        # Check the duration value of the currently provided record and return the duration as a rounded integer representing number of hours worked
        seconds = self.duration
        hours = round(seconds / 3600)
        return hours

# Time sheet tracks current status of user, i.e. if they are currently clocked in or not
class TimeSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clockedOut = models.DateTimeField(blank=True, null=True)
    clockedIn = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField()

    # Clock the provided timesheet in
    def clockin(self):
        # Take currenttime and enter it as clockIn time
        currenttime = datetime.datetime.now().replace(microsecond=0)
        # Update active status to true to show user is currently clocked in
        self.active = True
        self.clockedIn = currenttime
        # Reset clockout time
        self.clockedOut = None
        self.save()    

    # Clock the provided timesheet out and pass duration of shift to TimeClock model
    def clockout(self):
        # Take currenttime and enter it as clockOut time
        currenttime = datetime.datetime.now().replace(microsecond=0)
        # Update active status to true to show user is currently clocked out
        self.active = False
        self.clockedOut = currenttime
        self.save()

        # Take date and duration of the shift
        shiftdate = self.clockedIn
        duration = (self.clockedOut - self.clockedIn).total_seconds()

        # Pass values to a TimeClock object which will store the duration of the shift
        clock = TimeClock.objects.create(user=self.user, date=shiftdate, duration=duration)
        clock.save()