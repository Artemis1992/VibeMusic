document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const emailInput = document.getElementById('id_email');
    const spinner = document.getElementById('email-spinner');
    const message = document.getElementById('email-message');

    emailInput.addEventListener('input', () => {
        spinner.classList.add('spinner-active');
        message.textContent = '';

        // Имитация проверки email (замените на AJAX при необходимости)
        setTimeout(() => {
            const email = emailInput.value;
            const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
            message.textContent = isValid ? 'Email подходит!' : 'Введите действительный email.';
            spinner.classList.remove('spinner-active');
            message.classList.toggle('text-success', isValid);
            message.classList.toggle('text-danger', !isValid);
        }, 1000);
    });
});