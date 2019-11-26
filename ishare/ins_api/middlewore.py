import time
from django.http import HttpResponse
from django.http import JsonResponse
import math
from .models import ApiList
import hashlib
class TimeMiddleware(object):
	"""docstring for TimeMiddleware"""
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if request.path == "/api/Application/" or request.path[:9] == "/captcha/" or request.path[:7] == "/admin/" or request.path[:7] == "/media/" or request.path[:8] == "/static/" or request.path == "/api/timestamp/" or request.path[:7] == "/users/" or request.path[:10] == "/api-auth/":
			response = self.get_response(request)
			return response
		else:
			now = time.time()
			try:
				timestamp = float(request.GET['timestamp'])
			except:
				return JsonResponse({'status':'TimeError'})
			if abs(int(now - timestamp)) > 20:
				return JsonResponse({'status':'Timeout'})
			response = self.get_response(request)
			return response


class ApiMiddleware(object):
	"""docstring for ApiMiddleware"""
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if request.path == "/api/Application/" or request.path[:9] == "/captcha/" or request.path[:7] == "/admin/" or request.path[:7] == "/media/" or request.path[:8] == "/static/" or request.path == "/api/timestamp/" or request.path[:7] == "/users/" or request.path[:10] == "/api-auth/":
			response = self.get_response(request)
			return response
		else:
			try:
				timestamp = str(request.GET['timestamp'])
				appId = request.GET['appid']
				if ApiList.objects.get(appId=appId):
					api = ApiList.objects.get(appId=appId)
				else:
					return JsonResponse({'status':'Permission denied 403'})
				appKey = api.appKey
				sign = request.GET['sign']
				if sign != hashlib.md5((timestamp+appKey).encode(encoding='utf-8')).hexdigest():
					return JsonResponse({'status':'Permission denied 405'})
				response = self.get_response(request)
				return response
			except:
				return JsonResponse({'status':'Unknown Error'})



		
		
		