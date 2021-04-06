# RISK-Board-Game-Simulator
A game simulator for the strategic board game of RISK in python.

## Gameplay:
[
![RISK sample](https://user-images.githubusercontent.com/47074790/113744734-9934f900-9722-11eb-9057-b6439e17efbf.JPG)
](url)

## Rules and Description
RISK is a strategic board game that can be played by 2 or more players. The board is divided into a given number of territories. The goal is to occupy all the territories on the board. Each player is initially given an equal number of troops. Placement of troops is done turn-wise until all the territories in the map are occupied. The game then proceeds turn-wise. At the beginning of each turn, a player is issued a card (by picking up 1 card from a deck; 3 types of cards in total; the player can cash-in anytime and recieve a fixed number of troops if he/she has all three types of cards) and some number of troops depending on the territories he/she currently holds. Extra bonus in the form of troops is given if a player occupies entire continents. Each turn has three phases : deploy, attack and fortify. Deploy : Place the newly recieved troops, Attack : Attack neighbouring territories and Fortify : Move troops between neighbouring territories. In the attack phase, if the player wins, the player occupies the territory won. The Attacking player can attack with a minimum of 3 troops and the defending player can defend with a minimum of 2 troops. Both the attacking and defending player roll their dices (number of dices equal to the attacking/defending troops) and the highest and second highest dices are compared. The player with higher number of dice wins wins the attack (in case of tie, defender wins). At any point, the attacking player can decide to stop the attack.
