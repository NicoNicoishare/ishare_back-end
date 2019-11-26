from rest_framework import serializers
from users.models import User
from .models import Posts, Photos, Comments, LikesLink

# 用于Restful框架风格的序列化类
class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username',
				  'nickname', 'gender', 'birthday',
				  'following_num', 'followed_num',
				  'following_num', 'profile_picture',
				  'introduction','address')

class BriefUser(object):
	"""docstring for BriefUser"""
	def __init__(self, user_id, username, nickname, gender, birthday, following_num, followed_num, profile_picture, is_guanzhu):
		self.user_id = user_id
		self.username = username
		self.nickname = nickname
		self.gender = gender
		self.birthday = birthday
		self.following_num = following_num
		self.followed_num = followed_num
		self.profile_picture = profile_picture
		self.is_guanzhu = is_guanzhu


class BriefUserSerializer(serializers.Serializer):
	user_id = serializers.IntegerField()
	username = serializers.CharField()
	nickname = serializers.CharField()
	gender = serializers.IntegerField()
	birthday = serializers.CharField()
	following_num = serializers.IntegerField()
	followed_num = serializers.IntegerField()
	profile_picture = serializers.ImageField()
	is_guanzhu = serializers.BooleanField()

class BriefPost(object):
	"""docstring for ClassName"""
	def __init__(self, username, introduction, Pub_time, likes_num, com_num, profile_picture, photo_0, is_dianzan, is_shoucang, post_id, user_id, photo_num):
		self.username = username
		self.profile_picture = profile_picture
		self.introduction = introduction
		self.Pub_time = Pub_time
		self.likes_num = likes_num
		self.com_num = com_num
		self.photo_0 = photo_0
		self.is_dianzan = is_dianzan
		self.is_shoucang = is_shoucang
		self.post_id = post_id
		self.user_id = user_id
		self.photo_num = photo_num

class BriefPostTest(object):
	"""docstring for BriefPost"""
	def __init__(self, *args, **kwargs):
		super(BriefPostTest, self).__init__()
		self.args = args
		self.kwargs = kwargs
		

class BriefPostTestSerializer(serializers.Serializer):
	introduction = serializers.CharField()
	Pub_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
	likes_num = serializers.IntegerField()
	com_num = serializers.IntegerField()
	photo_0 = serializers.ImageField()
	photo_0_thumbnail = serializers.ImageField()
	is_many = serializers.BooleanField()
		

class BriefPostSerializer(serializers.Serializer):
	username = serializers.CharField(max_length=15)
	introduction = serializers.CharField(max_length=150)
	Pub_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
	profile_picture = serializers.ImageField()
	likes_num = serializers.IntegerField()
	com_num = serializers.IntegerField()
	photo_0 = serializers.ImageField()
	photo_0_thumbnail = serializers.ImageField()
	is_shoucang = serializers.BooleanField()
	is_dianzan = serializers.BooleanField()
	is_many = serializers.BooleanField()
	post_id = serializers.IntegerField()
	post_user_id = serializers.IntegerField()
	user_id = serializers.IntegerField()

	
		

class PostSerializer(serializers.ModelSerializer): 
	class Meta:
		model = Posts
		fields = ('id', 'user', 'introduction',
				  'Pub_time', 'likes_num',
				  'com_num','photo_0')

class PhotoSerializer(serializers.Serializer):
	photo_thumbnail = serializers.ImageField()
	id = serializers.IntegerField()
	post = serializers.IntegerField()
	photo = serializers.ImageField()



class CommentSerializer(serializers.Serializer):
	user_id = serializers.IntegerField()
	username = serializers.CharField()
	profile_picture = serializers.ImageField()
	comment_id = serializers.IntegerField()
	content = serializers.CharField()
	time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

	

class LikesLinkSerializer(serializers.ModelSerializer):
	class Meta:
		model = LikesLink
		fields = ('id','user','post','time')

class BriefLikesLink(object):
	"""docstring for BriefLikesLink"""
	def __init__(self, username, user_id, post_id, introduction, photo_0, profile_picture, time, photo_0_thumbnail, post_user_id):
		self.username = username
		self.user_id = user_id
		self.post_id = post_id
		self.post_user_id = post_user_id
		self.introduction = introduction
		self.photo_0 = photo_0
		self.photo_0_thumbnail = photo_0_thumbnail
		self.profile_picture = profile_picture
		self.time = time

class BriefLikesLinkSerializer(serializers.Serializer):
	"""点赞"""
	username = serializers.CharField()
	user_id = serializers.IntegerField()
	post_id = serializers.IntegerField()
	post_user_id = serializers.IntegerField()
	introduction = serializers.CharField()
	photo_0 = serializers.ImageField()
	photo_0_thumbnail = serializers.ImageField()
	profile_picture = serializers.ImageField()
	time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')



class Message(object):
	def __init__(self, **kwargs):
		super(Message, self).__init__()
		self.kwargs = kwargs

class Message_1Serializer(serializers.Serializer):
	"""docstring for Message_1Serializer"""
	user_id = serializers.IntegerField()
	username = serializers.CharField()
	profile_picture = serializers.ImageField()
	messageType = serializers.IntegerField()
	time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
	is_guanzhu = serializers.BooleanField()

class Message_2Serializer(serializers.Serializer):
	user_id = serializers.IntegerField()
	username = serializers.CharField()
	profile_picture = serializers.ImageField()
	messageType = serializers.IntegerField()
	time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
	post_id = serializers.IntegerField()
	post_user_id = serializers.IntegerField()
	photo_0 = serializers.ImageField()
	photo_0_thumbnail = serializers.ImageField()

class Message_3Serializer(serializers.Serializer):
	user_id = serializers.IntegerField()
	username = serializers.CharField()
	profile_picture = serializers.ImageField()
	messageType = serializers.IntegerField()
	time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
	post_id = serializers.IntegerField()
	post_user_id = serializers.IntegerField()
	photo_0 = serializers.ImageField()
	photo_0_thumbnail = serializers.ImageField()
	content = serializers.CharField()
