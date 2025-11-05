document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form[action*="/add_comment/"]');
    if (!form) return;

    const textarea = document.getElementById('comment-content');
    const commentsContainer = document.getElementById('comments-container');
    const commentCountBadge = document.getElementById('comment-count-value');

    // === ЭМОДЗИ ===
    document.querySelectorAll('.emoji-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const emoji = this.textContent;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;
            textarea.value = text.substring(0, start) + emoji + text.substring(end);
            textarea.focus();
            textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
        });
    });

    // === ОТПРАВКА ФОРМЫ ===
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const content = textarea.value;

        // СОХРАНЯЕМ ВСЕ ПРОБЕЛЫ, ПЕРЕНОСЫ, ОТСТУПЫ
        formData.set('content', content);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Вставляем комментарий в начало
                commentsContainer.insertAdjacentHTML('afterbegin', data.html);
                textarea.value = '';
                document.getElementById('comment-image').value = '';

                // Обновляем счётчик
                const count = parseInt(commentCountBadge.textContent) + 1;
                commentCountBadge.textContent = count;

                // Прокрутка
                commentsContainer.firstElementChild.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(err => {
            console.error(err);
            alert('Ошибка сети');
        });
    });
});