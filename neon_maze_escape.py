import cv2
import numpy as np
import random
import time

# =========================
# Webcam Setup
# =========================
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# =========================
# Colors
# =========================
WHITE = (255, 255, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
PINK = (255, 0, 255)
YELLOW = (0, 255, 255)

# =========================
# Game Variables
# =========================
score = 0
start_time = time.time()
game_over = False

player_radius = 25

laser_speed = 10
laser_gap = 180

lasers = []

# =========================
# Create Initial Lasers
# =========================
for i in range(5):
    x = 1400 + i * 300
    gap_y = random.randint(150, 500)
    lasers.append([x, gap_y])

# =========================
# Particle Effects
# =========================
particles = []

# =========================
# Main Loop
# =========================
while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (1280, 720))

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detect Blue Color
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    player_x = 200
    player_y = 360

    if len(contours) > 0:
        largest = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest) > 1000:
            x, y, w, h = cv2.boundingRect(largest)

            player_x = x + w // 2
            player_y = y + h // 2

    # =========================
    # Background Glow
    # =========================
    overlay = frame.copy()

    for i in range(0, 1280, 40):
        cv2.line(overlay, (i, 0), (i, 720), (20, 20, 20), 1)

    for i in range(0, 720, 40):
        cv2.line(overlay, (0, i), (1280, i), (20, 20, 20), 1)

    frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

    # =========================
    # Draw Player Glow
    # =========================
    cv2.circle(frame, (player_x, player_y), 45, CYAN, -1)
    cv2.circle(frame, (player_x, player_y), player_radius, WHITE, -1)

    # =========================
    # Update Lasers
    # =========================
    if not game_over:
        for laser in lasers:
            laser[0] -= laser_speed

            x = int(laser[0])
            gap_y = int(laser[1])

            # Top Laser
            cv2.rectangle(frame, (x, 0), (x + 60, gap_y), PINK, -1)

            # Bottom Laser
            cv2.rectangle(frame, (x, gap_y + laser_gap), (x + 60, 720), PINK, -1)

            # Neon Glow
            cv2.rectangle(frame, (x - 10, 0), (x + 70, gap_y), (100, 0, 100), 3)
            cv2.rectangle(frame, (x - 10, gap_y + laser_gap), (x + 70, 720), (100, 0, 100), 3)

            # Collision Detection
            if player_x + player_radius > x and player_x - player_radius < x + 60:
                if player_y - player_radius < gap_y or player_y + player_radius > gap_y + laser_gap:
                    game_over = True

            # Respawn Lasers
            if x < -100:
                laser[0] = 1400
                laser[1] = random.randint(120, 500)
                score += 1

                if laser_speed < 25:
                    laser_speed += 0.5

    # =========================
    # Particle Effects
    # =========================
    particles.append([player_x, player_y, random.randint(-5, 5), random.randint(-5, 5), random.randint(3, 8)])

    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 0.2

        cv2.circle(frame, (int(p[0]), int(p[1])), int(max(p[4], 1)), CYAN, -1)

        if p[4] <= 0:
            particles.remove(p)

    # =========================
    # HUD
    # =========================
    cv2.putText(frame, f"Score: {score}", (40, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, YELLOW, 3)

    survival_time = int(time.time() - start_time)

    cv2.putText(frame, f"Time: {survival_time}s", (40, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, GREEN, 2)

    cv2.putText(frame, "Use a BLUE object to control", (850, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)

    # =========================
    # Game Over Screen
    # =========================
    if game_over:
        cv2.rectangle(frame, (250, 220), (1030, 500), (0, 0, 0), -1)

        cv2.putText(frame, "GAME OVER", (430, 330),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, RED, 6)

        cv2.putText(frame, f"Final Score: {score}", (470, 410),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, WHITE, 3)

        cv2.putText(frame, "Press R to Restart or Q to Quit", (350, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, CYAN, 2)

    # =========================
    # Display
    # =========================
    cv2.imshow("Neon Maze Escape", frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        break

    # Restart
    if key == ord('r') and game_over:
        score = 0
        laser_speed = 10
        start_time = time.time()
        game_over = False

        lasers = []

        for i in range(5):
            x = 1400 + i * 300
            gap_y = random.randint(150, 500)
            lasers.append([x, gap_y])

cap.release()
cv2.destroyAllWindows()
