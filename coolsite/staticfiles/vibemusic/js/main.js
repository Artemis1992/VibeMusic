/* main.js */

document.addEventListener('DOMContentLoaded', function() {
    // Установка фонового изображения
    const backgroundImage = document.body.dataset.backgroundImage;
    if (backgroundImage) {
        document.body.classList.add('dynamic-background');
        document.body.style.setProperty('--background-image', `url(${backgroundImage})`);
    }

    // Управление плеером
    const audioPlayer = document.querySelector('.audio-player');
    const audio = audioPlayer.querySelector('.audio-element');
    const progress = document.getElementById('progress');
    const playPauseBtn = document.querySelector('.play-pause-btn');
    const playIcon = playPauseBtn.querySelector('.play-icon');
    const pauseIcon = playPauseBtn.querySelector('.pause-icon');
    let isSeeking = false;
    let currentTrack = null;

    const covers = document.querySelectorAll('.album-cover');

    console.log('Covers found:', covers.length);
    console.log('Audio player found:', !!audioPlayer);
    console.log('Progress element found:', !!progress);

    if (!audioPlayer || !audio || !progress) {
        console.error('Required audio elements not found:', { audioPlayer, audio, progress });
        return;
    }

    covers.forEach(cover => {
        const playButton = cover.querySelector('.play-button');
        const playIconCover = cover.querySelector('.play-icon');
        const pauseIconCover = cover.querySelector('.pause-icon');
        const audioSrc = cover.getAttribute('data-src');

        if (!playButton || !playIconCover || !pauseIconCover || !audioSrc) {
            console.error('Missing elements or data-src:', { playButton, playIconCover, pauseIconCover, audioSrc });
            return;
        }

        playButton.addEventListener('click', function() {
            console.log('Clicked track:', audioSrc);
            if (currentTrack !== audioSrc) {
                if (!audio.paused) audio.pause();
                audio.src = audioSrc;
                audio.load();
                audio.play().then(() => {
                    console.log('Playing:', audioSrc);
                    audioPlayer.style.display = 'block';
                    covers.forEach(c => {
                        const cSrc = c.getAttribute('data-src');
                        c.querySelector('.play-icon').style.display = cSrc === audioSrc ? 'none' : 'block';
                        c.querySelector('.pause-icon').style.display = cSrc === audioSrc ? 'block' : 'none';
                        c.classList.toggle('playing', cSrc === audioSrc);
                    });
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'block';
                    currentTrack = audioSrc;
                }).catch(err => console.error('Play error:', err.message));
            } else {
                if (audio.paused) {
                    audio.play().then(() => {
                        console.log('Resuming:', audioSrc);
                        cover.querySelector('.play-icon').style.display = 'none';
                        cover.querySelector('.pause-icon').style.display = 'block';
                        cover.classList.add('playing');
                        playIcon.style.display = 'none';
                        pauseIcon.style.display = 'block';
                    }).catch(err => console.error('Resume error:', err));
                } else {
                    audio.pause();
                    console.log('Pausing:', audioSrc);
                    cover.querySelector('.play-icon').style.display = 'block';
                    cover.querySelector('.pause-icon').style.display = 'none';
                    cover.classList.remove('playing');
                    playIcon.style.display = 'block';
                    pauseIcon.style.display = 'none';
                }
            }
        });
    });

    // Кнопка воспроизведения/паузы
    playPauseBtn.addEventListener('click', () => {
        console.log('Play/Pause button clicked, paused:', audio.paused);
        if (audio.paused) {
            audio.play().then(() => {
                console.log('Playback resumed successfully');
                playIcon.style.display = 'none';
                pauseIcon.style.display = 'block';
                if (currentTrack) {
                    const activeCover = document.querySelector(`.album-cover[data-src="${currentTrack}"]`);
                    if (activeCover) {
                        activeCover.querySelector('.play-icon').style.display = 'none';
                        activeCover.querySelector('.pause-icon').style.display = 'block';
                        activeCover.classList.add('playing');
                    }
                }
            }).catch(err => console.error('Play error:', err.message));
        } else {
            audio.pause();
            console.log('Paused playback via button');
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
            if (currentTrack) {
                const activeCover = document.querySelector(`.album-cover[data-src="${currentTrack}"]`);
                if (activeCover) {
                    activeCover.querySelector('.play-icon').style.display = 'block';
                    activeCover.querySelector('.pause-icon').style.display = 'none';
                    activeCover.classList.remove('playing');
                }
            }
        }
    });

    // Обновление прогресса
    audio.addEventListener('timeupdate', () => {
        if (!isSeeking && audio.duration && !isNaN(audio.duration)) {
            const percent = (audio.currentTime / audio.duration) * 100;
            progress.value = percent;
            console.log('Time update:', audio.currentTime.toFixed(2), 'of', audio.duration.toFixed(2), 'Progress:', percent.toFixed(2));
        }
    });

    // Перемотка
    progress.addEventListener('mousedown', () => isSeeking = true);
    progress.addEventListener('input', () => {
        if (isSeeking && audio.readyState > 0 && audio.duration && !isNaN(audio.duration)) {
            const seekTime = (progress.value / 100) * audio.duration;
            audio.currentTime = seekTime;
            console.log('Seeking to:', seekTime.toFixed(2), 'Duration:', audio.duration.toFixed(2));
        } else {
            console.error('Cannot seek:', { readyState: audio.readyState, duration: audio.duration });
        }
    });
    progress.addEventListener('mouseup', () => {
        isSeeking = false;
        console.log('Seek completed');
    });

    // Проверка метаданных
    audio.addEventListener('loadedmetadata', () => {
        console.log('Metadata loaded:', audio.duration, 'ReadyState:', audio.readyState);
    });

    audio.addEventListener('canplay', () => {
        console.log('Can play:', audio.duration);
    });

    audio.addEventListener('ended', () => {
        console.log('Playback ended');
        audioPlayer.style.display = 'none';
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        if (currentTrack) {
            const activeCover = document.querySelector(`.album-cover[data-src="${currentTrack}"]`);
            if (activeCover) {
                activeCover.querySelector('.play-icon').style.display = 'block';
                activeCover.querySelector('.pause-icon').style.display = 'none';
                activeCover.classList.remove('playing');
            }
        }
        currentTrack = null;
        progress.value = 0;
    });

    audio.addEventListener('error', (e) => {
        console.error('Audio error:', e.message);
    });
});