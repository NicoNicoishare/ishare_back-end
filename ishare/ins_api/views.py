from django.shortcuts import render
from django.http import HttpResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.db.models import Q
from rest_framework import serializers, authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from django.http import Http404
from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.hashers import make_password,check_password
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
import rsa
from .serializers import UserSerializer, PostSerializer, PhotoSerializer, CommentSerializer
from .serializers import BriefUser, BriefUserSerializer, LikesLinkSerializer, BriefPostSerializer, BriefPost
from .serializers import BriefLikesLink, BriefLikesLinkSerializer
from .models import LikesLink, PostsLink, Comments
from .models import ApiApplicationer, Posts, UsersActive, Keys, Photos, FollowsLink
import hashlib
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, mixins
import time
from users.utils import EmailActivationTokenGenerator, send_activation_email
from users.signals import user_activated, user_registered
from itertools import chain
from operator import attrgetter
from .serializers import Message, Message_1Serializer, Message_2Serializer, Message_3Serializer
from .serializers import BriefPostTest, BriefPostTestSerializer

def apiApplication(request):
	if request.method == 'POST':
		email = request.POST['email']
		name = request.POST['name']
		hashkey = request.POST['captcha_0']
		captcha = request.POST['captcha_1']
		realCaptcha = CaptchaStore.objects.get(hashkey=hashkey)
		if (realCaptcha.response == captcha.lower()):
			try:
				user = ApiApplicationer.objects.get(email=email)
				return render(request,'Application.html',{'message':'Please Not Again'})
			except:
				ApiApplicationer.objects.create(email=email,name=name)
				return render(request,'Application.html',{'message':'Success'})
		return render(request,'Application.html',{'message':'CaptchaError'})

	hashkey = CaptchaStore.generate_key()
	image_url = captcha_image_url(hashkey)
	content = {
	'image_url':image_url,
	'hashkey':hashkey,
	}
	return render(request,'Application.html',{'hashkey':hashkey,
											  'image_url':image_url})

class ShortPost(APIView):
	def get(self, request, pk, format=None):
		post = Posts.objects.get(pk=pk)
		user = User.objects.get(id=post.user.id)
		if LikesLink.objects.filter(user=request.user,post=post):
			is_dianzan = True
		else:
			is_dianzan = False
		if PostsLink.objects.filter(user=request.user,post=post):
			is_shoucang = True
		else:
			is_shoucang = False
		if len(Photos.objects.filter(post=post)) > 1:
			is_many = True
		else:
			is_many = False
		serializer = BriefPostSerializer({'username':user.username,
							  			  'introduction':post.introduction,
							  			  'Pub_time':post.Pub_time,
							  			  'likes_num':post.likes_num,
							  			  'com_num':post.com_num,
							  			  'profile_picture':user.profile_picture,
							  			  'photo_0':post.photo_0,
							  			  'photo_0_thumbnail':post.photo_0_thumbnail,
							  			  'is_dianzan':is_dianzan,
							  			  'is_shoucang':is_shoucang,
							  			  'post_id':post.id,
							  			  'post_user_id':post.user.id,
							  			  'user_id':user.id,
							  			  'is_many':is_many,
							  			  })
		return Response(serializer.data)

class UserDetail(APIView):
	permission_classes = (IsAuthenticated,)
	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except:
			raise Http404

	def get(self, request, pk, format=None):
		"""10"""
		user = self.get_object(pk)
		serializer = UserSerializer(user)
		post_num = len(Posts.objects.filter(user=user))
		return Response({'result':serializer.data,'post_num':post_num})

	def put(self, request, format=None):
		"""11"""
		data = request.data
		try:
			user = User.objects.get(id=request.user.id)
			try:
				user.profile_picture = data['profile_picture']
			except:
				pass
			try:
				user.nickname = data['nickname']
			except:
				pass
			try:
				user.gender = data['gender']
			except:
				pass
			try:
				user.birthday = data['birthday']
			except:
				pass
			try:
				user.introduction = data['introduction']
			except:
				pass
			try:
				user.address = data['address']
			except:
				pass
			user.save()
			return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

class PhotoList(APIView):
	def get(self, request):
		postid = request.GET['postid']
		photoList = Photos.objects.filter(post=postid).order_by('-time')
		photos = []
		for photo in photoList:
			photos.append({'id':photo.id,
						   'post':photo.post.id,
						   'photo':photo.photo,
						   'photo_thumbnail':photo.photo_thumbnail,
						   })
		photo_num = len(photoList)
		serializer = PhotoSerializer(photos, many=True)
		return Response({'photo_num':photo_num,'result':serializer.data})

class UserRegister(APIView):
	"""2"""
	def post(self, request, format=None):
		data = request.data
		username = data['username']
		email = data['email']
		password = data['password']
		nickname = data['nickname']
		try:
			User.objects.get(username=username)
			return Response({'status':'AccountError'})
		except:
			try:
				User.objects.get(email=email)
				return Response({'status':'EmailError'})
			except:
				try:
					password = make_password(password)
			
					user = User.objects.create(username=username,email=email,password=password,nickname=nickname)
					opts = {
					'user': user,
					'request': request,
					'from_email': None,
					'email_template': 'users/activation_email.html',
					'subject_template': 'users/activation_email_subject.html',
					'html_email_template': None,
					}
					send_activation_email(**opts)
					user_registered.send(sender=user.__class__, request=request, user=user)
					return Response({'status':'Success'})
				except:
					return Response({'status':'UnknownError'})

class Accounts(APIView):
	"""3"""
	def post(self, request, format=None):
		data = request.data
		try:
			if User.objects.filter(username=data['account']) or User.objects.filter(email=data['account']):
				return Response({'status':'Exist'})
			else:
				return Response({'status':'NotExist'})
		except:
			return Response({'status':'UnknownError'})

class UserToken(APIView):
	"""1"""
	def post(self, request, format=None,):
		data = request.data
		try:
			login_type = data['login_type']
		except:
			return Response({'status':'UnknownError'})
		if login_type == 'email':
			try:
				email = data['email']
				user = User.objects.get(email=email)
			except:
				return Response({'status':'EmailError'})
		else:
			try:
				username = data['username']
				user = User.objects.get(username=username)
			except:
				return Response({'status':'UserNameError'})
		password = data['password']
		if not user.is_active:
			return Response({'status':'NotActive'})
		if user.check_password(password):
			try:
				token = Token.objects.get(user=user)
				token.delete()
			except:
				pass
			token = Token.objects.create(user=user)
			serializer = UserSerializer(user)
			return Response({'status':'Success','Authorization':'Token '+ token.key, "result":[serializer.data]})
		else:
			return Response({'status':'PasswordError'})

class PostDetail(APIView):
	"""22"""
	def get(self, request, pk, format=None):
		try:
			post = Posts.objects.get(pk=pk)
			serializer = PostSerializer(post)
			return Response(serializer.data)
		except:
			return Response({'status':'UnknownError'})

class PostsAPI(generics.ListCreateAPIView):
	"""7"""
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		# try:
			# 新增代码
			# 是否搜索热门
			isPopular = request.GET.get("isPopular", False)
			# 是否进行文本搜索
			isSearch = request.GET.get("isSearch", False)

			# 原代码
			if isPopular:
				postList = Posts.objects.all().order_by('-likes_num')
				page = int(request.GET['page'])

				postList = postList[(page - 1) * 5: page * 5]
			elif isSearch:
				searchText = request.GET.get("searchText", '')
				postList = Posts.objects.filter(introduction__contains=searchText)
				page = int(request.GET['page'])

				postList = postList[ (page-1)*5: page * 5]
			else:
				user = request.user
				userlist = [user.id]
				likeList = FollowsLink.objects.filter(From = user)
				for like in likeList:
					userlist.append(like.To.id)
				userlist = list(set(userlist))
				postList = Posts.objects.filter(user__in=userlist).order_by('-Pub_time')

				postIDList = []
				for post in postList:
					postIDList.append(post.
									  id)

				page = int(request.GET['page'])

				if page == 1:
					postIDList = postIDList[:5]
					postList = Posts.objects.filter(id__in=postIDList).order_by('-Pub_time')
				else:
					post_id = int(request.GET['post_id'])
					postIDList_2 = []
					for postID in postIDList:
						if postID < post_id:
							postIDList_2.append(postID)
					postIDList = postIDList_2[:5]
					if not postIDList:
						return Response({'status':'null'})
					postList = Posts.objects.filter(id__in=postIDList).order_by('-Pub_time')


			# 根据上面得到的postList 进行生成返回数据
			photos = []
			photoList = []

			posts = []
			for post in postList:
				album = Photos.objects.filter(post=post)
				for photo in album:
					photos.append({'id':photo.id,
								   'photo':photo.photo,
								   'photo_thumbnail':photo.photo_thumbnail,
								   'post':photo.post.id,
								   })
				serializer = PhotoSerializer(photos, many=True)
				photoList.append(serializer.data)
				photos = []

			for post in postList:
					if LikesLink.objects.filter(user=request.user,post=post):
						is_dianzan = True
					else:
						is_dianzan = False
					if PostsLink.objects.filter(user=request.user,post=post):
						is_shoucang = True
					else:
						is_shoucang = False
					if len(Photos.objects.filter(post=post)) > 1:
						is_many = True
					else:
						is_many = False
					posts.append({'post_id':post.id,
								  'post_user_id':post.user.id,
								  'user_id':post.user.id,
								  'username':post.user.username,
								  'profile_picture':post.user.profile_picture,
								  'introduction':post.introduction,
								  'Pub_time':post.Pub_time,
								  'likes_num':post.likes_num,
								  'com_num':post.com_num,
								  'photo_0':post.photo_0,
								  'photo_0_thumbnail':post.photo_0_thumbnail,
								  'is_dianzan':is_dianzan,
								  'is_shoucang':is_shoucang,
								  'is_many':is_many,
										   })
			serializer = BriefPostSerializer(posts,many=True)
			return Response({'status':'Success','result':serializer.data,'photoList':photoList})
		# except:
		# 	return Response({'status':'UnknownError'})

	def post(self, request, format=None):
		data = request.data
		photo_num = int(data['photo_num'])
		try:
			introduction = data['introduction']
		except:
			introduction = ""
		post = Posts.objects.create(user=request.user, introduction=introduction,photo_0=data['photo_0'])
		for i in range(photo_num):
			photo = Photos.objects.create(photo=data['photo_'+ str(i)],post=post)
			photo.save()
		post.save()
		return Response({'status':'Success'})

	def put(self, request,format=None):
		"""7+"""
		data = request.data
		try:
			pk = request.data['pk']
			post = Posts.objects.get(pk=pk)
			post.introduction = data['introduction']
			post.save()
			return Response({'status':'Success'})
		except:
			return Response({'status':'Failure'})

	def delete(self, request, format=None):
		"""23"""
		try:
			pk = request.GET['pk']
			user = request.user
			post = Posts.objects.get(pk=pk,user=user)
			post.delete()
			return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

class PostList(mixins.ListModelMixin,
			   mixins.CreateModelMixin,
			   generics.GenericAPIView):
	queryset = Posts.objects.all()
	serializer_class = PostSerializer
	permission_classes = (IsAuthenticated,)
	pagination_class = PageNumberPagination
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)



	def get_queryset(self):
		user = self.request.user
		userlist = [user.id]
		likeList = FollowsLink.objects.filter(From=user)
		for like in likeList:
			userlist.append(like.To.id)
		userlist = list(set(userlist))
		postList = Posts.objects.filter(user__in=userlist).order_by('-Pub_time')
		return postList

class UserPost(APIView):
	permission_classes = (IsAuthenticated,)
	def get(self, request, pk,format=None):
		try:
			user = User.objects.get(pk=pk)
			postList = Posts.objects.filter(user=user).order_by('-Pub_time')
			posts = []
			photos = []
			photoList = []
			for post in postList:
				album = Photos.objects.filter(post=post)
				for photo in album:
					photos.append({'id':photo.id,
								   'photo':photo.photo,
								   'photo_thumbnail':photo.photo_thumbnail,
								   'post':photo.post.id,
								   })
				serializer = PhotoSerializer(photos, many=True)
				photoList.append(serializer.data)
				photos = []
			for post in postList:
				if LikesLink.objects.filter(user=request.user,post=post):
					is_dianzan = True
				else:
					is_dianzan = False
				if PostsLink.objects.filter(user=request.user,post=post):
					is_shoucang = True
				else:
					is_shoucang = False
				photo_num = len(Photos.objects.filter(post=post))
				if photo_num > 1:
					is_many = True
				else:
					is_many = False
				posts.append({'post_id':post.id,
							  'post_user_id':post.user.id,
							  'user_id':post.user.id,
							  'username':post.user.username,
							  'profile_picture':post.user.profile_picture,
							  'introduction':post.introduction,
							  'Pub_time':post.Pub_time,
							  'likes_num':post.likes_num,
							  'com_num':post.com_num,
							  'photo_0':post.photo_0,
							  'photo_0_thumbnail':post.photo_0_thumbnail,
							  'is_dianzan':is_dianzan,
							  'is_shoucang':is_shoucang,
							  'is_many':is_many,
							  })
			serializer = BriefPostSerializer(posts, many=True)

			return Response({'status':'Success','result':serializer.data,'photoList':photoList})
		except:
			return Response({'status':'UnknownError'})

class CheckFollow(APIView):
	def get(self, request, pk, format=None):
		try:
			user = User.objects.get(pk=pk)
			if FollowsLink.objects.filter(From=request.user,To=user):
				return Response({'status':'Yes'})
			else:
				return Response({'status':'No'})
		except:
			return Response({'status':'UnknownError'})

class PasswordForget(APIView):
	"""5"""
	def get(self, request,format=None):
		try:
			email = request.GET['email']
		except:
			return Response({'status':'UnknownError'})
		try:
			user = User.objects.get(email=email)
		except:
			return Response({'status':'NotExist'})
		hashkey = CaptchaStore.generate_key()
		captcha = CaptchaStore.objects.get(hashkey=hashkey)
		code = captcha.challenge
		UsersActive.objects.create(user=user,hashkey=hashkey,code=code,status=2)
		sendemail = EmailMessage('Captcha','Your captcha is' + code,"alex_noreply@163.com",[email,])
		sendemail.send()
		return Response({'status':'Success','hashkey':hashkey})

	def post(self, request, format=None):
		try:
			data = request.data
			captcha = data['captcha']
			hashkey = data['hashkey']
			password = data['password']
			password2 = data['password2']
			captchastore = CaptchaStore.objects.get(hashkey=hashkey)
			response = captchastore.response
			useractive = UsersActive.objects.get(hashkey=hashkey)
			user = useractive.user
			if response.lower() == captcha.lower() and password == password2:
				user.password = make_password(password)
				user.save()
				captchastore.delete()
				useractive.delete()
				return Response({'status':'Success'})
			else:
				return Response({'status':'Failure'})
		except:
			return Response({'status':'UnknownError'})

class ChangePassword(APIView):
	def post(self, request, format=None):
		try:
			data = request.data
			oldPassword = data['oldPassword']
			password = data['password']
			password2 = data['password2']
			if request.user.check_password(oldPassword) and password == password2:
				request.user.password = make_password(password)
				request.user.save()
				return Response({'status':'Success'})
			else:
				return Response({'status':'Failure'})
		except:
			return Response({'status':'UnknownError'})

class CommentsAPI(APIView):
	"""24"""
	permission_classes = (IsAuthenticated,)
	def get(self, request, format=None):
		try:
			post = request.GET['post_id']
			commentList = Comments.objects.filter(post=post).order_by('-time')
			comments = []
			for comment in commentList:
				comments.append({'user_id':comment.user.id,
								 'username':comment.user.username,
								 'profile_picture':comment.user.profile_picture,
								 'comment_id':comment.id,
								 'content':comment.content,
								 'time':comment.time,
								 })
			serializer = CommentSerializer(comments, many=True)
			return Response(serializer.data)
		except:
			return Response({'status':'UnknownError'})

	def post(self, request,format=None):
		data = request.data
		post = Posts.objects.get(id=data['post_id'])
		comment = Comments.objects.create(user=request.user, post=post, content=data['content'])
		comment.save()
		post.comNumIncrease()
		return Response({'status':'Success'})
		# except:
		# 	return Response({'status':'UnknownError'})

	def delete(self, request, format=None):
		try:
			data = request.data
			comment = Comments.objects.get(id=data['comment_id'])
			if comment.user == request.user:
				post = Posts.objects.get(id=comment.post.id)
				comment.delete()
				post.comNumDrease()
				return Response({'status':'Success'})
			return Response({'status':'Failure'})
		except:
			return Response({'status':'UnknownError'})

class Search(APIView):
	"""8"""
	def post(self, request, format=None):
		try:
			data = request.data
			page = int(request.GET['page'])
			searchType = data['searchType']
			if searchType == 'user':
				keyword = data['keyword']
				users = User.objects.filter(Q(username__contains=keyword)| Q(nickname__contains=keyword)).order_by('-date_joined')
				userIDList = []
				userList = []
				for user in users:
					userIDList.append(user.id)
				if page == 1:
					userIDList = userIDList[:10]
				else:
					user_id = int(request.GET['user_id'])
					now = userIDList.index(user_id)
					userIDList = userIDList[now+1:now+11]
				users = User.objects.filter(id__in=userIDList).order_by('-date_joined')
				for user in users:
					if FollowsLink.objects.filter(From=request.user,To=user):
						is_guanzhu = True
					else:
						is_guanzhu = False
					userList.append(BriefUser(user_id=user.id,
											  username=user.username,
											  nickname=user.nickname,
											  gender=user.gender,
											  birthday=user.birthday,
											  following_num=user.following_num,
											  followed_num=user.followed_num,
											  profile_picture=user.profile_picture,
											  is_guanzhu=is_guanzhu
												  ))
				serializer = BriefUserSerializer(userList, many=True)



			if searchType == 'post':
				keyword = data['keyword']
				postList = Posts.objects.filter(introduction__contains=keyword).order_by('-Pub_time')
				postIDList = []
				postIDList_2 = []
				for post in postList:
					postIDList.append(post.id)
				if page == 1:
					postIDList = postIDList[:5]
				else:
					post_id = int(request.GET['post_id'])
					for postID in postIDList:
						if postID < post_id:
							postIDList_2.append(postID)
					postIDList = postIDList_2[:5]
				postList = Posts.objects.filter(id__in=postIDList).order_by('-Pub_time')
				posts = []
				for post in postList:
					if LikesLink.objects.filter(user=request.user,post=post):
						is_dianzan = True
					else:
						is_dianzan = False
					if PostsLink.objects.filter(user=request.user,post=post):
						is_shoucang = True
					else:
						is_shoucang = False
					if len(Photos.objects.filter(post=post)) > 1:
						is_many = True
					else:
						is_many = False
					posts.append({'username':post.user.username,
								  'profile_picture':post.user.profile_picture,
								  'introduction':post.introduction,
								  'Pub_time':post.Pub_time,
								  'likes_num':post.likes_num,
								  'com_num':post.com_num,
								  'photo_0':post.photo_0,
								  'photo_0_thumbnail':post.photo_0_thumbnail,
								  'is_shoucang':is_shoucang,
								  'is_dianzan':is_dianzan,
								  'post_id':post.id,
								  'post_user_id':post.user.id,
								  'user_id':post.user.id,
								  'is_many':is_many,
								  })
				serializer= BriefPostSerializer(posts, many=True)
			if not serializer.data:
				return Response({'status':'null'})
			return Response({'status':'Success','result':serializer.data})
		except:
			return Response({'status':'UnknownError'})

class FollowPost(APIView):
	def get(self, request, format=None):
		"""9"""
		data = request.data
		user = request.user
		try:
			followList = FollowsLink.objects.filter(From=user)
			userList = []
			for follow in followList:
				userList.append(follow.To.id)
			postList = Posts.objects.filter(user__in=userList).order_by('-Pub_time')
			serializer = PostSerializer(postList, many=True)
			return Response(serializer.data)
		except:
			return Response({'status':'UnknownError'})

class LikeList(APIView):
	"""点赞列表"""
	def get(self, request, format=None):
		"""13"""
		try:
			likeList = LikesLink.objects.filter(user=request.user)
			postIDList = []
			for like in likeList:
				postIDList.append(like.post.id)
			postList = Posts.objects.filter(id__in=postIDList).order_by('-Pub_time')
			posts = []
			for post in postList:
				if LikesLink.objects.filter(user=request.user,post=post):
					is_dianzan = True
				else:
					is_dianzan = False
				if PostsLink.objects.filter(user=request.user,post=post):
					is_shoucang = True
				else:
					is_shoucang = False
				if len(Photos.objects.filter(post=post)) > 1:
					is_many = True
				else:
					is_many = False

				posts.append({'username':post.user.username,
							  'profile_picture':post.user.profile_picture,
							  'introduction':post.introduction,
							  'Pub_time':post.Pub_time,
							  'likes_num':post.likes_num,
							  'com_num':post.com_num,
							  'photo_0':post.photo_0,
							  'photo_0_thumbnail':post.photo_0_thumbnail,
							  'is_dianzan':is_dianzan,
							  'is_shoucang':is_shoucang,
							  'post_id':post.id,
							  'post_user_id':post.user.id,
							  'user_id':post.user.id,
							  'is_many':is_many
							  })
			serializer = BriefPostSerializer(posts,many=True)
			return Response({'status':'Success','result':serializer.data})
		except:
			return Response({'status':'UnknownError'})

	def post(self, request, format=None):
		"""20"""
		try:
			data = request.data
			pk = data['pk']
			post = Posts.objects.get(pk=pk)
			if LikesLink.objects.filter(post=post,user=request.user):
				like = LikesLink.objects.filter(post=post,user=request.user)
				like.delete()
				post.likeNumDreacase()
				return Response({'status':'Failure'})
			post.likeNumIncrease()
			post.save()
			like = LikesLink.objects.create(post=post,user=request.user)
			like.save()
			return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

	def delete(self, request, format=None):
		try:
			data = request.data
			pk = data['pk']
			post = Posts.objects.get(pk=pk)
			if not LikesLink.objects.filter(post=post,user=request.user):
				return Response({'status':'Failure'})
			else:
				LikesLink.objects.filter(post=post,user=request.user).delete()
				post.likeNumDreacase()
				post.save()
				return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

class PostsLinkApi(APIView):
	""""""
	def get(self, request, format=None):
		"""12"""
		try:
			user = request.user
			likeList = PostsLink.objects.filter(user=user)
			postList = []
			for like in likeList:
				postList.append(like.post.id)
			posts = Posts.objects.filter(id__in=postList).order_by('-Pub_time')
			postList = []
			result = []
			for post in posts:
				if LikesLink.objects.filter(post=post,user=user):
					is_dianzan = True
				else:
					is_dianzan = False
				if len(Photos.objects.filter(post=post)) > 1:
					is_many = True
				else:
					is_many = False
				postList.append({'username':post.user.username,
								 'introduction':post.introduction,
								 'Pub_time':post.Pub_time,
								 'profile_picture':post.user.profile_picture,
								 'likes_num':post.likes_num,
								 'com_num':post.com_num,
								 'photo_0':post.photo_0,
								 'photo_0_thumbnail':post.photo_0_thumbnail,
								 'is_shoucang':True,
								 'is_dianzan':is_dianzan,
								 'is_many':is_many,
								 'post_id':post.id,
								 'post_user_id':post.user.id,
								 'user_id':post.user.id,
					})

			serializer = BriefPostSerializer(postList,many=True)
			return Response({'status':'Success','result':serializer.data})
		except:
			return Response({'status':'UnknownError'})


	def post(self, request, format=None):
		"""20,21"""
		data = request.data
		try:
			post_id = data['post_id']
			post = Posts.objects.get(id=post_id)
			if PostsLink.objects.filter(post=post,user=request.user):
				like = PostsLink.objects.filter(post=data['post_id'],user=request.user)
				like.delete()
				return Response({'status':'Failure'})
			else:
				like = PostsLink.objects.create(post=post,user=request.user)
				like.save()
				return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

	def delete(self, request, format=None):
		data = request.data
		try:
			linkid = data['id']
			post=Posts.objects.get(id=linkid)
			like = PostsLink.objects.filter(post=post,user=request.user)
			like.delete()
			return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

class FollowPerson(APIView):
	"""14"""
	permission_classes = (IsAuthenticated,)
	def get(self, request, format=None):
		try:
			user_id = request.GET['user_id']
			user = User.objects.get(id=user_id)
			followList = FollowsLink.objects.filter(From=user).order_by('-time')
			ToList = []
			for follow in followList:
				ToList.append(follow.To.id)
			userList = User.objects.filter(id__in=ToList)
			users = []
			for user_in in userList:
				if FollowsLink.objects.filter(From=request.user,To=user_in):
					is_guanzhu = True
				else:
					is_guanzhu = False
				users.append(BriefUser(user_id=user_in.id,
									   username=user_in.username,
				                       nickname=user_in.nickname,
									   gender=user_in.gender,
									   birthday=user_in.birthday,
									   following_num=user_in.following_num,
									   followed_num=user_in.followed_num,
									   profile_picture=user_in.profile_picture,
									   is_guanzhu=is_guanzhu))
			serializer = BriefUserSerializer(users, many=True)
			if serializer.data:
				return Response({'status':'Success','result':serializer.data})
			else:
				return Response({'status':'null'})
		except:
			return Response({'status':'UnknownError'})


class ToPerson(APIView):
	"""15"""
	def get(self, request, format=None):
		try:
			user_id = request.GET['user_id']
			user = User.objects.get(id=user_id)
			followList = FollowsLink.objects.filter(To=user).order_by('-time')
			FromList = []
			for follow in followList:
				FromList.append(follow.From.id)
			userList = User.objects.filter(id__in=FromList)
			users = []
			for user_in in userList:
				if FollowsLink.objects.filter(From=user,To=user_in):
					is_guanzhu = True
				else:
					is_guanzhu = False
				users.append(BriefUser(user_id=user_in.id,
									   username=user_in.username,
									   nickname=user_in.nickname,
									   gender=user_in.gender,
									   birthday=user_in.birthday,
									   following_num=user_in.following_num,
									   followed_num=user_in.followed_num,
									   profile_picture=user_in.profile_picture,
									   is_guanzhu=is_guanzhu))
			serializer = BriefUserSerializer(users, many=True)
			return Response(serializer.data)
		except:
			return Response({'status':'UnknownError'})

class FollowMessage(APIView):
	"""17"""
	def get(self, request, format=None):
		followList = FollowsLink.objects.filter(From=request.user)
		ToList = []
		for follow in followList:
			ToList.append(follow.To.id)
		likes = LikesLink.objects.filter(user__in=ToList).order_by('-time')
		likeList = []
		for like in likes:
			likeList.append(BriefLikesLink(username=like.user.username,
										   user_id=like.user.id,
										   post_id=like.post.id,
										   post_user_id=like.post.user.id,
										   introduction=like.post.introduction,
										   photo_0=like.post.photo_0,
										   photo_0_thumbnail=like.post.photo_0_thumbnail,
										   profile_picture=like.user.profile_picture,
										   time=like.time,
										   ))

		serializer = BriefLikesLinkSerializer(likeList,many=True)
		return Response({'status':'Success','result':serializer.data})
		# except:
		# 	return Response({'status':'UnknownError'})

class Follow(APIView):
	permission_classes = (IsAuthenticated,)
	def post(self, request, format=None):
		"""18,19"""
		user = request.user
		try:
			data = request.data
			To = User.objects.get(pk=data['pk'])
			if FollowsLink.objects.filter(From=user,To=To):
				follow = FollowsLink.objects.filter(From=user,To=To)
				user.following_numDe()
				To.followed_numDe()
				follow.delete()
				return Response({'status':'Failure'})
			else:
				follow = FollowsLink.objects.create(From=user, To=To)
				user.following_numIn()
				To.followed_numIn()
				follow.save()
				return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

	def delete(self, request, format=None):
		user = request.user
		try:
			data = request.data
			To = User.objects.get(pk=data['pk'])
			if FollowsLink.objects.filter(From=user,To=To):
				follow = FollowsLink.objects.filter(From=user,To=To)
				user.following_numDe()
				To.followed_numDe()
				follow.delete()
				return Response({'status':'Success'})
			else:
				return Response({'status':'Failure'})
		except:
			return Response({'status':'UnknownError'})

class PublicKey(APIView):
	def get(self, request, format=None):
		(pubkey, privkey) = rsa.newkeys(1024)
		pubkey = pubkey.save_pkcs1()
		privkey = privkey.save_pkcs1()
		key = Keys.objects.create(publicKey=pubkey,privateKey=privkey)
		key.save()
		return Response({'pubkey':pubkey})

class MessageList(APIView):
	"""16"""
	def get(self, request, format=None):
		user = request.user
		posts = Posts.objects.filter(user=user)
		postIDList = []
		for post in posts:
			postIDList.append(post.id)
		follows = FollowsLink.objects.filter(To=user)
		likes = LikesLink.objects.filter(post__in=postIDList)
		comments = Comments.objects.filter(post__in=postIDList)
		messages = sorted(chain(follows,likes,comments),key=attrgetter('time'),reverse=True)
		messageList = []
		result = []
		for message in messages:
			if type(message) == FollowsLink:
				if FollowsLink.objects.filter(From=request.user,To=message.From):
					is_guanzhu = True
				else:
					is_guanzhu = False
				message = Message(user_id=message.From.id,
								  username=message.From.username,
								  profile_picture=message.From.profile_picture,
								  messageType=1,
								  time=message.time,
								  is_guanzhu=is_guanzhu,
								  )
				serializer = Message_1Serializer(message.kwargs)
				result.append(serializer.data)
			if type(message) == LikesLink:
				message = Message(user_id=message.user.id,
								  username=message.user.username,
								  profile_picture=message.user.profile_picture,
								  messageType=2,
								  time=message.time,
								  post_id=message.post.id,
								  post_user_id=message.post.user.id,
								  photo_0=message.post.photo_0,
								  photo_0_thumbnail=message.post.photo_0_thumbnail,
								  )
				serializer = Message_2Serializer(message.kwargs)
				result.append(serializer.data)
			if type(message) == Comments:
				message = Message(user_id=message.user.id,
								  username=message.user.username,
								  profile_picture=message.user.profile_picture,
								  messageType=3,
								  time=message.time,
								  post_id=message.post.id,
								  post_user_id=message.post.user.id,
								  photo_0=message.post.photo_0,
								  photo_0_thumbnail=message.post.photo_0_thumbnail,
								  content=message.content
								  )
				serializer = Message_3Serializer(message.kwargs)
				result.append(serializer.data)
		return Response({'status':'Success','result':result})


		

		
class Test(APIView):
	def get(self, request, format=None):
		timestamp = time.time()
		timestamp = str(timestamp)
		return Response({'timestamp':timestamp})
		# user = request.user
		# serializer = UserSerializer(user)
		# return Response(serializer.data)

	def post(self, request, format=None):
		# a = ""
		# for i in request.data:
		# 	a += i
		# 	a += request.data[i]
		# print(a)
		# b = hashlib.md5(a.encode(encoding='utf-8'))
		# c = hashlib.md5(("a123b456").encode(encoding='gb2312'))
		# if b.hexdigest() == c.hexdigest():
		# 	print("True")
		# else:
		# 	print("False")
		# print(b.hexdigest())
		# print(c.hexdigest())
		print(request.path)
		if request.path == "/api/test/":
			print("True")
		else:
			print("False")
		return Response({'status':'OK'})

	def delete(self, request, format=None):
		try:
			return Response({'status':'Success'})
		except:
			return Response({'status':'UnknownError'})

def show_picture(request, url):
	image_data = open('media/' + url, 'rb').read()
	return HttpResponse(image_data, content_type='image/png')
