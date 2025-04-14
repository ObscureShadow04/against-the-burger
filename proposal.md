# Impending Doom

## Repository
<https://github.com/ObscureShadow04/impending-doom.git>

## Description
The final deliverable will be a side-scrolling game in which the player must defeat a giant killer space robot before it reaches planet Earth. The wacky concept and style of the game seeks to emulate the feeling of a flash game from the early 2000s.

## Features
- Controllable Character
	- The player's character will be able to move up and down using the arrow keys
   	- The player's character will be able to fire projectiles at the robot while holding the spacebar

- Giant Killer Space Robot (G.K.S.R.)
	- The G.K.S.R. will fire waves of projectiles at the player
 	- The G.K.S.R. will have different attack phases depending on how much health it has left
	- The amount of projectiles per wave will increase and the time in-between waves will decrease as the G.K.S.R.'s health decreases

- Power-Ups 
	- The G.K.S.R. will have a small chance to drop power-ups which can help the player
	- The power-ups will drift across the screen toward the side of the screen where the player is
	- It is up to the player to move to the space where the power-up will be in order to collect it
 	- The power-ups will include:
		- Speed Increaser to help with maneuvering to avoid incoming projectiles
  		- Health Pack to recover a fraction of lost health
		- Projectile Amplifier will allow the player to fire projectiles that deal greater damage to the G.K.S.R.

- Dynamic UI
	- Player UI will include:
		- Health Bar to display the player's health
  		- Power-Up Slot to display which power-up is currently active
  
	- G.K.S.R. UI will include:
 		- Health Bar to display the G.K.S.R.'s remaining health
   		- Phase Indicator to display which attack phase the G.S.K.R. is in
		- ETA to Earth Indicator to display how much time the player has left to defeat the G.K.S.R.

## Challenges
- Collision detection for pygame sprites in a 2D space
- Detecting keyboard input to control the player
- Playing audio files and synchronizing it with in-game events
- Using .gif files to animate sprites in pygame

## Outcomes
Ideal Outcome:
- The ideal outcome would be a game with beyond the bare minimum mechanics of just being able to control the character, having the G.K.S.R. attack the player, and basic UI. In this ideal scenario, the player, the G.K.S.R., the projectiles they fire will all have animated sprites. The player will have a time limit to defeat the G.K.S.R. and will have to deal with its multiple attack phases, making for a very dynamic challenge that will be sure to entertain the player. Additionally, the ideal scenario will also have the UI elements have their own sprites to increase the visual appeal of the game.

Minimal Viable Outcome:
- At the very minimum, the final deliverable game will have the core mechanics of being able to control the character (being able to move and shoot), have the G.S.K.R. attack the player, and very basic UI to serve as visual indication for the player's and G.K.S.R.'s health. It may not have the visual appeal of cool sprites, sound effects, or the added challenge of the G.K.S.R.'s attack phases, but it should still provide some challenge for the player to overcome.

## Milestones

- Week 1
  1. Controllable Player (Player can move, shoot, and has finite health)
  2. Basic G.K.S.R. functionality (fires waves of projectiles and has finite health)
  3. Basic UI (visual indicators for information relevant to the player and the G.K.S.R.)

- Week 2
  1. Implementation of Power-Ups (Speed Increaser, Health Pack, Weapon Amplifier)
  2. Advanced G.K.S.R. functionality (attack phases and limited time to defeat)
  3. Advanced UI (visual indicators for advanced G.K.S.R. mechanics and player power-ups)

- Week 3
  1. Sound Effects
  2. Basic Animated Player and G.K.S.R. Sprites
  3. Basic UI Sprites

- Week 4 (Final)
  1. Final Animated Player and G.K.S.R. Sprites
  2. Final UI Sprites
