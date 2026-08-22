const state = {
  currentEngine: 'non-ai', 
  rawFile: null,
  originalImage: null, 
  enhancedSrc: null, 
  presets: {},
  modelsData: {},
  activePresetKey: 'esmagic',
  sliderSplitPos: 50, 
  viewMode: 'split', 
  isHoldingOriginal: false,
  isProcessing: false,
  apiKeys: {
    replicate: localStorage.getItem('webmagic_key_replicate') || '',
    stability: localStorage.getItem('webmagic_key_stability') || '',
    huggingface: localStorage.getItem('webmagic_key_hf') || '',
    openai: localStorage.getItem('webmagic_key_openai') || ''
  }
};

const elements = {
  
  tabNonAi: document.getElementById('tab-non-ai'),
  tabAi: document.getElementById('tab-ai'),
  sectionNonAi: document.getElementById('section-non-ai'),
  sectionAi: document.getElementById('section-ai'),
  btnOpenApiModal: document.getElementById('btn-open-api-modal'),
  btnShowHelp: document.getElementById('btn-show-help'),
  keyIndicator: document.getElementById('key-indicator'),

  presetsContainer: document.getElementById('presets-container'),
  btnResetSliders: document.getElementById('btn-reset-sliders'),
  sliderSharpness: document.getElementById('slider-sharpness'),
  sliderClahe: document.getElementById('slider-clahe'),
  sliderDenoise: document.getElementById('slider-denoise'),
  sliderVibrance: document.getElementById('slider-vibrance'),
  sliderContrast: document.getElementById('slider-contrast'),
  sliderWarmth: document.getElementById('slider-warmth'),
  sliderScale: document.getElementById('slider-scale'),

  valSharpness: document.getElementById('val-sharpness'),
  valClahe: document.getElementById('val-clahe'),
  valDenoise: document.getElementById('val-denoise'),
  valVibrance: document.getElementById('val-vibrance'),
  valContrast: document.getElementById('val-contrast'),
  valWarmth: document.getElementById('val-warmth'),
  valScale: document.getElementById('val-scale'),

  aiProviderSelect: document.getElementById('ai-provider-select'),
  aiModelSelect: document.getElementById('ai-model-select'),
  aiModelDesc: document.getElementById('ai-model-desc'),
  aiModelBadge: document.getElementById('ai-model-badge'),
  aiModelSpec: document.getElementById('ai-model-spec'),
  aiScaleSelect: document.getElementById('ai-scale-select'),
  aiFaceEnhance: document.getElementById('ai-face-enhance'),
  aiCustomPrompt: document.getElementById('ai-custom-prompt'),
  aiKeyReminderBox: document.getElementById('ai-key-reminder-box'),
  currentProviderName: document.getElementById('current-provider-name'),
  btnQuickConfigKey: document.getElementById('btn-quick-config-key'),

  btnEnhanceMain: document.getElementById('btn-enhance-main'),
  btnEnhanceText: document.getElementById('btn-enhance-text'),
  enhanceSpinner: document.getElementById('enhance-spinner'),
  exportFormat: document.getElementById('export-format'),
  btnDownload: document.getElementById('btn-download'),

  dropzone: document.getElementById('dropzone'),
  fileInput: document.getElementById('file-input'),
  btnBrowseFile: document.getElementById('btn-browse-file'),
  btnLoadSample: document.getElementById('btn-load-sample'),
  viewportActive: document.getElementById('viewport-active'),
  btnChangeImage: document.getElementById('btn-change-image'),
  btnFullscreen: document.getElementById('btn-fullscreen'),

  comparisonStage: document.getElementById('comparison-stage'),
  imageWrapper: document.getElementById('image-wrapper'),
  imgEnhanced: document.getElementById('img-enhanced'),
  imgOriginal: document.getElementById('img-original'),
  beforeContainer: document.getElementById('before-container'),
  sliderHandle: document.getElementById('slider-handle'),
  statResOrig: document.getElementById('stat-res-orig'),
  statResEnhanced: document.getElementById('stat-res-enhanced'),

  sideBySideContainer: document.getElementById('side-by-side-container'),
  imgSideOrig: document.getElementById('img-side-orig'),
  imgSideEnhanced: document.getElementById('img-side-enhanced'),

  modeSplit: document.getElementById('mode-split'),
  modeSide: document.getElementById('mode-side'),
  modeOriginalHold: document.getElementById('mode-original-hold'),

  processingOverlay: document.getElementById('processing-overlay'),
  processStatusTitle: document.getElementById('process-status-title'),
  processStatusDesc: document.getElementById('process-status-desc'),

  apiModal: document.getElementById('api-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  btnSaveKeys: document.getElementById('btn-save-keys'),
  btnClearKeys: document.getElementById('btn-clear-keys'),
  keyReplicate: document.getElementById('key-replicate'),
  keyStability: document.getElementById('key-stability'),
  keyHf: document.getElementById('key-hf'),
  keyOpenai: document.getElementById('key-openai'),

  helpModal: document.getElementById('help-modal'),
  btnCloseHelp: document.getElementById('btn-close-help'),
  btnCloseHelpAction: document.getElementById('btn-close-help-action'),

  toastContainer: document.getElementById('toast-container')
};

async function initApp() {
  setupEventListeners();
  updateKeyIndicator();
  await loadPresets();
  await loadAiModels();
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'ph-info';
  if (type === 'success') icon = 'ph-check-circle';
  if (type === 'error') icon = 'ph-warning-circle';

  toast.innerHTML = `<i class="ph-bold ${icon}"></i><span>${message}</span>`;
  elements.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

const DEFAULT_PRESETS = {
  "esmagic": {
    "name": " EsMagic (Autonomous Pro)",
    "description": "Our signature all-in-one model: auto noise removal, dynamic shadow/highlight recovery, color harmonization, and edge crispening.",
    "params": {
      "clahe_clip": 2.6, "clahe_grid": 8, "sharpness": 1.5, "saturation": 1.3,
      "denoise": 14, "contrast": 1.18, "brightness": 1.06, "vibrance": 1.35, "warmth": 0, "gamma": 1.05, "scale": 1.0
    }
  },
  "auto_vibrant": {
    "name": "Auto Vibrant",
    "description": "Smart dynamic range boost, vivid colors, and subtle micro-sharpening.",
    "params": {
      "clahe_clip": 2.2, "clahe_grid": 8, "sharpness": 1.4, "saturation": 1.35,
      "denoise": 10, "contrast": 1.15, "brightness": 1.05, "vibrance": 1.3, "warmth": 0, "gamma": 1.0, "scale": 1.0
    }
  },
  "crisp_portrait": {
    "name": "Crisp Portrait",
    "description": "Smooth skin tones with edge-preserving bilateral filtering and selective eye/hair sharpening.",
    "params": {
      "clahe_clip": 1.5, "clahe_grid": 8, "sharpness": 1.6, "saturation": 1.1,
      "denoise": 22, "contrast": 1.1, "brightness": 1.08, "vibrance": 1.15, "warmth": 4.0, "gamma": 0.98, "scale": 1.0
    }
  },
  "night_restore": {
    "name": "Night Shot Restore",
    "description": "Deep shadow recovery, aggressive multi-stage chroma denoising, and balanced contrast.",
    "params": {
      "clahe_clip": 3.8, "clahe_grid": 12, "sharpness": 1.2, "saturation": 1.2,
      "denoise": 35, "contrast": 1.25, "brightness": 1.25, "vibrance": 1.2, "warmth": -2.0, "gamma": 1.2, "scale": 1.0
    }
  },
  "clarify_document": {
    "name": "Document & Scan Clarify",
    "description": "High-contrast text clarification, shadow removal, and background whitening.",
    "params": {
      "clahe_clip": 4.5, "clahe_grid": 16, "sharpness": 2.5, "saturation": 0.8,
      "denoise": 15, "contrast": 1.5, "brightness": 1.15, "vibrance": 0.9, "warmth": 0.0, "gamma": 0.9, "scale": 1.0
    }
  },
  "vintage_cleanup": {
    "name": "Vintage Photo Restore",
    "description": "Restores faded historical photographs, fixes yellowing/fading, and sharpens soft film scans.",
    "params": {
      "clahe_clip": 2.8, "clahe_grid": 8, "sharpness": 1.8, "saturation": 1.25,
      "denoise": 25, "contrast": 1.2, "brightness": 1.05, "vibrance": 1.2, "warmth": -5.0, "gamma": 1.05, "scale": 1.0
    }
  },
  "super_sharp_2x": {
    "name": "Super Sharp 2x (Non-AI)",
    "description": "High-quality Lanczos-4 upscaling combined with unsharp masking and detail enhancement.",
    "params": {
      "clahe_clip": 2.0, "clahe_grid": 8, "sharpness": 1.7, "saturation": 1.1,
      "denoise": 12, "contrast": 1.1, "brightness": 1.0, "vibrance": 1.1, "warmth": 0.0, "gamma": 1.0, "scale": 2.0
    }
  }
};

const DEFAULT_MODELS = {
  "replicate": {
    "name": "Replicate AI",
    "models": {
      "real-esrgan": {
        "name": "Real-ESRGAN (General Super-Resolution)",
        "description": "State-of-the-art general super-resolution 2x/4x/8x upscaling.",
        "default_scale": 4
      },
      "gfpgan": {
        "name": "GFPGAN (TencentARC Face Restoration)",
        "description": "Practical face restoration algorithm for vintage & degraded portrait photos.",
        "default_scale": 2
      },
      "codeformer": {
        "name": "CodeFormer (Robust Face & Detail Restorer)",
        "description": "Codebook-based face reconstruction and artifact removal.",
        "default_scale": 2
      }
    }
  },
  "stability": {
    "name": "Stability AI",
    "models": {
      "creative-upscale": {
        "name": "Stability Creative Upscaler",
        "description": "Generative hallucination upscaler up to 4K resolution.",
        "default_scale": 4
      },
      "conservative-upscale": {
        "name": "Stability Conservative Upscaler",
        "description": "High-fidelity preservation upscaler with minimal distortion.",
        "default_scale": 4
      },
      "fast-upscale": {
        "name": "Stability Fast Upscale (ESRGAN)",
        "description": "Rapid 4x super-resolution.",
        "default_scale": 4
      }
    }
  },
  "huggingface": {
    "name": "Hugging Face Inference",
    "models": {
      "swinir": {
        "name": "SwinIR Super-Resolution",
        "description": "Transformer-based classical super-resolution.",
        "default_scale": 2
      },
      "restormer": {
        "name": "Restormer Image Restoration",
        "description": "Transformer model for real-world denoising and deblurring.",
        "default_scale": 1
      }
    }
  }
};

async function loadPresets() {
  try {
    const res = await fetch('/api/presets');
    const contentType = res.headers.get('content-type') || '';
    if (res.ok && contentType.includes('application/json')) {
      const data = await res.json();
      state.presets = data.presets || DEFAULT_PRESETS;
    } else {
      state.presets = DEFAULT_PRESETS;
    }
  } catch (err) {
    state.presets = DEFAULT_PRESETS;
  }
  renderPresets();
}

async function loadAiModels() {
  try {
    const res = await fetch('/api/models');
    const contentType = res.headers.get('content-type') || '';
    if (res.ok && contentType.includes('application/json')) {
      const data = await res.json();
      state.modelsData = data.providers || DEFAULT_MODELS;
    } else {
      state.modelsData = DEFAULT_MODELS;
    }
  } catch (err) {
    state.modelsData = DEFAULT_MODELS;
  }
  updateAiModelOptions();
}

function updateAiModelOptions() {
  const provider = elements.aiProviderSelect.value;
  const pInfo = state.modelsData[provider];
  if (!pInfo) return;

  elements.currentProviderName.textContent = pInfo.name;
  elements.aiModelSelect.innerHTML = '';

  const models = pInfo.models || {};
  Object.keys(models).forEach(mKey => {
    const opt = document.createElement('option');
    opt.value = mKey;
    opt.textContent = models[mKey].name;
    elements.aiModelSelect.appendChild(opt);
  });

  updateAiModelDescription();
  checkProviderKeyStatus();
}

function updateAiModelDescription() {
  const provider = elements.aiProviderSelect.value;
  const modelKey = elements.aiModelSelect.value;
  const modelInfo = state.modelsData[provider]?.models?.[modelKey];
  if (modelInfo) {
    elements.aiModelDesc.textContent = modelInfo.description;
    elements.aiModelBadge.textContent = provider.toUpperCase();
    if (modelInfo.default_scale) {
      elements.aiScaleSelect.value = modelInfo.default_scale.toString();
      elements.aiModelSpec.textContent = `Default Scale: ${modelInfo.default_scale}x`;
    } else {
      elements.aiModelSpec.textContent = 'Multi-Scale';
    }
  }
}

function checkProviderKeyStatus() {
  const provider = elements.aiProviderSelect.value;
  const key = state.apiKeys[provider];
  if (key && key.trim().length > 0) {
    elements.aiKeyReminderBox.classList.add('hidden');
  } else {
    elements.aiKeyReminderBox.classList.remove('hidden');
  }
}

function updateKeyIndicator() {
  const hasAny = Object.values(state.apiKeys).some(k => k && k.trim().length > 0);
  elements.keyIndicator.classList.toggle('active', hasAny);
}

let rAFSync = null;
let rAFFilter = null;

function syncImageDimensions() {
  if (!state.originalImage) return;
  if (rAFSync) cancelAnimationFrame(rAFSync);
  rAFSync = requestAnimationFrame(() => {
    const rect = elements.imgEnhanced.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      elements.imgOriginal.style.width = `${rect.width}px`;
      elements.imgOriginal.style.height = `${rect.height}px`;
    }
  });
}

function applyLiveFilters() {
  if (!state.originalImage || state.currentEngine === 'ai') return;
  if (rAFFilter) cancelAnimationFrame(rAFFilter);
  rAFFilter = requestAnimationFrame(() => {
    const contrast = parseFloat(elements.sliderContrast.value);
    const vibrance = parseFloat(elements.sliderVibrance.value);
    const brightness = 1.0;
    const warmth = parseInt(elements.sliderWarmth.value);

    let filterStr = `contrast(${contrast}) saturate(${vibrance}) brightness(${brightness})`;
    
    if (warmth > 0) {
      filterStr += ` sepia(${warmth * 1.5}%)`;
    } else if (warmth < 0) {
      filterStr += ` hue-rotate(${warmth * 0.8}deg)`;
    }

    elements.imgEnhanced.style.filter = filterStr;
    if (elements.imgSideEnhanced) {
      elements.imgSideEnhanced.style.filter = filterStr;
    }
  });
}

function setupEventListeners() {
  
  elements.tabNonAi.addEventListener('click', () => switchEngine('non-ai'));
  elements.tabAi.addEventListener('click', () => switchEngine('ai'));

  ['dragenter', 'dragover'].forEach(name => {
    elements.dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      elements.dropzone.classList.add('dragover');
    });
  });
  ['dragleave', 'drop'].forEach(name => {
    elements.dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      elements.dropzone.classList.remove('dragover');
    });
  });
  elements.dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  elements.btnBrowseFile.addEventListener('click', () => elements.fileInput.click());
  elements.fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  });

  elements.btnLoadSample.addEventListener('click', loadSampleImage);
  elements.btnChangeImage.addEventListener('click', () => elements.fileInput.click());

  [
    elements.sliderSharpness,
    elements.sliderClahe,
    elements.sliderDenoise,
    elements.sliderVibrance,
    elements.sliderContrast,
    elements.sliderWarmth,
    elements.sliderScale
  ].forEach(slider => {
    slider.addEventListener('input', () => {
      updateSliderLabels();
      applyLiveFilters();
    });
  });

  elements.btnResetSliders.addEventListener('click', () => {
    applyPreset('auto_vibrant');
  });

  elements.aiProviderSelect.addEventListener('change', () => {
    updateAiModelOptions();
  });
  elements.aiModelSelect.addEventListener('change', () => {
    updateAiModelDescription();
  });

  setupComparisonSliderEvents();

  elements.btnEnhanceMain.addEventListener('click', handleEnhanceClick);

  elements.btnDownload.addEventListener('click', downloadEnhancedImage);

  elements.modeSplit.addEventListener('click', () => setViewMode('split'));
  elements.modeSide.addEventListener('click', () => setViewMode('side'));
  
  elements.modeOriginalHold.addEventListener('mousedown', () => toggleHoldOriginal(true));
  elements.modeOriginalHold.addEventListener('mouseup', () => toggleHoldOriginal(false));
  elements.modeOriginalHold.addEventListener('mouseleave', () => toggleHoldOriginal(false));
  elements.modeOriginalHold.addEventListener('touchstart', (e) => { e.preventDefault(); toggleHoldOriginal(true); });
  elements.modeOriginalHold.addEventListener('touchend', (e) => { e.preventDefault(); toggleHoldOriginal(false); });

  window.addEventListener('resize', syncImageDimensions);

  elements.btnFullscreen.addEventListener('click', toggleFullscreen);

  elements.btnOpenApiModal.addEventListener('click', openApiModal);
  elements.btnQuickConfigKey.addEventListener('click', openApiModal);
  elements.btnCloseModal.addEventListener('click', closeApiModal);
  elements.apiModal.addEventListener('click', (e) => {
    if (e.target === elements.apiModal) closeApiModal();
  });
  elements.btnSaveKeys.addEventListener('click', saveApiKeys);
  elements.btnClearKeys.addEventListener('click', clearApiKeys);

  elements.btnShowHelp.addEventListener('click', openHelpModal);
  elements.btnCloseHelp.addEventListener('click', closeHelpModal);
  elements.btnCloseHelpAction.addEventListener('click', closeHelpModal);
  elements.helpModal.addEventListener('click', (e) => {
    if (e.target === elements.helpModal) closeHelpModal();
  });

  document.querySelectorAll('.btn-toggle-eye').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
      }
    });
  });

  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !e.repeat && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'SELECT') {
      e.preventDefault();
      toggleHoldOriginal(true);
    }
  });
  window.addEventListener('keyup', (e) => {
    if (e.code === 'Space') {
      toggleHoldOriginal(false);
    }
  });
}

function switchEngine(mode) {
  state.currentEngine = mode;
  elements.tabNonAi.classList.toggle('active', mode === 'non-ai');
  elements.tabAi.classList.toggle('active', mode === 'ai');
  elements.tabNonAi.setAttribute('aria-selected', mode === 'non-ai');
  elements.tabAi.setAttribute('aria-selected', mode === 'ai');

  elements.sectionNonAi.classList.toggle('hidden', mode !== 'non-ai');
  elements.sectionAi.classList.toggle('hidden', mode !== 'ai');

  if (mode === 'non-ai') {
    elements.btnEnhanceText.textContent = 'Render High-Quality HD';
    applyLiveFilters();
  } else {
    elements.btnEnhanceText.textContent = 'Run AI Super-Resolution';
    elements.imgEnhanced.style.filter = 'none';
    if (elements.imgSideEnhanced) elements.imgSideEnhanced.style.filter = 'none';
    checkProviderKeyStatus();
  }
}

function updateSliderLabels() {
  elements.valSharpness.textContent = `${parseFloat(elements.sliderSharpness.value).toFixed(1)}x`;
  elements.valClahe.textContent = `${parseFloat(elements.sliderClahe.value).toFixed(1)}`;
  elements.valDenoise.textContent = `${parseInt(elements.sliderDenoise.value)}`;
  elements.valVibrance.textContent = `${parseFloat(elements.sliderVibrance.value).toFixed(2)}x`;
  elements.valContrast.textContent = `${parseFloat(elements.sliderContrast.value).toFixed(2)}x`;
  
  const warmthVal = parseInt(elements.sliderWarmth.value);
  elements.valWarmth.textContent = warmthVal > 0 ? `+${warmthVal} Warm` : warmthVal < 0 ? `${warmthVal} Cool` : '0 Neutral';

  const scaleVal = parseFloat(elements.sliderScale.value);
  elements.valScale.textContent = scaleVal > 1.0 ? `${scaleVal}x Super-Res` : '1.0x (Original)';
}

function handleFileSelected(file) {
  if (!file.type.startsWith('image/')) {
    showToast('Please select a valid image file (PNG, JPG, WEBP)', 'error');
    return;
  }

  state.rawFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl = e.target.result;
    const img = new Image();
    img.onload = () => {
      state.originalImage = img;
      state.enhancedSrc = dataUrl;

      elements.imgOriginal.src = dataUrl;
      elements.imgEnhanced.src = dataUrl;
      elements.imgSideOrig.src = dataUrl;
      elements.imgSideEnhanced.src = dataUrl;

      elements.statResOrig.textContent = `Original: ${img.naturalWidth}x${img.naturalHeight}`;
      elements.statResEnhanced.textContent = `Enhanced: ${img.naturalWidth}x${img.naturalHeight}`;

      elements.dropzone.classList.add('hidden');
      elements.viewportActive.classList.remove('hidden');
      elements.btnDownload.disabled = false;

      setTimeout(() => {
        syncImageDimensions();
        updateSplitPosition(50);
        applyLiveFilters();
      }, 50);

      showToast(`Loaded image (${img.naturalWidth}x${img.naturalHeight})`, 'success');
    };
    img.src = dataUrl;
  };
  reader.readAsDataURL(file);
}

function loadSampleImage() {
  const sampleCanvas = document.createElement('canvas');
  sampleCanvas.width = 1200;
  sampleCanvas.height = 800;
  const ctx = sampleCanvas.getContext('2d');

  const grad = ctx.createLinearGradient(0, 0, 1200, 800);
  grad.addColorStop(0, '#0f172a');
  grad.addColorStop(0.4, '#4c1d95');
  grad.addColorStop(0.7, '#db2777');
  grad.addColorStop(1, '#ea580c');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 1200, 800);

  ctx.fillStyle = '#fef08a';
  ctx.shadowColor = '#f59e0b';
  ctx.shadowBlur = 50;
  ctx.beginPath();
  ctx.arc(600, 480, 110, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;

  ctx.fillStyle = '#312e81';
  ctx.beginPath();
  ctx.moveTo(0, 560);
  ctx.lineTo(280, 400);
  ctx.lineTo(600, 520);
  ctx.lineTo(920, 380);
  ctx.lineTo(1200, 580);
  ctx.lineTo(1200, 800);
  ctx.lineTo(0, 800);
  ctx.fill();

  ctx.fillStyle = '#09090b';
  ctx.beginPath();
  ctx.moveTo(0, 680);
  ctx.lineTo(380, 540);
  ctx.lineTo(750, 660);
  ctx.lineTo(1200, 600);
  ctx.lineTo(1200, 800);
  ctx.lineTo(0, 800);
  ctx.fill();

  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
  ctx.font = 'bold 42px Space Grotesk, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('WebMagic Ultra Studio Demo', 600, 750);

  sampleCanvas.toBlob(blob => {
    const file = new File([blob], 'sample_sunset.png', { type: 'image/png' });
    handleFileSelected(file);
  }, 'image/png');
}

function setupComparisonSliderEvents() {
  let isDragging = false;

  const onStart = (e) => {
    isDragging = true;
    updateSliderFromPointer(e);
  };

  const onMove = (e) => {
    if (!isDragging) return;
    updateSliderFromPointer(e);
  };

  const onEnd = () => {
    isDragging = false;
  };

  elements.sliderHandle.addEventListener('mousedown', onStart);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onEnd);

  elements.sliderHandle.addEventListener('touchstart', onStart, { passive: true });
  window.addEventListener('touchmove', onMove, { passive: true });
  window.addEventListener('touchend', onEnd);

  elements.comparisonStage.addEventListener('click', (e) => {
    if (state.viewMode === 'split' && !state.isHoldingOriginal) {
      updateSliderFromPointer(e);
    }
  });
}

function updateSliderFromPointer(e) {
  if (state.viewMode !== 'split') return;
  const rect = elements.imageWrapper.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  let pos = ((clientX - rect.left) / rect.width) * 100;
  pos = Math.max(0, Math.min(100, pos));
  updateSplitPosition(pos);
}

function updateSplitPosition(percent) {
  state.sliderSplitPos = percent;
  elements.sliderHandle.style.left = `${percent}%`;
  elements.beforeContainer.style.width = `${percent}%`;
  syncImageDimensions();
}

function setViewMode(mode) {
  state.viewMode = mode;
  elements.modeSplit.classList.toggle('active', mode === 'split');
  elements.modeSide.classList.toggle('active', mode === 'side');

  if (mode === 'split') {
    elements.imageWrapper.classList.remove('hidden');
    elements.sideBySideContainer.classList.add('hidden');
    elements.sliderHandle.style.display = 'block';
    setTimeout(() => {
      syncImageDimensions();
      updateSplitPosition(50);
    }, 50);
  } else if (mode === 'side') {
    elements.imageWrapper.classList.add('hidden');
    elements.sideBySideContainer.classList.remove('hidden');
  }
}

function toggleHoldOriginal(holding) {
  state.isHoldingOriginal = holding;
  elements.modeOriginalHold.classList.toggle('active', holding);

  if (holding) {
    elements.beforeContainer.style.width = '100%';
    elements.sliderHandle.style.display = 'none';
  } else {
    updateSplitPosition(state.sliderSplitPos);
    elements.sliderHandle.style.display = state.viewMode === 'split' ? 'block' : 'none';
  }
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    elements.comparisonStage.requestFullscreen().catch(err => {
      console.error('Fullscreen error:', err);
    });
  } else {
    document.exitFullscreen();
  }
}

async function handleEnhanceClick() {
  if (!state.rawFile && !state.originalImage) {
    showToast('Please upload an image first.', 'error');
    return;
  }

  if (state.currentEngine === 'non-ai') {
    await renderNonAiServer();
  } else {
    await renderAiServer();
  }
}

async function renderNonAiServer() {
  showProgressOverlay('Rendering High-Definition Output...', 'Applying CLAHE dynamic range, multi-stage bilateral denoising, and unsharp masking');

  try {
    const formData = new FormData();
    formData.append('file', state.rawFile || dataURItoBlob(elements.imgOriginal.src));
    if (state.activePresetKey) {
      formData.append('preset', state.activePresetKey);
    }
    formData.append('clahe_clip', elements.sliderClahe.value);
    formData.append('sharpness', elements.sliderSharpness.value);
    formData.append('saturation', elements.sliderVibrance.value);
    formData.append('vibrance', elements.sliderVibrance.value);
    formData.append('denoise', elements.sliderDenoise.value);
    formData.append('contrast', elements.sliderContrast.value);
    formData.append('warmth', elements.sliderWarmth.value);
    formData.append('scale', elements.sliderScale.value);
    formData.append('output_format', elements.exportFormat.value);

    const resp = await fetch('/api/enhance/non-ai', {
      method: 'POST',
      body: formData
    });

    if (!resp.ok) {
      let errMsg = 'Processing failed';
      try {
        const errJson = await resp.json();
        errMsg = errJson.detail || errMsg;
      } catch (_) {
        const text = await resp.text();
        if (text) errMsg = text.slice(0, 120);
      }
      throw new Error(errMsg);
    }

    const blob = await resp.blob();
    const resultUrl = URL.createObjectURL(blob);

    const resImg = new Image();
    resImg.onload = () => {
      state.enhancedSrc = resultUrl;
      elements.imgEnhanced.src = resultUrl;
      elements.imgEnhanced.style.filter = 'none'; 

      elements.imgSideEnhanced.src = resultUrl;
      elements.imgSideEnhanced.style.filter = 'none';

      elements.statResEnhanced.textContent = `Enhanced: ${resImg.naturalWidth}x${resImg.naturalHeight}`;
      hideProgressOverlay();
      setTimeout(syncImageDimensions, 50);
      showToast(`Enhanced image rendered successfully (${resImg.naturalWidth}x${resImg.naturalHeight})`, 'success');
    };
    resImg.src = resultUrl;

  } catch (err) {
    hideProgressOverlay();
    showToast(`Error: ${err.message}`, 'error');
  }
}

async function renderAiServer() {
  const provider = elements.aiProviderSelect.value;
  const modelName = elements.aiModelSelect.value;
  const userKey = state.apiKeys[provider];

  if (!userKey || userKey.trim().length === 0) {
    openApiModal();
    showToast(`Please enter your ${provider.toUpperCase()} API Key first.`, 'error');
    return;
  }

  showProgressOverlay(
    `Running ${elements.aiModelSelect.options[elements.aiModelSelect.selectedIndex]?.text || 'AI Super-Resolution'}...`,
    'Executing generative neural network super-resolution and face reconstruction'
  );

  try {
    const formData = new FormData();
    formData.append('file', state.rawFile || dataURItoBlob(elements.imgOriginal.src));
    formData.append('provider', provider);
    formData.append('model_name', modelName);
    formData.append('scale', elements.aiScaleSelect.value);
    formData.append('face_enhance', elements.aiFaceEnhance.checked);
    if (elements.aiCustomPrompt.value.trim()) {
      formData.append('prompt', elements.aiCustomPrompt.value.trim());
    }

    const headers = {};
    if (provider === 'replicate') headers['X-Replicate-Key'] = userKey.trim();
    if (provider === 'stability') headers['X-Stability-Key'] = userKey.trim();
    if (provider === 'huggingface') headers['X-HF-Token'] = userKey.trim();
    if (provider === 'openai') headers['X-OpenAI-Key'] = userKey.trim();

    const resp = await fetch('/api/enhance/ai', {
      method: 'POST',
      headers: headers,
      body: formData
    });

    if (!resp.ok) {
      let errMsg = 'AI enhancement failed';
      try {
        const errJson = await resp.json();
        errMsg = errJson.detail || errMsg;
      } catch (_) {
        const text = await resp.text();
        if (text) errMsg = text.slice(0, 120);
      }
      throw new Error(errMsg);
    }

    const blob = await resp.blob();
    const resultUrl = URL.createObjectURL(blob);

    const resImg = new Image();
    resImg.onload = () => {
      state.enhancedSrc = resultUrl;
      elements.imgEnhanced.src = resultUrl;
      elements.imgEnhanced.style.filter = 'none';

      elements.imgSideEnhanced.src = resultUrl;
      elements.imgSideEnhanced.style.filter = 'none';

      elements.statResEnhanced.textContent = `AI Super-Res: ${resImg.naturalWidth}x${resImg.naturalHeight}`;
      hideProgressOverlay();
      setTimeout(syncImageDimensions, 50);
      showToast(`AI Super-Resolution completed (${resImg.naturalWidth}x${resImg.naturalHeight})!`, 'success');
    };
    resImg.src = resultUrl;

  } catch (err) {
    hideProgressOverlay();
    showToast(`AI Processing Error: ${err.message}`, 'error');
  }
}

function showProgressOverlay(title, desc) {
  elements.processStatusTitle.textContent = title;
  elements.processStatusDesc.textContent = desc;
  elements.processingOverlay.classList.remove('hidden');
  elements.enhanceSpinner.classList.remove('hidden');
  elements.btnEnhanceMain.disabled = true;
}

function hideProgressOverlay() {
  elements.processingOverlay.classList.add('hidden');
  elements.enhanceSpinner.classList.add('hidden');
  elements.btnEnhanceMain.disabled = false;
}

function downloadEnhancedImage() {
  const enhancedSrc = state.enhancedSrc || elements.imgEnhanced.src;
  if (!enhancedSrc) return;

  const fmt = elements.exportFormat.value.toLowerCase();
  const a = document.createElement('a');
  a.href = enhancedSrc;
  a.download = `webmagic_enhanced_${Date.now()}.${fmt === 'jpeg' ? 'jpg' : fmt}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast(`Downloading enhanced image as ${fmt.toUpperCase()}`, 'success');
}

function openApiModal() {
  elements.keyReplicate.value = state.apiKeys.replicate || '';
  elements.keyStability.value = state.apiKeys.stability || '';
  elements.keyHf.value = state.apiKeys.huggingface || '';
  elements.keyOpenai.value = state.apiKeys.openai || '';
  elements.apiModal.classList.remove('hidden');
}

function closeApiModal() {
  elements.apiModal.classList.add('hidden');
}

function saveApiKeys() {
  state.apiKeys.replicate = elements.keyReplicate.value.trim();
  state.apiKeys.stability = elements.keyStability.value.trim();
  state.apiKeys.huggingface = elements.keyHf.value.trim();
  state.apiKeys.openai = elements.keyOpenai.value.trim();

  localStorage.setItem('webmagic_key_replicate', state.apiKeys.replicate);
  localStorage.setItem('webmagic_key_stability', state.apiKeys.stability);
  localStorage.setItem('webmagic_key_hf', state.apiKeys.huggingface);
  localStorage.setItem('webmagic_key_openai', state.apiKeys.openai);

  updateKeyIndicator();
  checkProviderKeyStatus();
  closeApiModal();
  showToast('API Keys saved securely on your device!', 'success');
}

function clearApiKeys() {
  elements.keyReplicate.value = '';
  elements.keyStability.value = '';
  elements.keyHf.value = '';
  elements.keyOpenai.value = '';
  saveApiKeys();
  showToast('All API Keys cleared.', 'info');
}

function openHelpModal() {
  elements.helpModal.classList.remove('hidden');
}

function closeHelpModal() {
  elements.helpModal.classList.add('hidden');
}

function dataURItoBlob(dataURI) {
  const byteString = atob(dataURI.split(',')[1]);
  const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ab], { type: mimeString });
}

document.addEventListener('DOMContentLoaded', initApp);
