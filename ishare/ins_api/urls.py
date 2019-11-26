from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from ins_api import views
urlpatterns = format_suffix_patterns([

	url(r'Application/',views.apiApplication),

	url(r'user/detail/(?P<pk>[0-9]+)/$',views.UserDetail.as_view()),
	url(r'user/detail/$',views.UserDetail.as_view()),
	
	url(r'user/register/$',views.UserRegister.as_view()),

	url(r'user/login/$',views.UserToken.as_view()),
	url(r'user/checkout/$',views.Accounts.as_view()),
	url(r'user/password/$',views.PasswordForget.as_view()),
	url(r'user/password/change/$',views.ChangePassword.as_view()),

	url(r'post/brief/(?P<pk>[0-9]+)/$',views.ShortPost.as_view()),
	url(r'home/post/$',views.PostList.as_view()),
	url(r'photoList/$',views.PhotoList.as_view()),
	url(r'post/like/$',views.PostsLinkApi.as_view()), 
	url(r'post/dianzan/$',views.LikeList.as_view()), 

	url(r'dynamic/$', views.PostsAPI.as_view()),

	url(r'post/comments/$',views.CommentsAPI.as_view()),

	url(r'search/$',views.Search.as_view()),

	url(r'timestamp/$',views.Test.as_view()),


	url(r'user/friends/$',views.FollowPerson.as_view()),
	url(r'user/lookme/$',views.ToPerson.as_view()),
	url(r'user/followed/$',views.FollowPost.as_view()),
	url(r'user/friendmessage/$',views.FollowMessage.as_view()),
	url(r'user/followyou/$',views.Follow.as_view()),

	url(r'user/posts/(?P<pk>[0-9]+)/$',views.UserPost.as_view()),
	url(r'user/checkfollow/(?P<pk>[0-9]+)/$',views.CheckFollow.as_view()),
	url(r'user/messages/$',views.MessageList.as_view()),

])