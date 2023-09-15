from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from core.models import Post, Comment, ReplyComment, Friend, FriendRequest, Notification
from userauths.models import User

import shortuuid


# Notifications Keys
noti_friend_request = "Friend Request"
noti_friend_request_accepted = "Friend Request Accepted"
noti_new_follower = "New Follower"
noti_new_like = "New Like"
noti_new_comment = "New Comment"
noti_comment_liked = "Comment Liked"
noti_comment_replied = "Comment Replied"

def send_notification(user, sender, post, comment, notification_type):
    notification = Notification.objects.create(
        user=user, 
        sender=sender, 
        post=post, 
        comment=comment, 
        notification_type=notification_type
    )
    return notification

@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect("userauths:sign-in")
    # all func must return something
    posts = Post.objects.filter(active=True, visibility="Everyone").order_by("-id")
    context = {"posts":posts}
    return render(request, "core/index.html", context) # /:slash

@login_required
def post_detail(request, slug):
    post = Post.objects.get(active=True, visibility="Everyone", slug=slug)
    context = {"p":post}
    return render(request, "core/post-detail.html", context)

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

@csrf_exempt
def like_post(request):
    id = request.GET['id']
    post = Post.objects.get(id = id)
    user = request.user
    bool = False

    if user in post.likes.all():
        post.likes.remove(user)
        bool = False
    else:
        post.likes.add(user)
        bool = True
        
        # Notification
        if post.user != request.user:
            send_notification(post.user, user, post, None, noti_new_like)

    
    data = {
        "bool":bool,
        "likes":post.likes.all().count()
    }
    return JsonResponse({"data":data}) #key:values

@csrf_exempt
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

    # Notifications system
    if new_comment.user != post.user:
        send_notification(post.user, user, post, new_comment, noti_new_comment)

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
@csrf_exempt
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

        # Notifications system
        if comment.user != user:
            send_notification(comment.user, user, comment.post, comment, noti_comment_liked)
    
    data = {
        "bool" : bool,
        "likes" : comment.likes.all().count()
    }
    return JsonResponse({"data":data})

# Reply Comment
@csrf_exempt
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

    # Notifications system
    if comment.user != user:
        send_notification(comment.user, user, comment.post, comment, noti_comment_replied)

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
@csrf_exempt
def delete_commnet(request):
    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    comment.delete()

    data = {
        "bool": True
    }

    return JsonResponse({"data":data})

# Add Friend
@csrf_exempt
def add_friend(request):
    sender = request.user
    receiver_id = request.GET['id']
    bool = False

    if sender.id == int(receiver_id):
        return JsonResponse({"error" : "You cannot send a friend request to yourself"})
    
    receiver = User.objects.get(id=receiver_id)

    try:
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        if friend_request:
            friend_request.delete()
        bool = False
        return JsonResponse({"error" : "Cancelled", "bool" : bool})    
    
    except FriendRequest.DoesNotExist:
        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        bool = True

        # Notifications system
        send_notification(receiver, sender, None, None, noti_friend_request)

        return JsonResponse({"success" : "Sent", "bool" : bool}) 

@csrf_exempt
def accept_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()

    receiver.profile.friends.add(sender)
    sender.profile.friends.add(receiver)

    friend_request.delete()
    
    send_notification(sender, receiver, None, None, noti_friend_request_accepted)

    data = {
        "message":"Accepted",
        "bool":True,
    }
    return JsonResponse({'data': data})

@csrf_exempt
def reject_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()
    friend_request.delete()

    data = {
        "message":"Rejected",
        "bool":True,
    }
    return JsonResponse({'data': data})

@csrf_exempt
def unfriend(request):
    sender = request.user
    friend_id = request.GET['id'] 
    bool = False

    if sender.id == int(friend_id):
        return JsonResponse({'error': 'You cannot unfriend yourself'})
    
    my_friend = User.objects.get(id=friend_id)
    
    if my_friend in sender.profile.friends.all():
        sender.profile.friends.remove(my_friend)
        my_friend.profile.friends.remove(sender)
        bool = True
        return JsonResponse({'success': 'Unfriend Successfull',  'bool':bool})