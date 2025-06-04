from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pyrebase
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Farmer, Notification

config = {
    "apiKey": "AIzaSyBFKJy-P2S8xHcB0DB5G-IUZ2hPgQ6VtEw",
    "authDomain": "farmlink-7044f.firebaseapp.com",
    "databaseURL": "https://farmlink-7044f-default-rtdb.firebaseio.com/",
    "projectId": "farmlink-7044f",
    "storageBucket": "farmlink-7044f.firebasestorage.app",
    "messagingSenderId": "7342876635",
   " appId": "1:7342876635:web:0669eec7a9faf3d2ab29fe",
   " measurementId": "G-1T9P7L96DN"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth() 
database = firebase.database()

def index(request):
    return HttpResponse("Hello Farmlink!")


# start of signup api
@csrf_exempt
@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        try:
            data = request.data  # ✅ This works with JSON content-type

            farmer_name = data.get("fullname")
            phone_number = data.get("phonenumber")
            email = data.get("email")
            area_of_residence = data.get("areaofresident")
            password = data.get("password")

            if not all([farmer_name, email, password, area_of_residence, phone_number]):
                return JsonResponse({"message": "Missing required fields"}, status=400)

            if Farmer.objects.filter(email=email).exists():
                return JsonResponse({"message": "Email already exists"}, status=400)

            farmer = authe.create_user_with_email_and_password(email, password)
            uid = farmer['localId']

            farmer = Farmer(
                farmer_name=farmer_name,
                phone_number=phone_number,
                email=email,
                area_of_residence=area_of_residence,
                password=uid
            )
            farmer.save()

            notification = Notification.objects.create(
                farmer_id=farmer,
                message="Welcome to G-Blog! Your account has been created successfully.",
                is_read=False
            )

            return JsonResponse({"message": "Successfully signed up"}, status=201)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "Signup failed", "error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

#end of signup api