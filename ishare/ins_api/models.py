from django.db import models
from users.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from users.storage import ImageStorage
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Posts(models.Model):
    """动态"""
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    introduction = models.CharField(max_length=150, default="", verbose_name="动态描述")
    Pub_time = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")
    likes_num = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    photo_0 = models.ImageField(max_length=100,verbose_name="图片", upload_to='photos/',storage=ImageStorage(),default="")
    photo_0_thumbnail = ImageSpecField(source='photo_0',
                                       format='JPEG',
                                       options={'quality':60})
    com_num = models.PositiveIntegerField(default=0, verbose_name="评论数")
    def likeNumIncrease(self):
        self.likes_num += 1
        self.save(update_fields=['likes_num'])

    def likeNumDreacase(self):
        self.likes_num -= 1
        self.save(update_fields=['likes_num'])

    def comNumIncrease(self):
        self.com_num += 1
        self.save(update_fields=['com_num'])

    def comNumDrease(self):
        self.com_num -= 1
        self.save(update_fields=['com_num'])

    class Meta:
        verbose_name = '动态信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.__str__() + '的动态:' + str(self.user_id)



class Photos(models.Model):
    """动态的图片"""
    post = models.ForeignKey(Posts, verbose_name="动态", on_delete=models.CASCADE)
    photo = models.ImageField(max_length=100, verbose_name="图片", upload_to='photos/',storage=ImageStorage())
    photo_thumbnail = ImageSpecField(source='photo',
                                     format='JPEG',
                                     options={'quality':60}
                                     )
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    def image_tag(self):
        return mark_safe("<img src='%s' width='100px' />" % self.photo.url)

    image_tag.short_description = _('动态图片')

    image_tag.allow_tags = True

    class Meta:
        verbose_name = '相册图片信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.post.__str__() + '的图片'


class Comments(models.Model):
    """动态评论"""
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, verbose_name="动态", on_delete=models.CASCADE)
    content = models.CharField(max_length=80, blank=False)
    time = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")

    class Meta:
        verbose_name = '评论信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.__str__() + '的评论'


class UsersActive(models.Model):
    """用于储存注册时的激活码和忘记密码发送的验证码"""
    STATUS_CHOICES = (
        (1, "注册"),
        (2, "忘记")
    )
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=2, verbose_name="状态")
    code = models.CharField(max_length=10, verbose_name="验证码", default="保存后自动生成验证码")
    hashkey = models.CharField(max_length=100, verbose_name='哈希值',default="")

    class Meta:
        verbose_name = '验证码信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.__str__() + '的验证码'


class LikesLink(models.Model):
    """点赞关联信息"""
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, verbose_name="动态", on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    class Meta:
        verbose_name = '点赞关联信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.__str__() + '点赞' + self.post.__str__()


class PostsLink(models.Model):
    """收藏关联信息"""
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, verbose_name="动态", on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    class Meta:
        verbose_name = '收藏关联信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.__str__() + '收藏' + self.post.__str__()


class ApiList(models.Model):
    appId = models.CharField(max_length=25,default="")
    appKey = models.CharField(max_length=100,default="")
    publicKey = models.CharField(max_length=180,default="")
    privateKey = models.CharField(max_length=500,default="")
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")


class ApiApplicationer(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=10)
    permission = models.BooleanField(default=False)


class FollowsLink(models.Model):
    """用于储存用户关注关联信息"""
    From = models.ForeignKey(User, verbose_name="关注者", on_delete=models.CASCADE, related_name='+')
    To = models.ForeignKey(User, verbose_name="被关注者", on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    class Meta:
        verbose_name = '用户关注关联信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.From.__str__() + '关注' + self.To.__str__()


class Keys(models.Model):
    publicKey = models.CharField(max_length=250)
    privateKey = models.CharField(max_length=900)
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")
