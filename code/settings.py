# game setup
WIDTH = 1280
HEIGTH = 720
FPS = 60
TILESIZE = 64

# weapons
weapon_data = {
    'sword': {'cooldown': 100, 'damage': 15, 'graphic': r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\weapons\sword\full.png'},
    'lance': {'cooldown': 400, 'damage': 30, 'graphic': r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\weapons\lance\full.png'},
    'axe': {'cooldown': 300, 'damage': 20, 'graphic': r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\weapons\axe\full.png'},
    'rapier': {'cooldown': 50, 'damage': 8, 'graphic': r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\weapons\rapier\full.png'},
    'sai': {'cooldown': 80, 'damage': 10, 'graphic': r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\weapons\sai\full.png'}
}

# WORLD_MAP = [
# ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
# ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ','p',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ','x','x','x','x','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x','x',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ',' ','x',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ','x','x','x','x','x',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ',' ','x','x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ',' ',' ','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
# ['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
# ]


# The game is absolutely unscalable (may be you will rewrite it later in the video 
# You call update method for all visible objects when in fact only player has update method. 
# You check collisions with all obstacles when you can check only with objects in small area around player. 
# And it absolutely blew my mind when you decided to sort all objects before drawing at each frame. 
# When the only thing which changes the relative position is player!
# To be more constructive. The usual way to deal with collisions is geohash. 
# You have to store your collidable objects in a hashmap with rounded coordinates as keys. 
# Then you have constant complexity of computing collisions.
# And you can store static objects in sorted group apart from dynamic 
# then at each step you will have to sort only dynamic object which are present on the screen. 
# Keeping in mind that you usually have way more static objects than dynamic, 
# it will be a significant reduce in computational complexity.
