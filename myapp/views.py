from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import Admin
from .serializer import *
import secrets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import *
from .serializer import CategorySerializer

from .models import Admin, AdminToken


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class AdminAPI(APIView):

    def get(self, request, pk=None):
        # GET single
        if pk:
            try:
                admin = Admin.objects.get(pk=pk)
                serializer = AdminSerializer(admin)
                return Response(serializer.data)
            except Admin.DoesNotExist:
                return Response({"error": "Not found"}, status=404)

        # GET all
        admins = Admin.objects.all()
        serializer = AdminSerializer(admins, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk=None):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = AdminSerializer(admin, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk=None):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = AdminSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        admin.delete()
        return Response({"message": "Deleted successfully"}, status=200)







class AdminLoginView(APIView):
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.validated_data

            refresh = RefreshToken.for_user(admin)

            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "admin_id": admin.id,
                "status": admin.status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import IsAuthenticated
class AdminProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin = request.user
        return Response({
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "status": admin.status
        })
    





@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"status": "error", "message": "Email and password required"},
                status=400,
            )

        # Verify admin
        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            return Response(
                {"status": "error", "message": "Invalid Email"},
                status=400,
            )

        if admin.password != password:
            return Response(
                {"status": "error", "message": "Invalid Password"},
                status=400,
            )

        # Generate or fetch token
        token_obj, created = AdminToken.objects.get_or_create(
            admin=admin,
            defaults={
                "token": secrets.token_hex(20)[:40]    # 40-length token
            }
        )

        return Response({
            "status": "success",
            "message": "Login successful",
            "token": token_obj.token,
            "data": {
                "id": admin.id,
                "password": admin.password,
                "email":admin.email
            }
        }, status=200)



@method_decorator(csrf_exempt, name='dispatch')
class AdminVerifyTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response({"status": "error", "message": "Authorization header missing"},
                            status=400)

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return Response({"status": "error", "message": "Invalid Authorization format"},
                            status=400)

        token = parts[1]

        # Check token in DB
        try:
            token_obj = AdminToken.objects.get(token=token)
        except AdminToken.DoesNotExist:
            return Response({"status": "error", "message": "Invalid token"},
                            status=401)

        admin = token_obj.admin

        return Response({
            "status": "success",
            "message": "Token verified",
            "data": {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "mobile": admin.mobile,
                "status": admin.status
            }
        }, status=200)






class CategoryAPI(APIView):

    # GET all or one
    def get(self, request, id=None):
        if id:
            try:
                cat = Category.objects.get(id=id)
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=404)

            serializer = CategorySerializer(cat)
            return Response(serializer.data)

        all_cat = Category.objects.all()
        serializer = CategorySerializer(all_cat, many=True)
        return Response(serializer.data)

    # POST create
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Category created", "data": serializer.data},
                status=201
            )
        return Response(serializer.errors, status=400)

    # PUT full update
    def put(self, request, id=None):
        if not id:
            return Response({"error": "ID required"}, status=400)

        try:
            cat = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        serializer = CategorySerializer(cat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Category updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)

    # PATCH partial update
    def patch(self, request, id=None):
        if not id:
            return Response({"error": "ID required"}, status=400)

        try:
            cat = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        serializer = CategorySerializer(cat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Category partially updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)

    # DELETE remove
    def delete(self, request, id=None):
        if not id:
            return Response({"error": "ID required"}, status=400)

        try:
            cat = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        cat.delete()
        return Response({"message": "Category deleted"}, status=200)




class InfluencerAPI(APIView):

    # GET all or one
    def get(self, request, id=None):
        if id:
            try:
                influencer = Influencer.objects.get(id=id)
            except Influencer.DoesNotExist:
                return Response({"error": "Influencer not found"}, status=404)

            serializer = InfluencerSerializer(influencer)
            return Response(serializer.data)

        influencers = Influencer.objects.all()
        serializer = InfluencerSerializer(influencers, many=True)
        return Response(serializer.data)

    # POST create influencer
    def post(self, request):
        serializer = InfluencerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Influencer created", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT full update
    def put(self, request, id=None):
        if not id:
            return Response({"error": "ID required for PUT"}, status=400)

        try:
            influencer = Influencer.objects.get(id=id)
        except Influencer.DoesNotExist:
            return Response({"error": "Influencer not found"}, status=404)

        serializer = InfluencerSerializer(influencer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Influencer updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)

    # PATCH partial update
    def patch(self, request, id=None):
        if not id:
            return Response({"error": "ID required for PATCH"}, status=400)

        try:
            influencer = Influencer.objects.get(id=id)
        except Influencer.DoesNotExist:
            return Response({"error": "Influencer not found"}, status=404)

        serializer = InfluencerSerializer(influencer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Influencer partially updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)

    # DELETE influencer
    def delete(self, request, id=None):
        if not id:
            return Response({"error": "ID required for DELETE"}, status=400)

        try:
            influencer = Influencer.objects.get(id=id)
        except Influencer.DoesNotExist:
            return Response({"error": "Influencer not found"}, status=404)

        influencer.delete()
        return Response({"message": "Influencer deleted successfully"})
    


class BannerAPIView(APIView):

    def get(self, request, pk=None):
        if pk:
            banner = get_object_or_404(Banner, pk=pk)
            serializer = BannerSerializer(banner)
        else:
            banners = Banner.objects.all()
            serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)
        serializer = BannerSerializer(banner, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)
        serializer = BannerSerializer(banner, data=request.data, partial=True)  # partial update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)
        banner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class SponsoredContentAPIView(APIView):

    # GET method (list or retrieve)
    def get(self, request, pk=None):
        if pk:
            # Get a single object
            content = get_object_or_404(sponsored_content, pk=pk)
            serializer = SponsoredContentSerializer(content)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Get all objects
            contents = sponsored_content.objects.all()
            serializer = SponsoredContentSerializer(contents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # POST method (create)
    def post(self, request):
        serializer = SponsoredContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT method (full update)
    def put(self, request, pk):
        content = get_object_or_404(sponsored_content, pk=pk)
        serializer = SponsoredContentSerializer(content, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH method (partial update)
    def patch(self, request, pk):
        content = get_object_or_404(sponsored_content, pk=pk)
        serializer = SponsoredContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE method
    def delete(self, request, pk):
        content = get_object_or_404(sponsored_content, pk=pk)
        content.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)