from django import forms
from django.http import response
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import login,authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import pandas as pd
from .models import Company, PlacementApplicationResponse,Student,PlacementApplication,PlacementApplicationResponseFiles,PlacementStatus
from django.contrib.auth.password_validation import password_changed,validate_password
from .forms import AddCompanyForm,StudentDetailsForm,CompanyApplicationForm
from django.core.exceptions import ValidationError
import json
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from .resources import CompanyResource,UserResource,StudentResource,PlacementApplicationResource,PlacementApplicationResponseResource,PlacementStatusResource
from plotly.offline import download_plotlyjs,init_notebook_mode,plot,iplot
import plotly.graph_objects as go
import cufflinks as cf
import chart_studio.plotly as ply
import plotly.express as px
from plotly.subplots import make_subplots
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
        dataset.drop_duplicates(subset = dataset.columns[0], keep = 'first', inplace = True)
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
        try:
            student = Student.objects.get(user_id=request.user.id)
            for field,attr in zip(studform.fields,student._meta.get_fields()[2:]):
                studform[field].initial = getattr(student,attr.name)
            return render(request,'academics.html',{'form':studform})
        except:  
            return render(request,'academics.html',{'form':studform})
    else:
        try:
            student = get_object_or_404(Student,user_id=request.user.id)
            studform = StudentDetailsForm(request.POST, request.FILES, instance=student)
            if studform.is_valid():
	            studform.save()
            return HttpResponseRedirect(request.path_info)
        except:
            studform = StudentDetailsForm(request.POST, request.FILES)
            studform.instance.user = request.user
            if studform.is_valid():
                studform.save()
            return HttpResponseRedirect(request.path_info)

def FormBuilder(params,required):
    keys = list(params.keys())
    values = list(params.values())
    form_title = params.get('title')
    form_description = params.get('description')
    formfields = {}
    for i in range(len(keys)):
        if 'type' in keys[i] :
            form_type = values[i]
            if form_type == 'Text':
                formfields[values[i-1]] = forms.CharField(max_length=25,required=required)
            elif form_type == 'Paragraph':
                formfields[values[i-1]] = forms.CharField(widget=forms.Textarea,required=required)
            elif form_type == 'Email':
                formfields[values[i-1]] = forms.EmailField(required=required)
            elif form_type == 'Integer':
                formfields[values[i-1]] = forms.IntegerField(required=required)
            elif form_type == 'Decimal':
                formfields[values[i-1]] = forms.DecimalField(max_digits=6, decimal_places=2,required=required)
            elif form_type == 'File Upload':
                formfields[values[i-1]] = forms.FileField(required=required)
            elif form_type == 'Choice':
                choices = [(choice,choice) for choice in params[keys[i+1]]]
                formfields[values[i-1]] = forms.ChoiceField(choices=choices,required=required)
    ApplicationForm = type('ApplicationForm',(CompanyApplicationForm,),formfields)
    form = ApplicationForm()
    return form,form_title,form_description
        
def todict(querydict):
    params = {}
    for key in querydict.keys():
        if len(querydict.getlist(key))>1:
            params[key] = querydict.getlist(key)
        else:
            params[key] = querydict[key]
    return params

def createform_view(request,company_id):
    if request.method == 'GET':
        return render(request,'createform.html',{'company_id':company_id})
    
    elif request.POST.get("preview"):
        placement_year = request.POST.get('year')
        params = todict(request.POST)
        form,form_title,form_description = FormBuilder(params,False)
        params = json.dumps(params,indent=2)
        return render(request,'preview.html',{'form':form,'title':form_title,'description':form_description,'params':params,'company_id':company_id,'placement_year':placement_year})

    elif request.POST.get("back"):
        return render(request,'createform.html',{'company_id':company_id})
    
    elif request.POST.get("save"):
        form_fields = request.POST.get("params")
        placement_year = request.POST.get('year')
        company = Company.objects.get(id=company_id)
        placement_application = PlacementApplication(company=company,form_fields=form_fields,placement_year=placement_year) 
        placement_application.save()
        return redirect('company')


def clean_responses(responses,fields):
    kl1 = list(fields)
    kl2 = list(responses)
    kv1 = list(fields.values())
    kv2 = list(responses.values())
    for i in range(len(kl1)):
        if i<len(kl2) and kl1[i] != kl2[i]:
            kl2.insert(i,kl1[i])
            kv2.insert(i,None)
        elif i>=len(kl2):
            kl2.append(kl1[i])
            kv2.append(None)
    responses = {}
    for i in range(len(kl2)):
        responses[kl2[i]] = kv2[i]
    return responses
    
def ResponsePreviewer(params,required,disabled):
    keys = list(params.keys())
    values = list(params.values())
    form_title = params.get('title')
    form_description = params.get('description')
    formfields = {}
    for i in range(len(keys)):
        if 'type' in keys[i] :
            form_type = values[i]
            if form_type == 'Text':
                formfields[values[i-1]] = forms.CharField(max_length=25,required=required,disabled=disabled)
            elif form_type == 'Paragraph':
                formfields[values[i-1]] = forms.CharField(widget=forms.Textarea,required=required,disabled=disabled)
            elif form_type == 'Email':
                formfields[values[i-1]] = forms.EmailField(required=required,disabled=disabled)
            elif form_type == 'Integer':
                formfields[values[i-1]] = forms.IntegerField(required=required,disabled=disabled)
            elif form_type == 'Decimal':
                formfields[values[i-1]] = forms.DecimalField(max_digits=6, decimal_places=2,required=required,disabled=disabled)
            elif form_type == 'File Upload':
                formfields[values[i-1]] = forms.FileField(required=required,disabled=disabled)
            elif form_type == 'Choice':
                choices = [(choice,choice) for choice in params[keys[i+1]]]
                formfields[values[i-1]] = forms.ChoiceField(choices=choices,required=required,disabled=disabled)
    ApplicationForm = type('ApplicationForm',(CompanyApplicationForm,),formfields)
    form = ApplicationForm()
    return form,form_title,form_description

def addfiles(responses,response_files):
    for response_file in response_files:
        responses[response_file.label] = response_file.file_uploaded
    return responses

def prepare_responses(params,responses):
    columns=[]
    params = json.loads(params)
    for key in params.keys():
        if 'field-' in key:
            columns.append(params[key])
    dataset = pd.DataFrame(columns=columns)
    rnos = []
    for response in responses:
        rnos.append(response.student.roll_number)
        response = json.loads(response.responses)
        dataset = dataset.append(response,ignore_index=True)
    dataset.insert(0,'Roll Number',rnos)
    return dataset

def prepare_criteria(params,dataset):
    params = json.loads(params)
    criteria = {}
    keys = list(params.keys())
    for i in range(len(keys)):
        key = keys[i]
        if 'type' in key:
            if params[key] == 'Integer' or params[key] == 'Decimal':
                col = dataset[params[keys[i-1]]]
                criteria[params[keys[i-1]]] = [params[key],col.min(),col.max()]
            elif params[key] == 'Choice':
                criteria[params[keys[i-1]]] = [(params[key])] + params[keys[i+1]]
    return criteria
            


def placement_applications_view(request):
    if request.method == 'GET':
        applications = PlacementApplication.objects.all()
        if not request.user.is_staff:
            student = Student.objects.get(user=request.user)
        if not applications.exists():
            applications = None 
        else:
            fields = []
            responses = []
            for application in applications:
                if not request.user.is_staff:
                    try:
                        responses.append(PlacementApplicationResponse.objects.get(student=student,placement_application=application))
                    except:
                        responses.append(None)
                else:
                    responses.append('admin')
                form_fields = json.loads(application.form_fields)
                fields.append(form_fields)
            applications = zip(applications,fields,responses)
        return render(request,'applications.html',{'applications':applications})

    elif  request.method == 'POST':
        if request.POST.get("delete"):
            id = request.POST.get("delete")
            instance = PlacementApplication.objects.get(id=id)
            instance.delete()
            return redirect('applications')

        if request.POST.get("preview"):
            params = request.POST.get("preview")
            params = params.replace("'",'"')
            params = json.loads(params)
            form,form_title,form_description = FormBuilder(params,False)
            return render(request,'fillform.html',{'form':form,'title':form_title,'description':form_description})

        if request.POST.get("back"):
            return redirect('applications')
        
        if request.POST.get("responses"):
            form_id = request.POST.get('responses')
            form = PlacementApplication.objects.get(id=form_id)
            params = form.form_fields
            responses = PlacementApplicationResponse.objects.filter(placement_application=form)
            result = prepare_responses(params,responses)
            criterias = prepare_criteria(params,result)
            return render(request,'responses.html',{'criterias':criterias,'form_id':form_id})

        if request.POST.get("apply"):
            form_id = request.POST.get("id")
            placement_application = PlacementApplication.objects.get(id=form_id)
            student = Student.objects.get(user=request.user)
            params = request.POST.get("apply")
            params = params.replace("'",'"')
            params = json.loads(params)
            placement_application_response = None
            form,form_title,form_description = FormBuilder(params,True)
            try:
                placement_application_response = get_object_or_404(PlacementApplicationResponse,placement_application=placement_application,student=student)
                responses = json.loads(placement_application_response.responses)
                responses = clean_responses(responses,form.fields)
            except:
                responses = None

            try:
                response_files = PlacementApplicationResponseFiles.objects.filter(response=placement_application_response)
                if response_files:
                    responses = addfiles(responses,response_files)
            except:
                response_files = None

            if responses:
                form.set_initial(responses)
            return render(request,'fillform.html',{'form':form,'title':form_title,'description':form_description,'form_id':form_id})

        if request.POST.get("filled"):
            form_id = request.POST.get('filled')
            responses = todict(request.POST)
            files = request.FILES
            del responses['csrfmiddlewaretoken']
            del responses['filled']
            responses = json.dumps(responses)
            student = Student.objects.get(user=request.user)
            placement_application = PlacementApplication.objects.get(id=form_id)
            response_files = []
            try:
                placement_application_response = get_object_or_404(PlacementApplicationResponse,placement_application=placement_application,student=student)
                placement_application_response.responses = responses

                try:
                    if files:
                        for file in files:
                            existing_files = PlacementApplicationResponseFiles.objects.filter(response=placement_application_response,label=file)
                            for existing_file in existing_files:
                                existing_file.file_uploaded = files[file]
                                response_files.append(existing_file) 
                    
                    else:
                        if files:
                            for file in files:
                                response_file = PlacementApplicationResponseFiles(response=placement_application_response,label=file,file_uploaded=files[file])
                                response_files.append(response_file)
                
                except:
                    pass
                            

            except:
                placement_application_response = PlacementApplicationResponse(
                student=student,responses=responses,placement_application=placement_application) 

                if files:
                    for file in files:
                        response_file = PlacementApplicationResponseFiles(response=placement_application_response,label=file,file_uploaded=files[file])
                        response_files.append(response_file)
                
            placement_application_response.save()
            if response_files:
                for response_file in response_files:
                    response_file.save()

            return redirect('applications')
        
        if request.POST.get("eligible") or request.POST.get("ineligible"):
            criteria = todict(request.POST)
            if request.POST.get("eligible"):
                form_id = request.POST.get('eligible')
            else:
                form_id = request.POST.get('ineligible')
            form = PlacementApplication.objects.get(id=form_id)
            params = form.form_fields
            responses = PlacementApplicationResponse.objects.filter(placement_application=form)
            dataset = prepare_responses(params,responses)
            original = dataset
            for key in criteria:
                if key.endswith('-min-'):
                    col = key.replace('-min-','')
                    dataset = dataset[dataset[col]>=criteria[key]]
                elif key.endswith('-max-'):
                    col = key.replace('-max-','')
                    dataset = dataset[dataset[col]<=criteria[key]]
                elif key.endswith('-choice-'):
                    col = key.replace('-choice-','')
                    if isinstance(criteria[key],str):
                        criteria[key] = [criteria[key]]
                    dataset = dataset[dataset[col].isin(criteria[key])]
            response = HttpResponse(content_type='text/csv')
            if request.POST.get("eligible"):
                response['Content-Disposition'] = 'attachment; filename=eligible.csv'
                dataset.to_csv(path_or_buf=response)  # with other applicable parameters
            else:
                response['Content-Disposition'] = 'attachment; filename=ineligible.csv'
                original = original[~original.isin(dataset)].dropna(how = 'all')
                ineligible = original
                ineligible.to_csv(path_or_buf=response)
            return response

        if request.POST.get("indiv"):
            form_id = request.POST.get('indiv')
            form = PlacementApplication.objects.get(id=form_id)
            responses = PlacementApplicationResponse.objects.filter(placement_application=form)
            files_uploaded = {}
            for response in responses:
                if response.student.roll_number not in files_uploaded.keys():
                    files_uploaded[response.student.roll_number] = {}
                try:
                    files = PlacementApplicationResponseFiles.objects.get(response=response)
                    files_uploaded[response.student.roll_number][files.label] = files.file_uploaded
                except:
                    pass
            return render(request,'indiv-responses.html',{'files':files_uploaded,'form_id':form_id})
        
        if request.POST.get("files-indiv"):
            roll_no = request.POST.get('files-indiv')
            form_id = request.POST.get('form_id')
            form = PlacementApplication.objects.get(id=form_id)
            student = Student.objects.get(roll_number=roll_no)
            response = PlacementApplicationResponse.objects.get(placement_application=form,student=student)
            files_uploaded = {}
            try:
                files = PlacementApplicationResponseFiles.objects.filter(response=response)
                for file in files:
                    files_uploaded[file.label] = file.file_uploaded
            except:
                pass
            print(files_uploaded)
            return render(request,'files.html',{'files':files_uploaded})
        

        if request.POST.get("response-indiv"):
            roll_no = request.POST.get('response-indiv')
            form_id = request.POST.get('form_id')
            placement_application = PlacementApplication.objects.get(id=form_id)
            student = Student.objects.get(roll_number=roll_no)
            params = placement_application.form_fields
            params = params.replace("'",'"')
            params = json.loads(params)
            placement_application_response = None
            form,form_title,form_description = ResponsePreviewer(params,False,True)
            try:
                placement_application_response = get_object_or_404(PlacementApplicationResponse,placement_application=placement_application,student=student)
                responses = json.loads(placement_application_response.responses)
                responses = clean_responses(responses,form.fields)
            except:
                responses = None

            try:
                response_files = PlacementApplicationResponseFiles.objects.filter(response=placement_application_response)
                if response_files:
                    responses = addfiles(responses,response_files)
            except:
                response_files = None

            if responses:
                form.set_initial(responses)
            return render(request,'fillform.html',{'form':form,'title':form_title,'description':form_description,'form_id':form_id})


def listdiff(list1,list2):
    list_difference = []
    for item in list1:
        if item not in list2:
            list_difference.append(item)
    return list_difference

def placement_status_view(request):
    if request.method == 'GET':
        status = {}
        rnos = PlacementApplicationResponse.objects.values_list('student__roll_number',flat=True).distinct()
        sent_offers = {}
        for rno in rnos:
            name = Student.objects.get(roll_number=rno).user.get_full_name()
            status[rno] = [name]
            student_responses = PlacementApplicationResponse.objects.filter(student=Student.objects.get(roll_number=rno))
            d0_company = []
            d1_company = []
            d2_company = []
            for student_response in student_responses:
                company = student_response.placement_application.company
                if company.day == 'Day 0':
                    d0_company.append(company.name)
                elif company.day == 'Day 1':
                    d1_company.append(company.name)
                elif company.day == 'Day 2':
                    d2_company.append(company.name)
            
            try:
                sent_offers = PlacementStatus.objects.get(student= Student.objects.get(roll_number=rno))
                sent_offers.offers = json.loads(sent_offers.offers)
                status[rno].append(listdiff(d0_company,sent_offers.offers['Day0']))
                status[rno].append(sent_offers.offers['Day0'])
                status[rno].append(listdiff(d1_company,sent_offers.offers['Day1']))
                status[rno].append(sent_offers.offers['Day1'])
                status[rno].append(listdiff(d2_company,sent_offers.offers['Day2']))
                status[rno].append(sent_offers.offers['Day2'])
            except:
                status[rno].append(d0_company)
                status[rno].append([])
                status[rno].append(d1_company)
                status[rno].append([])
                status[rno].append(d2_company)
                status[rno].append([])
        return render(request,'placement_status.html',{'statuses':status})

    if request.method == 'POST':
        rno = request.POST.get('offers')
        d0_offers = request.POST.getlist(str(rno)+'-Day0')
        d1_offers = request.POST.getlist(str(rno)+'-Day1')
        d2_offers = request.POST.getlist(str(rno)+'-Day2')
        if "" in d0_offers :
            d0_offers.remove("")
        if "" in d1_offers :
            d1_offers.remove("")
        if "" in d2_offers :
            d2_offers.remove("")
        offers = {}
        offers['Day0'] = d0_offers
        offers['Day1'] = d1_offers
        offers['Day2'] = d2_offers
        offers = json.dumps(offers)
        student = Student.objects.get(roll_number = rno)

        try:
            status = get_object_or_404(PlacementStatus,student=student)
            status.offers = offers
            status.save()
        except:
            status = PlacementStatus()
            status.student = student
            status.offers = offers
            status.save()

        return redirect('placement_status')


def placement_offers_view(request):
    if request.method == 'GET':
        student = Student.objects.get(user=request.user)
        try:
            offers = PlacementStatus.objects.get(student=student).offers
            offers = json.loads(offers)
            status = PlacementStatus.objects.get(student=student)
            if status.day0_selected_company_name == None:
                status.day0_selected_company_name = ""
            if status.day1_selected_company_name == None:
                status.day1_selected_company_name = ""
            if status.day2_selected_company_name == None:
                status.day2_selected_company_name = ""
        except:
            offers = {}
            status = []
        return render(request,'placement_offers.html',{'offers':offers,'status':status})

    elif request.method == 'POST':
        student = Student.objects.get(user=request.user)
        student_responses = PlacementApplicationResponse.objects.filter(student=student)   
        status = PlacementStatus(student = student)   
        if request.POST.getlist("day0sub"):
            cname = request.POST.getlist('day0')[0]
            for student_response in student_responses:
                company = student_response.placement_application.company
                if company.name==cname and company.day== 'Day 0':
                    salary = company.starting_salary
                    status.day0_selected_company_name = company.name
                    status.day0_selected_company_salary = salary
                    status.save(update_fields=['day0_selected_company_name','day0_selected_company_salary'])
                    break
            return redirect('placement_offers')

        elif request.POST.getlist("day1sub"):
            cname = request.POST.getlist('day1')[0]
            for student_response in student_responses:
                company = student_response.placement_application.company
                if company.name==cname and company.day== 'Day 1':
                    salary = company.starting_salary
                    status.day1_selected_company_name = company.name
                    status.day1_selected_company_salary = salary
                    status.save(update_fields=['day1_selected_company_name','day1_selected_company_salary'])
                    break
            return redirect('placement_offers')
        
        elif request.POST.getlist("day2sub"):
            cname = request.POST.getlist('day2')[0]
            for student_response in student_responses:
                company = student_response.placement_application.company
                if company.name==cname and company.day== 'Day 2':
                    salary = company.starting_salary
                    status.day2_selected_company_name = company.name
                    status.day2_selected_company_salary = salary
                    status.save(update_fields=['day2_selected_company_name','day2_selected_company_salary'])
                    break
            return redirect('placement_offers')

        
        elif request.POST.getlist("finalsub"):
            final = request.POST.getlist('final')[0]
            cname = final[0:final.find('(Day ')-1]
            day = final[final.find('(Day ') + 1:final.find('(Day ') + 6]
            for student_response in student_responses:
                company = student_response.placement_application.company
                if company.name == cname and company.day == day:
                    salary = company.starting_salary
                    status.placed_company_name = company.name
                    status.placed_company_salary = salary
                    status.placed_company_day = day
                    status.placed_year = Student.objects.get(user=request.user).expected_grad_year
                    status.save(update_fields=['placed_company_name','placed_company_salary','placed_company_day','placed_year'])
                    break
            return redirect('placement_offers') 

def backup_view(request):
    if request.method == 'GET':
        return render(request,'backup.html')
    
    elif request.method == 'POST':
        if request.POST.get('company'):
            dataset = CompanyResource().export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="companies.csv"'
            return response
        
        if request.POST.get('user'):
            dataset = UserResource().export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users.csv"'
            return response
        
        if request.POST.get('student'):
            dataset = StudentResource().export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="students.csv"'
            return response
        
        if request.POST.get('placementapp'):
            dataset = PlacementApplicationResource().export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="placement-applications.csv"'
            return response

        if request.POST.get('placementappres'):
            dataset = PlacementApplicationResponseResource().export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="placement-applications-responses.csv"'
            return response

        if request.POST.get('placementstatus'):
            dataset = PlacementStatusResource().export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="placement-status.csv"'
            return response

def getscatterplots(plot_dataset):
    fig = make_subplots(rows=1, cols=2)
    # Subplot 1
    fig.add_trace(
        go.Scatter(
            name="Yearly Placed",
            x=plot_dataset["Placement Year"],
            y=plot_dataset["Total Placed"],
        ),
        row=1,
        col=1,
    )

    # Subplot 2
    fig.add_trace(
        go.Scatter(
            name="Yearly Appeared",
            x=plot_dataset["Placement Year"],
            y=plot_dataset["Total Appeared"],
        ),
        row=1,
        col=2,
    )

    fig.update_layout(title='Yearly Placed and Appeared',xaxis_title='Placement Year',yaxis_title='Count')
    yearly_scatter_plot_div=plot(fig, output_type='div',include_plotlyjs=False)

    return yearly_scatter_plot_div


def getbarplots(plot_dataset):
    fig = make_subplots(rows=1, cols=2)
    # Subplot 1
    fig.add_trace(
        go.Bar(
            name="Yearly Placed",
            x=plot_dataset["Placement Year"],
            y=plot_dataset["Total Placed"],
        ),
        row=1,
        col=1,
    )

    # Subplot 2
    fig.add_trace(
        go.Bar(
            name="Yearly Appeared",
            x=plot_dataset["Placement Year"],
            y=plot_dataset["Total Appeared"],
        ),
        row=1,
        col=2,
    )

    fig.update_layout(title='Yearly Placed and Appeared Count',xaxis_title='Placement Year',yaxis_title='Count')
    yearly_bar_plot_div=plot(fig, output_type='div',include_plotlyjs=False)

    return yearly_bar_plot_div

def getpieplots(plot_dataset):
    fig = make_subplots(rows=1, cols=2,specs=[[{"type": "pie"}, {"type": "pie"}]])
    # Subplot 1
    fig.add_trace(
        go.Pie(
            name="Placed",
            labels=plot_dataset["Placement Year"],
            values=plot_dataset["Total Placed"],
            domain=dict(x=[0, 0.5]),
        ),
        row=1,col=1,
    )

    # Subplot 2
    fig.add_trace(
        go.Pie(
            name="Appeared",
            labels=plot_dataset["Placement Year"],
            values=plot_dataset["Total Appeared"],
            domain=dict(x=[0.5, 1.0]),
        ),
        row=1,col=2
    )

    fig.update_layout(title='Placed and Appeared per Year Percentage',xaxis_title='Placement Year',yaxis_title='Count')
    yearly_pie_plot_div=plot(fig, output_type='div',include_plotlyjs=False)

    return yearly_pie_plot_div


def getdata(years_options):
    dataset = pd.DataFrame(columns = ['Roll Number','Name','Placed_Company','Year'])
    students_applied_rno = PlacementApplicationResponse.objects.filter(placement_application__placement_year__in = years_options).values('student__roll_number').distinct()
    rnos = []
    names = []
    placed_companies = []
    years = []
    for rno in students_applied_rno:
        roll_num = rno['student__roll_number']
        student = Student.objects.get(roll_number = roll_num)
        years.append(student.expected_grad_year)
        rnos.append(roll_num)
        names.append(student.user.get_full_name())
        try :
            status = PlacementStatus.objects.get(student=student)
            if status.placed_company_name == '' or status.placed_company_name == None:
                placed_companies.append('')
            else:
                placed_companies.append(status.placed_company_name)
        except:
            placed_companies.append('')
    dataset['Roll Number'] = rnos
    dataset['Name'] = names
    dataset['Placed_Company'] = placed_companies
    dataset['Year'] = years
    total_placed = []
    total_appeared = []
    for year in years_options:
        appeared_dataset = dataset[dataset['Year'] == int(year)]
        placed_dataset = appeared_dataset[appeared_dataset['Placed_Company'] != '']
        total_placed.append(len(placed_dataset))
        total_appeared.append(len(appeared_dataset))
    
    plot_dataset = pd.DataFrame(columns=['Placement Year','Total Placed'])
    plot_dataset['Placement Year'] = years_options
    plot_dataset['Total Placed'] = total_placed
    plot_dataset['Total Appeared'] = total_appeared

    yearly_bar_plots = getbarplots(plot_dataset)
    yearly_pie_plots = getpieplots(plot_dataset)
    yearly_scatter_plots = getscatterplots(plot_dataset)
    return plot_dataset,yearly_bar_plots,yearly_pie_plots,yearly_scatter_plots
    

def report_view(request):
    year_options = PlacementStatus.objects.values('placed_year').distinct()
    if request.method == 'GET':
        return render(request,'report.html',{'year_options': year_options})

    if request.method == 'POST':
        if request.POST.get('yearly'):
            years = request.POST.getlist('yearly-select')
            dataset,yearly_bar_plots,yearly_pie_plots,yearly_scatter_plots = getdata(years)
            return render(request,'report.html',{'year_options': year_options,'bar_plot':yearly_bar_plots,'pie_plot':yearly_pie_plots,'scatter_plot':yearly_scatter_plots})