# DESIGN.md

Design system for ahmadidrisofficial.com. Written 30 August 2026, replacing the first look after feedback that the site read as machine generated.

Dials: DESIGN_VARIANCE 7, MOTION_INTENSITY 3, VISUAL_DENSITY 3. Redesign, overhaul. Mode is Persuade on the homepage and Read on the guides and case studies.

## 1. The world

A serious printed publication. University press rather than consultancy deck. The page should feel set rather than assembled: paper ground, ink type, hairlines instead of boxes, and enough air that the reader trusts the writing before reading it.

The one cultural reference is a colour with real provenance. The primary hue is the indigo of the Kofar Mata dye pits in Kano, in continuous use for over five hundred years. It is a colour, not a pattern, not a map, and not a flag. If asked, the reference is explainable in a sentence. Nothing else on the site gestures at heritage.

## 2. Colour

    --paper      #F3F1EA   unbleached ground, every page
    --paper-2    #E7E4DA   one shade down, used rarely
    --ink        #14192B   off black with a blue cast, all body text
    --indigo     #2A3D77   the dye colour, links and the rare fill
    --indigo-dp  #1B2547   the single dark surface
    --clay       #8F4526   warm accent, used once per page at most
    --muted      #565B6C   secondary text, 4.5:1 on paper
    --rule       #D6D2C6   hairlines

Rules. Ink is for type, not for large blocks. The old design put a navy slab behind the hero and another behind the statistics; there is now at most one dark surface on any page and the homepage does not use it. Gold is gone entirely. No gradient anywhere. Colour never carries meaning on its own.

## 3. Type

Fraunces for display, optical size at the top of its range so the contrast is real, tracking down to -0.03em, weight 600. It was already in the build and was being used at magazine-caption size, which wasted it.

Newsreader for body and for interface text, replacing Inter. It is built for reading on screen, it has character in the italic, and it suits a site whose longest pages are guides people actually read.

Measure 65 to 75 characters. Display capped at 6rem. Obvious steps between levels, never four similar sizes. Numbers in tabular figures wherever they sit in a column.

## 4. Structure

No eyebrows. Not one. The small uppercase label above a heading is the single clearest sign that a page was generated, and the heading carries its own weight.

Cards only where the reader picks one of several parallel things. Lists of work, of areas, of anything the reader reads rather than chooses, are set as typographic indexes: a rule, a title, a line of description, a year, and space. Never a grid of equal boxes with coloured top borders.

Section rhythm varies on purpose. Full width, then a narrow measure, then a two column split. If three consecutive sections have the same shape, one of them is wrong.

Navigation is five items. Work, Build, Writing, About, Contact.

## 5. Surface craft

Text selection, caret, focus ring, scrollbar, and underline offset are all themed. Links carry a 0.14em underline offset and a 1px rule that thickens on hover rather than appearing on hover. Focus rings are visible, 2px, clay, with an offset.

Shadows carry offset and blur or they are not used. No zero offset halos, no hard block shadows, no glass.

## 6. Motion

One authored moment on a page, and none of it required. The hero settles once on load. Everything else is state: hover, focus, the row that shifts four pixels under the cursor. Exponential ease out, 180 to 320ms. Under prefers-reduced-motion every animation resolves to its end state immediately.

## 7. Never

Eyebrows and kickers. Section numbers. Equal card grids as page structure. Coloured top borders on cards. The big number statistics band. Decorative glyphs as separators. Hand drawn decorative SVG standing in for an idea, including the swooping line that used to sit behind the hero. Emoji as icons. Gradient text. Scroll cues. Locale or time strips. Em dashes and en dashes, anywhere, in any file.
