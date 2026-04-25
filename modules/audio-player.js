class AudioPlayer {
  constructor() {
    this.audioElement = null;
    this.isPlaying = false;
    this.currentAudioDuration = 0;
    this.currentTime = 0;
    this.onTimeUpdate = null;
    this.onEnded = null;
    this.onError = null;
    
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('ttsPrev').addEventListener('click', () => this.skipBackward());
    document.getElementById('ttsNext').addEventListener('click', () => this.skipForward());
  }

  async loadAudio(audioUrl) {
    return new Promise((resolve, reject) => {
      if (this.audioElement) {
        this.audioElement.pause();
        this.audioElement = null;
      }

      this.audioElement = new Audio(audioUrl);
      
      this.audioElement.onloadedmetadata = () => {
        this.currentAudioDuration = this.audioElement.duration;
        this.updateTimeDisplay();
        resolve();
      };

      this.audioElement.ontimeupdate = () => {
        this.currentTime = this.audioElement.currentTime;
        this.updateProgress();
        this.updateTimeDisplay();
        
        if (this.onTimeUpdate) {
          this.onTimeUpdate(this.currentTime);
        }
      };

      this.audioElement.onended = () => {
        this.isPlaying = false;
        this.updatePlayButton();
        if (this.onEnded) {
          this.onEnded();
        }
      };

      this.audioElement.onerror = (error) => {
        console.error('音频加载失败:', error);
        if (this.onError) {
          this.onError(error);
        }
        reject(error);
      };
    });
  }

  play() {
    if (this.audioElement) {
      this.audioElement.play();
      this.isPlaying = true;
      this.updatePlayButton();
    }
  }

  pause() {
    if (this.audioElement) {
      this.audioElement.pause();
      this.isPlaying = false;
      this.updatePlayButton();
    }
  }

  toggle() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  stop() {
    if (this.audioElement) {
      this.audioElement.pause();
      this.audioElement.currentTime = 0;
      this.currentTime = 0;
      this.isPlaying = false;
      this.updatePlayButton();
      this.updateProgress();
      this.updateTimeDisplay();
    }
  }

  seek(time) {
    if (this.audioElement) {
      this.audioElement.currentTime = Math.min(time, this.currentAudioDuration);
      this.currentTime = this.audioElement.currentTime;
    }
  }

  skipBackward(seconds = 5) {
    if (this.audioElement) {
      const newTime = Math.max(0, this.currentTime - seconds);
      this.audioElement.currentTime = newTime;
      this.currentTime = newTime;
    }
  }

  skipForward(seconds = 5) {
    if (this.audioElement) {
      const newTime = Math.min(this.currentAudioDuration, this.currentTime + seconds);
      this.audioElement.currentTime = newTime;
      this.currentTime = newTime;
    }
  }

  updateProgress() {
    const progressBar = document.getElementById('ttsProgressBar');
    if (progressBar && this.currentAudioDuration > 0) {
      const progress = (this.currentTime / this.currentAudioDuration) * 100;
      progressBar.style.width = Math.min(progress, 100) + '%';
    }
  }

  updateTimeDisplay() {
    const timeDisplay = document.getElementById('ttsTime');
    if (timeDisplay) {
      const current = this.formatTime(this.currentTime);
      const duration = this.formatTime(this.currentAudioDuration);
      timeDisplay.textContent = `${current} / ${duration}`;
    }
  }

  updatePlayButton() {
    const btn = document.getElementById('ttsToggle');
    if (btn) {
      btn.textContent = this.isPlaying ? '⏸' : '▶';
    }

    const controls = document.querySelector('.tts-controls');
    if (controls) {
      controls.classList.toggle('playing', this.isPlaying);
    }
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  getCurrentTime() {
    return this.currentTime;
  }

  getDuration() {
    return this.currentAudioDuration;
  }

  getIsPlaying() {
    return this.isPlaying;
  }

  async loadAndPlay(audioUrl) {
    try {
      await this.loadAudio(audioUrl);
      this.play();
      return true;
    } catch (error) {
      console.error('加载并播放音频失败:', error);
      return false;
    }
  }

  async fallbackTTS(text) {
    if (!('speechSynthesis' in window)) {
      console.error('浏览器不支持语音合成');
      return false;
    }

    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 0.9;

    const voices = window.speechSynthesis.getVoices();
    const selectedVoiceId = document.getElementById('voiceSelect')?.value;
    const voice = voices.find(v => v.name === selectedVoiceId) || voices.find(v => v.lang.startsWith('zh'));
    
    if (voice) {
      utterance.voice = voice;
    }

    utterance.onend = () => {
      this.isPlaying = false;
      this.updatePlayButton();
      if (this.onEnded) {
        this.onEnded();
      }
    };

    utterance.onerror = (event) => {
      console.error('浏览器语音合成错误:', event.error);
      this.isPlaying = false;
      this.updatePlayButton();
      if (this.onError) {
        this.onError(event.error);
      }
    };

    window.speechSynthesis.speak(utterance);
    this.isPlaying = true;
    this.updatePlayButton();
    
    return true;
  }
}