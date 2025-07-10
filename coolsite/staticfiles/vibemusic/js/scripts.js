// vibemusic/static/vibemusic/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const backgroundImage = body.getAttribute('data-background-image');
    if (backgroundImage) {
        body.style.backgroundImage = `url('${backgroundImage}')`;
        body.style.backgroundSize = 'cover';
        body.style.backgroundPosition = 'center';
        body.style.backgroundAttachment = 'fixed';
    }
});