from django.shortcuts import render
import requests
from datetime import date
from django.templatetags.static import static
from decouple import config
import re

def home(request):

    context = {}
    api_key = config('api_key')
    imgapi_key = config('imgapi_key')

    if request.method == "POST":

        city = request.POST.get('city' , '').strip()

        if not city:
            context['error'] = "please enter city name"
            return render(request , 'error.html' , context)
        
        if not re.match(r'^[a-zA-Z\s\-]+$', city):
            context['error'] = "Invalid city name."
            return render(request, 'home.html', context)
        

        try :

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                context['error'] = " please recheck city or May be weather data not found"
                
                return render(request , 'home.html' ,context)

            try :
                unsplash_url = f"https://api.unsplash.com/search/photos?query={city}&client_id={imgapi_key}&orientation=landscape"
                image_response = requests.get(unsplash_url).json()
                if image_response["results"]:
                    city_image_url = image_response["results"][0]["urls"]["regular"]
                else:
                    city_image_url = "/static/images/default.jpg"  # fallback image

            except:
                city_image_url = "/static/images/default.jpg"
            

            context['city'] = city.upper()
            context['temp'] = data['main']['temp']
            context['icon'] = data['weather'][0]['icon']
            context['desc'] = data['weather'][0]['description']
            context['day']  = date.today()
            context['wind'] = round(data['wind']['speed'] * 3.6,1)
            context['humidity'] = data['main']['humidity']
            context['img'] = city_image_url


        except requests.exceptions.RequestException:
            context['error'] = "unable to connect to the weather service!. please try again after some time"

        except KeyError | ConnectionError :
            context['error'] = " unexpected data format from the weather"

        
        return render(request , 'home.html' ,context)
    
    else:

        city = 'tirupati'
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url , timeout=5)
        data = response.json()
        unsplash_url = f"https://api.unsplash.com/search/photos?query={city}&client_id={imgapi_key}&orientation=landscape"
        image_response = requests.get(unsplash_url).json()
        if image_response["results"]:
            city_image_url = image_response["results"][0]["urls"]["regular"]
        else:
            city_image_url = "/static/default.jpg"  # fallback image
        context['city'] = city.upper()
        context['temp'] = data['main']['temp']
        context['icon'] = data['weather'][0]['icon']
        context['desc'] = data['weather'][0]['description']
        context['day']  = date.today()
        context['wind'] = round(data['wind']['speed'] * 3.6,1)
        context['humidity'] = data['main']['humidity']
        context['img'] = city_image_url

        return render(request , 'home.html' ,context)
