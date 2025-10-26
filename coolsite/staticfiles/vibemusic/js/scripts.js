// scripts.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('Scripts.js loaded'); // Отладка: скрипт загружен

    // Обработка открытия модальных окон из dropdown-menu
    document.querySelectorAll('.dropdown-item[data-bs-toggle="modal"]').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Предотвращаем переход по href
            const target = this.getAttribute('data-bs-target');
            console.log('Attempting to open modal:', target);

            // Закрываем все dropdown-menu через Bootstrap API
            document.querySelectorAll('.dropdown').forEach(dropdown => {
                const bsDropdown = bootstrap.Dropdown.getInstance(dropdown.querySelector('[data-bs-toggle="dropdown"]'));
                if (bsDropdown) {
                    bsDropdown.hide();
                    console.log('Closed dropdown-menu for:', dropdown);
                }
            });

            // Открываем модал
            try {
                const modalElement = document.querySelector(target);
                if (modalElement) {
                    const modal = new bootstrap.Modal(modalElement, { backdrop: 'static' });
                    modal.show();
                    console.log('Modal opened:', target);
                } else {
                    console.error('Modal element not found for target:', target);
                }
            } catch (error) {
                console.error('Error opening modal:', error);
            }
        });
    });

    // Принудительное удаление modal-backdrop при закрытии модала
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            console.log('Modal closed:', modal.id);
            try {
                document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow = 'auto';
                document.body.style.paddingRight = '0';
                console.log('Backdrop removed, body styles reset');
            } catch (error) {
                console.error('Error cleaning up modal:', error);
            }
        });
    });
});