// music_player.js
document.addEventListener('DOMContentLoaded', () => {
    // Установка фонового изображения
    const backgroundImage = document.body.dataset.backgroundImage;
    if (backgroundImage) {
        document.body.classList.add('dynamic-background');
        document.body.style.setProperty('--background-image', `url(${backgroundImage})`);
    }

    // Элементы плеера
    const covers = document.querySelectorAll('.album-cover');
    const audioPlayer = document.querySelector('.audio-player');
    const audio = audioPlayer?.querySelector('.audio-element');
    const source = audio?.querySelector('source');
    const progress = document.getElementById('progress');
    const playPauseBtn = document.querySelector('.play-pause-btn');
    const playIcon = playPauseBtn?.querySelector('.play-icon');
    const pauseIcon = playPauseBtn?.querySelector('.pause-icon');
    const downloadBtn = document.getElementById('download-btn');
    let currentTrack = null;
    let isSeeking = false;

    if (!audioPlayer || !audio || !progress || !playPauseBtn || !playIcon || !pauseIcon || !downloadBtn) {
        console.error('Required elements not found:', { audioPlayer, audio, progress, playPauseBtn, playIcon, pauseIcon, downloadBtn });
        return;
    }

    // Изначально отключить ползунок
    progress.disabled = true;

    // Обработчик кликов по трекам
    covers.forEach(cover => {
        const playButton = cover.querySelector('.play-button');
        const playIconCover = cover.querySelector('.play-icon');
        const pauseIconCover = cover.querySelector('.pause-icon');
        const audioSrc = cover.getAttribute('data-src');

        if (!playButton || !playIconCover || !pauseIconCover || !audioSrc) {
            console.error('Missing elements or data-src:', { playButton, playIconCover, pauseIconCover, audioSrc });
            return;
        }

        playButton.addEventListener('click', () => {
            console.log('Clicked track:', audioSrc);
            if (currentTrack !== audioSrc) {
                if (!audio.paused) audio.pause();
                source.src = audioSrc;
                downloadBtn.href = audioSrc;
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
                    progress.style.backgroundImage = `linear-gradient(to right, #1DB954 0%, #6c757d 0%)`; // Сброс при новом треке
                }).catch(err => console.error('Play error:', err));
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

    // Кнопка Play/Pause
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
                        activeCover.querySelector('.play-icon').style.display = 'none';
                        activeCover.querySelector('.pause-icon').style.display = 'block';
                        activeCover.classList.add('playing');
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
                    activeCover.querySelector('.play-icon').style.display = 'block';
                    activeCover.querySelector('.pause-icon').style.display = 'none';
                    activeCover.classList.remove('playing');
                }
            }
        }
    });

    // Обновление прогресса с закрашиванием
    audio.addEventListener('timeupdate', () => {
        if (!isSeeking && audio.duration && !isNaN(audio.duration)) {
            const percent = (audio.currentTime / audio.duration) * 100;
            progress.value = percent;
            progress.style.backgroundImage = `linear-gradient(to right, #1DB954 ${percent}%, #6c757d ${percent}%)`;
            console.log('Time update - Progress:', percent.toFixed(2), 'Background:', progress.style.backgroundImage);
        }
    });

    // Перемотка
    progress.addEventListener('mousedown', () => {
        isSeeking = true;
        console.log('Seeking started');
    });

    progress.addEventListener('input', () => {
        if (isSeeking && audio.readyState > 0 && audio.duration && !isNaN(audio.duration)) {
            const percent = progress.value;
            const seekTime = (percent / 100) * audio.duration;
            audio.currentTime = seekTime;
            progress.style.backgroundImage = `linear-gradient(to right, #1DB954 ${percent}%, #6c757d ${percent}%)`;
            console.log('Seeking to:', seekTime.toFixed(2), 'Progress:', percent);
        }
    });

    progress.addEventListener('mouseup', () => {
        isSeeking = false;
        console.log('Seek completed');
    });

    // Листание треков
    const nextTrack = () => {
        if (!currentTrack) return;
        const tracks = document.querySelectorAll('.album-cover');
        const currentIndex = Array.from(tracks).findIndex(c => c.getAttribute('data-src') === currentTrack);
        const nextIndex = (currentIndex + 1) % tracks.length;
        tracks[nextIndex].querySelector('.play-button').click();
    };

    const prevTrack = () => {
        if (!currentTrack) return;
        const tracks = document.querySelectorAll('.album-cover');
        const currentIndex = Array.from(tracks).findIndex(c => c.getAttribute('data-src') === currentTrack);
        const prevIndex = (currentIndex - 1 + tracks.length) % tracks.length;
        tracks[prevIndex].querySelector('.play-button').click();
    };

    // Поддержка клавиш
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            playPauseBtn.click();
        }
        if (e.code === 'ArrowRight') nextTrack();
        if (e.code === 'ArrowLeft') prevTrack();
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
                activeCover.querySelector('.play-icon').style.display = 'block';
                activeCover.querySelector('.pause-icon').style.display = 'none';
                activeCover.classList.remove('playing');
            }
        }
        currentTrack = null;
        progress.value = 0;
        progress.style.backgroundImage = `linear-gradient(to right, #1DB954 0%, #6c757d 0%)`;
    });

    // Логирование метаданных
    audio.addEventListener('loadedmetadata', () => {
        console.log('Metadata loaded:', audio.duration, 'ReadyState:', audio.readyState);
        progress.disabled = false;
        progress.style.backgroundImage = `linear-gradient(to right, #1DB954 0%, #6c757d 0%)`; // Сброс при загрузке
    });

    audio.addEventListener('canplay', () => {
        console.log('Can play:', audio.duration);
    });

    audio.addEventListener('error', (e) => {
        console.error('Audio error:', e.message);
    });
});