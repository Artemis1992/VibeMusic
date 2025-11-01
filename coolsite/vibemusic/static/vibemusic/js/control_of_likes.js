// vibemusic/static/vibemusic/js/control_of_likes.js
document.addEventListener('DOMContentLoaded', function () {

    async function toggleLike(type, id, button) {
        if (!button || button.classList.contains('disabled')) return;

        // CSRF токен: из window.csrfToken (из шаблона) или из кук
        const csrfToken = window.csrfToken ||
                         document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         getCookie('csrftoken');
        if (!csrfToken) {
            console.error('CSRF токен не найден!');
            return;
        }

        const icon = button.querySelector('.heart-icon');
        const countSpan = button.querySelector('.like-count');
        button.classList.add('disabled');

        try {
            const response = await fetch(`/api/v1/like/${type}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ [`${type}_id`]: parseInt(id) })
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || err.detail || 'Ошибка сервера');
            }

            const data = await response.json();

            // Обновляем UI
            if (icon) {
                icon.style.fill = data.liked ? '#ff5733' : '#ffffff';
            }
            if (countSpan) {
                countSpan.textContent = data.count;
            }
            button.setAttribute('data-liked', data.liked);

            // Анимация
            button.style.transform = 'scale(1.3)';
            setTimeout(() => button.style.transform = '', 150);

        } catch (error) {
            console.error('Ошибка лайка:', error);
            alert('Не удалось поставить лайк: ' + error.message);
        } finally {
            button.classList.remove('disabled');
        }
    }

    // Вспомогательная функция для чтения куки
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Делегирование кликов
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.like-post-btn, .like-track-btn, .like-comment-btn');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        let type, id;

        if (btn.classList.contains('like-post-btn')) {
            type = 'post';
            id = btn.dataset.postId;  // ← dataset.postId → data-post-id
        } else if (btn.classList.contains('like-track-btn')) {
            type = 'track';
            id = btn.dataset.trackId; // ← dataset.trackId → data-track-id
        } else if (btn.classList.contains('like-comment-btn')) {
            type = 'comment';
            id = btn.dataset.commentId; // ← dataset.commentId → data-comment-id
        }

        if (!id) {
            console.error('ID не найден для кнопки:', btn);
            return;
        }

        toggleLike(type, id, btn);
    });
});