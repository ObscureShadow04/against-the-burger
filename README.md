# impending-doom

## Demo
Demo Video: <https://docs.google.com/presentation/d/1czC6vO1hhIFtTyRtIhtRMDZ7D9ge0V0zTaWBF4rLAtI/edit?usp=sharing>

## GitHub Repository
GitHub Repo: <https://github.com/ObscureShadow04/impending-doom.git>

## Description

### What Is The Program?
Impending Doom is a game in which the player controls a small spaceship and is tasked with defeating a Giant Killer Space Robot (abbreviated as G.K.S.R.) before it reaches planet Earth. The wacky concept seeks to emulate the feeling of a flash game from the early 2000s, while the art style takes inspiration from 16-bit games from the late 1980s and early 1990s.

### How Does The Game Work?
As it approaches Earth, the G.K.S.R. fires a wave of projectiles that travel toward the player. The player must use their tiny spaceship to *vertically* dodge the incoming projectiles and return fire on the G.K.S.R. The player is limited by the fact that they cannot move and shoot at the same time, requiring the player do so strategically. The player starts the game with 5 hitpoints, whereas the G.K.S.R. starts with 140 hitpoints. Both the player and the G.K.S.R's projectiles deal 1 hitpoint worth of damage.

To win the game, the player must fully deplete the G.K.S.R's hitpoints (represented by a red bar on the top right of the game window) ***before*** the G.K.S.R.'s ETA to Earth reaches 0 (represented by a purple bar at the top of the game window, which depletes after 70 seconds).

As the player depletes the G.K.S.R.'s hitpoints, the G.K.S.R. goes through 3 "attack phases" in which the its attacks become more frequent and difficult to avoid:
- Phase 1 lasts from 100-66% hitpoints. It fires projectiles from 5 of its 8 possible projectile origins every 2.0 seconds
- Phase 2 lasts from 66-33% hitpoints. It fires projectiles from 6 of its 8 possible projectile origins every 1.5 seconds
- Phase 3 lasts from 33-0% hitpoints. It fires projectiles from 7 of its 8 possible projectile origins every 1.0 seconds

The G.K.S.R.'s attack phase is visually inidcated by a change in the G.K.S.R.'s sprites.

The G.K.S.R. also has a random chance to drop powerups which can aid the player in different ways. There are a total of 3 unique powerups the player can collect for a temporary buff:
- 2x FireRate: doubles the rate at which the player's spaceship fires projectiles for 5 seconds, allowing for increased damage to the G.K.S.R.
- Increase MoveSpeed: doubles the speed at which the player's spaceship moves vertically for 5 seconds, allowing the player to dodge the G.K.S.R.'s projectile waves more easily
- Health: increases the players hitpoints by 1 hitpoint if it isn't already at max hitpoints

The active powerup is displayed in a box next to the player's hitpoints (represented by a blue bar on the top left of the game window). The G.K.S.R initially has a 40/100 chance to shoot a powerup per each projectile wave, but the chance decreases by 10/100 per each attack phase. Additionally, the player is limited on when they can collect a powerup. If the player has an powerup active on them, they are unable to collect another powerup for the time of the powerup's duration.

### Files and Directories
The first and most important directory within the src folder is the **images** folder. This cointains all of the sprites for the player, the G.K.S.R., their projectiles, the powerups, and more. The Filenames of the individual frames are just numbers ranging from 0-7 depending on what the sprite represents. These images are used by the AnimatedSprite object class to cycle through and visually represent within the game window. 

One notable example of this is seen within the gksr directory, where each of the G.K.S.R.'s attack phases have different sprites, which also serves as a good visual indicator of which of its attack phases is active. 

The theme of visual indication is also present within the endings directory, which contains images meant to display the result of the game. The color of the text within these images is meant to be linked to the condition that caused that ending. For example:
- game_end_1.png's text "You Win! G.K.S.R. Destroyed" is in blue to relate the ending to the player's blue hitpoint bar
- game_end_2.png's text "G.K.S.R. killed you" is in red to relate the ending to the G.K.S.R.'s red hitpoint bar
- game_end_3.png's text "G.K.S.R. reach Earth" is in purple to relate the ending to the depletion of the purple ETA

The other relevant directory within the src folder is the **sounds** folder. Hence the name, this contains all of the sounds used by the game. The sounds for the player and the G.K.S.R. were made using Chiptone to develop the feeling of playing a classic game. The background music was found on Pixabay and serves as an audio indicator of the G.K.S.R.'s ETA to Earth, as it plays for the 70 seconds the player has to defeat the G.K.S.R.

The final directory within the src folder is the **test_images** folder. This contains all of the original sprites used during the early development of the game. The program does not depend on these files, but they exist to remind the developer of how far the game has come over the nearly 4 weeks spent working on this project.

### Future Areas of Improvement
Thankfully, the development of this game was very fun and the developer managed to reach all of the goals planned in the project proposal. However, why stop here? Some features that could be added in the future include:
- **Full 2D Player Movement** - Instead of the player being locked in the horizontal axis, the player could move in both axes to dodge the G.K.S.R.'s projectile waves better.
- **Additional PowerUps** - Some player powerup ideas that were scrapped included Higher Damage Projectiles and the ability to move and shoot simultaneously. Maybe these could be reworked and implemented in a creative way that synergizes with the Full 2D Player Movement.
- **Entering The Atmosphere** - to serve as better visual indication of the G.K.S.R.'s ETA to Earth, the background could fade from dark purple (representing the vacuum of space) to to a pale blue (representing Earth's atmosphere) to indicate increasing proximity to Earth.

### Credits
The following are outside resources used to aid in the development of this project.

**Tutorials Referenced:**
- <https://youtu.be/3Yhhzflmxfs?si=Jqq7Oqs3KnPEOU_A>
- <https://youtu.be/xdkY6yhEccA?si=TBpxSH1geUkIVVic>
- <https://youtu.be/Xzmpl5tnJnc?si=d92S23CnUqSOJH3S>

**Pygame Documentation:**
- <https://www.pygame.org/docs/ref/draw.html>

**Program Used for Making Sound Effects:**
- <https://sfbgames.itch.io/chiptone>

**Program Used for Making Sprites:**
- <https://www.piskelapp.com/>

**Background Music Used In Game:**
- The Return Of The 8-Bit Era by DJARTMUSIC <https://pixabay.com/music/video-games-the-return-of-the-8-bit-era-301292/>
