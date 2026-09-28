from models import Notification, db

socketio = None


def init(socketio_instance):
    global socketio
    socketio = socketio_instance


def notify(user_id, message, url=""):
    n = Notification(user_id=user_id, message=message[:300], url=url[:300])
    db.session.add(n)
    db.session.commit()
    if socketio:
        socketio.emit(
            "notification",
            {"msg": message, "url": url, "id": n.id},
            to=f"user_{user_id}"
        )
    return n


def mark_read(user_id, notification_id=None):
    q = Notification.query.filter_by(user_id=user_id)
    if notification_id:
        q = q.filter_by(id=notification_id)
    q.update({"is_read": True})
    db.session.commit()


def unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()