// vibemusic/static/vibemusic/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const backgroundImage = body.getAttribute('data-background-image');       // Получаем атрибут data-background-image
    if (backgroundImage) {                                                   // Если изображение задано
        body.style.backgroundImage = `url('${backgroundImage}')`;            // Устанавливаем фоновое изображение
        body.style.backgroundSize = 'cover';                                 // Масштабируем изображение
        body.style.backgroundPosition = 'center';                            // Центрируем изображение
        body.style.backgroundAttachment = 'fixed';                           // Фиксируем фон
    }

    const followButtons = document.querySelectorAll('.follow-btn');           // Находим все кнопки подписки
    followButtons.forEach(button => {                                         // Перебираем кнопки
        button.addEventListener('click', function(e) {                        // Добавляем обработчик клика
            e.preventDefault();                                              // Предотвращаем переход по ссылке
            const url = this.getAttribute('href');                           // Получаем URL из кнопки
            const isFollowing = this.classList.contains('btn-danger');       // Проверяем, подписан ли пользователь
            fetch(url, {                                                     // Отправляем AJAX-запрос
                method: 'GET',                                               // Используем GET (как в toggle_follow)
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'                     // Указываем, что это AJAX-запрос
                }
            })
            .then(response => response.json())                                // Парсим JSON-ответ
            .then(data => {
                if (data.success) {                                          // Если запрос успешен
                    this.textContent = isFollowing ? 'Подписаться' : 'Отписаться';  // Меняем текст кнопки
                    this.classList.toggle('btn-danger');                     // Переключаем класс btn-danger
                    this.classList.toggle('btn-primary');                    // Переключаем класс btn-primary
                    // Показываем сообщение (если messages есть в шаблоне)
                    if (data.action === 'followed') {
                        showMessage('success', `Вы подписались на пользователя!`);  // Успех подписки
                    } else if (data.action === 'unfollowed') {
                        showMessage('success', `Вы отписались от пользователя!`);  // Успех отписки
                    }
                } else {
                    showMessage('error', 'Ошибка при выполнении действия.'); // Показываем ошибку
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);                             // Логируем ошибку в консоль
                showMessage('error', 'Произошла ошибка. Попробуйте снова.'); // Показываем ошибку
            });
        });
    });

    function showMessage(type, message) {                                     // Функция для показа сообщений
        const messageContainer = document.createElement('div');              // Создаём контейнер для сообщения
        messageContainer.className = `alert alert-${type} alert-dismissible fade show`;  // Стили Bootstrap
        messageContainer.style.position = 'fixed';
        messageContainer.style.top = '20px';
        messageContainer.style.right = '20px';
        messageContainer.style.zIndex = '1000';
        messageContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;                                                                   // HTML сообщения
        document.body.appendChild(messageContainer);                          // Добавляем в DOM
        setTimeout(() => {
            messageContainer.remove();                                       // Удаляем через 3 секунды
        }, 3000);
    }
});