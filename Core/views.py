import json
from .models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, Details, PasswordResetForm
from django.http import HttpResponse, HttpResponseRedirect
from .utils import Register_cnf, Forgot_Password_cnf
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def Home(request):
    if request.method == "GET":
        user = User.objects.get(id=request.user.id)
        data = {}
        if not user.Document_Status == 'ACCEPTED':
            usr = User.objects.get(id=request.user.id)
            form = Details()
            form.fields["User"].queryset = User.objects.filter(Email=request.user.Email)
            form.fields["User"].initial = get_object_or_404(User, Email=request.user.Email)
            ctx = {
                'form': form,
                'usr': usr,
            }
            data.update(ctx)
        if user.Document_Status == 'ACCEPTED':
            # raw_files = {'Documents': user.Documents.get_documents()}
            # data.update(raw_files)
            pass

        return render(request, "Core/home.html", data)

    if request.method == "POST":
        form = Details(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('homepage')
        else:
            data = {
                "form": form
            }
            return render(request, "Core/home.html", data)


def Login(request):
    if request.method == "GET" and not request.user.is_authenticated:
        form = LoginForm()
        data = {
            "form": form
        }
        return render(request, "Core/login.html", data)
    elif request.user.is_authenticated:
        messages.info(request, "Already Logged In")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, Email=form.cleaned_data["Email"], password=form.cleaned_data["Password"])
            if user:
                login(request, user)
                messages.success(request, "Login Successful")
                return redirect("homepage")
            else:
                data = {
                    "form": form
                }
                messages.error(request, "Invalid Email or Password")
                return render(request, "Core/login.html", data)
        else:
            data = {
                "form": form
            }
            return render(request, "Core/login.html", data)


def Register(request):
    register_cnf = Register_cnf()
    if request.method == "GET" and not request.user.is_authenticated:
        form = RegisterForm()
        data = {
            "form": form,
            "verify": False
        }
        return render(request, "Core/register.html", data)
    elif request.user.is_authenticated:
        messages.info(request, "Already Logged In")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to previous page
    if request.method == "POST":
        if 'req' in request.POST:
            if request.POST.get("req") == 'resend_otp':
                email = request.session.get("data").get("Email")
                secret = register_cnf.send_cnf_otp(email)
                request.session[email] = secret
                return HttpResponse(json.dumps({'status': 'success', 'msg': 'OTP RESENT SUCCESSFULLY'}))
            return HttpResponse(json.dump({'status': 'error', 'msg': 'Invalid Request'}))
        elif 'otp' in request.POST:
            otp = request.POST.get("otp")
            try:
                int(otp)
            except ValueError:
                data = {
                    "form": RegisterForm(request.session.get("data")),
                    "verify": True,
                    "msg": "Enter A Valid OTP"
                }
                return render(request, "Core/register.html", data)
            try:
                secret = request.session.get(request.session.get("data").get("Email"))
            except KeyError:
                messages.error("NO OTP FOUND FOR THIS EMAIL")
                return redirect("registerpage")
            if register_cnf.verify_cnf_otp(otp, secret):
                form = RegisterForm(request.session.get("data"))
                if form.is_valid():
                    form.save()
                    messages.success(request, "Registration Successful\nKindly Login To Continue")
                    request.session.pop(request.session.get("data").get("Email"))
                    request.session.pop("data")
                    return redirect("loginpage")
                else:
                    data = {
                        "form": form,
                        "verify": True,
                        "msg": "Form Validation Error Occured"
                    }
                    return render(request, "Core/register.html", data)
            else:
                messages.error(request, "Invalid OTP")
                data = {
                    "form": RegisterForm(request.session.get("data")),
                    "verify": True,
                    "msg": "Invalid OTP"
                }
                return render(request, "Core/register.html", data)
        else:
            form = RegisterForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get("Email")
                secret = register_cnf.send_cnf_otp(email)
                request.session[email] = secret
                request.session["data"] = form.cleaned_data
                data = {
                    "form": form,
                    "verify": True,
                    "countdown": True,
                }
                return render(request, "Core/register.html", data)
            else:
                data = {
                    "form": form,
                    "verify": False
                }
                return render(request, "Core/register.html", data)


def Logout(request):
    logout(request)
    messages.success(request, "Logout Successful")
    return redirect("homepage")


def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get("emailid")
        try:
            user = User.objects.get(Email=email)
            reset_password = Forgot_Password_cnf()
        except User.DoesNotExist:
            messages.error(request, "No User Found With This Email")
            return redirect("forgotpasswordpage")
        token = reset_password.send_cnf(request, user)
        if token:
            messages.success(request, "Password Reset Link Sent To Your Email")
            return redirect("loginpage")
        else:
            messages.error(request, "Error Occured")
            return redirect("forgotpasswordpage")
    return render(request, "Core/forgot_password.html")


def ResetPassword(request, id1, id2):
    if request.method == 'GET':
        reset_password = Forgot_Password_cnf()
        user = reset_password.verify_cnf(id1, id2)
        form = PasswordResetForm()
        form.fields["user"].initial = user
        if user:
            data = {
                "form": form
            }
            return render(request, "Core/reset_password.html", data)
        else:
            messages.error(request, "Invalid Link")
            return redirect("loginpage")
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password Reset Successful")
            return redirect("loginpage")
        else:
            print(form.errors)
            data = {
                "form": form
            }
            return render(request, "Core/reset_password.html", data)
