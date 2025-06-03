from django.shortcuts import render
from django.http import HttpResponse
import pyrebase

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