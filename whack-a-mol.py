# IMPORTS
import pygame
import random
import time
import math
import csv

# PYGAME INITIALISATION
pygame.init() #Initialize pygame

# CSV PARSING
def read_csv(): # Parse CSV file containing chemical elements
  with open("./assets/elements_table.csv", "r") as csv_file: # Open file
    csv_reader = csv.reader(csv_file) # Create a reader
    next(csv_reader) # Skip header row
    return list(csv_reader) # Create list from CSV table

# GAME CONSTANTS
GRID_SIZE = 4 # Dimensions of the grid
CELL_SIZE = 450 / GRID_SIZE # Size of each mole hole
GRID_SPACING = 10  # Space between the mole holes

SCREEN_WIDTH = CELL_SIZE * GRID_SIZE + GRID_SPACING * (GRID_SIZE - 1) # Width of the game window
SCREEN_HEIGHT = SCREEN_WIDTH + 210 # Height of the game window

FPS = 60 # Frames per second of the game

MOLE_SIZE = CELL_SIZE * 2 / 3 # Size of each mole
MOLE_TIME = 2 # Time a mole stays up in seconds
MAX_MOLES = GRID_SIZE ** 2 - GRID_SIZE # Maximum number of moles at once (This number is hardly ever reached due to staggering)
MOLE_STAGGER_HIGH = 1.2 / GRID_SIZE # 0.2 at grid size 4. High end of staggering random selection pool
MOLE_STAGGER_LOW = 1 / 3 * MOLE_STAGGER_HIGH # Low end of staggering random selection pool
GAME_LENGTH = 120 # Length of the game in seconds

MOLE_IMAGE_PATH = "./assets/images/mole.png" # Path to the image of a circle to be used for the moles
HAMMER_IMAGE_PATH = "./assets/images/microscope.png" # Path to the image of a microscope to be used for the hammer
MUSIC_PATH = "./assets/sounds/whack-a-mol-theme.wav" # Path to the file containing background music 
HIT_EFFECT_PATH = "./assets/sounds/effect.wav" # Path to hit sound effect file
SWOOSH_EFFECT_PATH = "./assets/sounds/swoosh.wav" # Path to swoosh sound effect file
INCORRECT_EFFECT_PATH = "./assets/sounds/incorrect.wav" # Path to incorrect sound effect
GAME_OVER_PATH = "./assets/sounds/game_over.wav" # Path to game over tune sound file

ELEMENTS_LIST = read_csv() # CSV file containing chemical elements in list form
ELEMENT_TIME = 15 # Length of time an element will be the chosen element
ELEMENT_WEIGHT = 0.32 / GRID_SIZE  # 0.08 at grid size 4. Chance to use the chosen element as new mole element (small positive weighting for help)

# SETUP DISPLAY
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the display object
pygame.display.set_caption("Whack-a-Mol") # Set the name that will appear at the top of the window

# LOAD IMAGES
mole_image = pygame.image.load(MOLE_IMAGE_PATH) # Load the mole image 
mole_image = pygame.transform.scale(mole_image, (MOLE_SIZE, MOLE_SIZE)) # Scale mole image to correct size
hammer_image = pygame.image.load(HAMMER_IMAGE_PATH) # Load the hammer image
hammer_image = pygame.transform.scale(hammer_image, (70, 70)) # Scale hammer image to correct size

# SETUP FONT
font = pygame.font.SysFont("courier", 36) # Create a large font in Courier

# SETUP CLOCK
clock = pygame.time.Clock() # Create FPS throttle clock

# SETUP MIXER
pygame.mixer.init() # Initialise pygame's built-in mixer
pygame.mixer.music.load(MUSIC_PATH) # Load music file
pygame.mixer.music.play(loops = -1) # Play music on loop
hit_sound  = pygame.mixer.Sound(HIT_EFFECT_PATH) # Assign hit sound effect to variable
swoosh_sound = pygame.mixer.Sound(SWOOSH_EFFECT_PATH) # Assign swoosh sound effect to variable
incorrect_sound = pygame.mixer.Sound(INCORRECT_EFFECT_PATH) # Assign incorrect sound effect to variable
game_over_sound = pygame.mixer.Sound(GAME_OVER_PATH) # Assign game over tune to a variable

# FUNCTIONS
def draw_grid(): # Draw grid of holes
  for row in range(GRID_SIZE): # Repeat for each row
    for col in range(GRID_SIZE): # Repeat for each column
      x = col * (CELL_SIZE + GRID_SPACING) # Set new X coordinate of hole
      y = row * (CELL_SIZE + GRID_SPACING) # Set new Y coordinate of hole
      pygame.draw.rect(screen, (0, 0, 0), (x, y, CELL_SIZE, CELL_SIZE), 0, 10) # Draw hole

def draw_mole(mole_position): # Draw mole at given position
  row, col = mole_position # Set the row and column to the given position
  x = col * (CELL_SIZE + GRID_SPACING) + (CELL_SIZE - MOLE_SIZE) // 2 # Calculate the X position of the given column
  y = row * (CELL_SIZE + GRID_SPACING) + (CELL_SIZE - MOLE_SIZE) // 2 # Calculate the Y position of the given column
  screen.blit(mole_image, (x, y)) # Blit mole onto screen at the calculated X and Y positions

def get_cell_of_mouse_pos(pos): # Calculate cell that mouse pointer is within
  x, y = pos # Set the X and Y to the given mouse position
  col = x // (CELL_SIZE + GRID_SPACING) # Calculate the column the mouse pointer is in
  row = y // (CELL_SIZE + GRID_SPACING) # calculate the row the mouse pointer is in
  return row, col # Return calculated values

def update_grid_constants(chosen_grid_size): # Update grid size and relevant constants 
  grid_size = chosen_grid_size # Grid dimensions
  cell_size = 450 / chosen_grid_size # Size of each hole
  grid_spacing = 10 # Space between holes
  screen_width = cell_size * chosen_grid_size + grid_spacing * (chosen_grid_size - 1) # Width of screen
  screen_height = screen_width + 210 # Height of screen
  mole_size = cell_size * 2 / 3 # Size of each mole
  max_moles = chosen_grid_size ** 2 - chosen_grid_size # Maximum number of moles
  mole_stagger_high = 1.2 / chosen_grid_size # High end of random mole stagger time
  mole_stagger_low = 1 / 3 * mole_stagger_high # Low end of mole stagger time
  element_weight = 0.32 / chosen_grid_size # Weighting that mole element will be chosen element
  return grid_size, cell_size, screen_width, screen_height, mole_size, max_moles, mole_stagger_high, mole_stagger_low, element_weight # Return updated constants

# START SCREEN SETUP
start = True # Set run condition for start screen
early_quit = False # Set condition to quit entire game to false

# START SCREEN
selected_grid_size = 4  # Default grid size
while start: # Continuous loop
  screen.fill((15, 28, 61)) # Fill screen with a background colour

  title_text = font.render("Whack-a-Mol!", True, (0, 255, 0)) # Render title text with font
  title_rect = title_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 - 40)) # Center title text
  screen.blit(title_text, title_rect) # Draw title text on screen

  grid_size_text = font.render(f"Grid size: {selected_grid_size}", True, (255, 255, 255)) # Render grid size text with font
  grid_size_rect = grid_size_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT//2)) # Center grid size text
  screen.blit(grid_size_text, grid_size_rect) # Draw grid size text on screen

  start_text = font.render("Press [S] to start", True, (200, 200, 200)) # Render start text with font
  start_rect = start_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 40)) # Center start text
  screen.blit(start_text, start_rect) # Draw start text on screen

  for event in pygame.event.get(): # Iterate for each event in event queue
    if event.type == pygame.QUIT:   
      start = False # Set run condition for start screen to False
      early_quit = True # Set condition to quit whole game to true
    elif event.type == pygame.KEYDOWN: # Check if event is a keypress
      if event.key == pygame.K_ESCAPE: # Check if key pressed is escape key
        start = False # Set run condition for start screen to False
        early_quit = True # Set condition to quit whole game to True
      elif event.key == pygame.K_s: # Check if key pressed is S key
        start = False # Set run condition for start screen to false
      elif event.key in [pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]: # Check if key pressed is a number key from 3 to 8
        selected_grid_size = int(event.unicode) # Set selected grid size to the number key pressed

  pygame.display.flip() # Update display

# UPDATE NECESSARY CONSTANTS
GRID_SIZE, CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, MOLE_SIZE, MAX_MOLES, MOLE_STAGGER_HIGH, MOLE_STAGGER_LOW, ELEMENT_WEIGHT = update_grid_constants(selected_grid_size) # Set relevant constants to ouput of constant update fuunction
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Re-create the screen element
mole_image = pygame.transform.scale(mole_image, (MOLE_SIZE, MOLE_SIZE)) # Resize the image of the mole

# GAMELOOP SETUP
running = True # Set running variable to true
if early_quit == True: # Check if condition to quite whole game is true
  running = False # Prevent gameloop from running

moles = [] # Create empty list that will contain all moles. Each mole is a dictionary: {"pos": (row, col), "spawn_time": float, "symbol": str}
next_mole_time = time.time() + random.uniform(MOLE_STAGGER_LOW, MOLE_STAGGER_HIGH) # Each mole will spawn after a small random stagger

old_element_time = time.time() # Set the time that a new element was picked
chosen_element = random.choice(ELEMENTS_LIST) # Chose a new element from the list

start_time = time.time() # Set the time that the round was started
pygame.mouse.set_visible(False) # Hide the default mouse cursor
score = 0 # Set initial value for score to zero

# GAMELOOP
while running: # Gameloop condition
  screen.fill((15, 28, 61)) # Fill screen with a background colour
  draw_grid() # Call the function to draw the grid

  current_time = time.time() # Get current time
  elapsed_time = current_time - start_time # Calculate time elapsed since start of round
  remaining_time = GAME_LENGTH - elapsed_time # Calculate time remaining in round

  if remaining_time <= 0: # Stop gameloop if player runs out of time
    running = False # Stop Gameloop

  if current_time - old_element_time >= ELEMENT_TIME: # Check if time is up for current element
    chosen_element = random.choice(ELEMENTS_LIST) # Chose a new element
    old_element_time = current_time # Reset the time that a new element was picked
    if score > 0: # Check if score is greater than 0 to prevent negative score
      score += -1 # Remove one point from score

  moles = [mole for mole in moles if current_time - mole["spawn_time"] <= MOLE_TIME] # Remove moles that have been up for too long from the mole list
  
  if len(moles) < MAX_MOLES and current_time >= next_mole_time: # Add new moles if current mole count is under the maximum mole limit (Next mole time is for staggering)
    taken_positions = [mole["pos"] for mole in moles] # Pick a random hole not already used by another mole
    while True: # Loop continuously
      new_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) # Select a new hole
      if new_pos not in taken_positions: # Check if selected hole is not in use
        break # Break the while loop. Otherwise, it will continue looping until it finds an empty hole
    if random.random() < ELEMENT_WEIGHT: # Weighted chance for mole's symbol to be that of the current element
      element = chosen_element # Set new mole's symbol to current element's
    else: 
      other_elements = [element for element in ELEMENTS_LIST if element != chosen_element] # Create a list of elements that are NOT the chosen_element
      element = random.choice(other_elements) # Pick at random from the list of elements that are not the chosen elements
    symbol = element[1] # Set the new mole's symbol to the randomly picked element's atomic symbol 
    moles.append({"pos": new_pos, "spawn_time": current_time, "symbol": symbol}) # Add the new mole to the list of moles
    next_mole_time = current_time + random.uniform(MOLE_STAGGER_LOW, MOLE_STAGGER_HIGH) # Stagger next mole spawn

  for event in pygame.event.get(): # Iterate through each event in the event queue
    if event.type == pygame.QUIT: # Check if event is QUIT (User clicking the close button)
      running = False # Stop gameloop
      early_quit = True # Set condition to quit whole game to true
    elif event.type == pygame.KEYDOWN: # Check if the event is a keypress
      if event.key == pygame.K_ESCAPE: # Check if the key being pressed is Escape
        running = False # Stop gameloop
    elif event.type == pygame.MOUSEBUTTONDOWN: # Check if the event is a mouse click
      mouse_pos = pygame.mouse.get_pos() # Get mouse position at moment of click
      clicked_cell = get_cell_of_mouse_pos(mouse_pos) # Call function to find cell mouse was in when clicked
      swoosh_sound.play() # Play swoosh sound effect
      for mole in moles: # Iterate for each mole
        if clicked_cell == mole["pos"]: # Check if the cell click contained the mole
          if mole["symbol"] == chosen_element[1]: # Compare the symbol of the clicked mole and 
            score += 10 # Add 2 to the score
            hit_sound.play() # Play hit sound effect
            chosen_element = random.choice(ELEMENTS_LIST) # Pick new random element from elements list
            old_element_time = current_time # Reset the time that a new element was picked
          else:
            for i in range(5):
              if score > 0: # Check  if the score is greater than 0
                score += -1 # Remove 1 point (total of 5 maximum)
          moles.remove(mole) # Remove the specific mole from the moles list
          break # Break loop through moles

  for mole in moles: # Draw moles and symbols
    draw_mole(mole["pos"]) # Draw mole
    row, col = mole["pos"] # Get row and column for symbol to be drawn
    x = col * (CELL_SIZE + GRID_SPACING) + CELL_SIZE // 2 # Calculate symbol Y
    y = row * (CELL_SIZE + GRID_SPACING) + CELL_SIZE // 2 # calculate symbol X
    symbol_surface = font.render(mole["symbol"], True, (255, 255, 0)) # Render symbol with font
    symbol_rect = symbol_surface.get_rect(center=(x, y)) # Place symbol over mole
    screen.blit(symbol_surface, symbol_rect) # Draw symbol
  
  black_rect_y = CELL_SIZE * GRID_SIZE + GRID_SPACING * GRID_SIZE # Calculate the Y position of the black rectangle
  black_rect_width = SCREEN_WIDTH - 100 # Calculate the X position of the black rectangle
  pygame.draw.rect(screen, (0, 0, 0), (50, black_rect_y, black_rect_width, 70) , 0, 10) # Draw rectanglular background for element text and progress bar

  element_time_left = ELEMENT_TIME - (current_time - old_element_time) # Calculate time left for the current element
  if element_time_left < 0: # Check if element time is less than zero
    element_time_left = 0 # Prevent element time from being negative
  bar_fraction = element_time_left / ELEMENT_TIME # Calculate the fraction of the element time passed
  bar_y = CELL_SIZE * GRID_SIZE + GRID_SPACING * GRID_SIZE # Calculate dynamic Y position of progress bar
  bar_width = (SCREEN_WIDTH - 100) * bar_fraction # Calculate width of progress bar
  pygame.draw.rect(screen, (0, 255, 0), (50, bar_y, bar_width, 10), 0, 10) # Draw element progress bar

  element_text = font.render(chosen_element[0], True, (0, 255, 0)) # Render element text with font
  element_text_rect = element_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 160)) # Centre element text
  screen.blit(element_text, element_text_rect) # Draw element text on screen

  time_remaining_text = font.render(f"Time remaining: {math.floor(remaining_time)}s", True, (255, 255, 255)) # Render time remaining text with font
  screen.blit(time_remaining_text, (10, SCREEN_HEIGHT - 100)) # Draw time remaining text on screen

  score_text = font.render(f"Score: {score}", True, (255, 255, 255)) # Render score text with font
  screen.blit(score_text, (10, SCREEN_HEIGHT - 50)) # Draw score text on screen

  mouse_pos = pygame.mouse.get_pos() # Update mouse position variable
  hammer_rect = hammer_image.get_rect(center = mouse_pos) # Position hammer over mouse position
  screen.blit(hammer_image, hammer_rect.topleft) # Draw hammer

  pygame.display.flip() # Update the display
  clock.tick() # Tick

# GAME OVER SCREEN SETUP
pygame.mouse.set_visible(True) # Show the cursor again
game_over = True # Set run condition for game over screen
if early_quit == True: # If the early quit variable is true
  game_over = False # Skip the game over screen
game_over_sound.play() # Play game over tune

# GAME OVER SCREEN
while game_over:
  screen.fill((15, 28, 61))  # Fill with a background color

  game_over_text = font.render("Game Over!", True, (0, 255, 0)) # Render game over text with font
  game_over_rect = game_over_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 - 40)) # Center game over text
  screen.blit(game_over_text, game_over_rect) # Draw game over text on screen

  final_score_text = font.render(f"Final score: {score}", True, (255, 255, 255)) # Render final score text with font
  final_score_rect = final_score_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT//2 + 20)) # Center final score text
  screen.blit(final_score_text, final_score_rect) # Draw final score text on screen

  instruction_text = font.render("Press [ESC] to quit", True, (200, 200, 200)) # Render instruction text with font
  instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)) # Center instruction text
  screen.blit(instruction_text, instruction_rect) # Draw instruction text on screen

  for event in pygame.event.get(): # Iterate through event queue
    if event.type == pygame.QUIT: # Check if event type is QUIT
      game_over = False # Set run condition for game over screen to False
    elif event.type == pygame.KEYDOWN: # Check if the event type is a keypress
      if event.key == pygame.K_ESCAPE: # Check if the keypress is the Escape key
        game_over = False # Set run condition for game over screen to False

  pygame.display.flip() # Update display
  clock.tick(30) # Tick