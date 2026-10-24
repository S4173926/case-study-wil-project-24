# Presentation source

The checked-in PowerPoint is the original pre-presentation file. It has not been regenerated
or restyled during this cleanup.

The build script requires Node.js and these packages:

```bash
npm install --no-save pptxgenjs react react-dom react-icons sharp jszip
node build.js
```

Run these commands inside this directory. Rebuilding overwrites the local PowerPoint; keep
an original copy when comparing output. The local `apply_theme.js` helper copies `theme.xml`
into the generated presentation. `theme.xml` was extracted from the existing PowerPoint,
including its colour and font definitions. No font files are included.

Dependency versions were not recorded in the original project. A fresh build with newer
packages is not guaranteed to be byte-identical or visually identical to the original file.
