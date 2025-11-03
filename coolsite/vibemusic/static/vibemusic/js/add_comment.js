// vibemusic/static/vibemusic/js/add_comment.js
document.addEventListener('DOMContentLoaded', function () {
    const textarea = document.getElementById('comment-content');
    const form = textarea?.closest('form');

    if (!form || !textarea) return;

    // === РАЗРЕШАЕМ ПРОБЕЛЫ В НАЧАЛЕ ===
    textarea.addEventListener('keydown', function (e) {
        if (e.key === ' ' && this.selectionStart === 0) {
            // НЕ БЛОКИРУЕМ — ПРОПУСКАЕМ
            // e.preventDefault(); ← УДАЛИ ЭТУ СТРОКУ!
            return;
        }
    });

    // === ЭМОДЗИ ===
    document.querySelectorAll('.emoji').forEach(span => {
        span.addEventListener('click', function () {
            const emoji = this.textContent.trim();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            textarea.value = textarea.value.substring(0, start) + emoji + textarea.value.substring(end);
            textarea.focus();
            textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
        });
    });

    // === ОТПРАВКА ФОРМЫ ===
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!textarea.value.trim() && !form.querySelector('[name="image"]').files.length) {
            alert('Введите текст или прикрепите изображение');
            return;
        }

        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.ok) {
                form.reset();
                location.reload();
            } else {
                const err = await response.json();
                alert(err.error || 'Ошибка');
            }
        } catch (err) {
            alert('Нет соединения');
        }
    });
});

