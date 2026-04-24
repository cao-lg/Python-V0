let weekData = null;

class LearningPlatform {
  constructor() {
    this.currentPageIndex = 0;
    this.captionLines = [];
    this.currentCaptionIndex = 0;
    this.ttsInterval = null;
    this.audioContext = null;
    this.audioBuffer = null;
    this.sourceNode = null;
    this.isPlaying = false;
    this.audioStartTime = 0;
    this.currentAudioDuration = 0;
    this.init();
  }

  async init() {
    await this.loadWeekData('week1');
    this.setupEventListeners();
    this.renderPage();
  }

  async loadWeekData(week) {
    try {
      const response = await fetch(`data/${week}.json`);
      weekData = await response.json();
    } catch (error) {
      console.error('加载周数据失败:', error);
    }
  }

  setupEventListeners() {
    document.getElementById('prevBtn').addEventListener('click', () => this.goToPrev());
    document.getElementById('nextBtn').addEventListener('click', () => this.goToNext());
    document.getElementById('weekSelect').addEventListener('change', (e) => this.changeWeek(e.target.value));
    document.getElementById('ttsToggle').addEventListener('click', () => this.toggleTTS());
  }

  goToPrev() {
    if (this.currentPageIndex > 0) {
      this.currentPageIndex--;
      this.renderPage();
      this.updateNav();
    }
  }

  goToNext() {
    if (this.currentPageIndex < weekData.pages.length - 1) {
      this.currentPageIndex++;
      this.renderPage();
      this.updateNav();
    }
  }

  async changeWeek(week) {
    try {
      const response = await fetch(`data/${week}.json`);
      weekData = await response.json();
      this.currentPageIndex = 0;
      this.renderPage();
      this.updateNav();
    } catch (error) {
      console.error('加载周数据失败:', error);
    }
  }

  updateNav() {
    const total = weekData.pages.length;
    document.getElementById('pagination').textContent = `${this.currentPageIndex + 1} / ${total}`;
    document.getElementById('prevBtn').disabled = this.currentPageIndex === 0;
    document.getElementById('nextBtn').disabled = this.currentPageIndex === total - 1;
  }

  renderPage() {
    const page = weekData.pages[this.currentPageIndex];
    const container = document.getElementById('slideContent');
    
    container.innerHTML = this.renderPageContent(page);
    container.style.animation = 'none';
    setTimeout(() => {
      container.style.animation = 'fadeIn 0.6s ease-out';
    }, 50);
  }

  renderPageContent(page) {
    switch(page.type) {
      case 'cover':
        return this.renderCover(page);
      case 'objectives':
        return this.renderObjectives(page);
      case 'concept':
        return this.renderConcept(page);
      case 'features':
        return this.renderFeatures(page);
      case 'setup':
        return this.renderSetup(page);
      case 'code':
        return this.renderCode(page);
      case 'summary':
        return this.renderSummary(page);
      case 'ending':
        return this.renderEnding(page);
      default:
        return '<p>内容加载中...</p>';
    }
  }

  renderCover(page) {
    return `
      <div class="cover-page">
        <div class="cover-icon">🚀</div>
        <h1 class="cover-title">Python 零基础学习平台</h1>
        <p class="cover-subtitle">第${weekData.week}周：${weekData.title}</p>
        <div class="cover-badge">${page.title}</div>
        <div class="progress-bar-container">
          <div class="progress-bar"></div>
        </div>
        <p style="color: var(--text-muted); font-size: 14px; margin-top: 16px;">准备好开始学习了吗？点击下一页</p>
      </div>
    `;
  }

  renderObjectives(page) {
    const knowledgeItems = page.knowledge.map(item => `<li>${item}</li>`).join('');
    const skillsItems = page.skills.map(item => `<li>${item}</li>`).join('');
    
    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">📚 ${page.title}</h2>
        </div>
        <div class="cards-grid">
          <div class="card highlight-card">
            <div class="card-icon">💡</div>
            <h3 class="card-title">知识目标</h3>
            <ul class="card-list">${knowledgeItems}</ul>
          </div>
          <div class="card">
            <div class="card-icon">🎯</div>
            <h3 class="card-title">能力目标</h3>
            <ul class="card-list">${skillsItems}</ul>
          </div>
        </div>
      </div>
    `;
  }

  renderConcept(page) {
    const pointsHTML = page.points.map(point => `
      <div class="feature-item">
        <div class="feature-icon purple">${point.icon}</div>
        <div class="feature-content">
          <h3>${point.title}</h3>
          <p>${point.desc}</p>
        </div>
      </div>
    `).join('');

    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">🔍 ${page.title}</h2>
          <p class="slide-subtitle">${page.subtitle}</p>
        </div>
        <div style="display: flex; flex-direction: column; gap: 16px;">
          ${pointsHTML}
        </div>
      </div>
    `;
  }

  renderFeatures(page) {
    const colors = ['blue', 'purple', 'green', 'yellow'];
    const featuresHTML = page.features.map((feature, index) => `
      <div class="card">
        <div class="card-icon">${feature.icon}</div>
        <h3 class="card-title">${feature.title}</h3>
        <p class="card-text">${feature.desc}</p>
      </div>
    `).join('');

    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">✨ ${page.title}</h2>
        </div>
        <div class="cards-grid">
          ${featuresHTML}
        </div>
      </div>
    `;
  }

  renderSetup(page) {
    const stepsHTML = page.steps.map(step => `
      <div class="feature-item">
        <div class="feature-icon blue">${step.number}</div>
        <div class="feature-content">
          <h3>${step.title}</h3>
          <p>${step.desc}</p>
        </div>
      </div>
    `).join('');

    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">🛠️ ${page.title}</h2>
        </div>
        <div style="display: flex; flex-direction: column; gap: 16px;">
          ${stepsHTML}
        </div>
      </div>
    `;
  }

  renderCode(page) {
    const escapedCode = page.code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">💻 ${page.title}</h2>
        </div>
        <div class="two-column">
          <div>
            <h3 style="color: var(--text-secondary); font-size: 14px; margin-bottom: 16px;">代码</h3>
            <div class="code-block">
              <pre><code>${escapedCode}</code></pre>
            </div>
          </div>
          <div>
            <h3 style="color: var(--text-secondary); font-size: 14px; margin-bottom: 16px;">运行结果</h3>
            <div class="code-block" style="min-height: 150px;">
              <pre>${page.output}</pre>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderSummary(page) {
    const keyPointsHTML = page.keyPoints.map(point => `<li>${point}</li>`).join('');
    
    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">📋 ${page.title}</h2>
        </div>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">${page.stats.concepts}</div>
            <div class="stat-label">核心概念</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${page.stats.exercises}</div>
            <div class="stat-label">课堂练习</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${page.stats.projects}</div>
            <div class="stat-label">项目任务</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${page.stats.codeLines}</div>
            <div class="stat-label">代码行数</div>
          </div>
        </div>
        <div class="divider"></div>
        <div class="card">
          <h3 class="card-title">📝 本周要点</h3>
          <ul class="card-list">${keyPointsHTML}</ul>
        </div>
      </div>
    `;
  }

  renderEnding(page) {
    return `
      <div class="footer-page">
        <div class="footer-icon">🎉</div>
        <h2 class="footer-title">${page.message}</h2>
        <p class="footer-text">${page.nextStep}</p>
        <button class="cta-btn" onclick="window.platform.resetToFirstPage()">重新学习</button>
      </div>
    `;
  }

  async toggleTTS() {
    const btn = document.getElementById('ttsToggle');
    if (btn.textContent === '▶') {
      btn.textContent = '⏸';
      await this.startTTSWithCaptions();
    } else {
      btn.textContent = '▶';
      this.stopTTSWithCaptions();
    }
  }

  async startTTSWithCaptions() {
    const page = weekData.pages[this.currentPageIndex];
    const text = page.speech || '正在讲解当前内容';
    
    this.captionLines = text.split(/[，。！？；；]/).filter(line => line.trim());
    this.currentCaptionIndex = 0;
    
    document.getElementById('captionsContainer').style.display = 'block';
    this.showCurrentCaption();

    try {
      const voiceSelect = document.getElementById('voiceSelect');
      const selectedVoice = voiceSelect.value;
      
      const tts = new EdgeTTSBrowser({
        text: text,
        voice: selectedVoice,
        rate: '+0%',
        pitch: '+0Hz',
        volume: '+0%'
      });

      const audioBlob = await tts.ttsToFile();
      this.currentAudioDuration = await this.getAudioDuration(audioBlob);
      
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const arrayBuffer = await audioBlob.arrayBuffer();
      this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      
      this.playAudio();
    } catch (error) {
      console.error('TTS合成失败:', error);
      this.fallbackTTS(text);
    }
  }

  getAudioDuration(blob) {
    return new Promise((resolve) => {
      const audio = new Audio();
      audio.onloadedmetadata = () => {
        resolve(audio.duration);
        URL.revokeObjectURL(audio.src);
      };
      audio.onerror = () => {
        resolve(10);
        URL.revokeObjectURL(audio.src);
      };
      audio.src = URL.createObjectURL(blob);
    });
  }

  playAudio() {
    if (!this.audioBuffer || !this.audioContext) return;
    
    this.sourceNode = this.audioContext.createBufferSource();
    this.sourceNode.buffer = this.audioBuffer;
    this.sourceNode.connect(this.audioContext.destination);
    
    this.sourceNode.onended = () => {
      this.onAudioEnded();
    };
    
    this.audioStartTime = this.audioContext.currentTime;
    this.isPlaying = true;
    this.sourceNode.start();
    
    this.updateProgressLoop();
  }

  updateProgressLoop() {
    if (!this.isPlaying) return;
    
    const currentTime = this.audioContext.currentTime - this.audioStartTime;
    const progress = Math.min((currentTime / this.currentAudioDuration) * 100, 100);
    
    document.getElementById('ttsProgressBar').style.width = progress + '%';
    
    const captionProgress = ((this.currentCaptionIndex + progress / 100) / this.captionLines.length) * 100;
    document.getElementById('captionProgressBar').style.width = captionProgress + '%';
    
    const expectedCaptionIndex = Math.floor((progress / 100) * this.captionLines.length);
    if (expectedCaptionIndex !== this.currentCaptionIndex && expectedCaptionIndex < this.captionLines.length) {
      this.currentCaptionIndex = expectedCaptionIndex;
      this.showCurrentCaption();
    }
    
    if (progress < 100) {
      requestAnimationFrame(() => this.updateProgressLoop());
    }
  }

  onAudioEnded() {
    this.isPlaying = false;
    document.getElementById('ttsToggle').textContent = '▶';
    document.getElementById('captionsContainer').style.display = 'none';
    document.getElementById('ttsProgressBar').style.width = '0%';
    document.getElementById('captionProgressBar').style.width = '0%';
  }

  fallbackTTS(text) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      
      const voices = window.speechSynthesis.getVoices();
      const selectedVoiceId = document.getElementById('voiceSelect').value;
      const voice = voices.find(v => v.name === selectedVoiceId) || voices.find(v => v.lang.startsWith('zh'));
      
      if (voice) {
        utterance.voice = voice;
      }
      
      utterance.rate = 0.9;
      utterance.onend = () => {
        this.isPlaying = false;
        document.getElementById('ttsToggle').textContent = '▶';
      };
      
      window.speechSynthesis.speak(utterance);
    }
  }

  showCurrentCaption() {
    const captionElement = document.getElementById('captionLine');
    if (this.captionLines[this.currentCaptionIndex]) {
      captionElement.textContent = this.captionLines[this.currentCaptionIndex].trim();
      captionElement.classList.add('active');
    }
  }

  stopTTSWithCaptions() {
    this.isPlaying = false;
    
    if (this.sourceNode) {
      try {
        this.sourceNode.stop();
      } catch (e) {
        console.log('Audio already stopped');
      }
      this.sourceNode = null;
    }
    
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    document.getElementById('ttsProgressBar').style.width = '0%';
    document.getElementById('captionProgressBar').style.width = '0%';
    document.getElementById('captionsContainer').style.display = 'none';
    document.getElementById('captionLine').classList.remove('active');
  }

  resetToFirstPage() {
    this.stopTTSWithCaptions();
    this.currentPageIndex = 0;
    this.renderPage();
    this.updateNav();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.platform = new LearningPlatform();
});