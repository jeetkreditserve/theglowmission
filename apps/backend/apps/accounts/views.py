from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import CustomerNotificationSubscription
from apps.accounts.serializers import (
    CustomerLoginSerializer,
    CustomerNotificationSubscriptionSerializer,
    CustomerPasswordResetConfirmSerializer,
    CustomerPasswordResetRequestSerializer,
    CustomerProfileUpdateSerializer,
    CustomerRegisterSerializer,
    LoginSerializer,
    UserSerializer,
)
from apps.accounts.services import (
    authenticate_customer_login,
    confirm_customer_password_reset,
    create_customer_user,
    customer_profile_payload,
    disable_notification_subscription,
    register_notification_subscription,
    request_customer_password_reset,
    update_customer_profile,
    update_notification_subscription,
)


def auth_response(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key, "user": UserSerializer(user).data}


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(auth_response(serializer.validated_data["user"]))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"status": "ok"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CustomerRegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_customer_user(**serializer.validated_data)
        return Response(auth_response(user), status=status.HTTP_201_CREATED)


class CustomerLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_customer_login(**serializer.validated_data)
        return Response(auth_response(user))


class CustomerPasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = CustomerPasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(request_customer_password_reset(serializer.validated_data["email"]))


class CustomerPasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = CustomerPasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = confirm_customer_password_reset(**serializer.validated_data)
        Token.objects.filter(user=user).delete()
        return Response(auth_response(user))


class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(customer_profile_payload(request.user))

    def patch(self, request):
        serializer = CustomerProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(update_customer_profile(request.user, serializer.validated_data))


class CustomerNotificationSubscriptionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = CustomerNotificationSubscription.objects.filter(user=request.user).order_by("-last_registered_at", "-id")
        return Response(CustomerNotificationSubscriptionSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = CustomerNotificationSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription, created = register_notification_subscription(request.user, serializer.validated_data)
        return Response(
            CustomerNotificationSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CustomerNotificationSubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk: int):
        subscription = get_object_or_404(CustomerNotificationSubscription, pk=pk, user=request.user)
        serializer = CustomerNotificationSubscriptionSerializer(subscription, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        subscription = update_notification_subscription(request.user, subscription, serializer.validated_data)
        return Response(CustomerNotificationSubscriptionSerializer(subscription).data)

    def delete(self, request, pk: int):
        subscription = get_object_or_404(CustomerNotificationSubscription, pk=pk, user=request.user)
        disable_notification_subscription(request.user, subscription)
        return Response(status=status.HTTP_204_NO_CONTENT)
