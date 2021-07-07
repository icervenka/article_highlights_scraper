# Article highlight scraper

Simple scraper that extract recently published articles from major journals (Cell, Science, Nature) and saves the highlights as a jpg image. The script was meant to be run as an everyday cronjob, with resulting jpg files served by Plex via Wi-Fi to a TV placed in the corridor or in the office.

## Example usage
Downloads highlights from Cell journal website and saves the resulting image in the current directory. Uses `arial.ttf` and `arial_bold.ttf` located in the current directory as fonts.

`
article_scraper.py --journal cell --font_dir . --font_face arial arial_bold --outdir .
`

## Requirements
Truetype font and optionally its emphasized form (bold, italic etc.) for titles.
Directory where the fonts are stored and the basename of the font faces are
specified in separate arguments. Output directory needs to be writable.

## Result
![Cell news](cell_news_example.jpg)

## Issues
- Function for extracting HTML needs to updated whenever the layout of the journal website changes.
- Highlights that are missing one of the required parts (image, title, autors, commentary) are skipped.

Last updated: 2021-07-07.
