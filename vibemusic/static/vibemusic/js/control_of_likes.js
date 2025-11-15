// vibemusic/static/vibemusic/js/control_of_likes.js
document.addEventListener('DOMContentLoaded', function () {

    async function toggleLike(type, id, button) {
        if (!button || button.classList.contains('disabled')) return;

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

        console.log('Отправка лайка:', type, id); // ← ЛОГИРОВАНИЕ

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
            console.log('Ответ сервера:', data); // ← ЛОГИРОВАНИЕ

            // Обновляем UI
            if (icon) {
                icon.style.fill = data.liked ? '#ff5733' : (type === 'comment' ? '#888' : '#ffffff');
            }
            if (countSpan) {
                countSpan.textContent = data.count;
            }
            button.setAttribute('data-liked', data.liked);

            // Анимация
            button.style.transform = 'scale(1.4)';
            setTimeout(() => button.style.transform = '', 180);

        } catch (error) {
            console.error('Ошибка лайка:', error);
            alert('Не удалось поставить лайк: ' + error.message);
        } finally {
            button.classList.remove('disabled');
        }
    }

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

    // === ДЕЛЕГИРОВАНИЕ КЛИКОВ (ИСПРАВЛЕНО) ===
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.like-post-btn, .like-track-btn, .like-comment-btn');
        if (!btn) return;

        e.preventDefault();

        let type, id;

        if (btn.classList.contains('like-post-btn')) {
            type = 'post';
            id = btn.getAttribute('data-post-id');
        } else if (btn.classList.contains('like-track-btn')) {
            type = 'track';
            id = btn.getAttribute('data-track-id');
        } else if (btn.classList.contains('like-comment-btn')) {
            type = 'comment';
            id = btn.getAttribute('data-comment-id');
        }

        if (!id) {
            console.error('ID не найден для кнопки:', btn);
            return;
        }

        toggleLike(type, id, btn);
    });
});