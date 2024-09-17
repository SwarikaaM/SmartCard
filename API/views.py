from rest_framework.views import APIView
from rest_framework import status
from Core.models import User
from .authentication import DeviceAuthentication
from .serializers import UserSerializer
from .utils import is_authenticatedResponse, send_validator_email, verify_validator_email
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import time


# Create your views here.
def Handleemail(request, id1, id2):
    if request.method == "GET":
        stat, msg = verify_validator_email(id1, id2)
        return HttpResponse(msg)
    return HttpResponse("Invalid Request")


class UserAPI(APIView):
    authentication_classes = [DeviceAuthentication]

    def post(self, request, id):
        if id:
            user = User.objects.filter(RFID=id).first()
            serialized_data = None
            if not user:
                status_ = status.HTTP_404_NOT_FOUND
                message = "No User Is Registered With This RFID"
                flag = False
                return is_authenticatedResponse(data=serialized_data, status=status_, message=message, flag=flag)
            else:
                req = send_validator_email(user, request)
                max_wait_time = timedelta(seconds=180)  # 3 minutes
                end_time = timezone.now() + max_wait_time
                if not user.Document_Status == 'ACCEPTED':
                    status_ = status.HTTP_401_UNAUTHORIZED
                    if user.Document_Status == 'REJECTED':
                        message = "Documents Rejected"
                    elif user.Document_Status == 'PENDING':
                        message = "Documents Not Verified Yet"
                    else:
                        message = "Documents Not Submitted"
                    while timezone.now() < end_time:
                        req.refresh_from_db()  # Refresh the request object
                        if req.Is_Validated:
                            break
                        time.sleep(0.5)  # Sleep to avoid tight loop
                    else:
                        req.delete()
                        status_ = status.HTTP_401_UNAUTHORIZED
                        message = "Time Out"
                    flag = req.Is_Validated
                else:
                    status_ = status.HTTP_200_OK
                    message = "User Found"

                    while timezone.now() < end_time:
                        req.refresh_from_db()
                        if req.Is_Validated:
                            serialized_data = UserSerializer(user).data
                            break
                        time.sleep(0.5)
                    else:
                        status_ = status.HTTP_401_UNAUTHORIZED
                        message = "Time Out"
                    flag = req.Is_Validated
                req.delete()
                return is_authenticatedResponse(data=serialized_data, status=status_, message=message, flag=flag)
        else:
            return is_authenticatedResponse(data=None, status=status.HTTP_400_BAD_REQUEST,
                                            message="RFID Not Provided",
                                            flag=False)

    def get(self, request, **kwargs):
        return is_authenticatedResponse(data=None, status=status.HTTP_400_BAD_REQUEST, message="Invalid Request",
                                        flag=True)


class UserExists(APIView):
    authentication_classes = [DeviceAuthentication]

    def post(self, request, id):
        if id:
            user = User.objects.filter(RFID=id).first()
            serialized_data = None
            if not user:
                status_ = status.HTTP_404_NOT_FOUND
                message = "No User Is Registered With This RFID"
                flag = False
                return is_authenticatedResponse(data=serialized_data, status=status_, message=message, flag=flag)
            else:
                serialized_data =None
                status_ = status.HTTP_200_OK
                message = "User Found"
                flag = True
                return is_authenticatedResponse(data=serialized_data, status=status_, message=message, flag=flag)
