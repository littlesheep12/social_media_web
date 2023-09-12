from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import Post, Comment, ReplyComment

import shortuuid
# Create your views here.

@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect("userauths:sign-in")
    # all func must return something
    posts = Post.objects.filter(active=True, visibility="Everyone").order_by("-id")
    context = {"posts":posts}
    return render(request, "core/index.html", context) # /:slash

@csrf_exempt
def create_post(request):

    if request.method == 'POST':
        title = request.POST.get('post-caption')
        visibility = request.POST.get('visibility')
        image = request.FILES.get('post-thumbnail')

        print("Title ============", title)
        print("thumbnail ============", image)
        print("visibility ============", visibility)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            post = Post(title=title, image=image, visibility=visibility, user=request.user, slug=slugify(title) + "-" + str(uniqueid.lower()))
            post.save()

            
            return JsonResponse({'post': {
                'title': post.title,
                'image_url': post.image.url,
                "full_name":post.user.profile.full_name,
                "profile_image":post.user.profile.image.url,
                "date":timesince(post.date),
                "id":post.id,
            }})
        else:
            return JsonResponse({'error': 'Invalid post data'})

    return JsonResponse({"data":"Sent"})

def like_post(request):
    id = request.GET['id']
    post = Post.objects.get(id = id)
    user = request.user
    bool = False

    if user in post.likes.all():
        post.likes.remove(user) # already have save() function method
        bool = False
    else:
        post.likes.add(user)
        bool = True
    
    data = {
        "bool":bool,
        "likes":post.likes.all().count()
    }
    return JsonResponse({"data":data}) #key:values


def comment_on_post(request):
    id = request.GET['id']
    comment = request.GET['comment']
    post = Post.objects.get(id=id)
    comment_count = Comment.objects.filter(post=post).count()
    user = request.user

    new_comment = Comment.objects.create(
        post=post,
        comment=comment,
        user=user
    )

    data = {
        "bool":True,
        'comment':new_comment.comment,
        "profile_image":new_comment.user.profile.image.url,
        "date":timesince(new_comment.date),
        "comment_id":new_comment.id,
        "post_id":new_comment.post.id,
        "comment_count":comment_count + int(1)
    }
    return JsonResponse({"data":data})

# Like Comment
def like_comment(request):
    id = request.GET["id"]
    comment = Comment.objects.get(id = id)
    user = request.user
    bool = False

    if user in comment.likes.all():
        comment.likes.remove(user)
        bool = False
    else:
        comment.likes.add(user)
        bool = True
    
    data = {
        "bool" : bool,
        "likes" : comment.likes.all().count()
    }
    return JsonResponse({"data":data})

# Reply Comment
def reply_comment(request):
    id = request.GET['id']
    reply = request.GET['reply']

    comment = Comment.objects.get(id=id)
    user = request.user

    new_reply = ReplyComment.objects.create(
        comment=comment,
        reply=reply,
        user=user
    )

    # # Notifications system
    # if comment.user != user:
    #     send_notification(comment.user, user, comment.post, comment, noti_comment_replied)

    data = {
        "bool":True,
        'reply':new_reply.reply,
        "profile_image":new_reply.user.profile.image.url,
        "date":timesince(new_reply.date),
        "reply_id":new_reply.id,
        "post_id":new_reply.comment.post.id,
    }
    
    return JsonResponse({"data":data})

# Delete Comment
def delete_commnet(request):
    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    comment.delete()

    data = {
        "bool": True
    }

    return JsonResponse({"data":data})
