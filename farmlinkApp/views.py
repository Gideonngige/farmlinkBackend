from django.shortcuts import render
from django.http import HttpResponse
import pyrebase
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Farmer

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
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            # Use request.POST and request.FILES for form data and files
            farmer_name = request.POST.get("fullname")
            phone_number = request.POST.get("phonenumber")
            email = request.POST.get("email")
            area_of_residence = request.POST.get("areaofresidence")
            password = request.POST.get("password")

            # Check for missing fields
            if not all([name, email, password,area_of_residence, phone_number]):
                return JsonResponse({"message": "Missing required fields"}, status=400)

            # Check if email already exists
            if Farmer.objects.filter(email=email).exists():
                return JsonResponse({"message": "Email already exists"}, status=400)

            # Create farmer in Firebase
            farmer = authe.create_user_with_email_and_password(email, password)
            uid = farmer['localId']

            # Save farmer in your database
            farmer = Farmer(farmer_name=fullname, phone_number=phone_number email=email, area_of_residence=area_of_residence, password=uid)
            farmer.save()
            
            farmer2 = Farmer.objects.filter(email=email).first()
            notification = Notification.objects.create(
                farmer_id=user2,
                message="Welcome to G-Blog! Your account has been created successfully.",
                is_read=False
            )

            return JsonResponse({"message": "Successfully signed up"}, status=201)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "Signup failed", "error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)
#end of signup api