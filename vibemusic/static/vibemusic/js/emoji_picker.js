// vibemusic/static/vibemusic/js/emoji_picker.js

document.addEventListener('DOMContentLoaded', function () {
    const commentInput = document.getElementById('comment-content');
    if (!commentInput) return;

    // Делегируем клик на весь контейнер смайликов
    document.querySelectorAll('.emoji').forEach(span => {
        span.addEventListener('click', function () {
            const emoji = this.textContent.trim();  // Берем сам смайлик: hug, thinking и т.д.

            // Вставляем в textarea
            const start = commentInput.selectionStart;
            const end = commentInput.selectionEnd;
            const text = commentInput.value;

            commentInput.value = text.substring(0, start) + emoji + text.substring(end);
            commentInput.focus();
            commentInput.selectionStart = commentInput.selectionEnd = start + emoji.length;
        });
    });
});