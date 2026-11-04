/*
 * Hover Fit
 *
 * Hover Editor opens a link in a popover with a fixed size. For a link to a heading
 * (data-href="Note#Heading") inside an element with the class `hover-fit`, this plugin keeps the
 * popover invisible, measures the heading section (the heading and its blocks up to the next
 * heading of the same or a higher level), sets the popover width and height to fit it, scrolls
 * the heading to the top and then shows the popover. Other popovers are not touched; drag, pin
 * and resize work as usual.
 *
 * Use:  <pre class="hover-fit">... <a class="internal-link" data-href="Note#Heading"
 *       href="Note#Heading">tag</a> ...</pre>
 */
const { Plugin } = require('obsidian');

const SCOPE = '.hover-fit a.internal-link';
const MEASURE = 'hover-fit-measuring';  // class on the section blocks while they are measured
const POPOVER = 'hover-fit-popover';    // class on a popover this plugin sizes
const PAD = 12;          // px above and below the section inside the popover
const MAX_W_PX = 800;    // width cap in px: a line that fits stays on one line, a longer one wraps
const MAX_W = 0.9;       // and never wider than this share of the window
const MAX_H = 0.8;       // height cap (share of the window)
const POLL_MS = 50;      // wait between checks while the popover renders
const MAX_TRIES = 80;    // 80 x 50 ms = 4 s, then the popover is shown as it is
const DEBUG = false;     // log each step to the developer console (Ctrl+Shift+I)
const log = (...a) => { if (DEBUG) console.log('[hover-fit]', ...a); };
const SETTLE_MS = 120;   // after the section is laid out, let Hover Editor finish its own scroll

module.exports = class HoverFit extends Plugin {
	onload() {
		this.pending = null;

		// While measuring, nothing in the section may wrap. Themes set white-space on li / p
		// themselves, so an inline style on the block is not enough: force it on every element.
		const style = document.createElement('style');
		// max-content width: each block (and the lists in it) is as wide as its longest line, so
		// only forced breaks (<br>) break a line, whatever white-space rule the theme sets.
		style.textContent = `.${MEASURE}, .${MEASURE} ul, .${MEASURE} ol, .${MEASURE} li, .${MEASURE} p {
			width: max-content !important; max-width: none !important; }
		.${MEASURE}, .${MEASURE} * { white-space: nowrap !important; }
		/* no flash highlight on the linked heading: the popover shows only that section anyway */
		.${POPOVER} .is-flashing { background-color: transparent !important; box-shadow: none !important; }`;
		document.head.appendChild(style);
		this.register(() => style.remove());  // { sub, time } of the last hovered link in SCOPE

		this.registerDomEvent(document, 'mouseover', (evt) => {
			const a = evt.target instanceof Element ? evt.target.closest(SCOPE) : null;
			if (!a) return;
			const href = a.getAttribute('data-href') || a.getAttribute('href') || '';
			const i = href.indexOf('#');
			if (i >= 0) this.pending = { sub: decodeURIComponent(href.slice(i + 1)), time: Date.now() };
			log('hover link', href);
		}, true);

		const observer = new MutationObserver((muts) => {
			for (const m of muts) {
				for (const n of m.addedNodes) {
					if (n instanceof HTMLElement && n.classList.contains('popover')) log('popover added, class =', n.className);
					if (n instanceof HTMLElement && n.classList.contains('hover-editor')) this.start(n);
				}
			}
		});
		observer.observe(document.body, { childList: true });
		this.register(() => observer.disconnect());
	}

	start(hoverEl) {
		const p = this.pending;
		log('start, pending =', p);
		if (!p || Date.now() - p.time > 5000) return;
		this.pending = null;
		hoverEl.classList.add(POPOVER);

		// Transparent, not hidden: the popover is laid out and rendered as usual, only not seen.
		// The observer runs before the first paint, so the unsized popover never shows.
		hoverEl.style.opacity = '0';
		let shown = false;
		const show = () => { if (!shown) { shown = true; hoverEl.style.opacity = ''; } };

		let tries = 0;
		const step = () => {
			if (!hoverEl.isConnected) return;
			if (++tries > MAX_TRIES) { log('gave up: heading not found or not laid out', p.sub, Array.from(hoverEl.querySelectorAll('[data-heading]')).map((e) => e.getAttribute('data-heading'))); show(); return; }
			const blocks = this.findSection(hoverEl, p.sub);
			if (!blocks) { setTimeout(step, POLL_MS); return; }
			setTimeout(() => {
				try {
					if (!this.fit(hoverEl, blocks, show)) setTimeout(step, POLL_MS);  // not laid out yet
				} catch (e) {
					console.error('hover-fit', e);
					show();
				}
			}, SETTLE_MS);
		};
		step();
	}

	// The heading's blocks once they are rendered and have a size, else null.
	findSection(hoverEl, sub) {
		const h = Array.from(hoverEl.querySelectorAll('.markdown-preview-view :is(h1,h2,h3,h4,h5,h6)'))
			.find((el) => el.getAttribute('data-heading') === sub);
		if (!h || h.getBoundingClientRect().height === 0) return null;

		const level = Number(h.tagName[1]);
		const first = h.closest('.markdown-preview-section > div') || h;
		const blocks = [first];
		for (let el = first.nextElementSibling; el; el = el.nextElementSibling) {
			const c = el.firstElementChild;
			if (c && /^H[1-6]$/.test(c.tagName) && Number(c.tagName[1]) <= level) break;
			if (el.classList.contains('el-hr') || el.classList.contains('mod-footer')) break;
			blocks.push(el);
		}
		return blocks;
	}

	// Returns false when the section is not laid out yet (try again later).
	fit(hoverEl, blocks, show) {
		const scroller = blocks[0].closest('.markdown-preview-view');
		if (!scroller || !blocks[0].isConnected) return false;
		const win = hoverEl.ownerDocument.defaultView || window;
		const maxW = Math.min(MAX_W_PX, win.innerWidth * MAX_W);

		// natural width of each block: with MEASURE it is max-content, so only <br> breaks a line
		blocks.forEach((b) => b.classList.add(MEASURE));
		const natural = blocks.map((b) => b.getBoundingClientRect().width);
		blocks.forEach((b) => b.classList.remove(MEASURE));
		if (!natural.some((w) => w > 0)) return false;

		// first guess, then widen by what is still missing until no block wraps (or the cap is hit).
		// Measuring the room the blocks really get covers every padding and margin around them.
		const roomNow = blocks.map((b) => b.getBoundingClientRect().width);
		let width = hoverEl.offsetWidth + Math.max(...natural.map((w, k) => w - roomNow[k]));
		let pass = 0;
		const widen = () => {
			width = Math.round(Math.min(Math.max(width, 260), maxW));
			hoverEl.style.width = width + 'px';
			requestAnimationFrame(() => {
				const missing = Math.max(...natural.map((w, k) => w - blocks[k].getBoundingClientRect().width));
				log('pass', pass, 'width', width, 'missing', missing);
				if (missing > 0.5 && width < maxW && ++pass < 4) { width += Math.ceil(missing) + 1; widen(); return; }
				this.fitHeight(hoverEl, scroller, blocks, win, show);
			});
		};
		widen();
		return true;
	}

	// height at the final width (a line longer than the cap wraps), then scroll, clamp and show
	fitHeight(hoverEl, scroller, blocks, win, show) {
		const chromeH = hoverEl.offsetHeight - scroller.clientHeight;
		const top = blocks[0].getBoundingClientRect().top;
		const bottom = Math.max(...blocks.map((b) => b.getBoundingClientRect().bottom));
		const height = chromeH + (bottom - top) + 2 * PAD;
		log('height', height, 'chromeH', chromeH);
		hoverEl.style.height = Math.round(Math.min(Math.max(height, 80), win.innerHeight * MAX_H)) + 'px';

		requestAnimationFrame(() => {
			scroller.scrollTop += blocks[0].getBoundingClientRect().top - scroller.getBoundingClientRect().top - PAD;

			const r = hoverEl.getBoundingClientRect();
			const dx = Math.max(0, r.right - (win.innerWidth - 8));
			const dy = Math.max(0, r.bottom - (win.innerHeight - 8));
			if (dx || dy) {
				const x = parseFloat(hoverEl.style.left) - dx, y = parseFloat(hoverEl.style.top) - dy;
				if (!isNaN(x)) { hoverEl.style.left = x + 'px'; hoverEl.setAttribute('data-x', String(x)); }
				if (!isNaN(y)) { hoverEl.style.top = y + 'px'; hoverEl.setAttribute('data-y', String(y)); }
			}
			show();
		});
	}
};
