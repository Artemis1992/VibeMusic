document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-form');
    const fields = ['username', 'email', 'password1', 'password2'];

    fields.forEach(field => {
        const input = document.getElementById(`id_${field}`);
        const spinner = document.getElementById(`${field}-spinner`);
        const message = document.getElementById(`${field}-message`);

        input.addEventListener('input', () => {
            spinner.classList.add('spinner-active');
            message.textContent = '';

            // Имитация асинхронной проверки (замените на реальный AJAX-запрос к вашему API)
            setTimeout(() => {
                validateField(field, input.value, spinner, message);
            }, 1000); // Задержка для имитации проверки
        });
    });

    function validateField(field, value, spinner, message) {
        // Пример проверки (замените на реальную логику)
        let isValid = false;
        let messageText = '';

        if (field === 'username') {
            isValid = value.length >= 3;
            messageText = isValid ? 'Имя пользователя подходит!' : 'Имя пользователя слишком короткое.';
        } else if (field === 'email') {
            isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            messageText = isValid ? 'Email корректен!' : 'Введите действительный email.';
        } else if (field === 'password1') {
            isValid = value.length >= 8 && /[A-Z]/.test(value) && /[0-9]/.test(value);
            messageText = isValid ? 'Пароль надёжный!' : 'Пароль должен быть минимум 8 символов, с заглавной буквой и цифрой.';
        } else if (field === 'password2') {
            const password1 = document.getElementById('id_password1').value;
            isValid = value === password1;
            messageText = isValid ? 'Пароли совпадают!' : 'Пароли не совпадают.';
        }

        spinner.classList.remove('spinner-active');
        message.textContent = messageText;
        message.classList.toggle('text-success', isValid);
        message.classList.toggle('text-danger', !isValid);
    }
});