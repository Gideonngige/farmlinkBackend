from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import pyrebase
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Farmer, Notification, Question, Reply, Product, ProductOrder, FarmerPayment
import json
import cloudinary.uploader
from decimal import Decimal
from .serializers import NotificationSerializer

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
                message="Welcome to Farm Link! Your account has been created successfully.",
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


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def sell_product(request):
    if request.method == 'POST':
        try:
            farmer_id = request.POST.get("farmer_id")
            product_name = request.POST.get("product_name")
            product_image = request.FILES.get("product_image")
            description = request.POST.get("description")
            quantity = request.POST.get("quantity")
            price = request.POST.get("price")

            print(farmer_id, product_name, product_image, description, quantity, price)
            

            if not all([farmer_id, product_name, product_image, description, quantity, price]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            # Create the product
            result = cloudinary.uploader.upload(product_image)
            image_url = result.get('secure_url')
             
            farmer = Farmer.objects.filter(id=farmer_id).first()
            product = Product.objects.create(
                farmer_id = farmer,
                product_name=product_name,
                product_image=image_url,
                description=description,
                quantity=quantity,
                price=price,
            )

            return JsonResponse({"message": "Product posted successfully", "product_id": product.id}, status=201)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "An error occurred", "error": str(e)}, status=500)

# start of get farm product api
def get_products(request, product_name):
    try:
        products = Product.objects.filter(product_name=product_name)
        product_list = []
        for product in products:
            product_list.append({
                'id': product.id,
                'farmer_id':product.farmer_id.id,
                'product_name': product.product_name,
                'description': product.description,
                'quantity': product.quantity,
                'price': str(product.price),
                'product_image': product.product_image,
            })
        return JsonResponse({"products": product_list}, status=200)
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"message": "An error occurred", "error": str(e)}, status=500)


# buy function
@api_view(['POST'])
def buy(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get("productId")
            quantity = data.get('quantity')
            seller_id = data.get('sellerId')
            farmer_id = data.get('farmerId')
            amount = data.get('amount')

            product = Product.objects.filter(id=product_id).first()
            product.quantity -= Decimal(quantity)
            product.save()
 

            seller_id = Farmer.objects.filter(id=seller_id).first()
            farmer_id = Farmer.objects.filter(id=farmer_id).first()# save the order
            order = ProductOrder.objects.create(
                product_id=product,
                farmer_id=farmer_id,
                seller_id=seller_id,
                quantity=quantity,
                amount=amount
            )

            # Notification for each item
            Notification.objects.create(
                farmer_id=seller_id,
                message=f"You have received order of {product.product_name} from {farmer_id.farmer_name}. Be sure to deliver the product on time. Thank you.",
                is_read=False
            )

            return JsonResponse({"message":"Order placed successfully"}, status=200)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"message": "An error occurred", "error": str(e)}, status=500)


# get_notification api
@api_view(['GET'])
def get_farmer_notifications(request, farmer_id):
    try:
        farmer_id = Farmer.objects.get(id=farmer_id)
        notifications = Notification.objects.filter(farmer_id=farmer_id, is_read=False).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)


# get orders for seller
@api_view(['GET'])
def get_orders(request, farmer_id):
    try:
        farmer_id = Farmer.objects.get(id=farmer_id)
        orders = ProductOrder.objects.filter(seller_id=farmer_id, delivered=False).order_by('-created_at')
        order_list = []
        for order in orders:
            order_list.append({
                'id': order.id,
                'farmer_id':order.farmer_id.id,
                'product_name': order.product_id.product_name,
                'product_image': order.product_id.product_image,
                'farmer_name':order.farmer_id.farmer_name,
                'farmer_location':order.farmer_id.area_of_residence,
                'phone_number':order.farmer_id.phone_number,
                'quantity': order.quantity,
                'amount': str(order.amount),
                'delivered': order.delivered,
                'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return JsonResponse({"orders": order_list}, status=200)
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"message": "An error occurred", "error": str(e)}, status=500)

# get orders for farmer
@api_view(['GET'])
def get_farmer_orders(request, farmer_id):
    try:
        farmer_id = Farmer.objects.get(id=farmer_id)
        orders = ProductOrder.objects.filter(farmer_id=farmer_id, delivered=False).order_by('-created_at')
        order_list = []
        for order in orders:
            order_list.append({
                'id': order.id,
                'farmer_id':order.farmer_id.id,
                'product_name': order.product_id.product_name,
                'product_image': order.product_id.product_image,
                'quantity': order.quantity,
                'amount': str(order.amount),
                'delivered': order.delivered,
                'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return JsonResponse({"orders": order_list}, status=200)
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"message": "An error occurred", "error": str(e)}, status=500)


# start of confirm order api
@api_view(['GET'])
def confirm_order(request, order_id):
    try:
        order = ProductOrder.objects.get(id=order_id)
        order.delivered = True
        order.save()

        amount = order.amount * Decimal('0.85')

        # Get related model objects directly
        seller = order.seller_id  # This is actually the Farmer object
        buyer = order.farmer_id   # This is also the Farmer object
        product = order.product_id

        # Create farmer payment to the seller
        FarmerPayment.objects.create(
            farmer_id=seller,  # this is fine — it's a ForeignKey field expecting Farmer
            amount=amount
        )

        # Notify the buyer
        Notification.objects.create(
            farmer_id=buyer,
            message=f"Your order for {product.product_name} has been delivered successfully. Thank you for buying!",
            is_read=False
        )

        # Notify the seller
        Notification.objects.create(
            farmer_id=seller,
            message=f"You have received payment of Ksh.{amount:.2f} from {buyer.farmer_name}. Thank you.",
            is_read=False
        )

        return JsonResponse({'message': 'Order delivered successfully'}, status=200)

    except ProductOrder.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# end of confirm order api

# start of update profile api
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def updateprofile(request):
    try:
        farmer_id = request.data.get('farmer_id')
        farmer_name = request.data.get('farmer_name')
        phone_number = request.data.get('phone_number')
        area_of_residence = request.data.get('area_of_residence')
        profile_image = request.FILES.get('profile_image', None)

        farmer = Farmer.objects.get(id=farmer_id)

        if farmer_name:
            farmer.farmer_name = farmer_name
        if phone_number:
            farmer.phone_number = phone_number
        if area_of_residence:
            farmer.area_of_residence = area_of_residence
        
        image_url = None
        if profile_image:
            upload_result = cloudinary.uploader.upload(profile_image)
            image_url = upload_result.get("secure_url")
            farmer.profile_image = image_url  # Assuming this is an ImageField

        farmer.save()
        return JsonResponse({"message": "ok"})

    except Farmer.DoesNotExist:
        return JsonResponse({"message": "Farmer not found"}, status=404)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

# end of update profile api