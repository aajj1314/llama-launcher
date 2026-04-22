# Llama Launcher UI Optimization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize the Llama Launcher WebUI for better accessibility, performance, and user experience

**Architecture:** Improve existing HTML/CSS/JS codebase following web interface guidelines

**Tech Stack:** HTML5, CSS3, Vue 3, JavaScript

---

## File Structure

**Files to modify:**
- `templates/index.html` - Main WebUI interface

---

### Task 1: Accessibility Improvements

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add aria-label to icon buttons**

```html
<!-- Before -->
<button class="refresh-btn" @click="refreshModels">⟳ Refresh</button>

<!-- After -->
<button class="refresh-btn" @click="refreshModels" aria-label="Refresh models">⟳ Refresh</button>
```

- [ ] **Step 2: Add proper labels to form controls**

```html
<!-- Ensure all form controls have proper labels -->
<label for="mode-select">Running Mode</label>
<select id="mode-select" v-model="config.mode" :disabled="isRunning">
```

- [ ] **Step 3: Add keyboard support for interactive elements**

```html
<!-- Add keyboard support to model items -->
<div 
    class="model-item" 
    v-for="model in models" 
    :key="model.name"
    :class="{ selected: selectedModel === model.name }"
    @click="selectModel(model.name)"
    @keydown.enter="selectModel(model.name)"
    @keydown.space="selectModel(model.name)"
    tabindex="0"
>
```

- [ ] **Step 4: Add semantic HTML elements**

```html
<!-- Replace divs with semantic elements where appropriate -->
<header>
    <h1>🤖 Llama Launcher</h1>
    <nav class="status-badge">
        <span class="status-dot" :class="{ offline: !tuiOnline }"></span>
        <span>TUI {{ tuiOnline ? 'Online' : 'Offline' }}</span>
    </nav>
</header>
```

- [ ] **Step 5: Add skip link for main content**

```html
<!-- Add skip link at the beginning of body -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Add id to main content -->
<div id="app" class="container" id="main-content">
```

- [ ] **Step 6: Test accessibility improvements**

Open the WebUI and test keyboard navigation and screen reader support

- [ ] **Step 7: Commit**

```bash
git add templates/index.html
git commit -m "accessibility: improve WebUI accessibility"
```

### Task 2: Focus States and Interactive Elements

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Improve focus states for interactive elements**

```css
/* Add focus-visible styles */
.btn:focus-visible,
select:focus,
input:focus,
.model-item:focus-visible {
    outline: 2px solid var(--accent-cyan);
    outline-offset: 2px;
}

/* Remove outline-none without replacement */
select:focus, input:focus {
    outline: 2px solid var(--accent-cyan);
    border-color: var(--accent-cyan);
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
    transform: translateY(-1px);
}
```

- [ ] **Step 2: Add hover and active states**

```css
/* Ensure all interactive elements have hover states */
.model-item:hover {
    background: var(--bg-hover);
    border-color: var(--accent-cyan);
    transform: translateX(5px);
}

.model-item:active {
    transform: translateX(3px);
}
```

- [ ] **Step 3: Test focus and interactive states**

Open the WebUI and test keyboard navigation and mouse interactions

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "ui: improve focus states and interactive elements"
```

### Task 3: Form Improvements

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add autocomplete attributes**

```html
<!-- Add autocomplete to form inputs -->
<input type="number" v-model.number="config.port" min="1" max="65535" :disabled="isRunning" autocomplete="off">
<input type="text" v-model="config.llamaCppPath" :disabled="isRunning" placeholder="/path/to/llama.cpp" autocomplete="off">
```

- [ ] **Step 2: Add proper input types and inputmode**

```html
<!-- Use proper input types -->
<input type="number" v-model.number="config.port" min="1" max="65535" :disabled="isRunning" inputmode="numeric">
<input type="number" v-model.number="config.timeout" min="1" max="300" :disabled="isRunning" inputmode="numeric">
<input type="number" v-model.number="config.gpuMemory" min="0" :disabled="isRunning" inputmode="numeric">
```

- [ ] **Step 3: Add proper labels and ids**

```html
<!-- Add ids to form controls and associate with labels -->
<div class="form-group">
    <label for="port-input">Port (Server mode)</label>
    <input id="port-input" type="number" v-model.number="config.port" min="1" max="65535" :disabled="isRunning">
</div>
```

- [ ] **Step 4: Test form improvements**

Open the WebUI and test form interactions

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "forms: improve form accessibility and usability"
```

### Task 4: Animation and Performance Improvements

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add prefers-reduced-motion support**

```css
/* Add prefers-reduced-motion support */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
```

- [ ] **Step 2: Replace transition: all with specific properties**

```css
/* Before */
:root {
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* After */
:root {
    --transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

- [ ] **Step 3: Optimize animation performance**

```css
/* Use transform and opacity for animations */
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    border-color: var(--accent-cyan);
}
```

- [ ] **Step 4: Test animation performance**

Open the WebUI and test animations on different devices

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "animation: improve animation performance and accessibility"
```

### Task 5: Responsive Design Improvements

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Improve responsive breakpoints**

```css
/* Add more responsive breakpoints */
@media (max-width: 1024px) {
    .grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .container {
        padding: 16px;
    }
    
    header {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    
    .btn-group {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    h1 {
        font-size: 1.5rem;
    }
    
    .card {
        padding: 16px;
    }
    
    .model-item {
        padding: 12px 16px;
    }
}
```

- [ ] **Step 2: Add safe area support**

```css
/* Add safe area support for mobile devices */
@supports (padding: max(0px)) {
    .container {
        padding-left: max(20px, env(safe-area-inset-left));
        padding-right: max(20px, env(safe-area-inset-right));
        padding-top: max(20px, env(safe-area-inset-top));
        padding-bottom: max(20px, env(safe-area-inset-bottom));
    }
}
```

- [ ] **Step 3: Test responsive design**

Open the WebUI on different screen sizes

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "responsive: improve responsive design"
```

### Task 6: Dark Mode and Theming

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add color-scheme meta tag**

```html
<!-- Add color-scheme meta tag -->
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0d1117">
```

- [ ] **Step 2: Improve dark mode support**

```css
/* Improve dark mode support */
html {
    color-scheme: dark;
}

/* Ensure native form controls look good in dark mode */
select, input {
    background: var(--bg-dark);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: var(--transition);
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

- [ ] **Step 3: Test dark mode**

Open the WebUI and test dark mode on different browsers

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "theme: improve dark mode support"
```

### Task 7: Performance Optimizations

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add preconnect for CDN**

```html
<!-- Add preconnect for Vue CDN -->
<link rel="preconnect" href="https://cdn.jsdelivr.net">
```

- [ ] **Step 2: Optimize Vue script loading**

```html
<!-- Use defer for Vue script -->
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js" defer></script>
```

- [ ] **Step 3: Optimize model list rendering**

```javascript
// Add virtualization for large model lists
// Use a virtual list component or implement simple pagination
```

- [ ] **Step 4: Test performance**

Open the WebUI and test loading times and responsiveness

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "performance: optimize WebUI performance"
```

### Task 8: Error Handling and User Feedback

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Improve error messages**

```javascript
// Improve error messages with specific feedback
const saveConfig = async () => {
    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ctx_idx: config.value.ctxIdx,
                ngl_idx: config.value.nglIdx,
                port: config.value.port,
                llama_cpp_path: config.value.llamaCppPath,
                timeout: config.value.timeout,
                log_level: config.value.logLevel,
                gpu_memory: config.value.gpuMemory,
                mode: config.value.mode
            })
        });
        const data = await res.json();
        if (!data.success) {
            console.error('Config save failed:', data.error);
            alert('Config save failed: ' + data.error);
        } else {
            console.log('Config saved successfully');
            await fetchState();
            alert('Configuration saved successfully!');
        }
    } catch (e) {
        console.error('Failed to save config:', e);
        alert('Failed to save config: ' + e.message);
    }
};
```

- [ ] **Step 2: Add loading states**

```html
<!-- Add loading states to buttons -->
<button class="btn btn-primary" @click="startModel" :disabled="isRunning || !selectedModel">
    <span v-if="isStarting">Starting...</span>
    <span v-else>▶ Start</span>
</button>
```

- [ ] **Step 3: Test error handling**

Open the WebUI and test error scenarios

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "error: improve error handling and user feedback"
```

### Task 9: Final Testing and Validation

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Run accessibility tests**

Use browser dev tools to run accessibility audits

- [ ] **Step 2: Test cross-browser compatibility**

Test the WebUI on different browsers

- [ ] **Step 3: Test performance**

Use browser dev tools to measure performance

- [ ] **Step 4: Test functionality**

Test all WebUI functions including model selection, configuration, and server management

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "test: final testing and validation"
```

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-22-ui-optimization.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**