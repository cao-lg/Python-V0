class PageRenderer {
  constructor() {
    this.container = document.getElementById('slideContent');
    this.highlightedElements = [];
  }

  render(page, weekData) {
    this.clearHighlights();
    
    this.container.innerHTML = this.renderPageContent(page, weekData);
    
    this.container.style.animation = 'none';
    setTimeout(() => {
      this.container.style.animation = 'fadeIn 0.6s ease-out';
    }, 50);
  }

  renderPageContent(page, weekData) {
    switch(page.type) {
      case 'cover':
        return this.renderCover(page, weekData);
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

  renderCover(page, weekData) {
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
    const knowledgeItems = page.knowledge.map((item, index) => 
      `<li data-item-index="${index}" class="knowledge-item">${item}</li>`
    ).join('');
    const skillsItems = page.skills.map((item, index) => 
      `<li data-item-index="${index}" class="skills-item">${item}</li>`
    ).join('');
    
    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">📚 ${page.title}</h2>
        </div>
        <div class="cards-grid">
          <div class="card highlight-card" data-section="knowledge">
            <div class="card-icon">💡</div>
            <h3 class="card-title">知识目标</h3>
            <ul class="card-list">${knowledgeItems}</ul>
          </div>
          <div class="card" data-section="skills">
            <div class="card-icon">🎯</div>
            <h3 class="card-title">能力目标</h3>
            <ul class="card-list">${skillsItems}</ul>
          </div>
        </div>
      </div>
    `;
  }

  renderConcept(page) {
    const pointsHTML = page.points.map((point, index) => `
      <div class="feature-item" data-point-index="${index}">
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
        <div class="concept-container" style="display: flex; flex-direction: column; gap: 16px;">
          ${pointsHTML}
        </div>
      </div>
    `;
  }

  renderFeatures(page) {
    const featuresHTML = page.features.map((feature, index) => `
      <div class="card feature-card" data-feature-index="${index}">
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
    const stepsHTML = page.steps.map((step, index) => `
      <div class="feature-item setup-step" data-step-index="${index}">
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
        <div class="setup-container" style="display: flex; flex-direction: column; gap: 16px;">
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
          <div class="code-panel" data-panel="code">
            <h3 style="color: var(--text-secondary); font-size: 14px; margin-bottom: 16px;">代码</h3>
            <div class="code-block">
              <pre><code>${escapedCode}</code></pre>
            </div>
          </div>
          <div class="code-panel" data-panel="output">
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
    const keyPointsHTML = page.keyPoints.map((point, index) => 
      `<li data-point-index="${index}" class="summary-item">${point}</li>`
    ).join('');
    
    return `
      <div>
        <div class="slide-header">
          <h2 class="slide-title">📋 ${page.title}</h2>
        </div>
        <div class="stats-grid">
          <div class="stat-card" data-stat="concepts">
            <div class="stat-value">${page.stats.concepts}</div>
            <div class="stat-label">核心概念</div>
          </div>
          <div class="stat-card" data-stat="exercises">
            <div class="stat-value">${page.stats.exercises}</div>
            <div class="stat-label">课堂练习</div>
          </div>
          <div class="stat-card" data-stat="projects">
            <div class="stat-value">${page.stats.projects}</div>
            <div class="stat-label">项目任务</div>
          </div>
          <div class="stat-card" data-stat="codeLines">
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

  highlightElement(selector, options = {}) {
    this.clearHighlights();
    
    const element = document.querySelector(selector);
    if (element) {
      element.classList.add('highlighted');
      this.highlightedElements.push(element);
      
      if (options.scrollIntoView !== false) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }

  highlightStep(index) {
    this.clearHighlights();
    const step = document.querySelector(`[data-step-index="${index}"]`);
    if (step) {
      step.classList.add('highlighted');
      this.highlightedElements.push(step);
    }
  }

  highlightPoint(index) {
    this.clearHighlights();
    const point = document.querySelector(`[data-point-index="${index}"]`);
    if (point) {
      point.classList.add('highlighted');
      this.highlightedElements.push(point);
    }
  }

  highlightFeature(index) {
    this.clearHighlights();
    const feature = document.querySelector(`[data-feature-index="${index}"]`);
    if (feature) {
      feature.classList.add('highlighted');
      this.highlightedElements.push(feature);
    }
  }

  highlightKnowledge(index) {
    this.clearHighlights();
    const item = document.querySelector(`.knowledge-item[data-item-index="${index}"]`);
    if (item) {
      item.classList.add('highlighted');
      this.highlightedElements.push(item);
    }
  }

  highlightSkills(index) {
    this.clearHighlights();
    const item = document.querySelector(`.skills-item[data-item-index="${index}"]`);
    if (item) {
      item.classList.add('highlighted');
      this.highlightedElements.push(item);
    }
  }

  highlightStat(statName) {
    this.clearHighlights();
    const stat = document.querySelector(`[data-stat="${statName}"]`);
    if (stat) {
      stat.classList.add('highlighted');
      this.highlightedElements.push(stat);
    }
  }

  clearHighlights() {
    this.highlightedElements.forEach(el => el.classList.remove('highlighted'));
    this.highlightedElements = [];
  }
}