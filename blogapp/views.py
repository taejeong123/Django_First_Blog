from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateBlog
from .models import Blog, Comment
from .forms import BlogCommentForm
import requests
import json

# Create your views here.
def index(request):
    return render(request, 'index.html')

def blogMain(request):
    blogs =  Blog.objects.all()

    return render(request, 'blogMain.html', {'blogs': blogs})

def createBlog(request):
    if request.method == 'POST':
        form = CreateBlog(request.POST)

        if form.is_valid():
            form.save()
            return redirect('blogMain')
        else:
            return redirect('index')

    else:
        form = CreateBlog()
        return render(request, 'createBlog.html', {'form': form})

def detail(request, blog_id):
    blog_detail = get_object_or_404(Blog, pk=blog_id)
    comments = Comment.objects.filter(blog_id=blog_id)

    if request.method == 'POST':
        comment_form = BlogCommentForm(request.POST)

        if comment_form.is_valid():
            comment_content = comment_form.cleaned_data['comment_textfield']

            login_request_uri = 'https://kauth.kakao.com/oauth/authorize?'

            client_id = '2b772e480f01eb69c9a70c438dd11a25'
            redirect_uri = 'http://127.0.0.1:8000/oauth'

            login_request_uri += 'client_id=' + client_id
            login_request_uri += '&redirect_uri=' + redirect_uri
            login_request_uri += '&response_type=code&scope=talk_message'

            request.session['client_id'] = client_id
            request.session['redirect_uri'] = redirect_uri
            request.session['blog_id'] = blog_id
            request.session['comment_content'] = comment_content
            request.session['back_path'] = request.path

            return redirect(login_request_uri)
        else:
            return redirect('blogMain')

    else:
        comment_form = BlogCommentForm()

        context = {
            'blog_detail': blog_detail,
            'comments': comments,
            'comment_form': comment_form
        }

        return render(request, 'detail.html', context)

def oauth(request):
    code = request.GET['code']
    print('code = ' + str(code))

    client_id = request.session.get('client_id')
    redirect_uri = request.session.get('redirect_uri')
    blog_id = request.session.get('blog_id')
    comment_content = request.session.get('comment_content')
    back_path = request.session.get('back_path')

    access_token_request_uri = "https://kauth.kakao.com/oauth/token?grant_type=authorization_code"
 
    access_token_request_uri += "&client_id=" + client_id
    access_token_request_uri += "&redirect_uri=" + redirect_uri
    access_token_request_uri += "&code=" + code

    access_token_request_uri_data = requests.get(access_token_request_uri)
    json_data = access_token_request_uri_data.json()
    access_token = json_data['access_token']

    user_profile_info_uri = 'https://kapi.kakao.com/v1/api/talk/profile?access_token='
    user_profile_info_uri += str(access_token)

    user_profile_info_uri_data = requests.get(user_profile_info_uri)
    user_json_data = user_profile_info_uri_data.json()
    nickName = user_json_data['nickName']
    profileImageURL = user_json_data['profileImageURL']
    thumbnailURL = user_json_data['thumbnailURL']

    print('nickName = ' + str(nickName))
    print('profileImageURL = ' + str(profileImageURL))
    print('thumbnailURL = ' + str(thumbnailURL))

    if profileImageURL == "":
        profileImageURL = r'https://cdn.business2community.com/wp-content/uploads/2017/08/blank-profile-picture-973460_640.png'

    blogs = Blog.objects.all()

    Comment(
        blog=blogs[blog_id - 1],
        comment_user=nickName,
        comment_thumbnail_url=profileImageURL,
        comment_textfield=comment_content
    ).save()

    template_dict_data = str({
        "object_type": "text",
        "text": "<" + str(blog_id) + "번 게시판에 댓글이 작성되었습니다>" + comment_content,
        "link": {
            "web_url": "http://127.0.0.1:8000/blogMain/detial/" + str(blog_id),
            "mobile_web_url": "http://127.0.0.1:8000/blogMain/detial/" + str(blog_id)
        },
        "button_title": "바로 확인"
    })

    kakao_to_me_uri = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Bearer " + access_token,
    }

    template_json_data = "template_object=" + str(json.dumps(template_dict_data))

    template_json_data = template_json_data.replace("\"", "")
    template_json_data = template_json_data.replace("'", "\"")
    
    response = requests.request(method="POST", url=kakao_to_me_uri, data=template_json_data, headers=headers)
    print(response.json())

    return redirect(back_path)