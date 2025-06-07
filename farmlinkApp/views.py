from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pyrebase
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Farmer, Notification, Question, Reply
import json

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

#start of signin api
@csrf_exempt
@api_view(['POST'])
def signin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"message": "Email and password are required"}, status=400)

            farmer = authe.sign_in_with_email_and_password(email, password)
            
            if Farmer.objects.filter(email=email).exists():
                session_id = farmer['idToken']
                request.session['uid'] = str(session_id)
                get_farmer = Farmer.objects.filter(email=email).first()
                farmer_id = get_farmer.id
                print("Farmer ID:", farmer_id)  # Optional logging
                farmer_name = get_farmer.farmer_name
                phone_number = get_farmer.phone_number
                area_of_residence = get_farmer.area_of_residence
                profile_image = get_farmer.profile_image
                date_joined = get_farmer.date_joined
                return JsonResponse({"message": "Successfully logged in", "farmer_id":farmer_id, "farmer_name":farmer_name,"farmer_email":email,"phone_number":phone_number, "area_of_resident":area_of_residence, "profile_image":profile_image, "date_joined":date_joined}, status=200)
            else:
                return JsonResponse({"message": "No user found with this email, please register"}, status=404)

        except Exception as e:
            print("Error:", str(e))  # Optional logging
            return JsonResponse({"message": "Invalid credentials. Please check your email and password."}, status=401)

    return JsonResponse({"message": "Invalid request method"}, status=405)
#end of signin api

# start of question api
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            farmer_id = data.get("farmer_id")
            question_text = data.get("question_text")

            if not farmer_id or not question_text:
                return JsonResponse({"message": "Farmer ID and question text are required"}, status=400)

            farmer = Farmer.objects.filter(id=farmer_id).first()
            if not farmer:
                return JsonResponse({"message": "Farmer not found"}, status=404)

            question = Question.objects.create(
                farmer_id=farmer,
                question_text=question_text
            )

            return JsonResponse({"message": "Question posted successfully", "question_id": question.id}, status=200)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "Failed to post question", "error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

# end of question api

# start of get questions api
@csrf_exempt
@api_view(['GET'])
def get_questions(request):
    if request.method == 'GET':
        try:
            questions = Question.objects.all().order_by('-created_at')
            questions_list = []

            for question in questions:
                questions_list.append({
                    "id": question.id,
                    "farmer_id": question.farmer_id.id,
                    "question_text": question.question_text,
                    "farmer_name": question.farmer_id.farmer_name,
                    "profile_image": question.farmer_id.profile_image,
                    "created_at": question.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            return JsonResponse({"questions": questions_list}, status=200)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "Failed to retrieve questions", "error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

# start of reply api
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def reply(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            farmer_id = data.get("farmer_id")
            question_id = data.get("question_id")
            reply_text = data.get("reply_text")

            if not farmer_id or not reply_text:
                return JsonResponse({"message": "Farmer ID and question text are required"}, status=400)

            farmer = Farmer.objects.filter(id=farmer_id).first()
            if not farmer:
                return JsonResponse({"message": "Farmer not found"}, status=404)
            question = Question.objects.filter(id=question_id).first()
            if not question:
                return JsonResponse({"message":"Question not found"}, status=404)

            reply = Reply.objects.create(
                question=question,
                farmer_id=farmer,
                reply_text=reply_text
            )

            return JsonResponse({"message": "Reply sent successfully", "reply_id": reply.id}, status=200)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "Failed to send reply", "error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

# start get replies api
@csrf_exempt
@api_view(['GET'])
def get_replies(request, question_id):
    if request.method == 'GET':
        try:
            question = Question.objects.filter(id=question_id).first()
            replies = Reply.objects.filter(question=question).order_by('-created_at')
            replies_list = []

            for reply in replies:
                replies_list.append({
                    "id": reply.id,
                    "reply_text": reply.reply_text,
                    "farmer_name": reply.farmer_id.farmer_name,
                    "profile_image": reply.farmer_id.profile_image,
                    "created_at": reply.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            return JsonResponse({"replies": replies_list}, status=200)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "Failed to retrieve replies", "error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)