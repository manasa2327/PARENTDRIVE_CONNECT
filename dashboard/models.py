from typing import Any
from django.db import models
from datetime import datetime


class ParentTable(models.Model):
    
    ParentName=models.CharField(max_length=500)
    DriverName=models.CharField(max_length=500,primary_key=True)
    #speeddriver=models.ForeignKey('SpeedDriver',on_delete=models.CASCADE)
    ParentEmail=models.EmailField()
    Password=models.TextField()
    ConfirmPassword=models.TextField()
    class Meta:
        db_table="ParentTable"



class SpeedDriver(models.Model):
    Speed_ID=models.AutoField(primary_key=True)
    Drivername = models.ForeignKey('ParentTable', on_delete=models.SET_NULL, null=True, related_name='speed_drivers')
    Date=models.DateTimeField(default=datetime.now,blank=True,unique=False)
    latitude=models.FloatField()
    longitude=models.FloatField()
    target_speed=models.FloatField()
    class Meta:
        db_table="SpeedDriver"

class Results(models.Model):
    Results_ID=models.AutoField(primary_key=True)
    Driver_Name = models.ForeignKey('ParentTable', on_delete=models.SET_NULL, null=True, related_name='Results_drivers')
    DrivingDate=models.DateTimeField(default=datetime.now,blank=True,unique=False)
    latitude=models.FloatField()
    longitude=models.FloatField()
    target_speed=models.FloatField()
    Max_speed=models.FloatField()
    Route=models.TextField()
    Overspeed=models.BooleanField()
    Count_overspeed=models.IntegerField()
    class Meta:
        db_table="Results"

class ParentDashboard(models.Model):
    ParentDashboard_ID=models.AutoField(primary_key=True)
    Driver_name = models.ForeignKey('ParentTable', on_delete=models.SET_NULL, null=True, related_name='Dashboard_drivers')
    DriveDate=models.DateTimeField(default=datetime.now)
    StartAddress=models.TextField()
    EndAddress=models.TextField()
    Countofoverspeed=models.IntegerField()
    Duration=models.IntegerField(null=True)
    class Meta:
        db_table="ParentDashboard"






