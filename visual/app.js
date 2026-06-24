// 状态管理
let currentRoute = 'all';
let currentType = 'all';
let currentView = 'timeline';
let selectedEvent = null;
let searchQuery = '';

// 初始化
document.addEventListener('DOMContentLoaded', function() {
  initChapterNav();
  initDebutTimeline();
  renderTimeline();
  renderComparison();
  updateStats();
});

// 章节导航
function initChapterNav() {
  const scroll = document.getElementById('chapterScroll');
  CHAPTERS.forEach(ch => {
    const btn = document.createElement('div');
    btn.className = `chapter-btn phase-${ch.phase}`;
    btn.innerHTML = `<span class="ch-num">${ch.num === 0 ? '零' : ch.num}</span>${ch.name}`;
    btn.onclick = () => scrollToChapter(ch.num);
    scroll.appendChild(btn);
  });
}

// 角色登场时间轴
function initDebutTimeline() {
  const container = document.getElementById('debutTimeline');
  DEBUTS.forEach(d => {
    const node = document.createElement('div');
    node.className = 'debut-node';
    node.innerHTML = `
      <div class="debut-avatar" style="border-color: ${d.color}; color: ${d.color};">${d.avatar}</div>
      <div class="debut-name">${d.name}</div>
      <div class="debut-event">${d.event}</div>
    `;
    container.appendChild(node);
  });
}

// 渲染时间线
function renderTimeline() {
  const timeline = document.getElementById('timeline');
  timeline.innerHTML = '';

  const phases = [
    { key: 'prologue', title: '阶段零 · 共通序章', subtitle: '初遇与羁绊建立', chapters: 'E01-E15', phaseClass: 'prologue' },
    { key: 'ch1', title: '第一至三章 · 信任建立', subtitle: '情感基础阶段', chapters: '第1-3章', phaseClass: 'ch1' },
    { key: 'ch2', title: '第四至八章 · 关系深化', subtitle: '三路线分化开始', chapters: '第4-8章', phaseClass: 'ch2' },
    { key: 'pure', title: '第九至十二章 · 纯爱路线', subtitle: '信任→告白→契约', chapters: '第9-12章', phaseClass: 'pure' },
    { key: 'ntrs', title: '第十三至二十四章 · NTRS路线', subtitle: '坦白→共享→确认', chapters: '第13-24章', phaseClass: 'ntrs' },
    { key: 'passive', title: '被动NTR路线', subtitle: '缺席→堕落→争取', chapters: '穿插第1-24章', phaseClass: 'passive' },
    { key: 'end', title: '终章', subtitle: '三条路线的最终结局', chapters: '第24章', phaseClass: 'end' }
  ];

  phases.forEach(phase => {
    const section = document.createElement('div');
    section.className = `phase-section ${phase.phaseClass}`;
    section.id = `phase-${phase.key}`;

    const header = document.createElement('div');
    header.className = 'phase-header';
    header.innerHTML = `
      <div class="phase-dot ${phase.phaseClass}"></div>
      <span class="phase-title">${phase.title}</span>
      <span class="phase-subtitle">${phase.subtitle}</span>
      <span class="phase-chapters">${phase.chapters}</span>
    `;
    section.appendChild(header);

    // 过滤事件
    const phaseEvents = getFilteredEvents().filter(e => {
      if (phase.key === 'prologue') return e.route === 'prologue';
      if (phase.key === 'ch1') return e.chapter === '第一章' || e.chapter === '第二章' || e.chapter === '第三章';
      if (phase.key === 'ch2') return e.chapter === '第四章' || e.chapter === '第五章' || e.chapter === '第六章' || e.chapter === '第七章' || e.chapter === '第八章';
      if (phase.key === 'pure') return e.route === 'pure' && (e.chapter === '第九章' || e.chapter === '第十章' || e.chapter === '第十一章' || e.chapter === '第十二章');
      if (phase.key === 'ntrs') return e.route === 'ntrs' && (e.chapter === '第十三章' || e.chapter === '第十四章' || e.chapter === '第十五章' || e.chapter === '第十六章' || e.chapter === '第十七章' || e.chapter === '第十八章' || e.chapter === '第十九章' || e.chapter === '第二十章' || e.chapter === '第二十一章' || e.chapter === '第二十二章' || e.chapter === '第二十三章' || e.chapter === '第二十四章');
      if (phase.key === 'passive') return e.route === 'passive';
      if (phase.key === 'end') return e.chapter === '第二十四章';
      return false;
    });

    if (phaseEvents.length === 0) {
      section.classList.add('hidden-item');
    }

    phaseEvents.forEach((evt, idx) => {
      const item = createTimelineItem(evt, idx);
      section.appendChild(item);
    });

    timeline.appendChild(section);
  });
}

function createTimelineItem(evt, idx) {
  const item = document.createElement('div');
  item.className = `timeline-item ${evt.route}`;
  if (evt.debut) item.classList.add('debut');
  item.dataset.id = evt.id;
  item.dataset.route = evt.route;
  item.dataset.type = evt.type;

  const charsHtml = evt.chars.map(c => `<span class="char-tag">${c}</span>`).join('');
  const debutBadge = evt.debut ? '<span class="debut-badge">登场</span>' : '';

  item.innerHTML = `
    <div class="event-card">
      <div class="event-header">
        <span class="event-id">${evt.id}</span>
        <span class="event-title">${evt.title}</span>
        ${debutBadge}
        <span class="event-chapter-tag">${evt.chapter}</span>
      </div>
      <div class="event-summary">${evt.summary}</div>
      <div class="event-chars">${charsHtml}</div>
    </div>
  `;

  item.onclick = () => showEventDetail(evt);
  return item;
}

// 渲染对比视图
function renderComparison() {
  const grid = document.getElementById('comparisonGrid');
  grid.innerHTML = '';

  // 表头
  const header = document.createElement('div');
  header.className = 'comparison-grid-header';
  header.innerHTML = `
    <div class="comp-header-empty">章节</div>
    <div class="comp-header-pure">纯爱路线</div>
    <div class="comp-header-ntrs">NTRS路线</div>
    <div class="comp-header-passive">被动NTR</div>
  `;
  grid.appendChild(header);

  // 从第9章开始显示三路线对比
  const compareChapters = ['第九章','第十章','第十一章','第十二章','第十三章','第十四章','第十五章','第十六章','第十七章','第十八章','第十九章','第二十章','第二十一章','第二十二章','第二十三章','第二十四章'];

  compareChapters.forEach(chName => {
    const row = document.createElement('div');
    row.className = 'comparison-row';

    const pureEvents = EVENTS.filter(e => e.route === 'pure' && e.chapter === chName);
    const ntrsEvents = EVENTS.filter(e => e.route === 'ntrs' && e.chapter === chName);
    const passiveEvents = EVENTS.filter(e => e.route === 'passive' && e.chapter === chName);

    const chNum = chName.replace('第','').replace('章','');
    const isBranch = ['第九章','第十二章','第十五章','第二十四章'].includes(chName);

    row.innerHTML = `
      <div class="comp-chapter-cell ${isBranch ? 'branch-point' : ''}">
        <span class="ch-num">${chNum}</span>
        <span>${isBranch ? '分支点' : ''}</span>
      </div>
      <div class="comp-event-cell pure ${isBranch ? 'branch-point' : ''}">
        ${pureEvents.map(e => `<div class="comp-event-item pure" onclick="showEventDetailById('${e.id}')"><span class="eid">${e.id}</span>${e.title}</div>`).join('') || '<div style="color:#555;font-size:11px;">无事件</div>'}
      </div>
      <div class="comp-event-cell ntrs ${isBranch ? 'branch-point' : ''}">
        ${ntrsEvents.map(e => `<div class="comp-event-item ntrs" onclick="showEventDetailById('${e.id}')"><span class="eid">${e.id}</span>${e.title}</div>`).join('') || '<div style="color:#555;font-size:11px;">无事件</div>'}
      </div>
      <div class="comp-event-cell passive ${isBranch ? 'branch-point' : ''}">
        ${passiveEvents.map(e => `<div class="comp-event-item passive" onclick="showEventDetailById('${e.id}')"><span class="eid">${e.id}</span>${e.title}</div>`).join('') || '<div style="color:#555;font-size:11px;">无事件</div>'}
      </div>
    `;
    grid.appendChild(row);
  });
}

// 显示事件详情
function showEventDetail(evt) {
  selectedEvent = evt;
  const panel = document.getElementById('detailPanel');

  const routeLabels = {
    prologue: '阶段零·共通', pure: '纯爱路线', ntrs: 'NTRS路线',
    passive: '被动NTR', world: '世界事件', hidden: '隐藏事件',
    rich: '丰富性事件', rean: '黎恩专属'
  };
  const typeLabels = {
    main: '主线剧情', world: '世界事件', hidden: '隐藏事件',
    rich: '丰富性事件', rean: '黎恩专属', nsfw: 'NSFW深度', foot: '足控事件'
  };

  const prevEvent = getPrevEvent(evt);
  const nextEvent = getNextEvent(evt);

  panel.innerHTML = `
    <div class="detail-nav">
      <button class="nav-btn" onclick="showEventDetailById('${prevEvent ? prevEvent.id : ''}')" ${!prevEvent ? 'disabled' : ''}>← 上一个</button>
      <button class="nav-btn" onclick="showEventDetailById('${nextEvent ? nextEvent.id : ''}')" ${!nextEvent ? 'disabled' : ''}>下一个 →</button>
    </div>
    <div class="detail-title">${evt.title}</div>
    <div>
      <span class="detail-route ${evt.route}">${routeLabels[evt.route] || evt.route}</span>
      <span class="detail-type ${evt.type}">${typeLabels[evt.type] || evt.type}</span>
      <span class="detail-chapter">${evt.chapter}</span>
    </div>
    <div class="detail-section">
      <h4>事件摘要</h4>
      <p>${evt.summary}</p>
    </div>
    <div class="detail-section">
      <h4>登场角色</h4>
      <div class="detail-chars">
        ${evt.chars.map(c => `<span class="detail-char">${c}</span>`).join('')}
      </div>
    </div>
    ${evt.debut ? `
    <div class="detail-section">
      <h4>角色首次登场</h4>
      <div class="detail-chars">
        ${evt.debut.map(c => `<span class="detail-char" style="background:rgba(240,147,251,0.3);color:#f0c0fb;">${c} ★</span>`).join('')}
      </div>
    </div>
    ` : ''}
    <div class="detail-section">
      <h4>事件编号</h4>
      <p style="font-family:monospace;font-size:14px;color:#667eea;">${evt.id}</p>
    </div>
  `;
}

function showEventDetailById(id) {
  if (!id) return;
  const evt = EVENTS.find(e => e.id === id);
  if (evt) showEventDetail(evt);
}

function getPrevEvent(evt) {
  const idx = EVENTS.indexOf(evt);
  return idx > 0 ? EVENTS[idx - 1] : null;
}

function getNextEvent(evt) {
  const idx = EVENTS.indexOf(evt);
  return idx < EVENTS.length - 1 ? EVENTS[idx + 1] : null;
}

// 过滤功能
function getFilteredEvents() {
  return EVENTS.filter(e => {
    if (currentRoute !== 'all' && e.route !== currentRoute) return false;
    if (currentType !== 'all' && e.type !== currentType) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return e.title.toLowerCase().includes(q) || e.id.toLowerCase().includes(q) || e.summary.toLowerCase().includes(q);
    }
    return true;
  });
}

function filterRoute(route) {
  currentRoute = route;
  document.querySelectorAll('.route-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`.route-tab.${route}`).classList.add('active');
  renderTimeline();
  updateStats();
}

function filterType(type) {
  currentType = type;
  document.querySelectorAll('.type-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`.type-tab.${type}`).classList.add('active');
  renderTimeline();
  updateStats();
}

function searchEvents(query) {
  searchQuery = query;
  renderTimeline();
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
  document.getElementById(`viewTab${view.charAt(0).toUpperCase() + view.slice(1)}`).classList.add('active');

  if (view === 'timeline') {
    document.getElementById('timelineView').classList.remove('view-hidden');
    document.getElementById('comparisonView').classList.remove('active');
  } else {
    document.getElementById('timelineView').classList.add('view-hidden');
    document.getElementById('comparisonView').classList.add('active');
  }
}

function scrollToChapter(chNum) {
  const phaseMap = { 0: 'prologue', 1: 'ch1', 2: 'ch1', 3: 'ch1', 4: 'ch2', 5: 'ch2', 6: 'ch2', 7: 'ch2', 8: 'ch2', 9: 'pure', 10: 'pure', 11: 'pure', 12: 'pure', 13: 'ntrs', 14: 'ntrs', 15: 'ntrs', 16: 'ntrs', 17: 'ntrs', 18: 'ntrs', 19: 'ntrs', 20: 'ntrs', 21: 'ntrs', 22: 'ntrs', 23: 'ntrs', 24: 'end' };
  const phaseKey = phaseMap[chNum];
  if (phaseKey) {
    const el = document.getElementById(`phase-${phaseKey}`);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function updateStats() {
  const filtered = getFilteredEvents();
  document.getElementById('statMain').textContent = filtered.filter(e => e.type === 'main').length;
  document.getElementById('statWorld').textContent = filtered.filter(e => e.type === 'world').length;
  document.getElementById('statHidden').textContent = filtered.filter(e => e.type === 'hidden').length;
  document.getElementById('statRich').textContent = filtered.filter(e => e.type === 'rich').length;
  document.getElementById('statRean').textContent = filtered.filter(e => e.type === 'rean').length;
  document.getElementById('statNsfw').textContent = filtered.filter(e => e.type === 'nsfw').length;
  document.getElementById('statFoot').textContent = filtered.filter(e => e.type === 'foot').length;
}
