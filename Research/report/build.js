// Builds the final-year project report (Word) from the chapter files in src/.
//   node build.js            -> ~/Documents/IntelliERP/1-Final-Submission/IntelliERP-FYP-Report.docx
// Chapter files export an array of blocks: {h1|h2|h3: text}, {p: text}, {bullets: [...]}, {numbered: [...]},
// {table: {caption, head, rows, widths}}, {fig: {file, caption, width}}, {code: {caption, text}}, {pagebreak: true}.
// In text: **bold**, *italic*, `code`, [@key] or [@a; @b] for (Author, Year), @key for Author (Year).
const fs = require('fs');
const path = require('path');
const os = require('os');
const D = require('docx');
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, ShadingType, BorderStyle, PageBreak, Header, Footer, PageNumber, TableOfContents, StyleLevel,
  LevelFormat, TabStopType, VerticalAlign } = D;

const OUT = path.join(os.homedir(), 'Documents', 'IntelliERP', '1-Final-Submission', 'IntelliERP-FYP-Report.docx');
const ASSETS = path.join(__dirname, 'assets');
const META = require('./src/meta');
const TEXT_WIDTH = 9026; // A4 width 11906 minus 1-inch margins, in DXA
const FONT = 'Arial';

// ------------------------------------------------------------------ references
function parseBib(file) {
  const src = fs.readFileSync(file, 'utf8');
  const entries = {};
  const re = /@(\w+)\s*{\s*([^,]+),([\s\S]*?)\n}/g;
  let m;
  while ((m = re.exec(src))) {
    const fields = {};
    const fre = /(\w+)\s*=\s*{((?:[^{}]|{(?:[^{}]|{[^{}]*})*})*)}/g;
    let f;
    while ((f = fre.exec(m[3]))) fields[f[1].toLowerCase()] = f[2];
    entries[m[2].trim()] = { type: m[1].toLowerCase(), ...fields };
  }
  return entries;
}
const clean = s => (s || '').replace(/``/g, '“').replace(/''/g, '”').replace(/\$\\tau\$/g, 'τ')
  .replace(/\\`\{?(\w)\}?/g, (_, c) => ({ a: 'à', e: 'è', i: 'ì', o: 'ò', u: 'ù' }[c] || c)).replace(/\\'\{?(\w)\}?/g, (_, c) => ({ a: 'á', e: 'é', i: 'í', o: 'ó', u: 'ú', E: 'É', c: 'ć', n: 'ń', s: 'ś' }[c] || c))
  .replace(/\\"\{?(\w)\}?/g, (_, c) => ({ a: 'ä', o: 'ö', u: 'ü' }[c] || c)).replace(/\\c\{?c\}?/g, 'ç')
  .replace(/\\v\{?(\w)\}?/g, (_, c) => ({ c: 'č', s: 'š', z: 'ž' }[c] || c)).replace(/\\&/g, '&').replace(/--/g, '–')
  .replace(/[{}]/g, '').replace(/\\[a-z]+\s?/g, '').replace(/\s+/g, ' ').trim();
const BIB = { ...parseBib(path.join(__dirname, '..', 'journal', 'references.bib')), ...require('./src/extra-refs') };
const authorsOf = e => clean(e.author || e.editor || '').split(/\s+and\s+/).map(a => a.includes(',') ? a.split(',')[0].trim() : a.split(' ').slice(-1)[0]);
const used = new Set();
function citeShort(key) {
  const e = BIB[key];
  if (!e) throw new Error('unknown reference ' + key);
  used.add(key);
  const a = authorsOf(e);
  const who = e.author && /^[A-Z]{2,}|Team|Consortium/.test(clean(e.author)) && !clean(e.author).includes(',') ? clean(e.author)
    : a.length === 1 ? a[0] : a.length === 2 ? `${a[0]} and ${a[1]}` : `${a[0]} et al.`;
  return { who, year: e.year };
}
function harvard(key) {
  const e = BIB[key];
  const names = clean(e.author || '').split(/\s+and\s+/).map(n => {
    if (!n.includes(',')) return n;
    const [last, first] = n.split(',').map(s => s.trim());
    return `${last}, ${first.split(/[\s-]+/).filter(Boolean).map(p => p[0] + '.').join('')}`;
  });
  const who = names.length > 1 ? names.slice(0, -1).join(', ') + ' and ' + names.slice(-1) : names[0];
  const venue = clean(e.journal || e.booktitle || e.howpublished || e.publisher || '');
  const parts = [`${who} (${e.year}) ${clean(e.title)}.`];
  const ital = [];
  if (venue) ital.push(venue);
  let tail = '';
  if (e.volume) tail += `, ${clean(e.volume)}`;
  if (e.number) tail += `(${clean(e.number)})`;
  if (e.pages) tail += `, pp. ${clean(e.pages)}`;
  if (e.eprint) ital.push(`arXiv preprint arXiv:${e.eprint}`);
  const doi = e.doi ? ` doi:${e.doi}` : (e.url ? ` Available at: ${e.url}` : '');
  return { text: parts[0], venue: ital.join('. '), tail: tail + '.' + doi };
}

// ------------------------------------------------------------------ inline text
function expandCites(text) {
  text = text.replace(/\[((?:@[\w-]+;?\s*)+)\]/g, (_, keys) =>
    '(' + keys.split(';').map(k => k.trim().slice(1)).filter(Boolean).map(k => { const c = citeShort(k); return `${c.who}, ${c.year}`; }).join('; ') + ')');
  return text.replace(/(^|[\s(])@([a-z][\w-]*\d{4}[\w-]*)/g, (_, pre, k) => { const c = citeShort(k); return `${pre}${c.who} (${c.year})`; });
}
function runs(text, base = {}) {
  text = expandCites(text);
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith('**')) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
    else if (t.startsWith('`')) out.push(new TextRun({ text: t.slice(1, -1), font: 'Courier New', size: (base.size || 24) - 2 }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, font: FONT, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}
const para = (text, opts = {}) => new Paragraph({ children: runs(text, opts.run || {}), alignment: opts.align || AlignmentType.JUSTIFIED,
  spacing: { after: 160, line: 360, ...(opts.spacing || {}) }, ...(opts.extra || {}) });

// ------------------------------------------------------------------ images
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function image(file, widthIn) {
  const full = path.join(ASSETS, file);
  const { w, h } = pngSize(full);
  const width = Math.round(widthIn * 96), height = Math.round(width * h / w);
  const maxH = 8.6 * 96;
  const scale = height > maxH ? maxH / height : 1;
  return new ImageRun({ type: 'png', data: fs.readFileSync(full), transformation: { width: Math.round(width * scale), height: Math.round(height * scale) } });
}

// ------------------------------------------------------------------ blocks
let chapter = 0, figNo = 0, tabNo = 0;
const captionRun = { size: 20, italics: true, color: '1F3B73' };
function caption(label, text, style) {
  return new Paragraph({ style, alignment: AlignmentType.CENTER, spacing: { before: 80, after: 200 },
    children: runs(`${label} ${chapter}.${label === 'Figure' ? figNo : tabNo} : ${text}`, captionRun), keepNext: label === 'Table' });
}
function cell(text, { header = false, width, shade, keep = false } = {}) {
  return new TableCell({ width: { size: width, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
    shading: header ? { type: ShadingType.CLEAR, fill: 'D9E2F3', color: 'auto' } : shade ? { type: ShadingType.CLEAR, fill: shade, color: 'auto' } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: String(text).split('\n').map(line => new Paragraph({ spacing: { after: 0, line: 260 }, alignment: AlignmentType.LEFT, keepNext: keep || header,
      children: runs(line, { size: 19, bold: header }) })) });
}
function table({ head, rows, widths }) {
  const total = widths.reduce((a, b) => a + b, 0);
  const w = widths.map(x => Math.round(x / total * TEXT_WIDTH));
  w[w.length - 1] = TEXT_WIDTH - w.slice(0, -1).reduce((a, b) => a + b, 0);
  return new Table({ width: { size: TEXT_WIDTH, type: WidthType.DXA }, columnWidths: w,
    rows: [new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, { header: true, width: w[i] })) }),
      // short tables are kept on one page (keep-with-next on every row but the last); long ones repeat their header
      ...rows.map((r, k) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, { width: w[i], keep: rows.length <= 14 && k < rows.length - 1 })) }))] });
}
const BULLET = 'bullets', NUMBERED = 'numbered';
let numberedInstance = 0;
function render(block) {
  if (block.h1) {
    chapter = block.chapter ?? chapter + 1; figNo = 0; tabNo = 0;
    return [new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: block.h1, font: FONT })] })];
  }
  // the first front-matter page already starts a new section, so it needs no page break of its own
  if (block.front) { const first = !render.frontSeen; render.frontSeen = true;
    return [new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: !first, children: [new TextRun({ text: block.front, font: FONT })] })]; }
  if (block.h2) return [new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(block.h2) })];
  if (block.h3) return [new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(block.h3) })];
  if (block.p) return [para(block.p, block.line ? { spacing: { line: block.line } } : {})];  // `line`: tighter spacing (the abstract, to keep its keywords on its page)
  if (block.center) return [para(block.center, { align: AlignmentType.CENTER })];
  if (block.bullets) return block.bullets.map(b => new Paragraph({ numbering: { reference: BULLET, level: 0 }, alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 80, line: 340 }, children: runs(b) }));
  if (block.numbered) { numberedInstance++; return block.numbered.map(b => new Paragraph({ numbering: { reference: NUMBERED, level: 0, instance: numberedInstance },
    alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 340 }, children: runs(b) })); }
  if (block.table) { tabNo++; return [caption('Table', block.table.caption, 'TableCaption'), table(block.table), new Paragraph({ spacing: { after: 120 }, children: [] })]; }
  if (block.fig) { figNo++; return [new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 40 },
    children: [image(block.fig.file, block.fig.width || 6.2)] }), caption('Figure', block.fig.caption, 'FigureCaption')]; }
  if (block.code) {
    figNo++;
    const lines = block.code.text.replace(/\s+$/, '').split('\n');
    const border = { style: BorderStyle.SINGLE, size: 4, color: '8EA9DB' };
    return [new Table({ width: { size: TEXT_WIDTH, type: WidthType.DXA }, columnWidths: [TEXT_WIDTH], rows: [new TableRow({ children: [new TableCell({
      width: { size: TEXT_WIDTH, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: 'F4F6FA', color: 'auto' },
      borders: { top: border, bottom: border, left: border, right: border }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: lines.map(l => new Paragraph({ spacing: { after: 0, line: 230 }, children: [new TextRun({ text: l.replace(/\t/g, '    ') || ' ', font: 'Courier New', size: 16 })] })) })] })] }),
      new Paragraph({ children: [], spacing: { after: 0 } }),
      ...(block.code.source ? [para(`**Source:** \`${block.code.source}\``, { spacing: { after: 40 } })] : []),
      caption('Figure', block.code.caption, 'FigureCaption')];
  }
  if (block.pagebreak) return [new Paragraph({ children: [new PageBreak()] })];
  if (block.raw) return block.raw;
  throw new Error('unknown block ' + JSON.stringify(block).slice(0, 80));
}

// ------------------------------------------------------------------ cover and lists
function cover() {
  const c = (text, size, opts = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: opts.after ?? 160, before: opts.before ?? 0 },
    children: [new TextRun({ text, font: FONT, size, bold: opts.bold, italics: opts.italics })] });
  const box = border => ({ top: border, bottom: border, left: border, right: border });
  // The logo and the photograph live in private/ (not committed); without them the cover shows a placeholder.
  const picture = (file, widthInches, placeholder, after) => {
    const full = path.join(__dirname, 'private', file);
    if (!fs.existsSync(full)) return c(placeholder, 20, { italics: true, after });
    const data = fs.readFileSync(full), w = data.readUInt32BE(16), h = data.readUInt32BE(20);
    const width = Math.round(widthInches * 96);
    return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after }, children: [new ImageRun({ type: 'png', data,
      transformation: { width, height: Math.round(width * h / w) } })] });
  };
  const b = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
  const field = (label, value) => new Paragraph({ spacing: { after: 120 }, tabStops: [{ type: TabStopType.LEFT, position: 3000 }],
    children: [new TextRun({ text: label, font: FONT, size: 24 }), new TextRun({ text: '\t: ' + value, font: FONT, size: 24 })] });
  return [
    picture('inti-logo.png', 3.6, '[INTI International University logo]', 300),
    c('FINAL YEAR PROJECT REPORT', 26, { after: 240 }),
    new Table({ width: { size: TEXT_WIDTH, type: WidthType.DXA }, columnWidths: [TEXT_WIDTH], rows: [new TableRow({ children: [new TableCell({
      width: { size: TEXT_WIDTH, type: WidthType.DXA }, borders: box(b), margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children: [c('PROJECT TITLE:', 28, { after: 100 }), c(META.title, 24, { after: 60 })] })] })] }),
    c('', 12, { after: 200 }),
    new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 200, line: 340 }, children: [new TextRun({ font: FONT, size: 24,
      text: `"A dissertation submitted in partial fulfillment of the requirement of an Honours Degree in Computer Science at INTI International University under the management and supervision of the Faculty of Data Science and Information Technology."` })] }),
    new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 300, line: 340 }, children: [new TextRun({ font: FONT, size: 24, italics: true,
      text: `I declare that this project is my own work, it has not been copied in part or in whole from any source except where duly acknowledged. As such, all uses of previously published works (from books, journals, internet, etc.) have been properly acknowledged within the report to an item in the references or bibliographies. I hereby submit my dissertation, dated ${META.submissionDate} for review and assessment.` })] }),
    c('by', 24, { after: 200 }),
    picture('student-photo.png', 1.05, '[Student photograph]', 200),
    field('Student Name', META.student), field('Student ID', META.studentId), field('IC No / Passport No', META.passport),
    field('Project ID', META.projectId), field('Supervisor (INTI)', META.supervisor),
    field('Home Institution', META.home), field('Home Department', META.homeDepartment),
    field('Home Supervisor', META.homeSupervisor), field('Head of Department', META.homeHod),
    field('Programme', META.mobility),
  ];
}
function tocBlock(title, opts) {
  return [new Paragraph({ style: 'FrontTitle', pageBreakBefore: true, children: [new TextRun({ text: title, font: FONT })] }),
    new TableOfContents(title, opts)];
}

// ------------------------------------------------------------------ assemble
const order = ['front', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'];
const body = [];
for (const name of order) {
  const blocks = require('./src/' + name);
  if (name === 'front') {
    for (const b of blocks) {
      if (b.toc) {
        body.push(...tocBlock('Table of Contents', { hyperlink: true, headingStyleRange: '1-3' }));
        body.push(...tocBlock('List of Figures', { hyperlink: true, stylesWithLevels: [new StyleLevel('FigureCaption', 1)] }));
        body.push(...tocBlock('List of Tables', { hyperlink: true, stylesWithLevels: [new StyleLevel('TableCaption', 1)] }));
      } else body.push(...render(b));
    }
  } else for (const b of blocks) body.push(...render(b));
}
// references, sorted, Harvard style (only references cited in the text)
const refs = [...used].sort((a, b) => harvard(a).text.localeCompare(harvard(b).text));
const refBlocks = [new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: 'References', font: FONT })] }),
  ...refs.map(k => { const h = harvard(k); return new Paragraph({ alignment: AlignmentType.LEFT, indent: { left: 567, hanging: 567 }, spacing: { after: 140, line: 300 },
    children: [new TextRun({ text: h.text + ' ', font: FONT, size: 22 }), ...(h.venue ? [new TextRun({ text: h.venue, italics: true, font: FONT, size: 22 })] : []),
      new TextRun({ text: h.tail, font: FONT, size: 22 })] }); })];
const appendices = require('./src/appendix').flatMap(render);

const headerFooter = {
  headers: { default: new Header({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: TEXT_WIDTH }],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999', space: 2 } },
    children: [new TextRun({ text: `Project Title: ${META.shortTitle}`, font: FONT, size: 20 }), new TextRun({ text: '\tPage ', font: FONT, size: 20 }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20, bold: true }), new TextRun({ text: ' of ', font: FONT, size: 20 }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 20, bold: true })] })] }) },
  footers: { default: new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.CENTER, position: TEXT_WIDTH / 2 }, { type: TabStopType.RIGHT, position: TEXT_WIDTH }],
    children: [new TextRun({ text: `Prepared by ${META.student}`, font: FONT, size: 16 }), new TextRun({ text: `\t${META.programme}`, font: FONT, size: 16 }),
      new TextRun({ text: `\t${META.session}`, font: FONT, size: 16 })] })] }) },
};

const doc = new Document({
  creator: META.student, title: META.title, features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 32, bold: true, color: '000000' },
        paragraph: { spacing: { before: 0, after: 240 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 27, bold: true, color: '000000' },
        paragraph: { spacing: { before: 280, after: 140 }, keepNext: true, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 24, bold: true, italics: true, color: '000000' },
        paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 2 } },
      { id: 'FigureCaption', name: 'FigureCaption', basedOn: 'Normal', run: { font: FONT, size: 20, italics: true } },
      { id: 'TableCaption', name: 'TableCaption', basedOn: 'Normal', run: { font: FONT, size: 20, italics: true } },
      { id: 'FrontTitle', name: 'Front Title', basedOn: 'Normal', run: { font: FONT, size: 30, color: '1F4E79' }, paragraph: { spacing: { after: 200 } } },
    ],
  },
  numbering: { config: [
    { reference: BULLET, levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: NUMBERED, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [
    { properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: cover() },
    { properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440, header: 700, footer: 600 } } }, ...headerFooter,
      children: [...body, ...refBlocks, ...appendices] },
  ],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  const missing = Object.keys(BIB).filter(k => !used.has(k));
  console.log(`written ${OUT} (${Math.round(buf.length / 1024)} KB); ${used.size} references cited, ${missing.length} in the bibliography not cited`);
});
