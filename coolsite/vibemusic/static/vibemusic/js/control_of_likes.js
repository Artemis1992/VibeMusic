// control_of_likes.js
document.addEventListener('DOMContentLoaded', function() {
    // Лайки постов
    document.querySelectorAll('.like-post-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            const heartIcon = this.querySelector('.heart-icon');
            const likeCount = this.querySelector('.like-count');

            fetch(toggleLikeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ type: 'post', post_id: postId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.setAttribute('data-liked', data.liked ? 'true' : 'false');
                    heartIcon.setAttribute('fill', data.liked ? '#ff5733' : '#ffffff');
                    likeCount.textContent = data.like_count;
                } else {
                    console.error('Ошибка от сервера:', data.message);
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });

    // Лайки треков
    document.querySelectorAll('.like-track-btn').forEach(button => {
        button.addEventListener('click', function() {
            const trackId = this.getAttribute('data-track-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            const heartIcon = this.querySelector('.heart-icon');
            const likeCount = this.querySelector('.like-count');

            fetch(toggleLikeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ type: 'track', track_id: trackId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.setAttribute('data-liked', data.liked ? 'true' : 'false');
                    heartIcon.setAttribute('fill', data.liked ? '#ff5733' : '#ffffff');
                    likeCount.textContent = data.like_count;
                } else {
                    console.error('Ошибка от сервера:', data.message);
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });

    // Лайки комментариев
    document.querySelectorAll('.like-comment-btn').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            const heartIcon = this.querySelector('.heart-icon');
            const likeCount = this.querySelector('.like-count');

            fetch(toggleLikeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ type: 'comment', comment_id: commentId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.setAttribute('data-liked', data.liked ? 'true' : 'false');
                    heartIcon.setAttribute('fill', data.liked ? '#ff5733' : '#ffffff');
                    likeCount.textContent = data.like_count;
                } else {
                    console.error('Ошибка от сервера:', data.message);
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });

    // Подписка/отписка
    document.querySelectorAll('.follow-btn').forEach(button => {
        button.addEventListener('click', function() {
            const profileId = this.getAttribute('data-profile-id');
            fetch(`/follow/${profileId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.textContent = data.action === 'followed' ? 'Отписаться' : 'Подписаться';
                    this.classList.toggle('btn-primary', data.action === 'unfollowed');
                    this.classList.toggle('btn-secondary', data.action === 'followed');
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });
});