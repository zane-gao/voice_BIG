# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## mode
- mode: custom
- mode_behavior: Three-act product-defense narrative. Act 1 starts from user workflow and product pain, Act 2 introduces MMSB-Graph as the structural engine, Act 3 closes with evaluation, engineering loop, boundary, and contributions. Titles should be claim-like and speaker notes should connect product value to research support.

## visual_style
- visual_style: soft-rounded

## colors
- bg: #F8FAFC
- surface: #FFFFFF
- primary: #155E75
- accent: #0F766E
- secondary_accent: #2563EB
- text: #172033
- text_secondary: #475569
- text_tertiary: #94A3B8
- border: #CBD5E1
- success: #16A34A
- warning: #F59E0B
- soft_teal: #CCFBF1
- soft_blue: #E0F2FE
- soft_amber: #FEF3C7
- soft_green: #DCFCE7

## typography
- font_family: "Microsoft YaHei", Arial, sans-serif
- emphasis_family: SimHei, "Microsoft YaHei", Arial, sans-serif
- code_family: Consolas, monospace
- body: 20
- title: 36
- subtitle: 26
- annotation: 15
- cover_title: 64
- footer: 12

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: pencil, microphone, network, route-2, device-desktop, file-export, json, photo, speakerphone, database, chart-dots, test-pipe, layers-linked, server, git-branch, target, bulb, wand, presentation, video, chart-bar, code, movie, player-play, player-record, timeline

## images
- mmsb_diagnostics: images/mmsb_diagnostics.png | no-crop

## page_rhythm
- P01: anchor
- P02: breathing
- P03: dense
- P04: dense
- P05: breathing
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: dense
- P13: breathing
- P14: anchor

## page_charts
- P03: basic_table
- P04: icon_grid
- P05: pipeline_with_stages
- P06: layered_architecture
- P08: vertical_pillars
- P09: process_flow
- P10: icon_grid
- P11: basic_table
- P12: circular_stages
- P13: vertical_list

## forbidden
- Mixing icon libraries
- rgba()
- `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<script>`, `<iframe>`, `<symbol>`+`<use>`
- `<g opacity>` (set opacity on each child element individually)
- HTML named entities in text (`&nbsp;`, `&mdash;`, `&copy;`, `&ndash;`, `&reg;`, `&hellip;`, `&bull;`)
