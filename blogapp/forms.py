from django import forms
from .models import Blog, Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class CreateBlog(forms.ModelForm):
    class Meta:
        model = Blog

        fields = ['title', 'author', 'body']

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'width: 100%',
                    'placeholder': '제목을 입력하세요.'
                    }
            ),
            'author': forms.Select(
                attrs={'class': 'custom-select'}
            ),
            'body': forms.CharField(widget=CKEditorUploadingWidget())
        }

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ['comment_textfield']
        widgets = {
            'comment_textfield': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'cols': 40
                }
            )
        }