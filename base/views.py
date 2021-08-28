from django.http import response
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import login,authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import pandas as pd
from .models import Company,Student
from django.contrib.auth.password_validation import password_changed,validate_password
from .forms import AddCompanyForm,StudentDetailsForm
from django.core.exceptions import ValidationError
import csv
# Create your views here.

def index_view(request):
    if request.user is not None:
        logout(request)
    return render(request,'index.html')

@csrf_exempt
def login_handle_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        user = authenticate(username = username, password=password)
        if user is not None:
            login(request,user)
            return render(request,'home.html')
        else:
            messages.error(request,"Invalid username or password.")
            return redirect(request.META['HTTP_REFERER'])
    else:
        return render(request,'home.html')


def student_cred_view(request):
    if "GET" == request.method:
        return render(request, 'student_cred.html', {})
    else:
        file = request.FILES["excel_file"]
        if file.name.endswith('.csv'):
            dataset = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            dataset = pd.read_excel(file)
        else:
            messages.error(request,"Invalid file format.")
            return render(request, 'student_cred.html', {})
        student_details = dataset.iloc[:,0].values
        pwd = []
        for student_uname in student_details:
            username = student_uname
            password = User.objects.make_random_password()
            user = User.objects.create_user(username=username,email=username,password=password)
            pwd.append(password)
        dataset['password'] = pwd
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=credentials.csv'
        dataset.to_csv(path_or_buf=response)  # with other applicable parameters
        return response


def company_view(request):
    companies = Company.objects.all()
    if not companies.exists():
        companies = None 
    if request.method == 'GET':
        addform = AddCompanyForm()
        return render(request,'company.html',{'companies': companies, 'addform':addform})
    else:
        if request.POST.get("addcompany"):
            addform = AddCompanyForm(request.POST, request.FILES)
            if addform.is_valid():
                addform.save()
            return HttpResponseRedirect(request.path_info)
        elif request.POST.get("deletecompany"):  # You can use else in here too if there is only 2 submit types.
            id = request.POST.get("deletecompany")
            instance = Company.objects.get(id=id)
            instance.delete()
            return HttpResponseRedirect(request.path_info)
        elif request.POST.get("updatecompany"): 
            id = request.POST.get("updatecompany")
            company = get_object_or_404(Company,pk=id)
            form = AddCompanyForm(request.POST, request.FILES, instance=company)
            if form.is_valid():
	            form.save()
            return HttpResponseRedirect(request.path_info)


def profile_view(request):
    if request.method == 'GET':
        return render(request,'profile.html')
    else:
        if request.POST.get("profile"):
            fn = request.POST['fn']
            ln = request.POST['ln']
            username = request.POST['username'] 
            email = request.POST['email']
            if User.objects.exclude(pk=request.user.id).filter(username=username).exists():
                messages.error(request,"Username already exists.")
                return redirect(request.META['HTTP_REFERER'])
            if User.objects.exclude(pk=request.user.id).filter(email=email).exists():
                messages.error(request,"Email already exists.")
                return redirect(request.META['HTTP_REFERER'])
            user=User.objects.get(pk=request.user.id)
            user.first_name=fn
            user.last_name=ln
            user.email=email
            user.username=username
            user.save()
        elif request.POST.get("pwd"):
            username = request.POST['username'] 
            old_pwd = request.POST['old']
            new_pwd = request.POST['new']
            confirm_pwd = request.POST['confirm']
            user=User.objects.get(pk=request.user.id)
            if not user.check_password(old_pwd):
                messages.error(request,"Old password incorrect.")
                return redirect(request.META['HTTP_REFERER'])
            if new_pwd != confirm_pwd:
                messages.error(request,"Passwords do not match.")
                return redirect(request.META['HTTP_REFERER'])
            try:
                validate_password(new_pwd,user=user)
            except ValidationError as err:
                messages.error(request,err.messages[0])
                return redirect(request.META['HTTP_REFERER'])
            user.set_password(new_pwd)
            user.save()
            user = authenticate(username = username, password=new_pwd)
            if user is not None:
                login(request,user)
        return HttpResponseRedirect(request.path_info)


def academics_view(request):
    if request.method == 'GET':
        studform = StudentDetailsForm()
        return render(request,'academics.html',{'form':studform})
    else:
        studform = StudentDetailsForm(request.POST, request.FILES)
        studform.instance.user = request.user
        if studform.is_valid():
            studform.save()
        return HttpResponseRedirect(request.path_info)