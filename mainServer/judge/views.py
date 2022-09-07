from django.http import HttpResponse
from django.shortcuts import render
import json
# Create your views here.


def ide(request):
    return render(request,"judge/ide.html")
def runcode(request):
    language = request.POST['language']
    if language == "C":
        language = "c"
    elif language == "C++":
        language = "cpp"
    elif language == "JAVA":
        language = "java"
    else:
        language = "py"
    code = request.POST['code']
    custom_input = request.POST['custom_input']
    payload = {
        "code": code,
        "language": language,
        "input": custom_input
    }
    import urllib.request
    req = urllib.request.Request("https://codex-api.herokuapp.com/", method="POST")
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(payload)
    data = data.encode()
    response = urllib.request.urlopen(req, data=data)
    response = response.read().decode('UTF-8')
    response = json.loads(response)
    try:
        output = response['output']
    except:
        output=response['error']
    # print(var.json())
    response_data = {}
    se_text = '''<table style="width: 100%;">
	<tbody>
		<tr>
			<td style="width: 100%; background-color: rgb(209, 213, 216);"><strong>&gt;_ &nbsp;</strong>Compile info
				<br>
			</td>
		</tr>
		<tr>
			<td style="width: 100%; background-color: rgb(239, 239, 239);"><strong><span style="font-size: 18px;">Status&nbsp;</span></strong><span style="font-size: 18px; color: rgb(97, 189, 109);">Executed</span><span style="font-size: 18px;"><em><span style="color: rgb(184, 49, 47);">&nbsp;</span></em>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<strong>Time</strong> 0.4s</span>
				<br>
			</td>
		</tr>
		<tr>
			<td style="width: 100.0000%;">
			<center><textarea style="border:white;margin-bottom:5px;width:99%;font-family:Courier New" rows="7">''' + \
              output + '''</textarea></center>
			</td>
		</tr>
	</tbody>
</table>'''

    response_data['response'] = se_text
    return HttpResponse(json.dumps(response_data), content_type="application/json")