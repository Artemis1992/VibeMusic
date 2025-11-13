# vibemusic/services/toggle_follow.py

def toggle_follow(follower, target):
    """
    Переключает подписку: подписаться / отписаться.

    follower — пользователь, который хочет подписаться
    target — пользователь, на которого подписываются
    """
    if follower == target:
        return False, "Нельзя подписаться на себя"

    if target.followers.filter(id=follower.id).exists():
        target.followers.remove(follower)
        return False, "unsubscribe"

    target.followers.add(follower)
    return True, "subscribe"
