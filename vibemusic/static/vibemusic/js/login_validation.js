// vibemusic/static/vibemusic/js/login_validation.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const fields = ['username', 'password'];

    // Валидация при вводе
    fields.forEach(field => {
        const input = document.getElementById(field);
        const spinner = document.getElementById(`${field}-spinner`);
        const message = document.getElementById(`${field}-message`);

        input.addEventListener('input', () => {
            spinner.classList.add('spinner-active');
            message.textContent = '';

            setTimeout(() => {
                validateField(field, input.value, spinner, message);
            }, 1000); // Задержка для имитации проверки
        });
    });

    // Обработка отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Предотвращаем стандартную отправку

        const usernameSpinner = document.getElementById('username-spinner');
        const passwordSpinner = document.getElementById('password-spinner');
        const usernameMessage = document.getElementById('username-message');
        const passwordMessage = document.getElementById('password-message');

        // Показываем спиннеры
        usernameSpinner.style.display = 'inline-block';
        passwordSpinner.style.display = 'inline-block';
        usernameMessage.textContent = '';
        passwordMessage.textContent = '';

        // Проверяем поля перед отправкой
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        let isValid = true;

        if (username.length < 3) {
            usernameMessage.textContent = 'Имя пользователя слишком короткое.';
            usernameMessage.classList.add('text-danger');
            isValid = false;
        }
        if (password.length < 8) {
            passwordMessage.textContent = 'Пароль должен быть минимум 8 символов.';
            passwordMessage.classList.add('text-danger');
            isValid = false;
        }

        if (!isValid) {
            usernameSpinner.style.display = 'none';
            passwordSpinner.style.display = 'none';
            return;
        }

        // Отправка формы через AJAX
        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            usernameSpinner.style.display = 'none';
            passwordSpinner.style.display = 'none';
            if (data.success) {
                // Перезагрузка страницы после успешного входа
                window.location.href = data.redirect_url || '{% url "vibemusic:home" %}';
            } else {
                usernameMessage.textContent = data.username_error || 'Ошибка входа';
                passwordMessage.textContent = data.password_error || '';
                usernameMessage.classList.add('text-danger');
                passwordMessage.classList.add('text-danger');
            }
        })
        .catch(error => {
            usernameSpinner.style.display = 'none';
            passwordSpinner.style.display = 'none';
            alert('Произошла ошибка сети');
            console.error('Error:', error);
        });
    });

    function validateField(field, value, spinner, message) {
        let isValid = false;
        let messageText = '';

        if (field === 'username') {
            isValid = value.length >= 3;
            messageText = isValid ? 'Имя пользователя подходит!' : 'Имя пользователя слишком короткое.';
        } else if (field === 'password') {
            isValid = value.length >= 8;
            messageText = isValid ? 'Пароль подходит!' : 'Пароль должен быть минимум 8 символов.';
        }

        spinner.classList.remove('spinner-active');
        message.textContent = messageText;
        message.classList.toggle('text-success', isValid);
        message.classList.toggle('text-danger', !isValid);
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
});