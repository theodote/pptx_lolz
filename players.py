from pathlib import Path
from telegram import User, File
import json
import asyncio
import imageio
from collections import UserDict

slide_formats = ['.png', '.jpg', '.jpeg', '.gif']

MAX_SLIDES = 10
MAX_TITLES = 3
MAX_SUBTITLES = 3

class Player:
    def __init__(self, *, user: User | None = None, id: int | None = None):
        if not (user is None) ^ (id is None):
            raise TypeError("Either User or ID should be provided, but not both")
        
        if id:      # for loading players from dirs
            self.id = id
        if user:    # for creating new players
            self.id = user.id
            self.first_name = user.first_name
            self.last_name = user.last_name or ''
            self.username = user.username
        
        global players
        self.path = players_path / Path(str(self.id))
        self.user_path = self.path / Path("user.json")
        self.titles_path = self.path / Path(f"titles.json")
        self.subtitles_path = self.path / Path(f"subtitles.json")
        
        self.path.mkdir(exist_ok=True)
        self.user_path.touch()
        self.titles_path.touch()
        self.subtitles_path.touch()
        
        self.slide_paths = []
        self.update_slides()
        
        self.titles = []
        self.subtitles = []
        if id:      # player already exists. calling a new player by ID is an error
            with open(self.user_path, 'r') as f:
                user_data = json.load(f)
            self.first_name = user_data['first_name']
            self.last_name = user_data['last_name'] or ''
            self.username = user_data['username']
            with open(self.titles_path, 'r') as f:
                self.titles = json.load(f)
            with open(self.subtitles_path, 'r') as f:
                self.subtitles = json.load(f)
                
        self.save()
    
    @property
    def count_slides(self): return len(self.slide_paths)
    @property
    def count_titles(self): return len(self.titles)
    @property
    def count_subtitles(self): return len(self.subtitles)
    
    @property
    def remaining_slides(self): return MAX_SLIDES - self.count_slides
    @property
    def remaining_titles(self): return MAX_TITLES - self.count_titles
    @property
    def remaining_subtitles(self): return MAX_SUBTITLES - self.count_subtitles
    
    def update_slides(self):
        self.slide_paths = [
            path
            for path in self.path.iterdir()
            if path.is_file()
            and path.suffix.lower() in slide_formats
        ]
    
    async def save_slide(self, attachment, extension=None) -> Path:
        if extension is None:
            if attachment.file_name is not None:
                extension = attachment.file_name.split('.')[-1]
            else:
                extension = 'mp4'   # for imageio
        file_name = f"{self.count_slides + 1}.{extension}"
        file_path = self.path / Path(file_name)
        file = await attachment.get_file()
        
        await file.download_to_drive(file_path)
        self.update_slides()
        return file_path
    
    async def save_gif(self, attachment) -> Path:
        mp4_path = await self.save_slide(attachment)
        
        def convert_to_gif(mp4_path):
            gif_path = Path(mp4_path.parent) / Path(f"{mp4_path.stem}.gif")
            with imageio.get_reader(mp4_path) as reader:
                fps = reader.get_meta_data()['fps']
                frames = [frame for frame in reader]
            
            imageio.mimsave(gif_path, frames, fps=fps)
            mp4_path.unlink()
            return gif_path
        
        gif_path = await asyncio.to_thread(convert_to_gif, mp4_path)
        
        self.update_slides()
        return gif_path
        
    def save_title(self, title):
        self.titles.append(title)
        self.save_titles()
    def save_subtitle(self, subtitle):
        self.subtitles.append(subtitle)
        self.save_subtitles()
        
    def save_user(self):
        with open(self.user_path, 'w') as f:
            user_data = {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'username': self.username,
            }
            json.dump(user_data, f)
    def save_titles(self):
        with open(self.titles_path, 'w') as f:
            json.dump(self.titles, f)
    def save_subtitles(self):
        with open(self.subtitles_path, 'w') as f:
            json.dump(self.subtitles, f)
    def save(self):
        self.save_user()
        self.save_titles()
        self.save_subtitles()
        
    def clear_slides(self):
        for path in self.slide_paths:
            path.unlink()
        self.update_slides()
    def clear_titles(self):
        self.titles.clear()
        self.save_titles()
    def clear_subtitles(self):
        self.subtitles.clear()
        self.save_subtitles()
        
class Players(UserDict):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.path.mkdir(exist_ok=True)
        ids = [
            int(path.name)
            for path in self.path.iterdir()
            if path.is_dir()
        ]
        self.update({ id: Player(id=id) for id in ids })
    def save(self):
        for player in self.values():
            player.save()
        
players_path = Path("./players")
players = Players(players_path)
        
# def load_players():
#     global players
#     players_path.mkdir(exist_ok=True)
#     ids = [
#         int(path.name)
#         for path in players_path.iterdir()
#         if path.is_dir()
#     ]
    
#     players = { id: Player(id=id) for id in ids }
    
# def save_players():
#     for player in players:
#         player.save()