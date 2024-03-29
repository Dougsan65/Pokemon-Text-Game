# Pokemon Game

This Python script is a text-based Pokemon game that allows players to create characters, capture Pokemon, manage items like Pokeballs, and perform various in-game actions. It utilizes the PokeAPI to fetch Pokemon data and interacts with a PostgreSQL database to save player information and game progress.

## Features:

- **Player Management:** Create new player profiles, change players, and view player information.
- **Pokemon Capture:** Explore different generations of Pokemon and capture them using various types of Pokeballs.
- **Item Management:** Manage inventory items like Pokeballs and check the quantity of each item.
- **Auto Save:** Option to enable auto-saving of game progress at regular intervals.
- **Audio Background:** Background music played using the `pygame` library to enhance the gaming experience.

## How to Use:

1. **Setup Environment:**
   - Ensure Python and necessary libraries (`requests`, `pygame`) are installed.
   - Set up a PostgreSQL database named "PokemonMainDatabase" and configure the `dbconnect.py` file with the database connection details.

2. **Run the Script:**
   - Execute the `pokemon_game.py` script.
   - Enter the player's name to start the game or create a new profile if it doesn't exist.

3. **Gameplay:**
   - Navigate through the menu options by entering the corresponding number for each action.
   - Explore different generations, capture Pokemon, manage items, and save progress as needed.

4. **Auto Save:**
   - Optionally enable auto-saving by selecting the corresponding option in the menu.
   - Auto-save will periodically save the game progress to the database.

5. **Exit:**
   - Choose the "Exit" option to gracefully exit the game and close the database connection.

## Dependencies:
- Python 3.x
- `requests` library
- `pygame` library
- PostgreSQL database

## Credits:
- **PokeAPI:** Data source for Pokemon information.
- **pygame:** Library for playing background music.

## Author:
[doug]
