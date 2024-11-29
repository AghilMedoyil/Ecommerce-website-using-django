from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {'notifications': unread_notifications, 'notification_count': unread_count}
    return {'notifications': [], 'notification_count': 0}
