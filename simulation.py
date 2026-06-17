import pygame
import math
import random
import collections

WIDTH, HEIGHT = 1200, 700
FPS = 60

COLOR_BG = (10, 15, 20)           
COLOR_CABIN_WALL = (40, 45, 50)   
COLOR_CABIN_FLOOR = (30, 35, 40)
COLOR_CEILING = (20, 20, 25)
COLOR_RADAR_SCAN = (0, 255, 150)  
COLOR_RADAR_HIT = (255, 50, 50)   
COLOR_UI_BG = (20, 25, 30)
COLOR_TEXT = (200, 200, 200)

def get_thermal_color(temp_c):
    norm = max(0, min(1, (temp_c - 36.0) / 4.0))
    r = int(255 * norm)
    g = int(255 * math.sin(norm * 3.14)) 
    b = int(255 * (1 - norm))
    return (r, g, b)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adaptive Bio-Safety Elevator: Final Engineering Demo")
font_ui = pygame.font.SysFont("Consolas", 14)
font_header = pygame.font.SysFont("Arial", 20, bold=True)

class LidarScanner:
    def __init__(self, x, y, angle_spread, max_depth):
        self.origin = (x, y)
        self.spread = angle_spread 
        self.depth = max_depth
        self.rays = []

    def scan(self, obstacles, active):
        self.rays = []
        if not active: return

        start_angle = 90 - (self.spread / 2)
        for i in range(30):
            angle = math.radians(start_angle + (i * (self.spread/30)))
            dx = math.cos(angle) * self.depth
            dy = math.sin(angle) * self.depth
            
            closest_dist = self.depth
            hit_pos = (self.origin[0] + dx, self.origin[1] + dy)
            hit_obj = False

            for obs in obstacles:
                # Simple distance check for simulation speed
                dist_to_obj = math.hypot(obs.x - self.origin[0], obs.y - self.origin[1])
                obj_angle = math.atan2(obs.y - self.origin[1], obs.x - self.origin[0])
                # Check if ray hits passenger bubble
                if dist_to_obj < closest_dist and abs(angle - obj_angle) < 0.2: 
                    closest_dist = dist_to_obj - 20 
                    hit_pos = (self.origin[0] + math.cos(angle)*closest_dist, 
                               self.origin[1] + math.sin(angle)*closest_dist)
                    hit_obj = True

            self.rays.append({'start': self.origin, 'end': hit_pos, 'hit': hit_obj})

    def draw(self, surface):
        for ray in self.rays:
            col = COLOR_RADAR_HIT if ray['hit'] else (COLOR_RADAR_SCAN[0], COLOR_RADAR_SCAN[1], COLOR_RADAR_SCAN[2], 50)
            pygame.draw.line(surface, col, ray['start'], ray['end'], 1)
            if ray['hit']: pygame.draw.circle(surface, COLOR_RADAR_HIT, ray['end'], 3)

class Particle:
    """ Cough Particles """
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        speed = random.uniform(2.0, 4.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 100

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = min(255, self.life * 2)
        s = pygame.Surface((6,6), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 255, alpha), (3,3), 3)
        surface.blit(s, (self.x, self.y))

class MistParticle:
    """ Ceiling Disinfection Mist """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.0, 1.0) 
        self.vy = random.uniform(1.0, 3.0)  
        self.life = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 3 
        if self.x < 350 or self.x > 850: self.vx *= -1

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((12,12), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 100, 255, self.life), (6,6), 6)
            surface.blit(s, (self.x, self.y))

class Passenger:
    def __init__(self):
        self.x, self.y = 100, 500
        self.temp = 36.6
        self.dragging = False
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: self.temp = min(42.0, self.temp + 0.05)
        if keys[pygame.K_DOWN]: self.temp = max(35.0, self.temp - 0.05)

    def draw(self, surface, thermal_mode):
        if thermal_mode:
            body_color = get_thermal_color(self.temp)
            text_color = (255, 255, 0)
        else:
            # Visual Feedback: Green if Healthy, Red if Fever
            body_color = (100, 200, 100) if self.temp < 37.8 else (255, 50, 50)
            text_color = (255, 255, 255)

        pygame.draw.circle(surface, body_color, (int(self.x), int(self.y - 30)), 15) 
        pygame.draw.rect(surface, body_color, (int(self.x - 15), int(self.y - 15), 30, 40)) 
        lbl = font_ui.render(f"{self.temp:.1f}C", True, text_color)
        surface.blit(lbl, (self.x - 15, self.y - 65))

class DataPlotter:
    def __init__(self, x, y, w, h, title, max_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.data = collections.deque([0]*w, maxlen=w)
        self.title = title
        self.max_val = max_val

    def push(self, val):
        self.data.append(val)

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1)
        
        points = []
        for i, val in enumerate(self.data):
            px = self.rect.left + i
            normalized = min(1.0, max(0.0, val / self.max_val))
            py = self.rect.bottom - (normalized * self.rect.height)
            points.append((px, py))
        
        if len(points) > 1: pygame.draw.lines(surface, (0, 255, 0), False, points, 1)
        surface.blit(font_ui.render(self.title, True, COLOR_TEXT), (self.rect.left + 5, self.rect.top + 5))
        surface.blit(font_ui.render(f"{self.data[-1]:.1f}", True, (0, 255, 0)), (self.rect.right - 40, self.rect.top + 5))

def main():
    clock = pygame.time.Clock()
    running = True
    
    lidar = LidarScanner(600, 100, 90, 500)
    passenger = Passenger()
    risk_plot = DataPlotter(850, 50, 300, 100, "RISK SCORE (0-100)", 100)
    temp_plot = DataPlotter(850, 180, 300, 100, "THERMAL INPUT (C)", 42)
    
    risk_score = 0.0
    is_occupied = False
    buttons = [pygame.Rect(750, 300 + i*60, 40, 40) for i in range(4)]
    
    # State Tracking
    contaminated_buttons = set() # Only buttons that got germs
    cleaning_mode = False
    clean_timer = 0
    thermal_mode = False
    
    ceiling_unit_rect = pygame.Rect(500, 70, 200, 40)
    
    # Particle Lists
    cough_particles = []
    mist_particles = []

    while running:
        screen.fill(COLOR_BG)
        
        # --- INPUT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t: thermal_mode = not thermal_mode
                # COUGH TRIGGER (Spacebar)
                if event.key == pygame.K_SPACE:
                    for _ in range(10): # Spawn spray
                        angle = random.uniform(0, 6.28)
                        cough_particles.append(Particle(passenger.x, passenger.y-30, angle))
            
            # MOUSE DRAG
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if math.hypot(event.pos[0]-passenger.x, event.pos[1]-passenger.y) < 40: passenger.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP: passenger.dragging = False
            elif event.type == pygame.MOUSEMOTION and passenger.dragging:
                passenger.x, passenger.y = event.pos

        # --- UPDATE LOGIC ---
        passenger.update()
        in_cabin = 300 < passenger.x < 900 and 150 < passenger.y < 650
        
        # 1. Update Cough Particles
        for p in cough_particles[:]:
            p.update()
            if p.life <= 0: cough_particles.remove(p)
            else:
                # Check if cough hits buttons
                for i, btn in enumerate(buttons):
                    if btn.collidepoint(p.x, p.y):
                        contaminated_buttons.add(i)
                        risk_score = min(100, risk_score + 5.0) # Cough hits increase risk

        # 2. Occupancy Logic
        if in_cabin:
            is_occupied = True
            lidar.scan([passenger], True)
            
            # --- RISK LOGIC FIXED ---
            # Only increase risk if passenger is SICK
            if passenger.temp > 37.8:
                risk_score = min(100, risk_score + 0.5)
            else:
                # If healthy, risk decays slowly (normalizing)
                risk_score = max(0, risk_score - 0.1)

            # Check Direct Contact
            for i, btn in enumerate(buttons):
                if btn.collidepoint(passenger.x, passenger.y):
                    # Only mark contaminated if Fever OR already High Risk
                    if passenger.temp > 37.8 or risk_score > 40:
                        contaminated_buttons.add(i)
                        risk_score = min(100, risk_score + 2.0)
                    # If healthy, do NOT add to contaminated_buttons
        
        else:
            # Passenger Left
            lidar.scan([], False)
            if is_occupied: 
                if risk_score > 30 or passenger.temp > 37.8 or len(contaminated_buttons) > 0:
                    cleaning_mode = True
                    clean_timer = 240 # 4 seconds
                else:
                    # Healthy passenger left -> Instant Reset
                    risk_score = 0
                    contaminated_buttons.clear()
            is_occupied = False
        
        # 3. Cleaning Mode Logic
        if cleaning_mode:
            clean_timer -= 1
            # Spawn Mist
            if clean_timer > 50:
                for _ in range(2):
                    mist_particles.append(MistParticle(random.randint(520, 680), 110))
            
            if clean_timer <= 0:
                cleaning_mode = False
                contaminated_buttons.clear()
                mist_particles = []
                risk_score = 0

        for p in mist_particles[:]:
            p.update()
            if p.life <= 0: mist_particles.remove(p)

        risk_plot.push(risk_score)
        temp_plot.push(passenger.temp)

        # --- DRAWING ---
        # Draw Room
        pygame.draw.rect(screen, COLOR_CABIN_WALL, (350, 150, 500, 400)) 
        pygame.draw.polygon(screen, COLOR_CABIN_FLOOR, [(350, 550), (850, 550), (1000, 700), (200, 700)]) 
        pygame.draw.polygon(screen, COLOR_CEILING, [(350, 150), (850, 150), (1000, 50), (200, 50)]) 

        # Draw Ceiling Unit
        pygame.draw.rect(screen, (50, 50, 60), ceiling_unit_rect) 
        pygame.draw.rect(screen, (100, 100, 120), ceiling_unit_rect, 2)
        for x in range(510, 700, 15):
            pygame.draw.line(screen, (30, 30, 35), (x, 75), (x, 105), 2)

        # Draw Mist (Behind Passenger)
        for p in mist_particles: p.draw(screen)

        # Draw Buttons
        lidar.draw(screen)
        for i, btn in enumerate(buttons):
            # DEFAULT COLOR: Dark Grey
            col = (50, 50, 50)
            
            # IF CONTAMINATED: Yellow (Only if sick person touched it)
            if i in contaminated_buttons:
                col = (200, 150, 0)
            
            # IF CLEANING: Purple Pulse
            if cleaning_mode and i in contaminated_buttons:
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                col = (int(100 + 155 * pulse), 0, int(100 + 155 * pulse))
                # Glow
                s = pygame.Surface((60,60), pygame.SRCALPHA)
                pygame.draw.circle(s, (150, 0, 255, 100), (30,30), 25)
                screen.blit(s, (btn.x-10, btn.y-10))

            pygame.draw.rect(screen, col, btn, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), btn, 1)

        # Draw Cough Particles
        for p in cough_particles: p.draw(screen)

        # Draw Passenger & UI
        passenger.draw(screen, thermal_mode)
        
        # Dashboard
        pygame.draw.rect(screen, COLOR_UI_BG, (830, 0, 370, HEIGHT))
        pygame.draw.line(screen, (100, 100, 100), (830, 0), (830, HEIGHT))
        risk_plot.draw(screen)
        temp_plot.draw(screen)
        
        # Status Text
        status = "SYSTEM: IDLE"
        col = (0, 255, 0)
        
        if is_occupied:
            if passenger.temp > 37.8:
                status = "DETECTED: FEVER HAZARD"
                col = (255, 50, 50)
            else:
                status = "PASSENGER DETECTED (SAFE)"
                col = (0, 200, 255)
                
        if cleaning_mode: 
            status = "BIO-HAZARD PROTOCOL ACTIVE"
            col = (255, 0, 255)
            screen.blit(font_ui.render(">> CEILING MIST: DISPERSING", True, (200, 100, 255)), (850, 350))
            screen.blit(font_ui.render(">> BEZEL UV-C: STERILIZING", True, (200, 100, 255)), (850, 370))
        
        screen.blit(font_header.render(status, True, col), (850, 320))
        
        y_inst = 450
        for line in ["CONTROLS:", "Drag: Move Passenger", "Up/Down: Change Temp", "Space: COUGH (Infect)", "'T': Thermal Mode"]:
            screen.blit(font_ui.render(line, True, COLOR_TEXT), (850, y_inst))
            y_inst += 20
        
        if thermal_mode:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(50); overlay.fill((0, 0, 100))
            screen.blit(overlay, (0,0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()


