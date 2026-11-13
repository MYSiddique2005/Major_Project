#!/usr/bin/env bash
# Rebuilds every research document and copies it to ~/Documents/IntelliERP:
#   1-Final-Submission/  FYP report (.docx and .pdf) and poster (.pdf and .png)
#   2-Publication/       journal paper and conference paper (.pdf and .docx)
#   bash Research/build-all.sh
# Needs pdflatex and bibtex (with IEEEtran), Node.js with `npm install` done in Research/report, Google Chrome
# for the figures and the poster, and LibreOffice for the report's PDF (Word can also save it as PDF).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HOME/Documents/IntelliERP"
mkdir -p "$OUT/1-Final-Submission" "$OUT/2-Publication"

# LaTeX: a local TeX Live install and the IEEEtran class, if they are set up this way
[ -f "$HOME/.local/tex/env.sh" ] && . "$HOME/.local/tex/env.sh"
export TEXINPUTS=".:$HOME/texmf/tex/latex/ieeetran//:" BSTINPUTS=".:$HOME/texmf/tex/latex/ieeetran//:"

latex() {  # folder, main file (without .tex), name of the copy in 2-Publication
  (cd "$HERE/$1" &&
    pdflatex -interaction=nonstopmode "$2" >/dev/null && bibtex "$2" >/dev/null &&
    pdflatex -interaction=nonstopmode "$2" >/dev/null && pdflatex -interaction=nonstopmode "$2" | grep "Output written" &&
    cp "$2.pdf" "$OUT/2-Publication/$3" &&
    rm -f "$2".{aux,bbl,blg,log,out})
}
latex journal trace IntelliERP-Journal-Paper.pdf
latex paper intellierp IntelliERP-Conference-Paper.pdf
rm -f "$HERE/journal/trace.pdf"   # the copy in ~/Documents is the one to use; paper/intellierp.pdf stays tracked

# Word versions of both papers (editable text and tables, figures as images)
node "$HERE/word/build-docx.js"

# FYP report: figures, then the Word file, then a PDF through LibreOffice
(cd "$HERE/report" && node make-figures.js >/dev/null && node render.js >/dev/null && node build.js)
DOCX="$OUT/1-Final-Submission/IntelliERP-FYP-Report.docx"
PROFILE="$HERE/report/render/lo4"   # a LibreOffice profile holding the ExportPdf macro, which also updates the contents lists
if [ -d "$PROFILE" ] && command -v libreoffice >/dev/null; then
  cp "$DOCX" "$HERE/report/render/r.docx"
  timeout 280 libreoffice -env:UserInstallation="file://$PROFILE" --headless \
    "macro:///Standard.Module1.ExportPdf(\"$HERE/report/render/r.docx\",\"$HERE/report/render/out.pdf\")"
  mv "$HERE/report/render/out.pdf" "$OUT/1-Final-Submission/IntelliERP-FYP-Report.pdf"
  rm -f "$HERE/report/render/r.docx"
  echo "written $OUT/1-Final-Submission/IntelliERP-FYP-Report.pdf"
else
  echo "Report PDF not made: open the .docx in Word, update the table of contents and save as PDF."
fi

# Poster
(cd "$HERE/poster" && node build.js)
