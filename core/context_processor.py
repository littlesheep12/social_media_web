from core.models import FriendRequest


def my_context_processor(request):
    try:
        friend_request = FriendRequest.objects.filter(receiver=request.user).order_by("-id")
    except:
        friend_request = None
    
    return {
        "friend_request" : friend_request,
    }