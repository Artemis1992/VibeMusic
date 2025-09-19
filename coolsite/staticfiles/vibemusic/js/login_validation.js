document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const fields = ['username', 'password'];

    fields.forEach(field => {
        const input = document.getElementById(field);
        const spinner = document.getElementById(`${field}-spinner`);
        const message = document.getElementById(`${field}-message`);

        input.addEventListener('input', () => {
            spinner.classList.add('spinner-active');
            message.textContent = '';

            // Имитация асинхронной проверки (замените на реальный AJAX-запрос)
            setTimeout(() => {
                validateField(field, input.value, spinner, message);
            }, 1000); // Задержка для имитации проверки
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
});