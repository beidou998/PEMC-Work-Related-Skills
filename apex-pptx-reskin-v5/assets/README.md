# Asset Inventory

All assets were derived from an authorized English APEX 2024 reference presentation during skill development. The original content presentation is not required at runtime and is intentionally not included in this distributable skill. These assets contain no study data, medical diagrams, patient photos, scans, or patient information.

The APEX and Bayer marks remain protected brand assets. Distribute and use this skill only within an environment where the recipient is authorized to use those marks. Do not publish the package or use the marks for unrelated organizations, projects, or external materials without approval.

## Native PowerPoint Master Source

### `source-master-layouts.pptx`

- Source: created directly from the English presentation by adding four empty slides bound to the source layouts, deleting the seven content slides, and removing every unused layout.
- Contains exactly four layouts used by the source: `Title Slide`, `1_Content page`, `Content_Columns`, and `Patient case_Option 2`.
- Keeps the original PowerPoint layout objects, original media, positions, crops, placeholders, and stacking order.
- Contains no study content, medical diagrams, patient photo, scan, research chart, or patient information.
- Use: preferred starting point for generating a new deck. Duplicate the appropriate empty slide or inherit its layout, then add new editable content.

### `master-objects.json`

- Machine-readable record of every relevant source layout object.
- Records design name, layout name, source slide, PowerPoint object name, embedded media name, position, size, crop values, fill color, and whether an item came from the layout or from the source slide itself.
- Use: exact reconstruction and automated placement.

## Master Elements and Components

### `element-cover-crystal-visual.png`

- Source: derived from `Picture 7` in the English `Title Slide` layout, whose original embedded media is `ppt/media/image2.png`.
- Content: transparent PNG containing only the faceted crystal composition, pale geometric surfaces, and its original shadows. The smooth grey slide background has been removed.
- Use: cover pages only. Create the pale neutral background as a native PowerPoint master fill, then place this element at the right edge. Keep its aspect ratio and allow the artwork to run off the top, right, and bottom edges as in the source.
- Important: the source visual was originally flattened over a pale grey photographic background. The transparent version is a careful extraction rather than an original layered source file.

### `element-content-corner-crystals.png`

- Source: derived from the original full-width picture objects in `1_Content page`, `Content_Columns`, and `Patient case_Option 2`; all use embedded `ppt/media/image9.png`.
- Content: transparent PNG containing only the crystal corner. The white background and bottom-right APEX mark are not included.
- Use: place as an independent object at the top-right edge of standard body, data, chart, mechanism, comparison, and case masters. Use a native white slide fill and place `logo-apex-primary.png` separately at bottom right.

### `component-case-sidebar.png`

- Source: reconstructed directly from `Picture 18` in the English `Patient case_Option 2` layout and embedded `ppt/media/image12.png`, using the layout's original crop values (`left=4.2%`, `bottom=1.875%`).
- Content: dark-purple vertical panel with faceted crystal decoration; no patient data or photo.
- Use: as the left panel on a case page. Preserve its proportions. Add a separate circular photo placeholder and newly supplied case text.

### `layout-case-blank.png`

- Source: rendered directly from the layout used by English slide 7 after deleting every slide-level object.
- Content: blank 16:9 case-page reference with the original sidebar, empty circular photo area, top-right crystal corner, and bottom-right APEX mark.
- Use: visual reference only. Do not use it as a production background; construct the case master from a native white fill, `element-content-corner-crystals.png`, `logo-apex-primary.png`, and `component-case-sidebar.png`.

## Logos

### `logo-apex-2024.png`

- Source: embedded `ppt/media/image21.png`, placed at the top left of English slide 1.
- Content: APEX 2024 logo and its original subtitle.
- Use: the left half of the cover's paired project branding. Do not recolor, stretch, crop, or separate the subtitle.

### `logo-apex-china.png`

- Source: embedded `ppt/media/image20.png`, placed at the top left of English slide 1.
- Content: APEX CHINA logo.
- Use: the right half of the cover's paired project branding. Do not recolor, stretch, or crop.

### `logo-apex-primary.png`

- Source: embedded `ppt/media/image10.png`, used in the supplied APEX layouts.
- Content: standalone APEX project logo.
- Use: only when a standalone APEX mark is needed instead of the paired cover lockup. Do not recolor, stretch, or crop.

### `logo-bayer.emf`

- Source: embedded `ppt/media/image3.emf`, used by the English slide 1 title layout as the Bayer corporate mark.
- Content: original vector Bayer logo.
- Use: top right of the cover, immediately right of `logo-cahst.png`, when Bayer branding is required and approved. Keep its aspect ratio and original colors. Prefer this EMF over a screenshot or manually recreated logo.
- Position updated 2026-08: moved from bottom-left (`x=0.5758, y=6.6699`) to top-right (`x=12.5841, y=0.1667`) to match the official 4-page master template `1 APEX模板 共4页.pptx` (external file, not distributed). The artwork itself is unchanged (confirmed byte-identical via MD5).

### `logo-cahst.png`

- Source: extracted from `图片 8` in the 2026-08 4-page master template `1 APEX模板 共4页.pptx` (external file, not distributed).
- Content: green circular partner badge for 中国人体健康科技促进会 (China Association for Promotion of Health Science and Technology).
- Use: top right of the cover, immediately left of `logo-bayer.emf`. Do not recolor, stretch, or crop.

## Fonts

No font files are included. The source deck does not embed reusable font files, and fonts must only be distributed under their licenses.

- English primary: Avenir Next LT Pro.
- English fallback: Arial.
- Chinese: Microsoft YaHei (`微软雅黑`), with Arial for Latin characters and numbers where suitable.
- The source uses bold weights heavily for titles, key numbers, and conclusions.

## Master Placement

The source canvas is 13.333333 × 7.5 inches. The following values reproduce the original composition and may be adjusted only when the artwork still touches the same slide edges:

- Cover crystal visual: right aligned; approximately `x=6.33 in`, `y=0`, `w=7.00 in`, `h=7.50 in`. Crop only by the slide boundary.
- Content corner crystals: right aligned; approximately `x=11.80 in`, `y=0`, `w=1.53 in`, `h=2.20 in`.
- Content APEX logo: approximately `x=12.14 in`, `y=7.07 in`, `w=0.98 in`, `h=0.30 in`.
- Case sidebar: left aligned; approximately `x=0.13 in`, `y=0`, `w=2.89 in`, `h=7.36 in`. The source layout also places a native dark-purple rectangle behind the left panel.
- Cover Bayer logo: top right; approximately `x=12.58 in`, `y=0.17 in`, `w=0.56 in`, `h=0.56 in`.
- Cover partner badge (`logo-cahst.png`): top right, left of the Bayer logo; approximately `x=11.75 in`, `y=0.08 in`, `w=0.73 in`, `h=0.73 in`.

The title, body, citations, and case fields must remain editable PowerPoint objects; they are not image assets.

Exact original layout-object coordinates and crop values are in `master-objects.json`. Values in `theme.json` describe placement of the separately extracted transparent elements.

## Not Included

- No agenda, divider, summary, closing, or thank-you decoration: these page types do not occur in the actual seven-slide deck.
- No medical mechanism illustrations, charts, study tables, scans, patient portraits, or case data: these are content, not reusable design assets.
- No generic footer text: citations and abbreviations vary by page and should remain editable.
- No flattened cover or content background: master fill, crystal artwork, and logos must remain separate objects.
