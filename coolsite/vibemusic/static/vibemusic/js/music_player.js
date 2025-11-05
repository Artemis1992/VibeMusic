// vibemusic/static/vibemusic/js/music_player.js
document.addEventListener('DOMContentLoaded', () => {
    // === ФОН ===
    const backgroundImage = document.body.dataset.backgroundImage;
    if (backgroundImage) {
        document.body.classList.add('dynamic-background');
        document.body.style.setProperty('--background-image', `url(${backgroundImage})`);
    }

    // === ЭЛЕМЕНТЫ ПЛЕЕРА ===
    const audioPlayer = document.querySelector('.audio-player');
    const audio = audioPlayer?.querySelector('.audio-element');
    const source = audio?.querySelector('source');
    const progress = document.getElementById('progress');
    const playPauseBtn = document.querySelector('.play-pause-btn');
    const playIcon = playPauseBtn?.querySelector('.play-icon');
    const pauseIcon = playPauseBtn?.querySelector('.pause-icon');
    const downloadBtn = document.getElementById('download-btn');
    const mainContainer = document.querySelector('.container');
    const prevBtn = document.querySelector('.prev-track-btn');
    const nextBtn = document.querySelector('.next-track-btn');
    const volumeControl = document.getElementById('volume');
    const modeBtn = document.getElementById('mode-btn');
    const modeIcons = {
        repeatOne: modeBtn?.querySelector('.repeat-one'),
        repeatAll: modeBtn?.querySelector('.repeat-all'),
        shuffle: modeBtn?.querySelector('.shuffle')
    };

    let currentTrack = null;
    let currentIndex = -1;
    let trackList = [];
    let isSeeking = false;
    let playbackMode = 'repeat-all'; // по умолчанию — повтор плейлиста

    // === ПРОВЕРКА ЭЛЕМЕНТОВ ===
    if (!audioPlayer || !audio || !source || !progress || !playPauseBtn || 
        !playIcon || !pauseIcon || !downloadBtn || !volumeControl || !modeBtn) {
        console.error('Player elements not found');
        return;
    }

    // === ОТСТУП ДЛЯ КОНТЕНТА ===
    const PLAYER_HEIGHT = 60;
    const updatePadding = (show) => {
        if (mainContainer) {
            mainContainer.style.paddingBottom = show ? `${PLAYER_HEIGHT + 20}px` : '1rem';
        }
    };

    audioPlayer.style.display = 'none';
    updatePadding(false);

    // === ГРОМКОСТЬ ===
    volumeControl.addEventListener('input', () => {
        audio.volume = volumeControl.value / 100;
    });

    // === СБОР ТРЕКОВ И КЛИК ПО ОБЛОЖКЕ ===
    document.querySelectorAll('.album-cover').forEach((cover, index) => {
        const playButton = cover.querySelector('.play-button');
        const audioSrc = cover.dataset.src;

        if (!playButton || !audioSrc) return;

        playButton.addEventListener('click', () => {
            currentIndex = index;
            if (currentTrack !== audioSrc) {
                playTrack(audioSrc);
            } else {
                audio.paused ? audio.play().then(syncIcons) : audio.pause();
            }
        });

        trackList.push({ src: audioSrc, cover });
    });

    // === КНОПКА PLAY/PAUSE В ПЛЕЕРЕ ===
    playPauseBtn.addEventListener('click', () => {
        audio.paused ? audio.play().then(syncIcons) : audio.pause();
    });

    // === СТРЕЛКИ ПЕРЕКЛЮЧЕНИЯ ===
    prevBtn?.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            playTrack(trackList[currentIndex].src);
        }
    });

    nextBtn?.addEventListener('click', () => {
        if (currentIndex < trackList.length - 1) {
            currentIndex++;
            playTrack(trackList[currentIndex].src);
        }
    });

    // === РЕЖИМЫ ВОСПРОИЗВЕДЕНИЯ ===
    modeBtn.addEventListener('click', () => {
        const modes = ['repeat-all', 'repeat-one', 'shuffle',];
        const currentIdx = modes.indexOf(playbackMode);
        playbackMode = modes[(currentIdx + 1) % modes.length];
        updateModeIcon();
        showModeNotification(); // ← работает!
    });

    const updateModeIcon = () => {
        Object.values(modeIcons).forEach(icon => {
            if (icon) icon.style.display = 'none';
        });
        modeBtn.querySelectorAll('svg').forEach(svg => svg.style.opacity = '0.6');

        if (playbackMode === 'repeat-one' && modeIcons.repeatOne) {
            modeIcons.repeatOne.style.display = 'block';
            modeIcons.repeatOne.style.opacity = '1';
        } else if (playbackMode === 'repeat-all' && modeIcons.repeatAll) {
            modeIcons.repeatAll.style.display = 'block';
            modeIcons.repeatAll.style.opacity = '1';
        } else if (playbackMode === 'shuffle' && modeIcons.shuffle) {
            modeIcons.shuffle.style.display = 'block';
            modeIcons.shuffle.style.opacity = '1';
        }
    };

    // === ВОСПРОИЗВЕДЕНИЕ ТРЕКА ===
    const playTrack = (src) => {
        const index = trackList.findIndex(t => t.src === src);
        if (index !== -1) currentIndex = index;

        source.src = src;
        downloadBtn.href = src;
        audio.load();

        audio.play().then(() => {
            currentTrack = src;
            audioPlayer.style.display = 'flex';
            updatePadding(true);
            syncIcons();
        }).catch(err => console.error('Play error:', err));
    };

    // === СИНХРОНИЗАЦИЯ ИКОНОК ===
    const syncIcons = () => {
        const isPlaying = !audio.paused;

        playIcon.style.display = isPlaying ? 'none' : 'block';
        pauseIcon.style.display = isPlaying ? 'block' : 'none';

        document.querySelectorAll('.album-cover').forEach(cover => {
            const src = cover.dataset.src;
            const playIcon = cover.querySelector('.play-icon');
            const pauseIcon = cover.querySelector('.pause-icon');

            if (playIcon && pauseIcon) {
                if (src === currentTrack && isPlaying) {
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'block';
                    cover.classList.add('playing');
                } else {
                    playIcon.style.display = 'block';
                    pauseIcon.style.display = 'none';
                    cover.classList.remove('playing');
                }
            }
        });

        updatePadding(isPlaying);
    };

    // === ПРОГРЕСС ===
    audio.addEventListener('timeupdate', () => {
        if (!isSeeking && audio.duration) {
            const percent = (audio.currentTime / audio.duration) * 100;
            progress.value = percent;
            progress.style.backgroundImage = `linear-gradient(to right, #1DB954 ${percent}%, #6c757d ${percent}%)`;
        }
    });

    progress.addEventListener('input', () => {
        isSeeking = true;
        const percent = progress.value;
        if (audio.duration) audio.currentTime = (percent / 100) * audio.duration;
        progress.style.backgroundImage = `linear-gradient(to right, #1DB954 ${percent}%, #6c757d ${percent}%)`;
    });

    progress.addEventListener('change', () => isSeeking = false);

    // === КОНЕЦ ТРЕКА ===
    audio.addEventListener('ended', () => {
        if (playbackMode === 'repeat-one') {
            audio.currentTime = 0;
            audio.play();
        } else if (playbackMode === 'repeat-all') {
            if (currentIndex < trackList.length - 1) {
                currentIndex++;
                playTrack(trackList[currentIndex].src);
            } else {
                currentIndex = 0;
                playTrack(trackList[0].src);
            }
        } else if (playbackMode === 'shuffle') {
            const randomIndex = Math.floor(Math.random() * trackList.length);
            currentIndex = randomIndex;
            playTrack(trackList[randomIndex].src);
        } else {
            if (currentIndex < trackList.length - 1) {
                currentIndex++;
                playTrack(trackList[currentIndex].src);
            } else {
                audioPlayer.style.display = 'none';
                updatePadding(false);
                currentTrack = null;
                currentIndex = -1;
                progress.value = 0;
                syncIcons();
            }
        }
    });

    // === КЛАВИАТУРА (ПРОБЕЛ) ===
    document.addEventListener('keydown', (e) => {
        if (document.body.classList.contains('modal-open') || 
            ['TEXTAREA', 'INPUT'].includes(document.activeElement.tagName)) return;

        if (e.code === 'Space') {
            e.preventDefault();
            playPauseBtn.click();
        }
    });

    // === ИНИЦИАЛИЗАЦИЯ ===
    updateModeIcon();
    syncIcons();

    // ========================================
    // УВЕДОМЛЕНИЯ — ОБЪЯВЛЯЕМ ПОСЛЕ ВСЕГО
    // ========================================

    const miniIcons = {
        1: `<svg class="icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16v2L10 16 4 10V4z"></path>
                <path d="M4 14h16v2L10 6l-6 6v2z"></path>
            </svg>`,
        2: `<svg class="icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M23 4v6h-6"></path>
                <path d="M1 20v-6h6"></path>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
                <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
            </svg>`,
        3: `<svg class="icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 3h4v4"></path>
                <path d="M21 3l-7 7"></path>
                <path d="M3 21l7-7"></path>
                <path d="M7 21H3v-4"></path>
            </svg>`
    };

    const notification = document.getElementById('notification');

    const showModeNotification = () => {
        const messages = {
            'repeat-all': 'Повтор плейлиста',
            'repeat-one': 'Повтор трека',
            'shuffle': 'Случайный порядок',
        };

        const iconMap = {
            'repeat-all': 1,
            'repeat-one': 2,
            'shuffle': 3,
        };

        const message = messages[playbackMode];
        const iconId = iconMap[playbackMode];

        if (notification && miniIcons[iconId]) {
            notification.innerHTML = miniIcons[iconId] + `<span>${message}</span>`;
            notification.classList.add('show');
            setTimeout(() => notification.classList.remove('show'), 2000);
        }
    };

    // (Если будут отдельные иконки — можно оставить)
    document.querySelectorAll('.icon-button').forEach(btn => {
        btn.addEventListener('click', () => {
            const message = btn.dataset.msg;
            const iconId = btn.dataset.icon;
            if (notification && miniIcons[iconId]) {
                notification.innerHTML = miniIcons[iconId] + `<span>${message}</span>`;
                notification.classList.add('show');
                setTimeout(() => notification.classList.remove('show'), 3000);
            }
        });
    });
});