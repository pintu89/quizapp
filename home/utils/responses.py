# home/utils/responses.py
from django.http import JsonResponse
from django.shortcuts import render
from home.models import Player

def success(message="", data=None, status=200):
    return JsonResponse({
        "status": "success",
        "message": message,
        "data": data
    }, status=status)

def error(message="", data=None, status=400):
    return JsonResponse({
        "status": "error",
        "message": message,
        "data": data
    }, status=status)

def unauthorized(message="Unauthorized"):
    return JsonResponse({
        "status": "error",
        "message": message
    }, status=401)

def not_found(message="Not Found"):
    return JsonResponse({
        "status": "error",
        "message": message
    }, status=404)

def server_error(message="Internal Server Error"):
    return JsonResponse({
        "status": "error",
        "message": message
    }, status=500)
def bad_request(message="Bad Request"):
    return JsonResponse({
        "status": "error",
        "message": message
    }, status=400)

