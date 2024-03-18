from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie
from .auth import generate_access_token
from django.views.decorators.csrf import csrf_protect
import jwt
from django.conf import settings
import requests
import json
from .models import Collection, Movies
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer, CollectionSerializer, MovieSerializer
from django.contrib.auth import authenticate, login, logout, get_user_model
from collections import defaultdict
from heapq import heapify, heappush, heappop, nsmallest


@api_view(["POST"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def register(request):
    User = get_user_model()
    username = request.data.get("username")
    password = request.data.get("password")
    response = Response()
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed("username and password required")
    if User.objects.filter(username=username):
        return HttpResponse(
            json.dumps(
                {"is_success": False, "message": f"Username already exists"}, indent=4
            )
        )
    user = User.objects.create_user(username=username, password=password)
    user.save()
    access_token = generate_access_token(user)
    response.data = {
        "access_token": access_token,
    }
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def custom_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    response = Response()
    if user is not None:
        login(request, user)
        response.data = {"is_success": True, "message": f"{username} User logged in"}
        return response
    response.data = {"is_success": False, "message": f"Invalid credentials"}
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def custom_logout(request):
    response = Response()
    logout(request)
    response.data = {"is_success": True, "message": f"Logged out successfully"}
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def movies(request):
    response = Response()
    res = requests.get("https://demo.credy.in/api/v1/maya/movies/")
    response.data = res.json()
    return response


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def collection(request):
    if request.method == "POST":
        response = Response()
        d = request.data
        collectionMovies = d.get("movies")
        c = Collection.objects.create(
            title=d["title"], description=d["description"], user=request.user
        )
        c.save()
        colUuid = str(c.uuid)
        for m in collectionMovies:
            if Movies.objects.filter(uuid=m["uuid"]).exists():
                c.movies.add(Movies.objects.get(uuid=m["uuid"]))
            else:
                movie = Movies.objects.create(
                    title=m["title"],
                    description=m["description"],
                    genres=m["genres"],
                    uuid=m["uuid"],
                )
                movie.save()
                c.movies.add(movie)
        response.data = {"collection_uuid": colUuid}
        return response
    elif request.method == "GET":
        response = Response()
        response.data = {"is_success": True, "data": {}}
        col = Collection.objects.filter(user=request.user)
        cArr = []
        genreFreq = defaultdict(int)
        for c in col:
            cArr.append(
                {"title": c.title, "uuid": str(c.uuid), "description": c.description}
            )
            for m in c.movies.all():
                for g in m.genres.split(","):
                    if g:
                        genreFreq[g] += 1
        response.data["data"]["collections"] = cArr
        maxHeap = []
        for k, v in genreFreq.items():
            heappush(maxHeap, (-v, k))
        fav = ",".join(i[1] for i in nsmallest(3, maxHeap))
        response.data["favourite_genres"] = fav
        return response


# http://127.0.0.1:8000/collection/08b78546-f9ee-4497-a498-f6ba7de571c9


@api_view(["PUT", "GET", "DELETE"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def update_collection(request, pk):
    if request.method == "PUT":
        title = request.data.get("title")
        description = request.data.get("description")
        movies = request.data.get("movies")
        response = Response()
        try:
            col = Collection.objects.get(uuid=pk)
            if title is not None:
                col.title = title
            if description is not None:
                col.description = description
            if movies is not None:
                col.movies.clear()
                for m in movies:
                    if Movies.objects.filter(uuid=m["uuid"]).exists():
                        col.movies.add(Movies.objects.get(uuid=m["uuid"]))
                    else:
                        movie = Movies.objects.create(
                            title=m["title"],
                            description=m["description"],
                            genres=m["genres"],
                            uuid=m["uuid"],
                        )
                        movie.save()
                        col.movies.add(movie)
            col.save()
            response.data = {
                "is_success": True,
                "message": f"Collection {col.title} updated successfully",
            }
            return response
        except Collection.DoesNotExist:
            response.data = {"is_success": False, "message": "Collection not found"}
            return response
    elif request.method == "GET":
        response = Response()
        try:
            col = Collection.objects.get(uuid=pk)
            response.data = {"title": col.title, "description": col.description}
            moviesArr = []
            for movie in col.movies.all():
                moviesArr.append(
                    {
                        "title": movie.title,
                        "description": movie.description,
                        "genres": movie.genres,
                        "uuid": str(movie.uuid),
                    }
                )
            response.data["movies"] = moviesArr
            return response
        except Collection.DoesNotExist:
            response.data = {"is_success": False, "message": "Collection not found"}
            return response
    elif request.method == "DELETE":
        response = Response()
        try:
            col = Collection.objects.get(uuid=pk)
            response.data = {
                "is_success": True,
                "message": f"Collection {col.title} deleted successfully",
            }
            col.delete()
            return response
        except Collection.DoesNotExist:
            response.data = {"is_success": False, "message": "Collection not found"}
            return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def get_count(request):
    response = Response()
    response.data = {"requests": request.session.get("count", 0)}
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def reset_count(request):
    response = Response()
    response.data = {"message": "request count reset successfully"}
    return response
