import copy
import random
import pygame
import sqlite3
import sys

# Initialize pygame
pygame.init()

# Initialize game variables
WIDTH = 500
HEIGHT = 550
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Water Sort PyGame')
font = pygame.font.Font('freesansbold.ttf', 24)
fps = 60
timer = pygame.time.Clock()
color_choices = ['red', 'orange', 'light blue', 'dark blue', 'dark green', 'pink', 'purple', 'dark gray',
                 'brown', 'light green', 'yellow', 'white']
tube_colors = []
initial_colors = []
tubes = 8
new_game = True
selected = False
tube_rects = []
select_rect = 100
win = False
start_button_rect = pygame.Rect(200, 300, 100, 50)

# Load background image
background_image = pygame.image.load("background_image.jpg")  
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(r"C:\Users\ADMIN\OneDrive\Desktop\WISE\game1.db")
print("Database connection established successfully.")
cursor = conn.cursor()

# Create a table to store game data if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS game_data (
                    game_id INTEGER PRIMARY KEY,
                    tubes INTEGER,
                    tube_colors TEXT,
                    initial_colors TEXT,
                    win INTEGER
                )''')
conn.commit()
print("game_data table created successfully.")


# Function to insert game data into the database
def insert_game_data(tubes, tube_colors, initial_colors, win):
    print("Inserting game data into the database:")
    print("Tubes:", tubes)
    print("Tube colors:", tube_colors)
    print("Initial colors:", initial_colors)
    print("Win:", win)
    cursor.execute('''INSERT INTO game_data (tubes, tube_colors, initial_colors, win)
                      VALUES (?, ?, ?, ?)''', (tubes, str(tube_colors), str(initial_colors), int(win)))
    conn.commit()


# Function to retrieve game data from the database
def retrieve_game_data():
    cursor.execute('''SELECT * FROM game_data''')
    return cursor.fetchall()


# Function to generate a new game setup
def generate_start():
    tubes_number = random.randint(8,10)
    tubes_colors = []
    available_colors = []
    for i in range(tubes_number):
        tubes_colors.append([])
        if i < tubes_number - 2:
            for j in range(4):
                available_colors.append(i)
    for i in range(tubes_number - 2):
        for j in range(4):
            color = random.choice(available_colors)
            tubes_colors[i].append(color)
            available_colors.remove(color)
    return tubes_number, tubes_colors


# Function to draw all tubes and colors on screen
def draw_tubes(tubes_num, tube_cols):
    tube_boxes = []
    if tubes_num % 2 == 0:
        tubes_per_row = tubes_num // 2
        offset = False
    else:
        tubes_per_row = tubes_num // 2 + 1
        offset = True
    spacing = WIDTH / tubes_per_row
    for i in range(tubes_per_row):
        for j in range(len(tube_cols[i])):
            pygame.draw.rect(screen, color_choices[tube_cols[i][j]], [5 + spacing * i, 200 - (50 * j), 65, 50], 0, 3)
        box = pygame.draw.rect(screen, 'blue', [5 + spacing * i, 50, 65, 200], 5, 5)
        if select_rect == i:
            pygame.draw.rect(screen, 'green', [5 + spacing * i, 50, 65, 200], 3, 5)
        tube_boxes.append(box)
    if offset:
        for i in range(tubes_per_row - 1):
            for j in range(len(tube_cols[i + tubes_per_row])):
                pygame.draw.rect(screen, color_choices[tube_cols[i + tubes_per_row][j]],
                                 [(spacing * 0.5) + 5 + spacing * i, 450 - (50 * j), 65, 50], 0, 3)
            box = pygame.draw.rect(screen, 'blue', [(spacing * 0.5) + 5 + spacing * i, 300, 65, 200], 5, 5)
            if select_rect == i + tubes_per_row:
                pygame.draw.rect(screen, 'green', [(spacing * 0.5) + 5 + spacing * i, 300, 65, 200], 3, 5)
            tube_boxes.append(box)
    else:
        for i in range(tubes_per_row):
            for j in range(len(tube_cols[i + tubes_per_row])):
                pygame.draw.rect(screen, color_choices[tube_cols[i + tubes_per_row][j]], [5 + spacing * i,
                                                                                          450 - (50 * j), 65, 50], 0, 3)
            box = pygame.draw.rect(screen, 'blue', [5 + spacing * i, 300, 65, 200], 5, 5)
            if select_rect == i + tubes_per_row:
                pygame.draw.rect(screen, 'green', [5 + spacing * i, 300, 65, 200], 3, 5)
            tube_boxes.append(box)
    return tube_boxes


# Function to calculate the move
def calc_move(colors, selected_rect, destination):
    chain = True
    color_on_top = 100
    length = 1
    color_to_move = 100
    if len(colors[selected_rect]) > 0:
        color_to_move = colors[selected_rect][-1]
        for i in range(1, len(colors[selected_rect])):
            if chain:
                if colors[selected_rect][-1 - i] == color_to_move:
                    length += 1
                else:
                    chain = False
    if 4 > len(colors[destination]):
        if len(colors[destination]) == 0:
            color_on_top = color_to_move
        else:
            color_on_top = colors[destination][-1]
    if color_on_top == color_to_move:
        for i in range(length):
            if len(colors[destination]) < 4:
                if len(colors[selected_rect]) > 0:
                    colors[destination].append(color_on_top)
                    colors[selected_rect].pop(-1)
    return colors


# Function to check for victory
def check_victory(colors):
    won = True
    for i in range(len(colors)):
        if len(colors[i]) > 0:
            if len(colors[i]) != 4:
                won = False
            else:
                main_color = colors[i][-1]
                for j in range(len(colors[i])):
                    if colors[i][j] != main_color:
                        won = False
    return won


# Function to display the landing page
def display_landing_page():
    screen.blit(background_image, (0, 0))
    welcome_text = font.render('Welcome to', True, 'white')
    screen.blit(welcome_text, (180, 200))
    colour_smash_text = font.render('Colour Smash', True, 'black')  # Change the text color to black
    screen.blit(colour_smash_text, (150, 240))  # Adjust the position if needed
    pygame.draw.rect(screen, 'green', start_button_rect)
    start_text = font.render('Start', True, 'white')
    screen.blit(start_text, (start_button_rect.x + 25, start_button_rect.y + 15))
    pygame.display.flip()



# Main game loop
while True:
    display_landing_page()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    run = True
                    while run:
                        screen.fill('black')
                        timer.tick(fps)

                        # Generate game board on new game setup, make a copy of the colors in case of restart
                        if new_game:
                            tubes, tube_colors = generate_start()
                            initial_colors = copy.deepcopy(tube_colors)
                            new_game = False
                        else:
                            tube_rects = draw_tubes(tubes, tube_colors)

                        # Check for victory every cycle
                        win = check_victory(tube_colors)

                        # Event handling
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                run = False
                            if event.type == pygame.KEYUP:
                                if event.key == pygame.K_SPACE:
                                    tube_colors = copy.deepcopy(initial_colors)

                                elif event.key == pygame.K_RETURN:
                                    # Insert game data into the database when starting a new game
                                    print("Starting a new game...")
                                    insert_game_data(tubes, tube_colors, initial_colors, win)
                                    new_game = True
                                    print("Game data inserted into the database.")
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if not selected:
                                    for item in range(len(tube_rects)):
                                        if tube_rects[item].collidepoint(event.pos):
                                            selected = True
                                            select_rect = item
                                else:
                                    for item in range(len(tube_rects)):
                                        if tube_rects[item].collidepoint(event.pos):
                                            dest_rect = item
                                            tube_colors = calc_move(tube_colors, select_rect, dest_rect)
                                            selected = False
                                            select_rect = 100

                        # Draw 'victory' text when winning in middle, always show restart and new board text at top
                        if win:
                            victory_text = font.render('You Won! Press Enter for a new board!', True, 'white')
                            screen.blit(victory_text, (30, 265))
                        restart_text = font.render('Stuck? Space-Restart, Enter-New Board!', True, 'white')
                        screen.blit(restart_text, (10, 10))

                        # Display all drawn items on screen
                        pygame.display.flip()

                    # Close the database connection when done
                    conn.close()
                    pygame.quit()
