from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=100) # 문자로 구성
    pub_date = models.DateTimeField(auto_now_add=True) # 날짜로 구성
    author = models.ForeignKey(User, on_delete=True, null=True, default=1)
    body = RichTextUploadingField() # 문자로 구성

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=True, null=True)
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_user = models.TextField(max_length=20)
    comment_thumbnail_url = models.TextField()
    comment_textfield = models.TextField()