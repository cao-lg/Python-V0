let weekData = null;

class LearningPlatform {
  constructor() {
    this.currentPageIndex = 0;
    
    this.captionSync = new CaptionSync();
    this.pageRenderer = new PageRenderer();
    this.audioPlayer = new AudioPlayer();
    
    this.init();
  }

  async init() {
    await this.loadWeekData('week1');
    this.setupEventListeners();
    this.renderPage();
  }

  async loadWeekData(week) {
    try {
      const response = await fetch(`data/${week}_with_timestamps.json`);
      if (!response.ok) {
        const fallbackResponse = await fetch(`data/${week}.json`);
        weekData = await fallbackResponse.json();
      } else {
        weekData = await response.json();
      }
    } catch (error) {
      console.error('加载周数据失败:', error);
    }
  }

  setupEventListeners() {
    document.getElementById('prevBtn').addEventListener('click', () => this.goToPrev());
    document.getElementById('nextBtn').addEventListener('click', () => this.goToNext());
    document.getElementById('weekSelect').addEventListener('change', (e) => this.changeWeek(e.target.value));
    document.getElementById('ttsToggle').addEventListener('click', () => this.toggleTTS());
    
    this.captionSync.onCaptionChange = (index, caption) => {
      this.onCaptionChange(index, caption);
    };
    
    this.audioPlayer.onTimeUpdate = (currentTime) => {
      this.captionSync.update(currentTime);
    };
    
    this.audioPlayer.onEnded = () => {
      this.onAudioEnded();
    };
    
    this.audioPlayer.onError = (error) => {
      console.error('音频错误:', error);
    };
  }

  goToPrev() {
    if (this.currentPageIndex > 0) {
      this.stopTTS();
      this.currentPageIndex--;
      this.renderPage();
      this.updateNav();
    }
  }

  goToNext() {
    if (this.currentPageIndex < weekData.pages.length - 1) {
      this.stopTTS();
      this.currentPageIndex++;
      this.renderPage();
      this.updateNav();
    }
  }

  async changeWeek(week) {
    this.stopTTS();
    
    try {
      await this.loadWeekData(week);
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
    this.pageRenderer.render(page, weekData);
    
    if (page.timestamps) {
      this.captionSync.setTimestamps(page.timestamps);
    } else {
      this.captionSync.setTimestamps([]);
    }
  }

  async toggleTTS() {
    const btn = document.getElementById('ttsToggle');
    
    if (btn.textContent === '▶') {
      await this.startTTSWithCaptions();
    } else {
      this.stopTTS();
    }
  }

  async startTTSWithCaptions() {
    const page = weekData.pages[this.currentPageIndex];
    const text = page.speech || '正在讲解当前内容';
    const week = document.getElementById('weekSelect').value;
    
    document.getElementById('captionsContainer').style.display = 'block';
    
    if (page.timestamps && page.timestamps.length > 0) {
      this.captionSync.setTimestamps(page.timestamps);
    } else {
      const lines = text.split(/[，。！？；；]/).filter(line => line.trim());
      const duration = lines.length * 3;
      const timestamps = lines.map((line, i) => ({
        text: line,
        start: (i / lines.length) * duration,
        end: ((i + 1) / lines.length) * duration
      }));
      this.captionSync.setTimestamps(timestamps);
    }

    const audioUrl = `audio/${week}/page${this.currentPageIndex}.mp3`;
    
    try {
      const success = await this.audioPlayer.loadAndPlay(audioUrl);
      if (!success) {
        throw new Error('音频加载失败');
      }
    } catch (error) {
      console.log('切换到浏览器原生语音合成');
      this.audioPlayer.fallbackTTS(text);
    }
  }

  stopTTS() {
    this.audioPlayer.stop();
    this.captionSync.hide();
    this.pageRenderer.clearHighlights();
  }

  onCaptionChange(index, caption) {
    const page = weekData.pages[this.currentPageIndex];
    this.highlightPageContent(page, index, caption);
  }

  highlightPageContent(page, captionIndex, caption) {
    this.pageRenderer.clearHighlights();
    
    const keywords = caption.text;
    
    switch(page.type) {
      case 'objectives':
        this.highlightObjectives(page, captionIndex, keywords);
        break;
      case 'concept':
        this.highlightConcept(page, captionIndex, keywords);
        break;
      case 'features':
        this.highlightFeatures(page, captionIndex, keywords);
        break;
      case 'setup':
        this.highlightSetup(page, captionIndex, keywords);
        break;
      case 'summary':
        this.highlightSummary(page, captionIndex, keywords);
        break;
      default:
        break;
    }
  }

  highlightObjectives(page, captionIndex, keywords) {
    if (captionIndex === 0) {
      this.pageRenderer.highlightElement('[data-section="knowledge"]');
    } else if (captionIndex === 1) {
      const knowledgeIndex = Math.min(Math.floor(captionIndex / 2), page.knowledge.length - 1);
      this.pageRenderer.highlightKnowledge(knowledgeIndex);
    } else if (captionIndex === 2) {
      const skillsIndex = Math.min(Math.floor((captionIndex - 2) / 2), page.skills.length - 1);
      this.pageRenderer.highlightSkills(skillsIndex);
    }
  }

  highlightConcept(page, captionIndex, keywords) {
    const pointIndex = Math.min(Math.floor(captionIndex / 4), page.points.length - 1);
    this.pageRenderer.highlightPoint(pointIndex);
  }

  highlightFeatures(page, captionIndex, keywords) {
    const featureIndex = Math.min(Math.floor(captionIndex / 4), page.features.length - 1);
    this.pageRenderer.highlightFeature(featureIndex);
  }

  highlightSetup(page, captionIndex, keywords) {
    const stepIndex = Math.min(Math.floor(captionIndex / 3), page.steps.length - 1);
    this.pageRenderer.highlightStep(stepIndex);
  }

  highlightSummary(page, captionIndex, keywords) {
    const stats = ['concepts', 'exercises', 'projects', 'codeLines'];
    const statIndex = Math.min(captionIndex, stats.length - 1);
    this.pageRenderer.highlightStat(stats[statIndex]);
    
    if (captionIndex >= page.keyPoints.length) {
      const pointIndex = Math.min(captionIndex - page.keyPoints.length, page.keyPoints.length - 1);
      this.pageRenderer.highlightPoint(pointIndex);
    }
  }

  onAudioEnded() {
    document.getElementById('captionsContainer').style.display = 'none';
    document.getElementById('ttsProgressBar').style.width = '0%';
    document.getElementById('captionProgressBar').style.width = '0%';
    this.pageRenderer.clearHighlights();
  }

  resetToFirstPage() {
    this.stopTTS();
    this.currentPageIndex = 0;
    this.renderPage();
    this.updateNav();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.platform = new LearningPlatform();
});