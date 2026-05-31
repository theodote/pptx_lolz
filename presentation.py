import players as pl
from pptx import Presentation
from pptx.util import Emu, Inches
from pathlib import Path
import random

import re
import time

def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    name = name.strip('. ')
    return name or f"I tried to break the game {time.time_ns()}"



presentations_path = Path("./presentations")

def generate(player: pl.Player, title_text: str, subtitle_text: str, slide_paths: list):
    prs = Presentation()
    # prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)  # make it 16/9
    # ...or don't! things are no longer centered :(
    
    title_slide_layout = prs.slide_layouts[0]
    title_slide = prs.slides.add_slide(title_slide_layout)
    
    title = title_slide.shapes.title
    subtitle = title_slide.placeholders[1]
    title.text = title_text
    subtitle.text = f"{subtitle_text}\n\n{player.first_name} {player.last_name}"
    
    blank_slide_layout = prs.slide_layouts[6]
    for slide_path in slide_paths:
        slide = prs.slides.add_slide(blank_slide_layout)
        
        pic = slide.shapes.add_picture(str(slide_path), 0, 0, width=prs.slide_width)
        if pic.height > prs.slide_height:
            pic.width, pic.height = Emu(pic.width * prs.slide_height / pic.height), prs.slide_height
            
        pic.left = Emu((prs.slide_width - pic.width) / 2)
        pic.top = Emu((prs.slide_height - pic.height) / 2)
        
    end_slide_layout = title_slide_layout
    end_slide = prs.slides.add_slide(end_slide_layout)
    
    thanks = end_slide.shapes.title
    name_surname = end_slide.placeholders[1]
    thanks.text = "Thank you for your attention."
    name_surname.text = f"{player.first_name} {player.last_name}"
    
    prs_path = presentations_path / f"{sanitize_filename(player.first_name)}.pptx"
    prs.save(prs_path)
    
generate(pl.players[403545875], "THE TITLE", "and the subtitle", pl.players[403545875].slide_paths)