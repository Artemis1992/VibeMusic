// JavaScript для панели смайликов
const emojiBtn = document.getElementById('emoji-btn');
const emojiPicker = document.getElementById('emoji-picker');
const commentInput = document.getElementById('comment-content');

emojiBtn.addEventListener('click', () => {
    emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'block' : 'none';
});

function insertEmoji(emoji) {
    const startPos = commentInput.selectionStart;
    const endPos = commentInput.selectionEnd;
    const text = commentInput.value;
    commentInput.value = text.substring(0, startPos) + emoji + text.substring(endPos);
    commentInput.focus();
    commentInput.selectionStart = commentInput.selectionEnd = startPos + emoji.length;
}

// Обработка лайков для постов
document.querySelectorAll('.like-post-btn').forEach(button => {
    button.addEventListener('click', function() {
        const postId = this.getAttribute('data-post-id');
        const isLiked = this.getAttribute('data-liked') === 'true';
        fetch(toggleLikeUrl, {  // Используем переменную из шаблона
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,  // Используем переменную из шаблона
            },
            body: JSON.stringify({ post_id: postId, type: 'post' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const heartIcon = this.querySelector('.heart-icon');
                const likeCount = this.querySelector('.like-count');
                heartIcon.style.fill = isLiked ? '#ffffff' : '#ff5733';
                this.setAttribute('data-liked', isLiked ? 'false' : 'true');
                likeCount.textContent = data.like_count;
            } else {
                alert(data.message || 'Войдите, чтобы поставить лайк.');
            }
        });
    });
});

// Обработка лайков для треков
document.querySelectorAll('.like-track-btn').forEach(button => {
    button.addEventListener('click', function() {
        const trackId = this.getAttribute('data-track-id');
        const isLiked = this.getAttribute('data-liked') === 'true';
        fetch(toggleLikeUrl, {  // Используем переменную
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,  // Используем переменную
            },
            body: JSON.stringify({ track_id: trackId, type: 'track' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const heartIcon = this.querySelector('.heart-icon');
                const likeCount = this.querySelector('.like-count');
                heartIcon.style.fill = isLiked ? '#ffffff' : '#ff5733';
                this.setAttribute('data-liked', isLiked ? 'false' : 'true');
                likeCount.textContent = data.like_count;
            } else {
                alert(data.message || 'Войдите, чтобы поставить лайк.');
            }
        });
    });
});

// Обработка лайков для комментариев
document.querySelectorAll('.like-comment-btn').forEach(button => {
    button.addEventListener('click', function() {
        const commentId = this.getAttribute('data-comment-id');
        const isLiked = this.getAttribute('data-liked') === 'true';
        fetch(toggleLikeUrl, {  // Используем переменную
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,  // Используем переменную
            },
            body: JSON.stringify({ comment_id: commentId, type: 'comment' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const heartIcon = this.querySelector('.heart-icon');
                const likeCount = this.querySelector('.like-count');
                heartIcon.style.fill = isLiked ? '#ffffff' : '#ff5733';
                this.setAttribute('data-liked', isLiked ? 'false' : 'true');
                likeCount.textContent = data.like_count;
            } else {
                alert(data.message || 'Войдите, чтобы поставить лайк.');
            }
        });
    });
});