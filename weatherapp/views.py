from django.shortcuts import render
import requests
from datetime import date
from decouple import config
import re

def home(request):
    context = {}
    api_key = config('api_key')
    imgapi_key = config('imgapi_key')

    # ---------- POST Request (User Searches City) ----------
    if request.method == "POST":
        city = request.POST.get('city', '').strip()

        # 1. Empty city name check
        if not city:
            context['error'] = "Please enter a city name."
            return render(request, 'error.html', context)

        # 2. Validate city name (letters, spaces, hyphens only)
        if not re.match(r'^[a-zA-Z\s\-]+$', city):
            context['error'] = "Invalid city name."
            return render(request, 'home.html', context)

        try:
            # Weather API call
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()

            if data.get("cod") != 200:
                context['error'] = "City not found or weather data unavailable."
                return render(request, 'home.html', context)

            # Unsplash API call
            try:
                unsplash_url = f"https://api.unsplash.com/search/photos?query={city}&client_id={imgapi_key}&orientation=landscape"
                image_response = requests.get(unsplash_url, timeout=5).json()
                if "results" in image_response and image_response["results"]:
                    city_image_url = image_response["results"][0]["urls"]["regular"]
                else:
                    city_image_url = "/static/images/default.jpg"
            except Exception:
                city_image_url = "/static/images/default.jpg"

            # Context data
            context.update({
                'city': city.upper(),
                'temp': data['main']['temp'],
                'icon': data['weather'][0]['icon'],
                'desc': data['weather'][0]['description'],
                'day': date.today(),
                'wind': round(data['wind']['speed'] * 3.6, 1),
                'humidity': data['main']['humidity'],
                'img': city_image_url
            })

        except requests.exceptions.RequestException:
            context['error'] = "Unable to connect to the weather service. Please try again later."
        except KeyError:
            context['error'] = "Unexpected data format from the weather service."

        return render(request, 'home.html', context)

    # ---------- GET Request (Default Page Load) ----------
    else:
        city = 'tirupati'
        try:
            # Weather API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()

            # Unsplash API
            unsplash_url = f"https://api.unsplash.com/search/photos?query={city}&client_id={imgapi_key}&orientation=landscape"
            image_response = requests.get(unsplash_url, timeout=5).json()
            if "results" in image_response and image_response["results"]:
                city_image_url = image_response["results"][0]["urls"]["regular"]
            else:
                city_image_url = "/static/images/default.jpg"

            context.update({
                'city': city.upper(),
                'temp': data['main']['temp'],
                'icon': data['weather'][0]['icon'],
                'desc': data['weather'][0]['description'],
                'day': date.today(),
                'wind': round(data['wind']['speed'] * 3.6, 1),
                'humidity': data['main']['humidity'],
                'img': city_image_url
            })

        except requests.exceptions.RequestException:
            context['error'] = "Unable to connect to the weather service."
        except KeyError:
            context['error'] = "Unexpected data format from the weather service."

        return render(request, 'home.html', context)
