"""
Definition of models.
"""

from django.db import models

# Create your models here.
class ContactInfo(models.Model):
    ###########################Form Related Columns#######################
    FirstName                   =models.CharField(max_length=255, null=True, blank=True) 
    LastName                    =models.CharField(max_length=255, null=True, blank=True)       
    Email                       =models.EmailField(max_length=255, null=True, blank=True)
    PhoneNumber                 =models.CharField(max_length=255, null=True, blank=True)
    Address1                    =models.CharField(max_length=255, null=True, blank=True)
    Address2                    =models.CharField(max_length=255, null=True, blank=True)
    City                        =models.CharField(max_length=12, null=True, blank=True)
    State                       =models.CharField(max_length=255, null=True, blank=True)
    Zipcode                     =models.CharField(max_length=255, null=True, blank=True)
    Country                     =models.CharField(max_length=255, null=True, blank=True)
    Link_Linkedin               =models.URLField(max_length=500, null=True, blank=True)
    Link_Linkedin_Name          =models.CharField(max_length=255, null=True, blank=True)
    Link_Linkedin_Comment       =models.CharField(max_length=1000, null=True, blank=True)
    Link_Linkedin_Embed         =models.CharField(max_length=4000, null=True, blank=True)
    Link_Github                 =models.URLField(max_length=500, null=True, blank=True)
    Link_Github_Name            =models.CharField(max_length=255, null=True, blank=True)
    Link_Github_Comment         =models.CharField(max_length=1000, null=True, blank=True)
    Link_Github_Embed           =models.CharField(max_length=4000, null=True, blank=True)
    Link_DataViz                =models.URLField(max_length=500, null=True, blank=True)
    Link_DataViz_Name           =models.CharField(max_length=255, null=True, blank=True)
    Link_DataViz_Comment        =models.CharField(max_length=1000, null=True, blank=True)
    Link_DataViz_Embed          =models.CharField(max_length=4000, null=True, blank=True)
    Link_Website                =models.URLField(max_length=500, null=True, blank=True)
    Link_Website_Name           =models.CharField(max_length=255, null=True, blank=True)
    Link_Website_Comment        =models.CharField(max_length=1000, null=True, blank=True)
    Link_Website_Embed          =models.CharField(max_length=4000, null=True, blank=True)
    Resume                      =models.FileField(max_length=255, upload_to='media/', null=True, blank=True)
    Picture                     =models.ImageField(max_length=255, upload_to='images/', null=True, blank=True)
    PictureLink                 =models.URLField(max_length=500, null=True, blank=True)
    Embedded_Code               =models.CharField(max_length=8000, null=True, blank=True)
    Comments                    =models.CharField(max_length=4000, null=True, blank=True)
    Current_Title               =models.CharField(max_length=255, null=True, blank=True)
    Current_Employeer           =models.CharField(max_length=255, null=True, blank=True)

class Usecases(models.Model):
    Title                       =models.CharField(max_length=500, null=True, blank=True)
    Description                 =models.CharField(max_length=4000, null=True, blank=True)
    Modifications               =models.CharField(max_length=4000, null=True, blank=True)
    PictureLink                 =models.URLField(max_length=500, null=True, blank=True)
    Active                      =models.CharField(max_length=255, null=True, blank=True)