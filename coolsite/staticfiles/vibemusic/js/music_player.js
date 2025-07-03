document.addEventListener('DOMContentLoaded', function() {
    const covers = document.querySelectorAll('.album-cover');
    const audioPlayer = document.querySelector('.audio-player');
    const audio = audioPlayer.querySelector('audio');
    const source = audio.querySelector('source');

    covers.forEach(cover => {
        const playButton = cover.querySelector('.play-button');
        const img = cover.querySelector('.album-image');
        const audioSrc = cover.getAttribute('data-src');

        playButton.addEventListener('click', function() {
            if (audio.src !== audioSrc) {
                // Установить новый трек
                source.src = audioSrc;
                audio.load();
                audio.play();
                audioPlayer.style.display = 'block';
                cover.classList.add('playing');
            } else if (audio.paused) {
                audio.play();
                cover.classList.add('playing');
                audioPlayer.style.display = 'block';
            } else {
                audio.pause();
                cover.classList.remove('playing');
            }
        });

        audio.addEventListener('play', function() {
            covers.forEach(c => {
                if (c.getAttribute('data-src') !== audioSrc) {
                    c.classList.remove('playing');
                }
            });
            cover.classList.add('playing');
        });

        audio.addEventListener('pause', function() {
            cover.classList.remove('playing');
        });

        audio.addEventListener('ended', function() {
            cover.classList.remove('playing');
            audioPlayer.style.display = 'none';
        });
    });
});