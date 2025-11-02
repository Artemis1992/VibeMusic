document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form[action*="add_comment"]');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': window.csrfToken || document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                // Добавляем в начало
                const container = document.getElementById('comments-container');
                container.insertAdjacentHTML('afterbegin', data.comment_html);

                // Обновляем счётчик
                document.getElementById('comment-count-value').textContent = data.comment_count;

                // Очистка
                form.reset();
                document.getElementById('comment-content').style.height = 'auto';
            } else {
                alert('Ошибка: ' + (data.errors?.content?.[0] || 'Проверьте данные'));
            }
        })
        .catch(err => {
            console.error(err);
            alert('Ошибка сервера');
        });
    });
});