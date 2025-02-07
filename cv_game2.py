import pygame
import cv2
import mediapipe as mp
import time

# Initialize Pygame
pygame.init()

# Set up display for the game
WIDTH, HEIGHT = 600, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IQ Maze Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Maze grid (1 = Wall, 0 = Path, S = Start, E = Exit)
maze = [
    ["S", 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, "E"],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 1]
]

# Maze settings
ROWS = len(maze)
COLS = len(maze[0])
CELL_SIZE = WIDTH // COLS  # Adjust size based on window width

# Player settings
# Find the player's starting position
for row in range(ROWS):
    for col in range(COLS):
        if maze[row][col] == "S":
            player_x, player_y = col, row  # Set player at "S"

player_color = (0, 0, 255)  # Blue

# MediaPipe hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Webcam feed setup
cap = cv2.VideoCapture(0)

# Movement speed control
movement_speed = 1  # How many steps the player moves per gesture

# Initialize last_move_time before the game loop
last_move_time = time.time()  # To control movement timing


# Player movement functions
def move_left():
    global player_x
    if player_x > 0 and maze[player_y][player_x - 1] != 1:
        player_x -= movement_speed


def move_right():
    global player_x
    if player_x < COLS - 1 and maze[player_y][player_x + 1] != 1:
        player_x += movement_speed


def move_up():
    global player_y
    if player_y > 0 and maze[player_y - 1][player_x] != 1:
        player_y -= movement_speed


def move_down():
    global player_y
    if player_y < ROWS - 1 and maze[player_y + 1][player_x] != 1:
        player_y += movement_speed


# Function to process webcam feed and track hand gestures
def process_webcam():
    global last_move_time  # Make sure to use the global variable

    _, frame = cap.read()  # Capture frame from webcam
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB (for MediaPipe)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Track position of the index finger tip (landmark 8)
            index_x = int(hand_landmarks.landmark[8].x * frame.shape[1])  # X position
            index_y = int(hand_landmarks.landmark[8].y * frame.shape[0])  # Y position

            # Print the finger's position for debugging
            print(f"Index Finger Position: X={index_x}, Y={index_y}")

            # Control player movement with index finger position
            current_time = time.time()

            # Move player only if enough time has passed to slow down the movement
            if current_time - last_move_time > 0.3:  # Delay of 0.3 seconds for slower movement
                if index_x < frame.shape[1] // 3:  # Move left
                    move_left()
                elif index_x > 2 * frame.shape[1] // 3:  # Move right
                    move_right()

                if index_y < frame.shape[0] // 3:  # Move up
                    move_up()
                elif index_y > 2 * frame.shape[0] // 3:  # Move down
                    move_down()

                last_move_time = current_time  # Update last move time

    return frame


def draw_maze():
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            if maze[row][col] == 1:  # Draw walls
                pygame.draw.rect(win, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
            elif maze[row][col] == "S":  # Start position
                pygame.draw.rect(win, (0, 255, 0), (x, y, CELL_SIZE, CELL_SIZE))  # Green
            elif maze[row][col] == "E":  # Exit position
                pygame.draw.rect(win, (255, 0, 0), (x, y, CELL_SIZE, CELL_SIZE))  # Red

    # Draw player
    pygame.draw.rect(win, player_color, (player_x * CELL_SIZE, player_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Main game loop
running = True
while running:
    # Process webcam feed and show it in OpenCV window
    frame = process_webcam()
    cv2.imshow("Webcam Feed", frame)

    # Handle the game logic and Pygame window
    win.fill(WHITE)
    draw_maze()  # Draw the game maze

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

    # Check if the player has reached the exit
    if maze[player_y][player_x] == "E":
        print("You won!")
        running = False

# Release the webcam and close both windows
cap.release()
cv2.destroyAllWindows()
pygame.quit()
