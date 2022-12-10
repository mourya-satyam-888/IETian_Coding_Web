import datetime
import json
import os
import random
import sys
import time
from datetime import date

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from users.models import Profile
from django.utils import timezone
import urllib3

from .forms import Statement
from .models import Problem, Solution, Result, Problem_Feature, Problem_Tags


# userrank = [i+1 for i,x in enumerate(sorted(USERS)) if x == 1111]


# def problem(request):
#     context = {
#         'problems': Problem.objects.order_by('-id'),

#     }
#     return render(request, 'judge/problems.html',context)
def user_info(request, name):
    try:
        usr = User.objects.get(username=name)
    except:
        return HttpResponse("No such user!")

    rank = 0
    p = Profile.objects.order_by('-rating')
    counter = 0
    for i in p:
        counter = counter + 1
        if i.user.username == name:
            break
    rank = counter

    graph = usr.graph_set.order_by('id')
    solutions = Solution.objects.filter(usr=User.objects.get(username=name)).order_by('-id')[:5]
    isAllowed = False
    if name == request.user.username:
        isAllowed = True
    return render(request, 'judge/profile.html',
                  {'usr': usr, 'rank': rank, 'graph': graph, 'last': graph.last(), 'solutions': solutions,
                   'isAllowed': isAllowed})


class UsersListView(ListView):
    model = Profile
    template_name = 'judge/users.html'
    context_object_name = 'users'
    ordering = ['-rating']
    paginate_by = 10


def judge(request):
    problems = Problem.objects.all()[:8]
    return render(request, 'judge/judge.html', {'problems': problems})

def is_faculty(request):
    email = request.user.email
    ##faculty email
    if email=="mouryas953@gmail.com":
        return True
    return False

def student_info(request):
    email = request.user.email
    if email == "satyammourya8989@gmail.com":
        return [2,"CS"]
    return [1,"IT"]
    ##returns {year,branch}

@login_required
def problems(request):
    faculty=is_faculty(request)
    if faculty:
        u=User.objects.get(id=request.user.id)
        p=u.problem_set.order_by("due_date")
        page = request.GET.get('page', 1)
        paginator = Paginator(p, 10)
        try:
            problems = paginator.page(page)
        except PageNotAnInteger:
            problems = paginator.page(1)
        except EmptyPage:
            problems = paginator.page(paginator.num_pages)
        return render(request, 'judge/problems.html', {'problems': problems, "faculty": True})
    student = student_info(request)
    today=timezone.now()
    p=Problem.objects.filter(year=student[0]).filter(branch=student[1]).filter(due_date__gt=today)
    page = request.GET.get('page', 1)
    paginator = Paginator(p, 10)
    try:
        problems = paginator.page(page)
    except PageNotAnInteger:
        problems = paginator.page(1)
    except EmptyPage:
        problems = paginator.page(paginator.num_pages)
    return render(request, 'judge/problems.html', {'problems': problems,"faculty":False})

@login_required
def solutions(request,pid):
    faculty=is_faculty(request)
    if faculty and Problem.objects.get(id=pid).auth==request.user:

        u=Problem.objects.get(id=pid)
        p=u.solution_set.filter(verdict="ac").order_by("-id")
        page = request.GET.get('page', 1)
        paginator = Paginator(p, 10)
        try:
            problems = paginator.page(page)
        except PageNotAnInteger:
            problems = paginator.page(1)
        except EmptyPage:
            problems = paginator.page(paginator.num_pages)
        return render(request, 'judge/solutions.html', {'solutions': problems, "faculty": True})
    return render(request, 'judge/solutions.html')
@login_required
def sol_detail(request,pid,sid):
    faculty=is_faculty(request)
    if faculty and Problem.objects.get(id=pid).auth==request.user:
        sol_file=Solution.objects.get(id=sid).solution_file.read().decode("UTF-8")
        return render(request, 'judge/sol_detail.html', {'sol_file': sol_file})
    return render(request, 'judge/sol_detail.html')
class ProblemListView(ListView):
    model = Problem
    template_name = 'judge/problems.html'
    context_object_name = 'problems'
    ordering = ['-id']
    paginate_by = 10

@login_required
def orderproblem(request):
    faculty = is_faculty(request)
    if faculty:
        u = User.objects.get(id=request.user.id)
        prob = u.problem_set.order_by("due_date")
    else:
        student = student_info(request)
        today = timezone.now()
        prob = Problem.objects.filter(year=student[0]).filter(branch=student[1]).filter(due_date__gt=today)
    by = request.GET.get('by')
    order = request.GET.get('order')
    if by == "accuracy":
        if order == "ascending":
            messages.success(request, f'Ordered by : Highest accuracy')
            p = prob.order_by('-problem_feature__accuracy')

        else:
            messages.success(request, f'Ordered by : Lowest accuracy')
            p = prob.order_by('problem_feature__accuracy')


    elif by == "submissions":
        if order == "ascending":
            messages.success(request, f'Ordered by : Most submissions')
            p = prob.order_by('-problem_feature__total_submission')
        else:
            messages.success(request, f'Ordered by : Least submissions')
            p = prob.order_by('problem_feature__total_submission')

    elif by == "difficulty":
        if order == "ascending":
            messages.success(request, f'Ordered by : Easy first')
            p = prob.order_by('difficultylevel')
        else:
            messages.success(request, f'Ordered by : Tough first')
            p = prob.order_by('-difficultylevel')

    else:
        if order == "ascending":
            messages.success(request, f'Ordered by : Newest first')
            p = prob.order_by('-date_added')
        else:
            messages.success(request, f'Ordered by : Oldest first')
            p = prob.order_by('date_added')

    page = request.GET.get('page', 1)
    paginator = Paginator(p, 10)
    try:
        problems = paginator.page(page)
    except PageNotAnInteger:
        problems = paginator.page(1)
    except EmptyPage:
        problems = paginator.page(paginator.num_pages)
    return render(request, 'judge/problems.html', {'problems': problems, 'ordered': "true", 'by': by, 'order': order,"faculty":faculty})

@login_required
def detail(request, pid):
    # faculty=is_faculty(request)
    # if faculty:
    #     if Problem.objects.get(id=pid).auth!=User.objects.get(id=request.user.id):
    #         return redirect("/problems/")
    #     problem = Problem.objects.get(id=pid)
    #     solutions = problem.solution_set.order_by('-id')
    #     arr = []
    #     counter = 0
    #     # for solution in solutions:
    #     #     if counter == 5:
    #     #         break
    #     #     if solution.result.verdict == 'ac':
    #     #         arr.append(solution)
    #     #         counter = counter + 1
    #     context = {
    #         'problem': problem,
    #         'solutions': arr
    #
    #     }
    #     return render(request, 'judge/detail.html', context)
    # student = student_info(request)
    # today = timezone.now()
    faculty = is_faculty(request)
    problem = Problem.objects.get(id=pid)
    if faculty:
        solutions = problem.solution_set.order_by('-id')
    else:
        solutions=problem.solution_set.filter(usr=request.user)
    arr = []
    counter = 0
    for solution in solutions:
         if counter == 5:
             break
         if solution.verdict == 'ac':
             arr.append(solution)
             counter = counter + 1
    context = {
        'problem': problem,
        'solutions': arr,
        "faculty":faculty

    }
    return render(request, 'judge/detail.html', context)

@login_required
def piechart(user_id, verdict):
    if not verdict == 'cdt':
        usr = User.objects.get(id=user_id)
        prof = Profile.objects.get(user=usr)
        if verdict == 'ac':
            prof.ac_solution = prof.ac_solution + 1
        elif verdict == 'wa':
            prof.wa_solution = prof.wa_solution + 1
        elif verdict == 'ce':
            prof.ce_solution = prof.ce_solution + 1
        elif verdict == 'tle':
            prof.tle_solution = prof.tle_solution + 1
        prof.save()

@login_required
def addproblem(request):
    if not is_faculty(request):
        return redirect("judge")
    form = Statement(request.POST)
    return render(request, 'judge/addproblem.html', {'form': form})

@login_required
def save(request):
    usr = User.objects.get(id=request.user.id)
    #due=datetime(request.POST["due_date"])
    due=datetime.datetime.strptime(request.POST["due_date"], '%Y-%m-%d')+datetime.timedelta(hours=23)+datetime.timedelta(minutes=59)
    print(due)
    p = usr.problem_set.create(title=request.POST['title'], statement=request.POST['statement'],
                               constraint=request.POST['constraint'],
                               input_format=request.POST['input_format'], output_format=request.POST['output_format'],
                               sample_input=request.POST['sample_input'],
                               sample_output=request.POST['sample_output'], explaination=request.POST['explaination'],
                               time_limit=request.POST['time_limit'],
                               difficulty=request.POST['difficulty'], input_file=request.FILES['input_file'],
                               output_file=request.FILES['output_file'], year=request.POST["year"], branch=request.POST["branch"],
                               due_date=due
                               )
    tags = request.POST.getlist('tag[]')
    p.save()
    f = Problem_Feature.objects.create(problem=p, accuracy=0, total_submission=0)
    f.save()
    a = Problem.objects.get(id=p.id)
    for tag in tags:
        t = Problem_Tags.objects.create(problem=a, tags=tag)
        t.save()

    # b = a.input_file.name
    # pathin = "media/" + b
    # infile = open(pathin, "rt")
    # c = a.output_file.name
    # pathout = "media/" + c
    # outfile = open(pathout, "rt")
    # url = 'http://127.0.0.1:5000/add_problem/'
    # var = requests.post(url, data={'sol_id': p.id, 'sol_time': a.time_limit},
    #                     files={'sol_in': infile, 'sol_out': outfile})
    # infile.close()
    # outfile.close()
    messages.success(request, f'Problem Added')
    return redirect('/judge/problems')

@login_required
def accuracy_submission(pid, verdict):
    f = Problem_Feature.objects.get(problem_id=pid)
    if verdict != "ce":
        if verdict == "ac":
            ca = ((f.accuracy * f.total_submission) / 100) + 1
            f.accuracy = (ca / (f.total_submission + 1)) * 100

        if verdict == "wa" or verdict == "tle":
            wa = (((100 - f.accuracy) * f.total_submission) / 100) + 1
            f.accuracy = 100 - (wa / (f.total_submission + 1)) * 100

        f.total_submission = f.total_submission + 1
        f.save()

@login_required
def submit(request, pid):
    # p=Problem.objects.get(id=pid)
    # sol=p.solution_set.create(usr=request.user,language=request.POST['language'],solution_file=request.FILES['myfile'])
    # p.save()
    # a=Solution.objects.get(id=sol.id)
    # b=a.solution_file.name
    # path="media/"+b
    # myfile=open(path,"rt")
    # lines = []
    # for line in myfile:
    #     lines.append(line)
    # url='http://192.168.43.182:8080/program/'
    # # var=requests.post(url,data={'sol_id':pid,'language':a.language},files={'solution':myfile})
    # myfile.close()
    # r=Result.objects.all()
    # # s=r.create(solution=a,verdict=var.json()['verdict'],time=var.json()['time'],message=var.json()['message'])
    # s=r.create(solution=a,verdict='ac',time=0.002,message="")
    # s.save()
    # accuracy_submission(pid,'ac')
    # context={
    #     'result':a.result,
    #     'code':lines
    #     }
    # print(lines)
    # time.sleep(3)
    p = Problem.objects.get(id=pid)
    context = {
        'id': pid,
        'title': p.title,
        'time_limit': p.time_limit
    }

    return render(request, 'judge/submit.html', context)

@login_required
def ide(request):
    return render(request, 'judge/ide.html')

@login_required
@csrf_exempt
def runcode(request):
    language = request.POST['language']
    if language == "C":
        language = "c"
    elif language == "C++":
        language = "cpp"
    elif language == "JAVA":
        language = "java"
    else:
        language = "python3"
    source_code = request.POST['code']
    input = request.POST['custom_input']
    payload = {
        "source_code": source_code,
        "language": language,
        "input": input,
        "api_key": "guest"
    }
    import urllib.request
    req = urllib.request.Request("http://api.paiza.io:80/runners/create", method="POST")
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(payload)
    data = data.encode()
    response = urllib.request.urlopen(req, data=data)
    response = response.read().decode('UTF-8')
    response = json.loads(response)
    print(response)
    id = response["id"]
    cnt = 0
    f = 1
    while cnt < 20 and f:
        u = "http://api.paiza.io:80/runners/get_status?id=" + str(id) + "&api_key=guest"
        req = urllib.request.Request(u, method="GET")
        response = urllib.request.urlopen(req)
        response = response.read().decode('UTF-8')
        response = json.loads(response)
        print(response)
        if response["status"] == "completed":
            f = 0
            break
        cnt += 1
        time.sleep(2)
    u = "http://api.paiza.io:80/runners/get_details?id=" + str(id) + "&api_key=guest"
    req = urllib.request.Request(u, method="GET")
    response = urllib.request.urlopen(req)
    response = response.read().decode('UTF-8')
    response = json.loads(response)
    # print(var.json())
    response_data = {}
    if response["build_result"] == "failure":
        output = response["build_stderr"]
    elif response["result"] == "failure":
        output = response.get("stderr", "")
    else:
        output = response.get("stdout", "")
    print(response, output)
    if response["result"] == None:
        response["result"] = "compile time error"
        response["time"] = "0.00"
    se_text = '''<table style="width: 100%;">
    	<tbody>
    		<tr>
    			<td style="width: 100%; background-color: rgb(209, 213, 216);"><strong>&gt;_ &nbsp;</strong>Compile info
    				<br>
    			</td>
    		</tr>
    		<tr>
    			<td style="width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Status&nbsp;</span></strong><span style="font-size: 18px; color: rgb(97, 189, 109);">''' + response.get(
        "result",
        "error") + '''</span><span style="font-size: 18px;"><em><span style="color: rgb(184, 49, 47);">&nbsp;</span></em>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<strong>Time</strong>''' + response.get(
        "time", "0") + '''s</span>
    				<br>
    			</td>
    		</tr>
    		<tr>
    			<td style="width: 100.0000%;">
    			<center><textarea style="border:white;margin-bottom:5px;width:99%;font-family:Courier New" rows="7">''' + output + '''</textarea></center>
    			</td>
    		</tr>
    	</tbody>
    </table>'''

    response_data['response'] = se_text
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# @csrf_exempt
# def viafile(request, pid):
#     p = Problem.objects.get(id=pid)
#     sol = p.solution_set.create(usr=request.user, language=request.POST['language'],
#                                 solution_file=request.FILES['myfile'])
#     p.save()
#     a = Solution.objects.get(id=sol.id)
#     b = a.solution_file.name
#     path = "media/" + b
#     myfile = open(path, "rt")
#     url = 'http://192.168.43.245:8000/program/'
#     var = requests.post(url, data={'sol_id': pid, 'language': a.language}, files={'solution': myfile})
#     myfile.close()
#     # r = Result.objects.all()
#     s = Result.objects.create(solution=a, verdict=var.json()['verdict'], time=var.json()['time'], message=var.json()['message'])
#     # s=r.create(solution=a,verdict='ac',time=0.002,message="")
#     s.save()
#     accuracy_submission(pid, var.json()['verdict'])
#     piechart(request.user.id, var.json()['verdict'])
#     response_data = {}
#     if var.json()['verdict'] == 'ac':
#         response_data['response'] = '''<table style="width: 100%;">
# 	<tbody>
# 		<tr>
# 			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgb(65, 168, 95);">AC</span> <span style="color: rgb(65, 168, 95);"><i class="fa fa-check-circle fr-deletable"></i>&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;<strong>Time&nbsp;</strong>''' + \
#                                     var.json()['time'] + '''</span></td>
# 		</tr>
# 	</tbody>
# </table>'''
#
#
#     elif var.json()['verdict'] == 'ce':
#         response_data['response'] = '''
#     <table style="width: 100%;">
# 	<tbody>
# 		<tr>
# 			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result&nbsp;</span></strong><span style="font-size: 18px;"><span style="color: rgb(184, 49, 47);">CE</span> <span style="color: rgb(184, 49, 47);"><i class="fa fa-warning  fr-deletable"></i>&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;<strong>Time&nbsp;</strong>0s</span></td>
# 		</tr>
# 		<tr>
# 			<td style="padding-left:20px;padding-right:20px;padding-bottom:5px;width: 100.0000%;"><i class="fa fa-terminal"></i>
# 				''' + var.json()['message'] + '''
# 		</tr>
# 	</tbody>
# </table>
#
# <br>
# '''
#     elif var.json()['verdict'] == 'wa':
#         response_data['response'] = '''
#         <table style="width: 100%;">
# 	<tbody>
# 		<tr>
# 			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgb(184, 49, 47);">WA</span> <span style="color: rgb(184, 49, 47);"><i class="fa fa-remove  fr-deletable"></i>&nbsp;</span><span style="color: rgb(65, 168, 95);">&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <strong>Time&nbsp;</strong>''' + \
#                                     var.json()['time'] + '''</span></td>
# 		</tr>
# 	</tbody>
# </table>
# '''
#     elif var.json()['verdict'] == 'tle':
#         response_data['response'] = '''
#         <table style="width: 100%;">
# 	<tbody>
# 		<tr>
# 			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgb(184, 49, 47);">TLE</span> <span style="color: rgb(184, 49, 47);"><i class="fa fa-clock-o fr-deletable"></i> &nbsp;</span><span style="color: rgb(65, 168, 95);">&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <strong>&nbsp;</strong></span></td>
# 		</tr>
# 	</tbody>
# </table>
#     '''
#     elif var.json()['verdict'] == 'cdt':
#         response_data['response'] = '''
#         <table style="width: 100%;">
# 	<tbody>
# 		<tr>
# 			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgba(255, 255, 255,);"> : CoolDown Time</span> <span style="color: rgb(135,206,235);"><i class="fa fa-fan fr-deletable"></i> &nbsp;</span><span style="color: rgb(65, 168, 95);">&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <strong>&nbsp;</strong></span></td>
# 		</tr>
# 	</tbody>
# </table>'''
#
#     return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def viacode(request, pid):

    lang = request.POST['language']
    language=""
    f_name = str(random.randint(0, 99999999))
    extension = ""
    if lang == "C":
        extension = ".c"
        language="c"
    elif lang == "C++":
        extension = ".cpp"
        language="cpp"
    elif lang == "JAVA":
        extension = ".java"
        language="java"
    else:
        extension = ".py"
        language = "python3"
    c = open(f_name + extension, "w+")
    c.write(request.POST['code'])
    p = Problem.objects.get(id=pid)
    sol = p.solution_set.create(usr=request.user, language=language, solution_file=File(c))
    p.save()
    c.close()
    # myfile = open(f_name + extension, "rt")
    a = Solution.objects.get(id=sol.id)
    # url = 'http://192.168.43.245:8000/program/'
    # var = requests.post(url, data={'sol_id': pid, 'language': a.language}, files={'solution': myfile})
    # myfile.close()
    ## to open input file for this

    inp=p.input_file.read().decode('UTF-8')
    lines=p.output_file.read().decode('UTF-8')

    ##lets call run api
    source_code = request.POST['code']
    input = inp
    payload = {
        "source_code": source_code,
        "language": language,
        "input": input,
        "api_key": "guest"
    }
    import urllib.request
    req = urllib.request.Request("http://api.paiza.io:80/runners/create", method="POST")
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(payload)
    data = data.encode()
    response = urllib.request.urlopen(req, data=data)
    response = response.read().decode('UTF-8')
    response = json.loads(response)
    print(response)
    id = response["id"]
    cnt = 0
    f = 1
    while cnt < 20 and f:
        u = "http://api.paiza.io:80/runners/get_status?id=" + str(id) + "&api_key=guest"
        req = urllib.request.Request(u, method="GET")
        response = urllib.request.urlopen(req)
        response = response.read().decode('UTF-8')
        response = json.loads(response)
        print(response)
        if response["status"] == "completed":
            f = 0
            break
        cnt += 1
        time.sleep(2)
    u = "http://api.paiza.io:80/runners/get_details?id=" + str(id) + "&api_key=guest"
    req = urllib.request.Request(u, method="GET")
    response = urllib.request.urlopen(req)
    response = response.read().decode('UTF-8')
    response = json.loads(response)
    # print(var.json())
    response_data = {}
    verdict=""
    rtime="0.0"
    if response["build_result"] == "failure":
        verdict = "ce"
        # output = response["build_stderr"]
    elif response["result"] == "failure":
        verdict = "ce"
    elif response["result"][0]=="t":
        verdict = "tle"
    else:
        verdict="find"
    if response["result"] == None:
        verdict="ce"
    if verdict=="find":
        output=response["stdout"].strip("\n")
        rtime = response["time"]
        lines=lines.strip("\n").strip().split("\n")
        output=output.split("\n")
        print(len(lines),len(output))
        fl=(len(lines)==len(output))
        if fl:
            for i in range(len(lines)):
                if lines[i].strip()!=output[i].strip():
                    fl=0
                    break
        if fl:
            verdict="ac"
        else:
            verdict="wa"
    print(verdict)
    # r = Result.objects.all()
    s = Result.objects.create(solution=a, verdict=verdict, time=rtime, message="")
    # s=r.create(solution=a,verdict='ac',time=0.002,message="")
    s.save()
    ss = Solution.objects.get(id=sol.id)
    ss.verdict = verdict
    ss.save()
    # accuracy_submission(pid, verdict)
    # piechart(request.user.id, verdict)
    response_data = {}
    if verdict == 'ac':
        response_data['response'] = '''<table style="width: 100%;">
	<tbody>
		<tr>
			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgb(65, 168, 95);">AC</span> <span style="color: rgb(65, 168, 95);"><i class="fa fa-check-circle fr-deletable"></i>&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;<strong>Time&nbsp;</strong>''' + \
                                    response['time'] + '''</span></td>
		</tr>
	</tbody>
</table>'''


    elif verdict == 'ce':
        response_data['response'] = '''
    <table style="width: 100%;">
	<tbody>
		<tr>
			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result&nbsp;</span></strong><span style="font-size: 18px;"><span style="color: rgb(184, 49, 47);">CE</span> <span style="color: rgb(184, 49, 47);"><i class="fa fa-warning  fr-deletable"></i>&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;<strong>Time&nbsp;</strong>0s</span></td>
		</tr>
		<tr>
			<td style="padding-left:20px;padding-right:20px;padding-bottom:5px;width: 100.0000%;"><i class="fa fa-terminal"></i>
				''' + verdict + '''
		</tr>
	</tbody>
</table>

<br>
'''
    elif verdict == 'wa':
        response_data['response'] = '''
        <table style="width: 100%;">
	<tbody>
		<tr>
			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgb(184, 49, 47);">WA</span> <span style="color: rgb(184, 49, 47);"><i class="fa fa-remove  fr-deletable"></i>&nbsp;</span><span style="color: rgb(65, 168, 95);">&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <strong>Time&nbsp;</strong>''' + \
                                    response['time'] + '''</span></td>
		</tr>
	</tbody>
</table>
'''
    elif verdict == 'tle':
        response_data['response'] = '''
        <table style="width: 100%;">
	<tbody>
		<tr>
			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgb(184, 49, 47);">TLE</span> <span style="color: rgb(184, 49, 47);"><i class="fa fa-clock-o fr-deletable"></i> &nbsp;</span><span style="color: rgb(65, 168, 95);">&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <strong>&nbsp;</strong></span></td>
		</tr>
	</tbody>
</table>
    '''
    elif verdict== 'cdt':
        response_data['response'] = '''
        <table style="width: 100%;">
	<tbody>
		<tr>
			<td style="padding:20px;width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Result</span></strong><span style="font-size: 18px;">&nbsp;<span style="color: rgba(255, 255, 255,);"> : CoolDown Time</span> <span style="color: rgb(135,206,235);"><i class="fa fa-fan fr-deletable"></i> &nbsp;</span><span style="color: rgb(65, 168, 95);">&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <strong>&nbsp;</strong></span></td>
		</tr>
	</tbody>
</table>
    '''
    os.remove(f_name + extension)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def filter_tags(request):
    if request.POST.getlist('tag[]'):
        f_name = str(random.randint(0, 99999999))
        f = open("media/filter_list/" + f_name + ".txt", "w+")
        for tag in request.POST.getlist('tag[]'):
            f.write(tag + "\n")
        f.close()
    taglst = []
    if request.POST.getlist('tag[]'):
        c = open("media/filter_list/" + f_name + ".txt", "rt")
    else:
        if request.GET.get('file_name', '') == "":
            return HttpResponseRedirect('/judge/problems')

        c = open("media/filter_list/" + request.GET.get('file_name', '') + ".txt", "rt")
    for tag in c:
        taglst.append(tag.strip())
    c.close()

    p_list = []
    page = request.GET.get('page', 1)
    faculty = is_faculty(request)
    if faculty:
        u = User.objects.get(id=request.user.id)
        p = u.problem_set.order_by("due_date")
    else:
        student = student_info(request)
        today = timezone.now()
        p = Problem.objects.filter(year=student[0]).filter(branch=student[1]).filter(
            due_date__gt=today)
    #p = Problem.objects.order_by('-id')
    for problem in p:
        taglist = [x.tags for x in problem.problem_tags_set.all()]
        if all(item in taglist for item in taglst):
            p_list.append(problem)

    paginator = Paginator(p_list, 10)
    try:
        problems = paginator.page(page)
    except PageNotAnInteger:
        problems = paginator.page(1)
    except EmptyPage:
        problems = paginator.page(paginator.num_pages)

    if request.POST.getlist('tag[]'):
        messages.success(request, f'Filtered by : {taglst}')
        return render(request, 'judge/problems.html', {'problems': problems, 'file_name': f_name})
    else:
        messages.success(request, f'Filtered by : {taglst}')
        return render(request, 'judge/problems.html',
                      {'problems': problems, 'file_name': str(request.GET.get('file_name', ''))})

@login_required
def get_data(request):
    p = Problem.objects.all()
    easy = 0
    medium = 0
    hard = 0
    expert = 0
    for problem in p:
        if problem.difficulty == "Easy":
            easy = easy + 1
        elif problem.difficulty == "Medium":
            medium = medium + 1
        elif problem.difficulty == "Hard":
            hard = hard + 1
        else:
            expert = expert + 1
    return HttpResponse(json.dumps({'arr': [expert, hard, medium, easy]}), content_type="application/json")


def filter_difficulty(request, diff):
    p = Problem.objects.filter(difficulty=diff).order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(p, 10)
    try:
        problems = paginator.page(page)
    except PageNotAnInteger:
        problems = paginator.page(1)
    except EmptyPage:
        problems = paginator.page(paginator.num_pages)
    messages.success(request, f'Difficulty level : {diff}')
    return render(request, 'judge/problems.html', {'problems': problems, 'flag': "flag"})
