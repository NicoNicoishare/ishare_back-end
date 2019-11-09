from django.contrib import admin, messages
from datetime import datetime, timedelta
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from random import Random
from .conf import settings
from .forms import UserChangeForm, UserCreationForm, UserActiveForm
from ins_api.models import *
from .utils import send_activation_email
from imagekit.admin import AdminThumbnail
from .models import User

try:
    from django.contrib.admin.utils import model_ngettext
except ImportError:  # pragma: no cover
    from django.contrib.admin.util import model_ngettext


'''class UserModelFilter(admin.SimpleListFilter):
    """
    An admin list filter for the UserAdmin which enables
    filtering by its child models.
    """
    title = _('user type')
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        user_types = set([user.user_type for user in model_admin.model.objects.all()])
        return [(user_type.id, user_type.name) for user_type in user_types]

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except TypeError:
            value = None

        if value:
            return queryset.filter(user_type_id__exact=value)
        else:
            return queryset


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'is_active')
    list_filter = (UserModelFilter, 'is_staff', 'is_superuser', 'is_active',)
    search_fields = ('email',)
    ordering = ('email',)
    actions = ('activate_users', 'send_activation_email', )
    readonly_fields = ('last_login', 'date_joined', )

    def get_queryset(self, request):
        # optimize queryset for list display.
        qs = self.model.base_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def activate_users(self, request, queryset):
        """
        Activates the selected users, if they are not already
        activated.

        """
        n = 0
        for user in queryset:
            if not user.is_active:
                user.activate()
                n += 1
        self.message_user(
            request,
            _('Successfully activated %(count)d %(items)s.') %
            {'count': n, 'items': model_ngettext(self.opts, n)},  messages.SUCCESS)
    activate_users.short_description = _('Activate selected %(verbose_name_plural)s')

    def send_activation_email(self, request, queryset):
        """
        Send activation emails for the selected users, if they are not already
        activated.
        """
        n = 0
        for user in queryset:
            if not user.is_active and settings.USERS_VERIFY_EMAIL:
                send_activation_email(user=user, request=request)
                n += 1

        self.message_user(
            request, _('Activation emails sent to %(count)d %(items)s.') %
            {'count': n, 'items': model_ngettext(self.opts, n)},  messages.SUCCESS)

    send_activation_email.short_description = \
        _('Send activation emails to selected %(verbose_name_plural)s')


admin.site.register(User, UserAdmin)'''


class UserFilterBirthday(admin.SimpleListFilter):
    title = u'生日'
    parameter_name = 'birthday'

    def lookups(self, request, model_admin):
        return (
            ('1', u'1月'),
            ('2', u'2月'),
            ('3', u'3月'),
            ('4', u'4月'),
            ('5', u'5月'),
            ('6', u'6月'),
            ('7', u'7月'),
            ('8', u'8月'),
            ('9', u'9月'),
            ('10', u'10月'),
            ('11', u'11月'),
            ('12', u'12月'),
        )

    def queryset(self, request, queryset):
        month = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        for i in month:
            if self.value() == i:
                return queryset.filter(birthday__month=i)


class UserFilterPubtime(admin.SimpleListFilter):
    title = u'注册时间'
    parameter_name = 'Reg_time'

    def lookups(self, request, model_admin):
        return (
            ('0', u'今天'),
            ('1', u'本周'),
            ('2', u'本月'),
            ('3', u'今年'),
            ('4', u'今年之前')
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            start = datetime.date(datetime.today())
            return queryset.filter(Reg_time__gte=start)
        elif self.value() == '1':
            start = datetime.now() - timedelta(days=7)
            return queryset.filter(Reg_time__gte=start)
        elif self.value() == '2':
            day = datetime.now().day
            start = datetime.now() - timedelta(days=day)
            return queryset.filter(Reg_time__gte=start)
        elif self.value() == '3':
            return queryset.filter(Reg_time__year=datetime.now().year)
        elif self.value() == '4':
            return queryset.exclude(Reg_time__year=datetime.now().year)


class LikesNumFilter(admin.SimpleListFilter):
    title = u'点赞数'
    parameter_name = 'likes_num'

    def lookups(self, request, model_admin):
        return (
            ('0', u'10000赞以上'),
            ('1', u'5000赞以上'),
            ('2', u'1000赞以上'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(likes_num__gte=10000)
        if self.value() == '1':
            return queryset.filter(likes_num__gte=5000)
        if self.value() == '2':
            return queryset.filter(likes_num__gte=1000)


class FollowNumFilter(admin.SimpleListFilter):
    title = u'关注数'
    parameter_name = 'com_num'

    def lookups(self, request, model_admin):
        return (
            ('0', u'10000评论以上'),
            ('1', u'5000评论以上'),
            ('2', u'1000评论以上'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(com_num__gte=10000)
        if self.value() == '1':
            return queryset.filter(com_num__gte=5000)
        if self.value() == '2':
            return queryset.filter(com_num__gte=1000)


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'is_active','password')
        }),
        (_('个人信息'), {
            'classes': ('wide',),
            'fields': ('image_tag', 'nickname', 'gender', 'address', 'birthday', 'introduction')
        }),
        (_('重要日期'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')
        }),
        (_('选填信息'), {
            'classes': ('wide',),
            'fields': ('profile_picture', 'nickname', 'gender', 'address', 'introduction', 'birthday')
        })
    )
    list_display = ('image_tag', 'username', 'email', 'birthday', 'gender',
                    'followed_num', 'following_num', 'Reg_time', 'is_active')
    search_fields = ('username', 'email', 'nickname')
    list_per_page = 30
    ordering = ('-Reg_time',)
    list_display_links = ('username', 'image_tag')
    list_filter = ('gender', UserFilterPubtime, UserFilterBirthday)
    list_editable = ('is_active',)
    readonly_fields = ('image_tag', 'last_login', 'date_joined','email')


class PostsAdmin(admin.ModelAdmin):
    fields = ('user', 'introduction')
    list_display = ('user', 'introduction', 'Pub_time', 'likes_num', 'com_num')
    search_fields = ('user__username', 'user__email', 'user__nickname')
    list_per_page = 30
    ordering = ('-Pub_time',)
    raw_id_fields = ('user',)
    list_filter = (LikesNumFilter, FollowNumFilter)


class PhotosAdmin(admin.ModelAdmin):
    fields = ('post', 'photo')
    admin_thumbnail = AdminThumbnail(image_field='photo_thumbnail',template='thumbnail.html')
    list_per_page = 30
    search_fields = ('post__user__username', 'post__user__nickname', 'post__user__email')
    list_display = ('post', 'admin_thumbnail')
    raw_id_fields = ('post',)
    readonly_fields = ('image_tag',)


class CommentsAdmin(admin.ModelAdmin):
    fields = ('user', 'post', 'content')
    list_display = ('user', 'post', 'time')
    list_per_page = 30
    search_fields = ('user__email', 'user__username', 'user__nickname', 'post__user__username',
                     'post__user__email', 'post__user__nickname')
    raw_id_fields = ('user', 'post')
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for obj in queryset:
            obj.post.comNumDrease()
            obj.delete()
    delete_selected.short_description = '删除所选的评论信息'

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.post.comNumIncrease()
        obj.save()

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.post.comNumDrease()
        obj.delete()


def createCode():
    code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(10):
        code += chars[random.randint(0, length)]
    return code


class UsersActiveAdmin(admin.ModelAdmin):
    add_form = UserActiveForm
    fields = ('user', 'status', 'code')
    list_per_page = 30
    list_display = ('user', 'status', 'code')
    search_fields = ('user__email', 'user__username', 'user__nickname')
    readonly_fields = ('code', 'status')
    raw_id_fields = ('user',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.code = createCode()
        obj.save()


class LikesLinkAdmin(admin.ModelAdmin):
    fields = ('user', 'post')
    list_display = ('user', 'post')
    list_per_page = 30
    search_fields = ('user__username', 'user__email', 'user__nickname', 'post__user__username', 'post__user__email',
                     'post__user__nickname')
    ordering = ('-post__Pub_time',)
    raw_id_fields = ('user', 'post')
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for obj in queryset:
            obj.post.likeNumDreacase()
            obj.delete()
    delete_selected.short_description = '删除所选的点赞信息'

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.post.likeNumIncrease()
        obj.save()

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.post.likeNumDreacase()
        obj.delete()


class PostsLinkAdmin(admin.ModelAdmin):
    fields = ('user', 'post')
    list_per_page = 30
    list_display = ('user', 'post')
    search_fields = ('user__username', 'user__email', 'user__nickname', 'post__user__username', 'post__user__email',
                     'post__user__nickname')
    ordering = ('-post__Pub_time',)
    raw_id_fields = ('user', 'post')



class FollowsLinkAdmin(admin.ModelAdmin):
    fields = ('From', 'To')
    list_display = ('From', 'To')
    search_fields = ('From__username', 'From__email', 'From__nickname', 'To__username', 'To__email', 'To__nickname')
    raw_id_fields = ('From', 'To')
    list_per_page = 30
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for obj in queryset:
            From = User.objects.get(id=obj.From.id)
            To = User.objects.get(id=obj.To.id)
            From.following_numDe()
            To.followed_numDe()
            obj.delete()
    delete_selected.short_description = '删除所选的关注信息'

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        From = User.objects.get(id=obj.From.id)
        To = User.objects.get(id=obj.To.id)
        From.following_numIn()
        To.followed_numIn()
        obj.save()

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        From = User.objects.get(id=obj.From.id)
        To = User.objects.get(id=obj.To.id)
        From.following_numDe()
        To.followed_numDe()
        obj.delete()



admin.site.site_header = 'INS管理页面'
admin.site.site_title = 'INS管理页面'
admin.site.index_title = 'INS'
admin.site.register(User, UserAdmin)
admin.site.register(Posts, PostsAdmin)
admin.site.register(Photos, PhotosAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(UsersActive, UsersActiveAdmin)
admin.site.register(LikesLink, LikesLinkAdmin)
admin.site.register(PostsLink, PostsLinkAdmin)
admin.site.register(FollowsLink, FollowsLinkAdmin)
