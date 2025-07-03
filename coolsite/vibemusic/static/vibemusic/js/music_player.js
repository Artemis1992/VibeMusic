document.addEventListener('DOMContentLoaded', function() {
    const covers = document.querySelectorAll('.album-cover');
    const audioPlayer = document.querySelector('.audio-player');
    const audio = audioPlayer.querySelector('audio');
    const source = audio.querySelector('source');
    let currentTrack = null; // Отслеживаем текущий трек

    covers.forEach(cover => {
        const playButton = cover.querySelector('.play-button');
        const playIcon = cover.querySelector('.play-icon');
        const pauseIcon = cover.querySelector('.pause-icon');
        const audioSrc = cover.getAttribute('data-src');

        playButton.addEventListener('click', function() {
            console.log('Clicked track:', audioSrc);
            console.log('Current track:', currentTrack);

            if (currentTrack !== audioSrc) {
                // Новый трек: останавливаем текущий, если он играет
                if (!audio.paused) {
                    audio.pause();
                    covers.forEach(c => {
                        c.classList.remove('playing');
                        c.querySelector('.play-icon').style.display = 'block';
                        c.querySelector('.pause-icon').style.display = 'none';
                    });
                }
                // Загружаем и воспроизводим новый трек
                source.src = audioSrc;
                audio.load();
                audio.play().then(() => {
                    console.log('Playing new track:', audioSrc);
                    audioPlayer.style.display = 'block';
                    cover.classList.add('playing');
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'block';
                    currentTrack = audioSrc;
                }).catch(err => console.error('Error playing audio:', err));
            } else {
                // Тот же трек
                if (audio.paused) {
                    // Если на паузе, возобновляем с текущей позиции
                    audio.play().then(() => {
                        console.log('Resuming track:', audioSrc, 'at time:', audio.currentTime);
                        cover.classList.add('playing');
                        playIcon.style.display = 'none';
                        pauseIcon.style.display = 'block';
                    }).catch(err => console.error('Error resuming audio:', err));
                } else {
                    // Если играет, ставим на паузу
                    audio.pause();
                    console.log('Pausing track:', audioSrc, 'at time:', audio.currentTime);
                    cover.classList.remove('playing');
                    playIcon.style.display = 'block';
                    pauseIcon.style.display = 'none';
                }
            }
        });

        audio.addEventListener('play', function() {
            console.log('Audio play event:', audioSrc);
            covers.forEach(c => {
                const cSrc = c.getAttribute('data-src');
                if (cSrc === currentTrack) {
                    c.classList.add('playing');
                    c.querySelector('.play-icon').style.display = 'none';
                    c.querySelector('.pause-icon').style.display = 'block';
                } else {
                    c.classList.remove('playing');
                    c.querySelector('.play-icon').style.display = 'block';
                    c.querySelector('.pause-icon').style.display = 'none';
                }
            });
        });

        audio.addEventListener('pause', function() {
            console.log('Audio pause event:', audioSrc);
            cover.classList.remove('playing');
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
        });

        audio.addEventListener('ended', function() {
            console.log('Audio ended event:', audioSrc);
            cover.classList.remove('playing');
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
            audioPlayer.style.display = 'none';
            currentTrack = null;
        });
    });
});