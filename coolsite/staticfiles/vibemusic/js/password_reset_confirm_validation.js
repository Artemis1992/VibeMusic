document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const fields = ['new_password1', 'new_password2'];

    fields.forEach(field => {
        const input = document.getElementById(`id_${field}`);
        const spinner = document.getElementById(`${field}-spinner`);
        const message = document.getElementById(`${field}-message`);

        input.addEventListener('input', () => {
            spinner.classList.add('spinner-active');
            message.textContent = '';

            setTimeout(() => {
                const value = input.value;
                let isValid = false;
                let messageText = '';

                if (field === 'new_password1') {
                    isValid = value.length >= 8;
                    messageText = isValid ? 'Пароль подходит!' : 'Пароль должен быть минимум 8 символов.';
                } else if (field === 'new_password2') {
                    const password1 = document.getElementById('id_new_password1').value;
                    isValid = value === password1 && value.length >= 8;
                    messageText = isValid ? 'Пароли совпадают!' : 'Пароли не совпадают или слишком короткие.';
                }

                spinner.classList.remove('spinner-active');
                message.textContent = messageText;
                message.classList.toggle('text-success', isValid);
                message.classList.toggle('text-danger', !isValid);
            }, 1000);
        });
    });
});