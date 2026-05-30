from pathlib import Path
from telegram import User
import json

players = {}

players_path = Path("players")
image_formats = ['.png', '.jpg', '.jpeg', '.gif']

class Player:
    def __init__(self, *, user: User | None = None, id: int | None = None):
        if (user is None) ^ (id is None):
            raise TypeError("Either User or ID should be provided, but not both")
        
        if user:    # for creating new players
            self.id = user.id
            
            self.firstname = user.first_name
            self.lastname = user.last_name
            self.username = user.username
        if id:      # for loading players from dirs
            self.id = id
        
        self.path = players_path / Path(self.id)
        self.user_path = self.path / Path("user.json")
        if id:
            with open(self.user_path, 'r') as f:
                user_data = json.load(f)
            self.firstname = user_data['first_name']
            self.lastname = user_data['last_name']
            self.username = user_data['username']
        Path.touch(self.user_path)
        
        self.titles_path = self.path / Path(f"titles.json")
        with open(self.titles_path, 'r') as f:
            self.titles = json.load(f)
        self.subtitles_path = self.path / Path(f"subtitles.json")
        with open(self.subtitles_path, 'r') as f:
            self.subtitles = json.load(f)
        
        self.image_paths = [
            path
            for path in Path(".").iterdir()
            if path.is_file()
            and path.suffix.lower() in image_formats
        ]
        
    def add_image(self):
        pass
        
def load_players():
    ids = [
        int(path.name)
        for path in players_path.iterdir()
        if path.is_dir()
    ]
    
    players = { id: Player(id) for id in ids }