// Word (.docx) versions of the two IEEE papers, made from their LaTeX sources.
//   node Research/word/build-docx.js            -> both papers
//   node Research/word/build-docx.js journal    -> one of: journal, conference
// Output: ~/Documents/IntelliERP/2-Publication/IntelliERP-Journal-Paper.docx and IntelliERP-Conference-Paper.docx.
//
// The LaTeX is compiled once (pdflatex, bibtex) so that section, table and figure numbers, citation numbers and the
// IEEE-formatted reference list are exactly those of the PDFs. Text, lists and tables become editable Word content in
// the IEEE two-column layout (Times New Roman 10 pt); TikZ figures, pgfplots charts and the displayed equation are
// compiled with LaTeX and inserted as 300-dpi images. Needs pdflatex, bibtex and pdftoppm, and Research/report's
// node_modules (npm install there).
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execSync } = require('child_process');
const D = require('../report/node_modules/docx');
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle,
  SectionType, LevelFormat, FootnoteReferenceRun, TableLayoutType, VerticalAlign } = D;

const RESEARCH = path.resolve(__dirname, '..');
const BUILD = path.join(__dirname, 'build');
const OUT = path.join(os.homedir(), 'Documents', 'IntelliERP', '2-Publication');
const PAPERS = {
  journal: { dir: 'journal', main: 'trace', out: 'IntelliERP-Journal-Paper.docx' },
  conference: { dir: 'paper', main: 'intellierp', out: 'IntelliERP-Conference-Paper.docx' },
};
const TEX = `. "$HOME/.local/tex/env.sh" 2>/dev/null; export TEXINPUTS=".:$HOME/texmf/tex/latex/ieeetran//:" BSTINPUTS=".:$HOME/texmf/tex/latex/ieeetran//:";`;
const sh = (cmd, cwd) => execSync(`bash -c '${TEX} ${cmd.replace(/'/g, `'\\''`)}'`, { cwd, stdio: 'pipe' });

// IEEE page (US Letter): 7.16 in text width, two 3.5 in columns.
const TW = 1440;                         // twips per inch
const PAGE = { width: 12240, height: 15840 };
const MARGIN = { top: 1080, bottom: 1440, left: 1037, right: 1037 };
const TEXT_W = PAGE.width - MARGIN.left - MARGIN.right;   // 10166 twips = 7.06 in
const COL_GAP = 0.24 * TW;
const COL_W = (TEXT_W - COL_GAP) / 2;
const FONT = 'Times New Roman';

// ------------------------------------------------------------------ LaTeX helpers
function stripComments(tex) {
  return tex.split('\n').map(line => {
    for (let i = 0; i < line.length; i++) if (line[i] === '%' && line[i - 1] !== '\\') return line.slice(0, i);
    return line;
  }).join('\n');
}
// The group starting at s[i] === '{' : returns [content, index after the closing brace].
function group(s, i) {
  let depth = 0;
  for (let j = i; j < s.length; j++) {
    if (s[j] === '\\') { j++; continue; }
    if (s[j] === '{') depth++;
    else if (s[j] === '}' && --depth === 0) return [s.slice(i + 1, j), j + 1];
  }
  throw new Error('unbalanced braces near: ' + s.slice(i, i + 60));
}
const skipSpace = (s, i) => { while (i < s.length && /\s/.test(s[i])) i++; return i; };

// User macros from the preamble: \newcommand{\name}[n]{body} (n = 0 or 1).
function macros(preamble) {
  const out = {};
  const re = /\\newcommand\{\\([a-zA-Z]+)\}(\[(\d)\])?/g;
  let m;
  while ((m = re.exec(preamble))) {
    const [body] = group(preamble, skipSpace(preamble, re.lastIndex));
    out[m[1]] = { n: Number(m[3] || 0), body };
  }
  return out;
}
function expand(s, defs) {
  for (let round = 0; round < 5; round++) {
    let changed = false;
    for (const [name, { n, body }] of Object.entries(defs)) {
      const re = new RegExp('\\\\' + name + '(?![a-zA-Z])', 'g');
      let m, out = '', last = 0;
      while ((m = re.exec(s))) {
        let end = re.lastIndex, text = body;
        if (n === 1) { const g = group(s, skipSpace(s, end)); text = body.replace(/#1/g, g[0]); end = g[1]; }
        out += s.slice(last, m.index) + text; last = end; re.lastIndex = end; changed = true;
      }
      s = out + s.slice(last);
    }
    if (!changed) break;
  }
  return s;
}

// ------------------------------------------------------------------ labels, citations, references
function readAux(file) {
  const aux = fs.readFileSync(file, 'utf8');
  const labels = {}, cites = {};
  for (const m of aux.matchAll(/\\newlabel\{([^}]+)\}\{\{([^}]*)\}/g)) labels[m[1]] = m[2];
  for (const m of aux.matchAll(/\\bibcite\{([^}]+)\}\{(\d+)\}/g)) cites[m[1]] = Number(m[2]);
  return { labels, cites };
}
function citeText(keys, cites) {
  const nums = [...new Set(keys.split(',').map(k => cites[k.trim()]).filter(Boolean))].sort((a, b) => a - b);
  const parts = [];
  for (let i = 0; i < nums.length;) {
    let j = i;
    while (j + 1 < nums.length && nums[j + 1] === nums[j] + 1) j++;
    if (j - i >= 2) parts.push(`[${nums[i]}]–[${nums[j]}]`);
    else for (let k = i; k <= j; k++) parts.push(`[${nums[k]}]`);
    i = j + 1;
  }
  return parts.join(', ') || '[?]';
}
function readBbl(file) {
  const bbl = fs.readFileSync(file, 'utf8');
  const body = bbl.slice(bbl.indexOf('\\bibitem'), bbl.indexOf('\\end{thebibliography}'));
  return body.split(/\\bibitem(?:\[[^\]]*\])?\{[^}]+\}/).slice(1).map(entry => entry
    .replace(/\\BIBentry(ALT|STD)interwordspacing/g, '').replace(/\\newblock/g, ' ')
    .replace(/\\BIBforeignlanguage\{[^}]*\}/g, '').replace(/\\url\{([^}]*)\}/g, '$1').replace(/\s+/g, ' ').trim());
}

// ------------------------------------------------------------------ inline LaTeX -> runs
const SYMBOLS = { rightarrow: '→', to: '→', leftarrow: '←', le: '≤', leq: '≤', ge: '≥', geq: '≥', neq: '≠', ne: '≠',
  in: '∈', times: '×', alpha: 'α', beta: 'β', theta: 'θ', tau: 'τ', pi: 'π', phi: 'φ', sigma: 'σ', mu: 'μ', delta: 'δ',
  ldots: '…', dots: '…', cdot: '·', pm: '±', approx: '≈', quad: '  ', qquad: '    ', enspace: ' ', ',': ' ', ';': ' ',
  ' ': ' ', '%': '%', '&': '&', '_': '_', '#': '#', $: '$', '{': '{', '}': '}', textbackslash: '\\', textasciitilde: '~',
  allowbreak: '', centering: '', raggedright: '', arraybackslash: '', footnotesize: '', small: '', scriptsize: '',
  normalsize: '', noindent: '', relax: '', par: '' };
const STYLE_CMDS = { emph: { italics: true }, textit: { italics: true }, textbf: { bold: true }, textsc: { smallCaps: true },
  texttt: { mono: true }, text: {}, mathrm: {}, textrm: {}, mbox: {}, MakeLowercase: { lower: true } };

function inline(s, ctx, style = {}, math = false) {
  const runs = [];
  let buf = '';
  const push = (text, st = style) => {
    if (!text) return;
    text = st.lower ? text.toLowerCase() : text;
    const last = runs[runs.length - 1];
    if (last && JSON.stringify(last.st) === JSON.stringify(st)) last.text += text; else runs.push({ text, st });
  };
  const flush = () => { push(buf); buf = ''; };
  let i = 0;
  while (i < s.length) {
    const ch = s[i];
    if (ch === '\\') {
      if (s[i + 1] === '\\') { flush(); runs.push({ br: true }); i += 2; if (s[i] === '[') i = s.indexOf(']', i) + 1; continue; }
      const m = /^\\([a-zA-Z]+|[\s\S])/.exec(s.slice(i));
      if (!m) { i++; continue; }
      const name = /^\s$/.test(m[1]) ? ' ' : m[1]; i += m[0].length;
      if (name in SYMBOLS) { buf += SYMBOLS[name]; if (/^[a-zA-Z]/.test(name) && s[i] === ' ' && !math) { /* keep the space */ } continue; }
      if (name === 'cite') { const g = group(s, skipSpace(s, i)); buf += citeText(g[0], ctx.cites); i = g[1]; continue; }
      if (name === 'ref' || name === 'eqref') { const g = group(s, i); buf += ctx.labels[g[0]] || '?'; i = g[1]; continue; }
      if (name === 'label') { i = group(s, i)[1]; continue; }
      if (name === 'textcolor') { i = group(s, i)[1]; const g = group(s, i); flush(); runs.push(...inline(g[0], ctx, style, math)); i = g[1]; continue; }
      if (name === 'href') { i = group(s, i)[1]; const g = group(s, i); flush(); runs.push(...inline(g[0], ctx, style, math)); i = g[1]; continue; }
      if (name === 'rule') { if (s[i] === '[') i = s.indexOf(']', i) + 1; i = group(s, i)[1]; i = group(s, i)[1]; buf += '____________________'; continue; }
      if (name === 'url' || name === 'nolinkurl') { const g = group(s, i); buf += g[0]; i = g[1]; continue; }
      if (name in STYLE_CMDS) {
        i = skipSpace(s, i);
        if (s[i] !== '{') continue;
        const g = group(s, i); flush();
        runs.push(...inline(g[0], ctx, { ...style, ...STYLE_CMDS[name] }, math && !['text', 'mathrm', 'mbox'].includes(name)));
        i = g[1]; continue;
      }
      if (name === 'item') continue;
      // unknown command: drop it, keep any argument's text
      continue;
    }
    if (ch === '{' ) { const g = group(s, i); flush(); runs.push(...inline(g[0], ctx, style, math)); i = g[1]; continue; }
    if (ch === '}') { i++; continue; }
    if (ch === '$' && !math) {
      const end = s.indexOf('$', i + 1); flush();
      runs.push(...inline(s.slice(i + 1, end), ctx, style, true)); i = end + 1; continue;
    }
    if (math && (ch === '^' || ch === '_')) {
      flush(); i++;
      const st = { ...style, [ch === '^' ? 'sup' : 'sub']: true };
      if (s[i] === '{') { const g = group(s, i); runs.push(...inline(g[0], ctx, st, true)); i = g[1]; }
      else if (s[i] === '\\') { const m = /^\\([a-zA-Z]+)/.exec(s.slice(i)); runs.push(...inline(m[0], ctx, st, true)); i += m[0].length; }
      else { push(s[i], st); i++; }
      continue;
    }
    if (math && ch === ' ') { i++; continue; }
    if (ch === '~') { buf += ' '; i++; continue; }
    if (s.startsWith('---', i)) { buf += '—'; i += 3; continue; }
    if (s.startsWith('--', i)) { buf += '–'; i += 2; continue; }
    if (s.startsWith('``', i)) { buf += '“'; i += 2; continue; }
    if (s.startsWith("''", i)) { buf += '”'; i += 2; continue; }
    if (ch === '`') { buf += '‘'; i++; continue; }
    if (ch === "'" && !math) { buf += '’'; i++; continue; }
    if (ch === '\n' || ch === '\t') { buf += ' '; i++; continue; }
    buf += ch; i++;
  }
  flush();
  // collapse repeated spaces across runs
  return runs.map(r => r.br ? r : { ...r, text: r.text.replace(/ {2,}/g, ' ') });
}
function textRuns(runs, base = {}) {
  return runs.map(r => r.br ? new TextRun({ break: 1 }) : new TextRun({
    text: r.text, font: r.st.mono ? 'Courier New' : FONT, size: base.size ?? 20, bold: base.bold || r.st.bold,
    italics: base.italics ? !r.st.italics : r.st.italics, smallCaps: base.smallCaps || r.st.smallCaps,
    superScript: r.st.sup, subScript: r.st.sub }));
}
const plain = (s, ctx) => inline(s, ctx).map(r => r.br ? ' ' : r.text).join('').trim();

// ------------------------------------------------------------------ images rendered by LaTeX
function renderImage(work, name, preamble, content, kind) {
  const doc = kind === 'math'
    ? `\\documentclass[border=1pt,varwidth]{standalone}\n${preamble}\n\\begin{document}\n$\\displaystyle ${content}$\n\\end{document}\n`
    : `\\documentclass[border=2pt]{standalone}\n${preamble}\n\\begin{document}\n${content}\n\\end{document}\n`;
  fs.writeFileSync(path.join(work, `${name}.tex`), doc);
  sh(`pdflatex -interaction=nonstopmode ${name} >/dev/null; pdftoppm -png -r 300 -singlefile ${name}.pdf ${name}`, work);
  const info = execSync(`pdfinfo ${name}.pdf`, { cwd: work }).toString();
  const [, w, h] = /Page size:\s+([\d.]+) x ([\d.]+)/.exec(info);
  return { file: path.join(work, `${name}.png`), widthIn: Number(w) / 72, heightIn: Number(h) / 72 };
}
function imageParagraph(img, maxWidthIn, after = 60) {
  const data = fs.readFileSync(img.file);
  const scale = Math.min(1, maxWidthIn / img.widthIn);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after }, keepNext: true, children: [
    new ImageRun({ type: 'png', data, transformation: { width: Math.round(img.widthIn * scale * 96), height: Math.round(img.heightIn * scale * 96) } })] });
}
function pngSize(file) { const b = fs.readFileSync(file); return [b.readUInt32BE(16), b.readUInt32BE(20)]; }

// ------------------------------------------------------------------ tables
function columnSpec(spec) {
  const cols = [];
  const s = spec.replace(/@\{[^}]*\}/g, '').replace(/>\{[^}]*\}/g, '');
  for (let i = 0; i < s.length; i++) {
    if ('lcr'.includes(s[i])) cols.push({ align: s[i] });
    else if (s[i] === 'p') { const g = group(s, i + 1); cols.push({ align: 'l', cm: parseFloat(g[0]) }); i = g[1] - 1; }
  }
  return cols;
}
function splitCells(row) {
  const cells = []; let depth = 0, cur = '';
  for (let i = 0; i < row.length; i++) {
    const c = row[i];
    if (c === '\\') { cur += c + (row[i + 1] ?? ''); i++; continue; }
    if (c === '{') depth++; if (c === '}') depth--;
    if (c === '&' && depth === 0) { cells.push(cur); cur = ''; continue; }
    cur += c;
  }
  cells.push(cur);
  return cells.map(x => x.trim());
}
function wordTable(spec, body, ctx, widthTw) {
  const cols = columnSpec(spec);
  const rowsTex = body.replace(/\\(toprule|bottomrule)(\[[^\]]*\])?/g, '').split(/\\\\(?:\[[^\]]*\])?/)
    .map(r => r.trim()).filter(r => r && r !== '\\midrule');
  const rows = [];
  let ruleAfter = new Set();
  rowsTex.forEach(r => {
    let text = r;
    if (text.startsWith('\\midrule')) { ruleAfter.add(rows.length - 1); text = text.replace(/^\\midrule/, '').trim(); }
    if (text) rows.push(splitCells(text));
  });
  // widths: p{} columns by their size, others by their longest cell
  const weights = cols.map((c, k) => c.cm ? c.cm * 6 : Math.max(4, ...rows.map(r => plain(r[k] ?? '', ctx).length)));
  const total = weights.reduce((a, b) => a + b, 0);
  const widths = weights.map(w => Math.floor(widthTw * w / total));
  const thick = { style: BorderStyle.SINGLE, size: 8, color: '000000' }, thin = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
  const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    alignment: AlignmentType.CENTER,
    rows: rows.map((r, ri) => new TableRow({ cantSplit: true, tableHeader: ri === 0, children: cols.map((c, k) => new TableCell({
      width: { size: widths[k], type: WidthType.DXA }, verticalAlign: VerticalAlign.TOP,
      margins: { top: 20, bottom: 20, left: 60, right: 60 },
      borders: { top: ri === 0 ? thick : none, bottom: ri === rows.length - 1 ? thick : (ruleAfter.has(ri) ? thin : none), left: none, right: none },
      children: [new Paragraph({ alignment: { l: AlignmentType.LEFT, c: AlignmentType.CENTER, r: AlignmentType.RIGHT }[c.align],
        children: textRuns(inline(r[k] ?? '', ctx), { size: 16 }) })] })) })),
  });
}

// ------------------------------------------------------------------ the paper
function build(key) {
  const P = PAPERS[key];
  const work = path.join(BUILD, key);
  fs.rmSync(work, { recursive: true, force: true }); fs.mkdirSync(work, { recursive: true });
  execSync(`cp -r ${path.join(RESEARCH, P.dir)}/. ${work}/`);
  sh(`pdflatex -interaction=nonstopmode ${P.main} >/dev/null; bibtex ${P.main} >/dev/null; pdflatex -interaction=nonstopmode ${P.main} >/dev/null; pdflatex -interaction=nonstopmode ${P.main} >/dev/null`, work);
  const ctx = readAux(path.join(work, `${P.main}.aux`));
  const references = readBbl(path.join(work, `${P.main}.bbl`));

  const tex = stripComments(fs.readFileSync(path.join(work, `${P.main}.tex`), 'utf8'));
  const preamble = tex.slice(0, tex.indexOf('\\begin{document}'));
  const figurePreamble = preamble.split('\n').filter(l => /^\\(usepackage|usetikzlibrary|pgfplotsset)/.test(l.trim())
    && !/\{(cite|hyperref|url)\}/.test(l)).join('\n') + '\n\\usepackage{graphicx}\n\\usepackage{mathptmx}';
  let body = tex.slice(tex.indexOf('\\begin{document}') + 16, tex.indexOf('\\end{document}'));
  body = expand(body, macros(preamble));

  // title and authors
  const title = plain(group(body, body.indexOf('\\title') + 6)[0], ctx);
  const authorTex = group(body, body.indexOf('\\author') + 7)[0];
  const front = [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: title, font: FONT, size: 48 })] })];
  const footnotes = {};
  if (authorTex.includes('\\IEEEauthorblockN')) {           // conference: author blocks side by side
    const blocks = authorTex.split('\\and').map(b => {
      const name = plain(group(b, b.indexOf('\\IEEEauthorblockN') + 17)[0], ctx);
      const aff = group(b, b.indexOf('\\IEEEauthorblockA') + 17)[0].split('\\\\').map(l => inline(l.trim(), ctx));
      return [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: name, font: FONT, size: 22 })] }),
        ...aff.map(l => new Paragraph({ alignment: AlignmentType.CENTER, children: textRuns(l, { size: 18 }) }))];
    });
    const w = Math.floor(TEXT_W / blocks.length);
    const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
    front.push(new Table({ width: { size: w * blocks.length, type: WidthType.DXA }, columnWidths: blocks.map(() => w), alignment: AlignmentType.CENTER,
      rows: [new TableRow({ children: blocks.map(b => new TableCell({ width: { size: w, type: WidthType.DXA },
        borders: { top: none, bottom: none, left: none, right: none }, children: b })) })] }));
    front.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
  } else {                                                   // journal: names line, affiliations in a footnote
    const names = authorTex.replace(/\\thanks\{/g, '\u0000{');
    const nameText = plain(names.split('\u0000')[0], ctx);
    const thanks = [...authorTex.matchAll(/\\thanks\{/g)].map(m => plain(group(authorTex, m.index + 7)[0], ctx));
    footnotes[1] = { children: thanks.map(t => new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 16 })] })) };
    front.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [
      new TextRun({ text: nameText, font: FONT, size: 22 }), new FootnoteReferenceRun(1)] }));
  }

  // body blocks
  const sections = [{ cols: 1, children: front }];
  let cur = { cols: 2, children: [] };
  sections.push(cur);
  const headings = new Set();      // a heading must stay with its text, so it moves below a full-width float
  const wide = children => {
    const moved = [];
    while (cur.children.length && headings.has(cur.children[cur.children.length - 1])) moved.unshift(cur.children.pop());
    sections.push({ cols: 1, children }); cur = { cols: 2, children: [...moved] }; sections.push(cur);
  };
  let secNo = 0, subNo = 0, figAuto = 0, runIn = null, listDepth = [];
  const roman = n => ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV'][n];
  const para = (text, opts = {}) => {
    const runs = inline(text, ctx);
    if (!runs.length && !runIn) return;
    const children = [];
    if (runIn) { children.push(...textRuns(inline(runIn, ctx), { italics: true }), new TextRun({ text: ' ', font: FONT, size: 20 })); runIn = null; }
    children.push(...textRuns(runs, opts.base ?? {}));
    cur.children.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: opts.indent ?? { firstLine: 202 },
      spacing: { after: 0, line: 240 }, numbering: opts.numbering, children }));
  };

  const env = (s, i, name) => { const end = s.indexOf(`\\end{${name}}`, i); return [s.slice(i, end), end + `\\end{${name}}`.length]; };
  let i = 0, text = '';
  const flushText = () => { text.split(/\n\s*\n/).forEach(p => { if (p.trim()) para(p.trim()); }); text = ''; };
  while (i < body.length) {
    const rest = body.slice(i);
    let m;
    if ((m = /^\\(title|author|markboth)\b/.exec(rest))) {
      let j = i + m[0].length;
      j = group(body, skipSpace(body, j))[1];
      if (m[1] === 'markboth') j = group(body, skipSpace(body, j))[1];
      i = j; continue;
    }
    if ((m = /^\\(maketitle|IEEEoverridecommandlockouts|IEEEpeerreviewmaketitle)\b/.exec(rest))) { i += m[0].length; continue; }
    if ((m = /^\\(section|subsection)(\*?)\s*\{/.exec(rest))) {
      flushText();
      const [t, j] = group(body, i + m[0].length - 1);
      const heading = plain(t, ctx);
      if (m[1] === 'section') {
        let label;
        if (m[2]) label = heading; else { secNo++; subNo = 0; label = `${roman(secNo)}. ${heading}`; }
        const h = new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 180, after: 80 },
          children: [new TextRun({ text: label, font: FONT, size: 20, smallCaps: true })] });
        headings.add(h); cur.children.push(h);
      } else {
        subNo++;
        const h = new Paragraph({ keepNext: true, spacing: { before: 100, after: 60 },
          children: [new TextRun({ text: `${String.fromCharCode(64 + subNo)}. ${heading}`, font: FONT, size: 20, italics: true })] });
        headings.add(h); cur.children.push(h);
      }
      i = j; continue;
    }
    if ((m = /^\\paragraph\s*\{/.exec(rest))) { flushText(); const [t, j] = group(body, i + m[0].length - 1); runIn = t.trim(); i = j; continue; }
    if ((m = /^\\begin\{abstract\}/.exec(rest))) {
      flushText(); const [t, j] = env(body, i + m[0].length, 'abstract');
      cur.children.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 120 }, children: [
        new TextRun({ text: 'Abstract—', font: FONT, size: 18, bold: true, italics: true }), ...textRuns(inline(t.trim(), ctx), { size: 18, bold: true })] }));
      i = j; continue;
    }
    if ((m = /^\\begin\{IEEEkeywords\}/.exec(rest))) {
      flushText(); const [t, j] = env(body, i + m[0].length, 'IEEEkeywords');
      cur.children.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 160 }, children: [
        new TextRun({ text: 'Index Terms—', font: FONT, size: 18, bold: true, italics: true }), ...textRuns(inline(t.trim(), ctx), { size: 18, bold: true })] }));
      i = j; continue;
    }
    if ((m = /^\\begin\{(itemize|enumerate)\}(\[[^\]]*\])?/.exec(rest))) {
      flushText(); const [t, j] = env(body, i + m[0].length, m[1]);
      const ref = m[1] === 'itemize' ? 'bullets' : `numbers-${listDepth.length}-${i}`;
      if (m[1] === 'enumerate') numberingRefs.push(ref);
      t.split('\\item').slice(1).forEach(item => para(item.trim(), { numbering: { reference: ref, level: 0 }, indent: undefined }));
      i = j; continue;
    }
    if ((m = /^\\begin\{(table|figure)(\*?)\}(\[[^\]]*\])?/.exec(rest))) {
      flushText(); const [t, j] = env(body, i + m[0].length, m[1] + m[2]);
      const isWide = m[2] === '*';
      const cap = t.indexOf('\\caption') >= 0 ? group(t, t.indexOf('\\caption') + 8)[0] : '';
      const lab = /\\label\{([^}]+)\}/.exec(t);
      const out = [];
      if (m[1] === 'table') {
        const tb = /\\begin\{tabular\}\{/.exec(t);
        const [spec, k] = group(t, tb.index + tb[0].length - 1);
        const tabBody = t.slice(k, t.indexOf('\\end{tabular}'));
        out.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120 }, children: [
          new TextRun({ text: `TABLE ${lab ? ctx.labels[lab[1]] : ''}`, font: FONT, size: 16 })] }));
        out.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { after: 60 }, children: textRuns(inline(cap, ctx), { size: 16, smallCaps: true }) }));
        out.push(wordTable(spec, tabBody, ctx, isWide ? TEXT_W : COL_W));
        out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      } else {
        figAuto++;
        const num = lab ? ctx.labels[lab[1]] : String(figAuto);
        const inc = /\\includegraphics(\[[^\]]*\])?\{([^}]+)\}/.exec(t);
        let img;
        if (inc) {
          const file = path.join(work, inc[2]); const [w, h] = pngSize(file);
          const widthIn = isWide ? 7.06 : 3.45;
          img = { file, widthIn, heightIn: widthIn * h / w };
        } else {
          const content = t.replace(/\\caption(\[[^\]]*\])?\{[\s\S]*$/, '').replace(/\\centering/g, '').replace(/\\label\{[^}]*\}/g, '');
          img = renderImage(work, `fig-${key}-${figAuto}`, figurePreamble, content.trim(), 'figure');
        }
        out.push(imageParagraph(img, isWide ? 7.0 : 3.45));
        out.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 160 }, children: [
          new TextRun({ text: `Fig. ${num}. `, font: FONT, size: 16 }), ...textRuns(inline(cap, ctx), { size: 16 })] }));
      }
      if (isWide) wide(out); else cur.children.push(...out);
      i = j; continue;
    }
    if (rest.startsWith('\\[')) {
      flushText(); const end = body.indexOf('\\]', i);
      const img = renderImage(work, `eq-${key}-${i}`, figurePreamble, body.slice(i + 2, end).trim(), 'math');
      cur.children.push(imageParagraph(img, 3.4, 80));
      i = end + 2; continue;
    }
    if ((m = /^\\(bibliographystyle|bibliography)\s*\{/.exec(rest))) { flushText(); i = group(body, i + m[0].length - 1)[1]; continue; }
    text += body[i]; i++;
  }
  flushText();

  // references
  cur.children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 180, after: 80 },
    children: [new TextRun({ text: 'References', font: FONT, size: 20, smallCaps: true })] }));
  references.forEach((r, k) => cur.children.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: 360, hanging: 360 },
    spacing: { after: 20 }, children: [new TextRun({ text: `[${k + 1}]\t`, font: FONT, size: 16 }), ...textRuns(inline(r, ctx), { size: 16 })],
    tabStops: [{ type: 'left', position: 360 }] })));

  const doc = new Document({
    creator: 'Mohammad Yasin Siddique', title,
    styles: { default: { document: { run: { font: FONT, size: 20 } } } },
    footnotes,
    numbering: { config: [
      { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 300, hanging: 200 } } } }] },
      ...numberingRefs.map(reference => ({ reference, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1)', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] })) ] },
    sections: sections.filter(s => s.children.length).map((s, k) => ({
      properties: { type: k === 0 ? undefined : SectionType.CONTINUOUS, page: { size: PAGE, margin: MARGIN },
        column: s.cols === 2 ? { count: 2, space: COL_GAP, equalWidth: true } : { count: 1 } },
      children: s.children })),
  });
  return Packer.toBuffer(doc).then(buf => {
    fs.mkdirSync(OUT, { recursive: true });
    const file = path.join(OUT, P.out);
    fs.writeFileSync(file, buf);
    console.log(`written ${file} (${Math.round(buf.length / 1024)} KB): ${secNo} sections, ${references.length} references`);
  });
}
const numberingRefs = [];

(async () => {
  const only = process.argv[2];
  for (const key of Object.keys(PAPERS)) if (!only || key === only) { numberingRefs.length = 0; await build(key); }
})().catch(error => { console.error(error); process.exit(1); });
