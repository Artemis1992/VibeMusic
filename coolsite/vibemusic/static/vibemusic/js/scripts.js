document.addEventListener('DOMContentLoaded', function() {
    // Динамический фон
    const body = document.body;
    const backgroundImage = body.getAttribute('data-background-image');
    if (backgroundImage) {
        body.style.backgroundImage = `url('${backgroundImage}')`;
        body.style.backgroundSize = 'cover';
        body.style.backgroundPosition = 'center';
        body.style.backgroundAttachment = 'fixed';
    }

    // Follow/Unfollow кнопки
    const followButtons = document.querySelectorAll('.follow-btn');
    followButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const isFollowing = this.classList.contains('btn-danger');
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.textContent = isFollowing ? 'Подписаться' : 'Отписаться';
                    this.classList.toggle('btn-danger');
                    this.classList.toggle('btn-primary');
                    if (data.action === 'followed') {
                        showMessage('success', `Вы подписались на пользователя!`);
                    } else if (data.action === 'unfollowed') {
                        showMessage('success', `Вы отписались от пользователя!`);
                    }
                } else {
                    showMessage('error', 'Ошибка при выполнении действия.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                showMessage('error', 'Произошла ошибка. Попробуйте снова.');
            });
        });
    });

    function showMessage(type, message) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `alert alert-${type} alert-dismissible fade show`;
        messageContainer.style.position = 'fixed';
        messageContainer.style.top = '20px';
        messageContainer.style.right = '20px';
        messageContainer.style.zIndex = '1000';
        messageContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(messageContainer);
        setTimeout(() => {
            messageContainer.remove();
        }, 3000);
    }

    // Фикс зависаний модалов и dirty-form
    let currentModal = null;
    let dirtyForm = null;

    const formsWithDirtyCheck = document.querySelectorAll('#profileEditForm');
    formsWithDirtyCheck.forEach(form => {
        let originalValues = new FormData(form);
        form.addEventListener('input', () => form.dataset.dirty = 'true');
        form.addEventListener('submit', () => {
            form.dataset.dirty = 'false';
        });
    });

    document.querySelectorAll('.close-modal-btn').forEach(btn => {
        btn.addEventListener('click', function(event) {
            currentModal = btn.closest('.modal');
            const form = currentModal.querySelector('form');
            if (form && form.dataset.dirty === 'true') {
                event.preventDefault();
                dirtyForm = form;
                new bootstrap.Modal(document.getElementById('confirmSaveModal')).show();
            }
        });
    });

    document.getElementById('saveChangesBtn')?.addEventListener('click', () => {
        if (dirtyForm) dirtyForm.submit();
    });

    document.getElementById('discardChangesBtn')?.addEventListener('click', () => {
        if (currentModal) bootstrap.Modal.getInstance(currentModal).hide();
    });

    // Фикс скролла модалов
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
        });
        modal.addEventListener('shown.bs.modal', () => {
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) modalBody.scrollTop = 0;
        });
    });
});