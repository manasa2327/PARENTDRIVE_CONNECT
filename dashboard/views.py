from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import ParentTable
from .models import SpeedDriver,ParentDashboard,Results
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth import authenticate
import requests
from django.http import StreamingHttpResponse
from django.template import Context,Template
import json
from datetime import datetime
import folium
import time
import overpy
import re
import threading
from django.contrib.auth.forms import SetPasswordForm
from django import forms

class CustomSetPasswordForm(SetPasswordForm):
    email = forms.EmailField()
    driver_name=forms.CharField()


# Create your views here.
email_sent = False

# Define a function to send the email
def send_email(Parentemail,driver):
    global email_sent
    htmly = get_template('Alert_Email.html')
    d = {'username': driver}
    subject, from_email, to = 'Speeding Alert', 'manasa2327@gmail.com', Parentemail
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    # Set the flag to True after sending email
    #email_sent = True
    # Schedule to reset the flag after 5 minutes
    #threading.Timer(300, reset_email_flag).start()

# Function to reset the email_sent flag after 5 minutes
def reset_email_flag():
    global email_sent
    email_sent = False

def signup_view(request):
    if request.method=='POST':
        Pname=request.POST.get('parentname')
        Dname=request.POST.get('drivername')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if ParentTable.objects.filter(DriverName=Dname).exists():
            messages.error(request, 'An account with this Driver already exists. Please choose a different Driver or select forget password')
        elif ParentTable.objects.filter(ParentName=Pname,DriverName=Dname).exists():
            messages.error(request, 'An account with this parent with same driver already exists. Please select forget password')
        elif pass1!=pass2:
            messages.error(request,'Your password and confirm password are not Same!!')
            #return HttpResponse("Your password and confirm password are not Same!!")
        elif (Pname == "" )or (Dname == "")or(email == "")or(pass1 == "")or(pass2 == ""):
             messages.error(request,'Enter all the inputs')
            #return HttpResponse("enter all the inputs")
        elif len(pass1)<8:
             messages.error(request,'Atleast 1 Alphabet is expected in the password\
                           Atleast 1 Number is expected in passsword\
                           password should contain minimum of 8 characters ')
             #return HttpResponse("length is less than 8")
        elif not any(char.isalpha() for char in pass1):
             messages.error(request,'Atleast 1 Alphabet is expected in the password\
                           Atleast 1 Number is expected in passsword\
                           password should contain minimum of 8 characters ')
             #return HttpResponse("Atleast 1 letter ")
        elif not any(char.isdigit() for char in pass1):
             messages.error(request,'Atleast 1 Alphabet is expected in the password\
                           Atleast 1 Number is expected in passsword\
                           password should contain minimum of 8 characters ')
             #return HttpResponse("Atleast 1 digit ")
        else:
            parent=ParentTable(ParentName=Pname,DriverName=Dname,Password=pass1,ConfirmPassword=pass2,ParentEmail=email)
            parent.save()
            #############################################################
            htmly = get_template('Email.html')
            d = { 'username': Pname }
            subject, from_email, to = 'welcome', 'manasa2327@gmail.com', email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            ################################################################
            messages.success(request,'your account created, click here to login:')
            #return redirect('login')
            
        
    return render(request,'signup.html')

def login(request):
     
    return render(request,'login.html')
    

       
    
    
def Driver(request):
     pass
   

def index(request):
    return render(request,'index.html')
def parentdashboard(request):
    val1=request.GET["parentname"]
    
    val2=request.GET["password1"]
    if (val1 == "" )or (val2 == ""):
             messages.error(request,'Enter all the inputs')
             return redirect('login')
    try:
        user=ParentTable.objects.get(ParentName=val1,Password=val2)

        
        dashboards=ParentDashboard.objects.filter(Driver_name=user.DriverName)
        

        
        return render(request,'parentdashboard.html',context=({'parentname':user.ParentName,'Driver':user.DriverName,'dashboards':dashboards}))
    except ParentTable.DoesNotExist:
         messages.error(request, "Invalid Username or password")
         return redirect('login')
    
def get_unique_datetimes_for_driver(driver_name):
    # Filter the DrivingDetails queryset to get instances where the driver name is 'manasa'
    driving_details = SpeedDriver.objects.filter(Drivername=driver_name)

    # Get unique datetime values
    unique_datetimes = driving_details.values_list('Date', flat=True).distinct()

    # Return the unique datetime values
    return unique_datetimes




   
            
def generate_response(request): 
        if request.method == 'POST':
        # Get the value of 'driver' from the POST request
            driver = request.POST.get('Driver')
        unique_datetimes = get_unique_datetimes_for_driver(driver)
        existing_dates = ParentDashboard.objects.values_list('DriveDate', flat=True)
        print(unique_datetimes,existing_dates)
        missing_dates = [date for date in unique_datetimes if date not in existing_dates]
        if missing_dates:
            print("--------------------------------------------------------------")
            for date in missing_dates:
                print("--------------------------------------------------------------")
                drivers=SpeedDriver.objects.filter(Drivername=driver,Date=date)
                print("--------------------------------------------------------------",driver, date)
                driver_instance = ParentTable.objects.get(DriverName=driver)
                Parentemail=driver_instance.ParentEmail
                address_components = []
                max_speed=None
                overspeeding=[] 
                consecutive_overspeed_count = 0
                overspeeding_count=0
                alerts=0
                duration=0
                for x in drivers:
                    duration=duration+1
                    print("--------------------------------------------------------------")
                    overspeeding_bool=False
                    print("____________________________________long,lan______________",x.latitude,x.longitude)
                    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={x.latitude},{x.longitude}&result_type=route&key=AIzaSyDh_xMoFxU7jEDAgyorFBN2bGPfdpm7SHI"
                
                    #response_API = requests.get(url).json()
                    response_API = requests.get(url)
                    data = response_API.json()
                    # Get the address components
                    address_component = data["results"][0]["formatted_address"]
                    print("____________________________________E_OK______________",address_component)
                    address_components.append(address_component)
                    #max speed calculation
                    
                    
                    max_speed_str= get_speed_limit(x.latitude, x.longitude)
                    
                    target_speed_mph=x.target_speed*0.621371
                    if max_speed_str is not None:
                        max_speed_int = int(re.search(r'\d+', max_speed_str).group())
                        max_speed=max_speed_int

                        if target_speed_mph>(max_speed+5):
                            
                            
                            overspeeding.append("Yes")
                            overspeeding_bool = False
                            
                            

                            # Increment consecutive overspeeding counter
                            consecutive_overspeed_count += 1
                            
                            if consecutive_overspeed_count >= 2:
                                send_email(Parentemail, driver)
                                alerts=alerts+1
                                overspeeding_count += 1
                                overspeeding.append("Yes,alert sent")
                                overspeeding_bool = True
                                
                                consecutive_overspeed_count = 0  # Reset counter
                        else:
                            overspeeding.append("No")
                            consecutive_overspeed_count = 0 
                            overspeeding_bool = False
                            
                            
                                
                        
                    else:
                            overspeeding.append("No")
                            consecutive_overspeed_count = 0 
                            overspeeding_bool = False
                    
                    result=Results(Driver_Name=driver_instance,DrivingDate=date,latitude=x.latitude,longitude=x.longitude,target_speed=target_speed_mph,Max_speed=max_speed,Route=address_component,Overspeed=overspeeding_bool,Count_overspeed=overspeeding_count)
                    result.save()
                duration=(duration/30)
                parent_dashboard=ParentDashboard(Driver_name=driver_instance,DriveDate=date,StartAddress=address_components[0],EndAddress=address_components[-1],Countofoverspeed=alerts,Duration=duration)
                parent_dashboard.save()
                print(consecutive_overspeed_count)
                    
            return HttpResponse("Updated the results with new driving changes ")  

        else:
                return HttpResponse("The dashboard is updated one,no changes")    

#view data
def view_dat(request):
    def show_data():
        if request.method == 'POST':
            # Get the value of 'driver' from the POST request
                driver = request.POST.get('Driver')
                date_time=request.POST.get('Datetime')
        
            
        
        date_time_crrt=date_time+"+00:00"    
        #print(driver, date_time_crrt)
        
        Results_drivers=Results.objects.filter(Driver_Name=driver,DrivingDate=date_time_crrt)
        
        
        t=get_template('Driver.html')
        is_anya = driver == "Anya"
                
        yield "<h1 class='text-light'>Hello </h1>"
        yield "<h2 class='text-light'>please find driving results for {} on {}</h2>".format(driver, date_time)
        
        
        yield t.render(({'drivers':Results_drivers, 'is_anya': is_anya}))
                    
    return StreamingHttpResponse(show_data(), content_type="text/html")


    
def view_maps(request):
    
        if request.method == 'POST':
            # Get the value of 'driver' from the POST request
                driver = request.POST.get('Driver')
                date_time=request.POST.get('Datetime')
        date_time_crrt=date_time+"+00:00" 
        print(date_time_crrt)
        locations=Results.objects.filter(Driver_Name=driver,DrivingDate=date_time_crrt)
       

        
        waypoints = []
        markerpoints=[]
        for loc in locations:
            waypoints.append({
            'lat': loc.latitude,  # Replace 'latitude' with the actual name of your latitude field
            'lng': loc.longitude  # Replace 'longitude' with the actual name of your longitude field
        }) 
        for loc in locations:
            if loc.Overspeed:
                markerpoints.append({
                'lat': loc.latitude,  # Replace 'latitude' with the actual name of your latitude field
                'lng': loc.longitude  # Replace 'longitude' with the actual name of your longitude field
            }) 
        
        #print(waypoints)
        center_index = len(locations) // 2
        center_lat = waypoints[center_index]['lat']
        center_lng = waypoints[center_index]['lng']
        start_lat=waypoints[0]['lat']
        start_lng=waypoints[0]['lng']
        end_lat=waypoints[-1]['lat']
        end_lng=waypoints[-1]['lng']
        
        return render(request, 'map.html',context=({'lat':center_lat,'lng':center_lng,'waypoints':waypoints,'start_lat':start_lat,'start_lng':start_lng,'end_lng':end_lng,'end_lat':end_lat,'markerpoints':markerpoints}))
        

            # Render the map HTML in a template
            
        #return HttpResponse("viewmaps")
def get_speed_limit(lat, lon):
    api = overpy.Overpass()
    
    # Query to fetch speed limit for given coordinates
    result = api.query(f"""
        way(around:10,{lat},{lon})[highway]["maxspeed"];
        out;
    """)
    
    if result.ways:
        speed_limit = result.ways[0].tags.get("maxspeed")
        if speed_limit:
            return speed_limit
    
    # If speed limit not available, find the nearest road and retrieve its speed limit
    nearest_road_result = api.query(f"""
        way(around:10,{lat},{lon})[highway];
        out;
    """)
    
    """if nearest_road_result.ways:
        nearest_road = nearest_road_result.ways[0]
        speed_limit = nearest_road.tags.get("maxspeed")
        if speed_limit:
            return speed_limit"""
    
    return None



def forgot_password(request):
    if request.method == 'POST':
        form = CustomSetPasswordForm(user=None, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            driver_name=form.cleaned_data['driver_name']
            password1 = form.cleaned_data['new_password1']
            password2 = form.cleaned_data['new_password2']
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect('forgot_password')
            try:
                user = ParentTable.objects.get(ParentEmail=email, DriverName=driver_name)
                user.Password = password1
                user.ConfirmPassword = password1
                user.save()
                # Send password reset confirmation email
                send_password_reset_confirmation_email(email,user.ParentName)
                messages.success(request, "Password has been reset successfully. Please check your email for confirmation.")
                return redirect('login')
            except ParentTable.DoesNotExist:
                messages.error(request, "No user found with this email address and Drivername")
                return redirect('forgot_password')
    else:
        form = CustomSetPasswordForm(user=None)
    return render(request, 'forgot_password.html', {'form': form})

def send_password_reset_confirmation_email(email,Pname):
            htmly = get_template('confirm_passwordreset.html')
            d = { 'username': Pname }
            subject, from_email, to = 'Password Reset', 'manasa2327@gmail.com', email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
