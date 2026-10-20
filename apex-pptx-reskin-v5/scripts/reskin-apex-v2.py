"""
APEX Template Reskin v2 — Complete approach
=============================================
1. Theme XML replacement (colors + fonts at theme level)
2. Font walk (catch hard-coded non-theme fonts)
3. Chart recoloring
4. Cover slide rebuild (match APEX Title Slide look: background + logos)
5. Font size adjustment per APEX spec

Usage:
    python reskin-apex-v2.py <source.pptx> [output.pptx] [--template <apex-template.pptx>]
"""

import sys
import os
import re
import shutil
import zipfile
from copy import deepcopy
from pathlib import Path
from lxml import etree

from pptx import Presentation
from pptx.util import Pt, Emu, Inches, Cm
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

# === APEX BRAND CONSTANTS ===
APEX_FONT_EN = "Avenir Next LT Pro"
APEX_FONT_CN = "Microsoft YaHei"
TITLE_COLOR = RGBColor.from_string("991BC5")
DEEP_PURPLE = RGBColor.from_string("310086")
BODY_COLOR = RGBColor.from_string("333333")
# Bar chart palette: purple + cyan contrast (user preference)
# Assign based on series count for maximum visual contrast
CHART_PALETTE_BY_COUNT = {
    1: ["8A2BE2"],                                      # 紫
    2: ["8A2BE2", "00E5FF"],                            # 紫 + 浅青
    3: ["8A2BE2", "00E5FF", "310086"],                  # 紫 + 浅青 + 深紫
    4: ["8A2BE2", "00E5FF", "310086", "008C95"],        # 紫 + 浅青 + 深紫 + 青
    5: ["8A2BE2", "00E5FF", "310086", "008C95", "5736CE"],
    6: ["8A2BE2", "00E5FF", "310086", "008C95", "5736CE", "00FDFD"],
}
APEX_CHART_FALLBACK = ["8A2BE2", "00E5FF", "310086", "008C95", "5736CE", "00FDFD"]

# Font size rules
COVER_TITLE_SIZE = Pt(40)
REF_SIZE = Pt(9)

TITLE_PH_TYPES = {1, 3}  # TITLE=1, CENTER_TITLE=3

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "1 APEX模板和参考页 1 (1).pptx"


def detect_language(prs):
    """Detect deck language (en/cn) from text content."""
    cjk_count = 0
    latin_count = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text
                cjk_count += len(re.findall(r'[\u4e00-\u9fff]', text))
                latin_count += len(re.findall(r'[a-zA-Z]', text))
    return "cn" if cjk_count > latin_count * 0.3 else "en"


def apply_apex_theme_xml(source_pptx, output_pptx, template_pptx):
    """Replace theme color scheme and font scheme with APEX values."""
    shutil.copy2(str(source_pptx), str(output_pptx))

    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

    with zipfile.ZipFile(str(template_pptx), 'r') as tz:
        apex_theme_xml = tz.read('ppt/theme/theme1.xml')
    apex_root = etree.fromstring(apex_theme_xml)
    apex_clr = apex_root.find('.//a:clrScheme', ns)
    apex_font = apex_root.find('.//a:fontScheme', ns)

    if apex_clr is None or apex_font is None:
        print("  WARNING: Could not extract APEX theme components")
        return

    with zipfile.ZipFile(str(output_pptx), 'r') as zr:
        all_files = zr.namelist()
        file_contents = {f: zr.read(f) for f in all_files}

    theme_files = [f for f in all_files if re.match(r'ppt/theme/theme\d+\.xml', f)]
    patched = 0

    for tf in theme_files:
        root = etree.fromstring(file_contents[tf])
        old_clr = root.find('.//a:clrScheme', ns)
        old_font = root.find('.//a:fontScheme', ns)

        if old_clr is not None:
            parent = old_clr.getparent()
            idx = list(parent).index(old_clr)
            parent.remove(old_clr)
            parent.insert(idx, deepcopy(apex_clr))
            patched += 1

        if old_font is not None:
            parent = old_font.getparent()
            idx = list(parent).index(old_font)
            parent.remove(old_font)
            parent.insert(idx, deepcopy(apex_font))

        file_contents[tf] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

    # Also patch master background to match APEX template (solidFill white)
    # This ensures layout-level background pictures are visible (bgRef may interfere)
    master_files = [f for f in all_files if re.match(r'ppt/slideMasters/slideMaster\d+\.xml', f)]
    pns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    ans = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    for mf in master_files:
        mroot = etree.fromstring(file_contents[mf])
        # Find existing <p:bg> and replace with solidFill white
        bg_elem = mroot.find('.//{%s}bg' % pns)
        if bg_elem is not None:
            parent = bg_elem.getparent()
            idx = list(parent).index(bg_elem)
            parent.remove(bg_elem)
            new_bg = etree.fromstring(
                '<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                '<p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
                '<a:effectLst/></p:bgPr></p:bg>'
            )
            parent.insert(idx, new_bg)
        file_contents[mf] = etree.tostring(mroot, xml_declaration=True, encoding='UTF-8', standalone=True)

    os.remove(str(output_pptx))
    with zipfile.ZipFile(str(output_pptx), 'w', zipfile.ZIP_DEFLATED) as zw:
        for fname, content in file_contents.items():
            zw.writestr(fname, content)

    print(f"  Theme XML: patched {patched} theme file(s)")


def walk_all_runs(slide):
    """Yield every text run in a slide (shapes, tables, groups)."""
    def _from_shape(shape):
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    yield run
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for para in cell.text_frame.paragraphs:
                        for run in para.runs:
                            yield run
        if shape.shape_type == 6:  # GROUP
            for child in shape.shapes:
                yield from _from_shape(child)

    for shape in slide.shapes:
        yield from _from_shape(shape)


def replace_fonts(prs, lang):
    """Replace all fonts to APEX standard."""
    target_font = APEX_FONT_EN if lang == "en" else APEX_FONT_CN
    changed = 0
    for slide in prs.slides:
        for run in walk_all_runs(slide):
            if run.font.name != target_font:
                run.font.name = target_font
                changed += 1
    print(f"  Fonts: updated {changed} text runs → {target_font}")


def recolor_charts(prs):
    """Recolor all chart series using purple + cyan contrast palette.
    Assigns colors based on series count for optimal visual contrast."""
    chart_count = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_chart:
                chart = shape.chart
                n_series = len(chart.series)
                # Pick palette based on series count
                palette = CHART_PALETTE_BY_COUNT.get(n_series, APEX_CHART_FALLBACK)
                for idx, series in enumerate(chart.series):
                    if idx < len(palette):
                        try:
                            fill = series.format.fill
                            fill.solid()
                            fill.fore_color.rgb = RGBColor.from_string(palette[idx])
                        except Exception:
                            pass
                chart_count += 1
    print(f"  Charts: recolored {chart_count} chart(s) (purple + cyan palette)")


def is_content_title_shape(shape):
    """Titles are often ordinary text boxes, not TITLE placeholders."""
    name = (getattr(shape, "name", None) or "")
    if name.startswith("标题") or "这里是标题" in name:
        return True
    if not getattr(shape, "is_placeholder", False):
        return False
    try:
        return int(shape.placeholder_format.type) in TITLE_PH_TYPES
    except Exception:
        return False


def iter_shapes(shape):
    yield shape
    if getattr(shape, "shape_type", None) == 6:
        for child in shape.shapes:
            yield from iter_shapes(child)


def recolor_titles(prs):
    """Style every content title — placeholders AND named title boxes.

    Non-placeholder titles do not inherit master titleStyle. Clearing color
    leaves Office red (#C00000) or inherit-black in place. Set explicit
    #991BC5 + bold so mixed Renji/Office pages match existing APEX pages.
    Skip slide 1 (cover).
    """
    count = 0
    for i, slide in enumerate(prs.slides, 1):
        if i == 1:
            continue
        for root in slide.shapes:
            for shape in iter_shapes(root):
                if not shape.has_text_frame or not is_content_title_shape(shape):
                    continue
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor.from_string("991BC5")
                        count += 1
    print(f"  Titles: styled {count} runs (#991BC5 bold; placeholders + 标题* boxes)")


OFFICE_COLOR_MAP = {
    "C00000": "991BC5",
    "4472C4": "310086",
    "2F5496": "310086",
    "5491FE": "9B7BF5",
    "5B9BD5": "5736CE",
    "70AD47": "008C95",
    "ED7D31": "FA0C73",
    "FFC000": "F5E94F",
    "222222": "333333",
    "44546A": "333333",
}


def recolor_office_text(prs):
    """Map leftover Office theme colors on ALL slides after the cover."""
    changed = 0
    for i, slide in enumerate(prs.slides, 1):
        if i == 1:
            continue
        for root in slide.shapes:
            shapes = list(iter_shapes(root))
            if root.has_table:
                for row in root.table.rows:
                    for cell in row.cells:
                        for para in cell.text_frame.paragraphs:
                            for run in para.runs:
                                try:
                                    hexcol = str(run.font.color.rgb)
                                except Exception:
                                    hexcol = None
                                if hexcol in OFFICE_COLOR_MAP:
                                    run.font.color.rgb = RGBColor.from_string(OFFICE_COLOR_MAP[hexcol])
                                    changed += 1
            for shape in shapes:
                if not shape.has_text_frame:
                    continue
                if is_content_title_shape(shape):
                    continue
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        try:
                            hexcol = str(run.font.color.rgb)
                        except Exception:
                            hexcol = None
                        if hexcol == "FFFFFF":
                            continue
                        if hexcol in OFFICE_COLOR_MAP:
                            run.font.color.rgb = RGBColor.from_string(OFFICE_COLOR_MAP[hexcol])
                            changed += 1
    print(f"  Office colors: remapped {changed} runs on all content slides")


def audit_brand_layer(prs):
    """Print leftover Office colors so a partial pass cannot be mistaken for done."""
    leftover = []
    for i, slide in enumerate(prs.slides, 1):
        if i == 1:
            continue
        hits = []
        for root in slide.shapes:
            for shape in iter_shapes(root):
                if not shape.has_text_frame:
                    continue
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if not (run.text or "").strip():
                            continue
                        try:
                            hexcol = str(run.font.color.rgb)
                        except Exception:
                            hexcol = None
                        if hexcol in OFFICE_COLOR_MAP:
                            hits.append(hexcol)
        if hits:
            leftover.append((i, len(hits), sorted(set(hits))))
    if leftover:
        print("  AUDIT leftover Office colors:")
        for i, n, colors in leftover:
            print(f"    slide {i}: {n} runs {colors}")
    else:
        print("  AUDIT: no leftover Office red/blue/orange on content slides")


def fix_font_sizes(prs):
    """
    Adjust font sizes per APEX spec (matching template last page):
    - Cover title (slide 1): 40pt (handled by rebuild_cover, but enforce here too)
    - Content slide titles: default 28pt
      - Long titles (>80 chars): allow down to 24pt (don't enlarge)
      - Short titles: force 28pt
    - Subtitle placeholder (OBJECT idx=12): 18pt
    - Keep reference/footer text as-is (already 9pt in source)
    """
    fixes = 0
    CONTENT_TITLE_DEFAULT = Pt(28)
    SUBTITLE_SIZE = Pt(18)
    LONG_TITLE_THRESHOLD = 80  # characters
    LONG_TITLE_MIN = Pt(24)

    for i, slide in enumerate(prs.slides, 1):
        for root in slide.shapes:
            for shape in iter_shapes(root):
                ph_type = ph_idx = None
                try:
                    if shape.is_placeholder:
                        ph_type = int(shape.placeholder_format.type)
                        ph_idx = shape.placeholder_format.idx
                except Exception:
                    pass

                if is_content_title_shape(shape) and shape.has_text_frame:
                    title_text = shape.text_frame.text
                    title_len = len(title_text)
                    for para in shape.text_frame.paragraphs:
                        for run in para.runs:
                            current = run.font.size
                            if i == 1:
                                if current != COVER_TITLE_SIZE:
                                    run.font.size = COVER_TITLE_SIZE
                                    fixes += 1
                            else:
                                if title_len > LONG_TITLE_THRESHOLD:
                                    if current is None or current > CONTENT_TITLE_DEFAULT:
                                        run.font.size = LONG_TITLE_MIN
                                        fixes += 1
                                else:
                                    if current is None or current != CONTENT_TITLE_DEFAULT:
                                        run.font.size = CONTENT_TITLE_DEFAULT
                                        fixes += 1

                elif ph_type == 7 and ph_idx == 12 and shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        for run in para.runs:
                            current = run.font.size
                            if current is None or current != SUBTITLE_SIZE:
                                run.font.size = SUBTITLE_SIZE
                                fixes += 1

    print(f"  Font sizes: {fixes} adjustments")


def rebuild_cover(prs, template_path):
    """
    Rebuild slide 1 to match the APEX template cover look.
    
    Key principle: background and logos go into the LAYOUT level (non-movable),
    only text styling stays at the slide level.
    
    Steps:
    - Inject background image + logos into source's cover LAYOUT
    - Clean slide-level decorations (old logos, shapes)
    - Style title: 40pt bold italic #991BC5
    - Style subtitle: white
    - Adjust positions to match template
    """
    template = Presentation(str(template_path))
    slide = prs.slides[0]
    
    # Switch cover to a dedicated Title Slide layout so cover chrome does not
    # bleed into content pages that share Blank/DEFAULT. Search every master:
    # Chinese decks name this layout 标题幻灯片, not "Title Slide".
    TITLE_LAYOUT_NAMES = {"title slide", "标题幻灯片"}
    title_slide_layout = None
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name.strip().lower() in TITLE_LAYOUT_NAMES:
                title_slide_layout = layout
                break
        if title_slide_layout is not None:
            break
    
    if title_slide_layout is None:
        # Fallback: use current layout
        source_layout = slide.slide_layout
    else:
        # Reassign slide to "Title Slide" layout via XML relationship
        from pptx.opc.constants import RELATIONSHIP_TYPE as RT
        # Remove old layout relationship and add new one
        slide_part = slide.part
        # Find and remove existing slideLayout relationship
        for rel in slide_part.rels.values():
            if "slideLayout" in rel.reltype:
                slide_part.drop_rel(rel.rId)
                break
        # Add relationship to title_slide_layout
        slide_part.relate_to(title_slide_layout.part, RT.SLIDE_LAYOUT)
        source_layout = title_slide_layout

    # Get the template's cover elements
    template_slide = template.slides[0]
    template_layout = template_slide.slide_layout

    # === Extract assets from template ===
    # All visual elements come from the template LAYOUT (background + all logos).
    # The template slide-level only has duplicate logos (APEX + APEX China) and
    # a separator line — we only take the line from slide level to avoid duplication.
    bg_image = None
    layout_logos = []
    for shape in template_layout.shapes:
        if shape.shape_type == 13:
            img = shape.image
            if shape.width > Inches(12):  # full-page background
                bg_image = {
                    'blob': img.blob,
                    'content_type': img.content_type,
                    'left': shape.left,
                    'top': shape.top,
                    'width': shape.width,
                    'height': shape.height,
                    'name': shape.name,
                }
            else:  # logos (APEX primary, APEX China, CAHST, Bayer)
                layout_logos.append({
                    'blob': img.blob,
                    'content_type': img.content_type,
                    'left': shape.left,
                    'top': shape.top,
                    'width': shape.width,
                    'height': shape.height,
                    'name': shape.name,
                })

    # From template slide: only extract the separator line (logos are already in layout)
    slide_line = None
    for shape in template_slide.shapes:
        if shape.shape_type == 9:  # line/connector
            slide_line = {
                'left': shape.left,
                'top': shape.top,
                'width': shape.width,
                'height': shape.height,
            }
            break

    # === Clean slide-level FIRST: remove decorative non-placeholder shapes ===
    # Keep text-bearing boxes — many finished decks put cover title/subtitle
    # in regular text boxes, not TITLE/SUBTITLE placeholders.
    sp_tree = slide.shapes._spTree
    shapes_to_remove = []
    for shape in slide.shapes:
        if shape.is_placeholder:
            continue
        has_text = False
        if shape.has_text_frame and shape.text_frame.text.strip():
            has_text = True
        if not has_text:
            shapes_to_remove.append(shape._element)
    for el in shapes_to_remove:
        sp_tree.remove(el)

    # === Inject into source LAYOUT (non-movable in normal edit mode) ===
    layout_sp_tree = source_layout.shapes._spTree
    
    # Remove existing non-placeholder shapes from layout
    layout_shapes_to_remove = []
    for shape in source_layout.shapes:
        if not shape.is_placeholder:
            layout_shapes_to_remove.append(shape._element)
    for el in layout_shapes_to_remove:
        layout_sp_tree.remove(el)
    
    from io import BytesIO
    from copy import deepcopy
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    from lxml import etree
    
    # Helper: add a picture to the layout with correct image relationship
    def add_picture_to_layout(layout, blob, left, top, width, height, send_to_back=False):
        """
        Add a picture to layout by:
        1. Adding to slide temporarily (slide has add_picture API)
        2. Getting the image part and its rId on the slide
        3. Creating a new relationship from layout part to the same image part
        4. Moving the XML element to layout spTree with updated rId
        """
        img_stream = BytesIO(blob)
        # Add to slide temporarily
        pic = slide.shapes.add_picture(img_stream, left, top, width, height)
        pic_elem = pic._element
        
        # Get the image rId from the blip element
        nsmap = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                 'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
        blip = pic_elem.find('.//p:blipFill/a:blip', nsmap)
        if blip is None:
            blip = pic_elem.find('.//a:blipFill/a:blip', nsmap)
        old_rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        
        # Get the image part from the slide's relationship
        slide_part = slide.part
        image_part = slide_part.rels[old_rId].target_part
        
        # Create relationship from layout part to the image part
        layout_part = layout.part
        new_rId = layout_part.relate_to(image_part, RT.IMAGE)
        
        # Update the blip element with new rId
        blip.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed', new_rId)
        
        # Remove from slide spTree
        sp_tree.remove(pic_elem)
        
        # Remove the now-orphaned relationship from slide
        slide_part.drop_rel(old_rId)
        
        # Add to layout spTree
        if send_to_back:
            layout_sp_tree.insert(2, pic_elem)
        else:
            layout_sp_tree.append(pic_elem)
        return pic_elem
    
    # Add background to layout
    if bg_image:
        add_picture_to_layout(
            source_layout, bg_image['blob'],
            bg_image['left'], bg_image['top'],
            bg_image['width'], bg_image['height'],
            send_to_back=True
        )

    # Add layout logos (APEX primary, APEX China, CAHST, Bayer) to layout
    for logo in layout_logos:
        add_picture_to_layout(
            source_layout, logo['blob'],
            logo['left'], logo['top'],
            logo['width'], logo['height']
        )

    # Add separator line to layout
    if slide_line:
        line_shape = slide.shapes.add_connector(
            1,  # straight connector
            slide_line['left'], slide_line['top'],
            slide_line['left'] + slide_line['width'],
            slide_line['top'] + slide_line['height']
        )
        line_shape.line.color.rgb = RGBColor.from_string("C7C9CB")
        line_shape.line.width = Pt(0.8)
        # Move from slide to layout
        line_elem = line_shape._element
        sp_tree.remove(line_elem)
        layout_sp_tree.append(line_elem)

    def _style_cover_title(shape):
        shape.left = Emu(int(0.58 * 914400))
        shape.top = Emu(int(2.98 * 914400))
        shape.width = Emu(int(7.02 * 914400))
        shape.height = Emu(int(2.03 * 914400))
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    run.font.bold = True
                    run.font.italic = True
                    run.font.size = COVER_TITLE_SIZE
                    run.font.color.rgb = RGBColor.from_string("991BC5")

    def _style_cover_subtitle(shape):
        shape.left = Emu(int(0.58 * 914400))
        shape.top = Emu(int(5.11 * 914400))
        shape.width = Emu(int(7.02 * 914400))
        shape.height = Emu(int(1.16 * 914400))
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(18)
                    # This template cover is pale-left / crystal-right, not full dark.
                    # Dark body text stays readable on the light title area.
                    run.font.color.rgb = RGBColor.from_string("333333")

    # === Style title and subtitle at slide level ===
    styled_title = False
    styled_subtitle = False
    for shape in slide.shapes:
        if not shape.is_placeholder:
            continue
        try:
            ph_type = shape.placeholder_format.type
        except Exception:
            continue
        if ph_type in (1, 3):  # TITLE / CENTER_TITLE
            _style_cover_title(shape)
            styled_title = True
        elif ph_type == 4:  # SUBTITLE
            _style_cover_subtitle(shape)
            styled_subtitle = True

    # Fallback: cover text lives in ordinary text boxes
    if not styled_title or not styled_subtitle:
        text_boxes = []
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                if shape.is_placeholder:
                    continue
                text_boxes.append(shape)
        text_boxes.sort(key=lambda s: s.top)
        if text_boxes and not styled_title:
            _style_cover_title(text_boxes[0])
            styled_title = True
        if len(text_boxes) > 1 and not styled_subtitle:
            _style_cover_subtitle(text_boxes[1])
            styled_subtitle = True

    added_items = []
    if bg_image:
        added_items.append("background→layout")
    added_items.append(f"{len(layout_logos)} logos→layout")
    if slide_line:
        added_items.append("separator→layout")
    print(f"  Cover rebuilt: {', '.join(added_items)} (all non-movable)")


def has_apex_layouts(prs):
    """Check if the deck already uses APEX layouts (with background pictures)."""
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if "Content page" in layout.name:
                for shape in layout.shapes:
                    if not shape.is_placeholder and shape.shape_type == 13:
                        if shape.width > Inches(12):  # full-page BG image
                            return True
    return False


def inject_content_backgrounds(prs, template_path):
    """
    Inject APEX Content page chrome into every content layout that does not
    already have a full-page background. Mixed decks (some APEX pages, some
    Office/Renji pages) still get the master background + footer logo on the
    non-APEX layouts. Cover layout is never touched.
    """
    # Extract assets from template's Content page layout
    template = Presentation(str(template_path))
    content_layout = None
    for master in template.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == "Content page":
                content_layout = layout
                break
        if content_layout:
            break
    
    if not content_layout:
        print("  WARNING: Cannot find 'Content page' layout in template")
        return
    
    # Full-page Content background already includes the bottom-right APEX mark.
    # Do not inject the separate footer logo or it doubles.
    bg = None
    for shape in content_layout.shapes:
        if shape.is_placeholder or shape.shape_type != 13:
            continue
        if shape.width > Inches(12):
            bg = {
                'blob': shape.image.blob,
                'left': shape.left,
                'top': shape.top,
                'width': shape.width,
                'height': shape.height,
            }
            break
    
    if not bg:
        print("  WARNING: Cannot find background image in template Content page layout")
        return
    
    from io import BytesIO
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    
    injected_layouts = set()
    cover_layout = prs.slides[0].slide_layout
    
    for i in range(1, len(prs.slides)):
        slide = prs.slides[i]
        layout = slide.slide_layout
        layout_name = layout.name or f"__unnamed_{id(layout)}"
        
        if layout is cover_layout:
            continue
        
        if layout_name in injected_layouts:
            continue
        
        has_bg = False
        for s in layout.shapes:
            if not s.is_placeholder and s.shape_type == 13 and s.width > Inches(12):
                has_bg = True
                break
        
        if has_bg:
            continue
        
        def _move_picture_to_layout(asset, send_to_back=False):
            layout_sp_tree = layout.shapes._spTree
            img_stream = BytesIO(asset['blob'])
            pic = slide.shapes.add_picture(
                img_stream, asset['left'], asset['top'], asset['width'], asset['height']
            )
            pic_elem = pic._element
            nsmap = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                     'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                     'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
            blip = pic_elem.find('.//p:blipFill/a:blip', nsmap)
            if blip is None:
                blip = pic_elem.find('.//a:blipFill/a:blip', nsmap)
            old_rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            slide_part = slide.part
            image_part = slide_part.rels[old_rId].target_part
            layout_part = layout.part
            new_rId = layout_part.relate_to(image_part, RT.IMAGE)
            blip.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed', new_rId)
            slide.shapes._spTree.remove(pic_elem)
            slide_part.drop_rel(old_rId)
            if send_to_back:
                layout_sp_tree.insert(2, pic_elem)
            else:
                layout_sp_tree.append(pic_elem)

        _move_picture_to_layout(bg, send_to_back=True)
        injected_layouts.add(layout_name)
    
    if injected_layouts:
        print(f"  Injected APEX master chrome into {len(injected_layouts)} layout(s): {', '.join(sorted(injected_layouts))}")
    else:
        print("  All layouts already have backgrounds")


def reskin(source_path, output_path, template_path):
    """Main reskin workflow."""
    source_path = Path(source_path).resolve()
    output_path = Path(output_path).resolve()
    template_path = Path(template_path).resolve()

    if not source_path.exists():
        print(f"ERROR: Source not found: {source_path}")
        sys.exit(1)
    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}")
        sys.exit(1)

    print(f"Source: {source_path}")
    print(f"Output: {output_path}")
    print(f"Template: {template_path}")
    print()

    # Step 1: Theme XML replacement
    print("[1/9] Applying APEX theme (color + font schemes)...")
    apply_apex_theme_xml(source_path, output_path, template_path)

    # Step 2-6: python-pptx modifications
    prs = Presentation(str(output_path))
    lang = detect_language(prs)
    print(f"  Language: {lang}")
    print()

    # Step 2: Rebuild cover slide
    print("[2/9] Rebuilding cover slide with APEX Title Slide look...")
    rebuild_cover(prs, template_path)
    print()

    # Step 3: Inject content backgrounds (for non-APEX source decks)
    print("[3/9] Checking content slide backgrounds...")
    inject_content_backgrounds(prs, template_path)
    print()

    # Step 4: Replace fonts
    print("[4/9] Replacing fonts...")
    replace_fonts(prs, lang)
    print()

    # Step 5: Recolor charts
    print("[5/9] Recoloring charts...")
    recolor_charts(prs)
    print()

    # Step 6: Recolor titles (placeholders + named 标题 boxes)
    print("[6/9] Recoloring titles...")
    recolor_titles(prs)
    print()

    # Step 7: Fix font sizes
    print("[7/9] Adjusting font sizes...")
    fix_font_sizes(prs)
    print()

    # Step 8: Map leftover Office colors on every content slide
    print("[8/9] Remapping Office colors on all content slides...")
    recolor_office_text(prs)
    print()

    # Step 9: Full-deck audit — do not stop after checking the second half
    print("[9/9] Auditing all slides for leftover Office colors...")
    audit_brand_layer(prs)
    print()

    # Save
    prs.save(str(output_path))
    print(f"✓ Done! Output: {output_path}")
    print(f"  Slides: {len(prs.slides)}")
    print(f"  Language: {lang}")
    print(f"  Font: {APEX_FONT_EN if lang == 'en' else APEX_FONT_CN}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Reskin a PPTX with APEX template (v2 - full cover rebuild + font sizes)")
    parser.add_argument("source", help="Source .pptx file to reskin")
    parser.add_argument("output", nargs="?",
                        help="Output .pptx path (default: <source>_APEX.pptx)")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE),
                        help="APEX template .pptx (default: skill root template)")
    args = parser.parse_args()

    source = Path(args.source)
    if args.output:
        output = Path(args.output)
    else:
        output = source.parent / f"{source.stem}_APEX{source.suffix}"

    reskin(source, output, args.template)


if __name__ == "__main__":
    main()
