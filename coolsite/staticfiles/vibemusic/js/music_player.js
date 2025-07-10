document.addEventListener('DOMContentLoaded', function() {
    // Установка фонового изображения
    const backgroundImage = document.body.dataset.backgroundImage;
    if (backgroundImage) {
        document.body.classList.add('dynamic-background');
        document.body.style.setProperty('--background-image', `url(${backgroundImage})`);
    }

    // Управление плеером
    const covers = document.querySelectorAll('.album-cover');
    const audioPlayer = document.querySelector('.audio-player');
    const audio = audioPlayer.querySelector('.audio-element');
    const source = audio.querySelector('source');
    const progress = document.getElementById('progress');
    const playPauseBtn = document.querySelector('.play-pause-btn');
    const playIcon = playPauseBtn ? playPauseBtn.querySelector('.play-icon') : null;
    const pauseIcon = playPauseBtn ? playPauseBtn.querySelector('.pause-icon') : null;
    const downloadBtn = document.getElementById('download-btn');
    let currentTrack = null;
    let isSeeking = false;

    console.log('Covers found:', covers.length);
    console.log('Audio player found:', !!audioPlayer);
    console.log('Progress element found:', !!progress);
    console.log('Play/Pause button found:', !!playPauseBtn);
    console.log('Download button found:', !!downloadBtn);

    if (!audioPlayer || !audio || !progress || !playPauseBtn || !playIcon || !pauseIcon || !downloadBtn) {
        console.error('Required elements not found:', { audioPlayer, audio, progress, playPauseBtn, playIcon, pauseIcon, downloadBtn });
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

        console.log('Setting up cover:', audioSrc);

        playButton.addEventListener('click', function() {
            console.log('Clicked track:', audioSrc);
            if (currentTrack !== audioSrc) {
                if (!audio.paused) audio.pause();
                source.src = audioSrc;
                downloadBtn.href = audioSrc; // Обновляем ссылку для скачивания
                audio.load();
                audio.play().then(() => {
                    console.log('Playing:', audioSrc);
                    audioPlayer.style.display = 'block';
                    cover.classList.add('playing');
                    playIconCover.style.display = 'none';
                    pauseIconCover.style.display = 'block';
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'block';
                    currentTrack = audioSrc;
                }).catch(err => console.error('Play error:', err));
            } else {
                if (audio.paused) {
                    audio.play().then(() => {
                        console.log('Resuming:', audioSrc);
                        cover.classList.add('playing');
                        playIconCover.style.display = 'none';
                        pauseIconCover.style.display = 'block';
                        playIcon.style.display = 'none';
                        pauseIcon.style.display = 'block';
                    }).catch(err => console.error('Resume error:', err));
                } else {
                    audio.pause();
                    console.log('Pausing:', audioSrc);
                    cover.classList.remove('playing');
                    playIconCover.style.display = 'block';
                    pauseIconCover.style.display = 'none';
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
                console.log('Playback resumed');
                playIcon.style.display = 'none';
                pauseIcon.style.display = 'block';
                if (currentTrack) {
                    const activeCover = document.querySelector(`.album-cover[data-src="${currentTrack}"]`);
                    if (activeCover) {
                        activeCover.classList.add('playing');
                        activeCover.querySelector('.play-icon').style.display = 'none';
                        activeCover.querySelector('.pause-icon').style.display = 'block';
                    }
                }
            }).catch(err => console.error('Play error:', err));
        } else {
            audio.pause();
            console.log('Paused');
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
            if (currentTrack) {
                const activeCover = document.querySelector(`.album-cover[data-src="${currentTrack}"]`);
                if (activeCover) {
                    activeCover.classList.remove('playing');
                    activeCover.querySelector('.play-icon').style.display = 'block';
                    activeCover.querySelector('.pause-icon').style.display = 'none';
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
    progress.addEventListener('mousedown', () => {
        isSeeking = true;
        console.log('Seeking started');
    });
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
        console.log('Seeking ended');
    });

    // Обработка окончания трека
    audio.addEventListener('ended', () => {
        console.log('Track ended');
        audioPlayer.style.display = 'none';
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        if (currentTrack) {
            const activeCover = document.querySelector(`.album-cover[data-src="${currentTrack}"]`);
            if (activeCover) {
                activeCover.classList.remove('playing');
                activeCover.querySelector('.play-icon').style.display = 'block';
                activeCover.querySelector('.pause-icon').style.display = 'none';
            }
        }
        currentTrack = null;
        progress.value = 0;
    });

    // Обработка ошибок
    audio.addEventListener('error', (e) => {
        console.error('Audio error:', e.message);
    });

    // Логирование метаданных
    audio.addEventListener('loadedmetadata', () => {
        console.log('Metadata loaded:', audio.duration, 'ReadyState:', audio.readyState);
    });

    audio.addEventListener('canplay', () => {
        console.log('Can play:', audio.duration);
    });
});