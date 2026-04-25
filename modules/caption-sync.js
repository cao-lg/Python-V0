class CaptionSync {
  constructor() {
    this.timestamps = [];
    this.currentIndex = 0;
    this.onCaptionChange = null;
  }

  setTimestamps(timestamps) {
    this.timestamps = timestamps || [];
    this.currentIndex = 0;
    this.updateUI();
  }

  update(currentTime) {
    if (!this.timestamps || this.timestamps.length === 0) return;

    let foundIndex = -1;
    for (let i = 0; i < this.timestamps.length; i++) {
      const caption = this.timestamps[i];
      if (currentTime >= caption.start && currentTime < caption.end) {
        foundIndex = i;
        break;
      }
    }

    if (foundIndex !== -1 && foundIndex !== this.currentIndex) {
      this.currentIndex = foundIndex;
      this.updateUI();
      
      if (this.onCaptionChange) {
        this.onCaptionChange(this.currentIndex, this.timestamps[this.currentIndex]);
      }
    }
  }

  updateUI() {
    const captionLine = document.getElementById('captionLine');
    const captionLineNext = document.getElementById('captionLineNext');
    const captionIndex = document.getElementById('captionIndex');
    const progressBar = document.getElementById('captionProgressBar');

    if (this.timestamps.length === 0) {
      captionLine.textContent = '';
      captionLineNext.textContent = '';
      captionIndex.textContent = '0/0';
      progressBar.style.width = '0%';
      return;
    }

    const currentCaption = this.timestamps[this.currentIndex];
    const nextCaption = this.timestamps[this.currentIndex + 1];

    if (currentCaption) {
      captionLine.textContent = currentCaption.text + '。';
      captionLine.classList.add('active');
    }

    if (nextCaption) {
      captionLineNext.textContent = nextCaption.text + '。';
      captionLineNext.classList.add('active');
    } else {
      captionLineNext.textContent = '';
      captionLineNext.classList.remove('active');
    }

    captionIndex.textContent = `${this.currentIndex + 1}/${this.timestamps.length}`;
    
    const progress = ((this.currentIndex + 1) / this.timestamps.length) * 100;
    progressBar.style.width = progress + '%';
  }

  getCurrentCaption() {
    return this.timestamps[this.currentIndex];
  }

  getCaptionCount() {
    return this.timestamps.length;
  }

  getCurrentIndex() {
    return this.currentIndex;
  }

  seekToCaption(index) {
    if (index >= 0 && index < this.timestamps.length) {
      this.currentIndex = index;
      this.updateUI();
      return this.timestamps[index].start;
    }
    return 0;
  }

  nextCaption() {
    if (this.currentIndex < this.timestamps.length - 1) {
      this.currentIndex++;
      this.updateUI();
      return this.timestamps[this.currentIndex].start;
    }
    return this.timestamps[this.currentIndex]?.end || 0;
  }

  prevCaption() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.updateUI();
      return this.timestamps[this.currentIndex].start;
    }
    return 0;
  }

  show() {
    document.getElementById('captionsContainer').style.display = 'block';
  }

  hide() {
    document.getElementById('captionsContainer').style.display = 'none';
    const captionLine = document.getElementById('captionLine');
    const captionLineNext = document.getElementById('captionLineNext');
    captionLine.classList.remove('active');
    captionLineNext.classList.remove('active');
  }
}