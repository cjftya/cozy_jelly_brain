import pygame
import threading
import sys
import time
import math
import random
from sim.core.event_bus import EventBus, EventType
from sim.object_meta.object_type import ObjectType
from log import Logger

class PygameApp:
    def __init__(self, engine):
        self.engine = engine
        self.running = False
        
        # State data
        self.agent_positions = {}  # agent_name -> {x, y, location, is_thinking, health, fatigue, hunger}
        self.world_info = {
            "date": "Day 1",
            "clock": "00:00",
            "day_cycle": "Morning",
            "season": "Spring",
            "weather": "SUNNY"
        }
        
        # Theme Color Palette (Sleek sci-fi dark mode)
        self.colors = {
            "bg": (14, 15, 19),
            "card_bg": (21, 23, 29),
            "room_bg": (27, 29, 37),
            "accent": (99, 137, 250),
            "text_light": (240, 243, 250),
            "text_dark": (130, 135, 150),
            "border": (40, 44, 58),
            "glow_warning": (239, 68, 68),
            "glow_thinking": (52, 211, 153),
            
            # Agent colors
            "TOM": (56, 139, 253),
            "JAIN": (244, 114, 182),
            "IRIS": (52, 211, 153),
            "RAIN": (251, 146, 60),
            "MOTHER": (192, 132, 252),
            "UNKNOWN": (156, 163, 175)
        }
        
        # Particles for weather overlays
        self.particles = []
        self.max_particles = 100
        
        self.lock = threading.Lock()
        self.agent_thinking_logs = {}
        
        # Subscribe to visual events
        EventBus().subscribe(EventType.AGENT_POSITION_UPDATED, self.on_agent_position_updated)
        EventBus().subscribe(EventType.WORLD_TICKED, self.on_world_ticked)
        EventBus().subscribe(EventType.AGENT_THINKING_LOG_APPENDED, self.on_agent_thinking_log_appended)

    def on_agent_position_updated(self, data):
        with self.lock:
            name = data.get("name", "UNKNOWN")
            self.agent_positions[name] = data

    def on_world_ticked(self, data):
        with self.lock:
            self.world_info.update(data)

    def on_agent_thinking_log_appended(self, data):
        with self.lock:
            if isinstance(data, dict):
                name = data.get("name")
                log = data.get("log")
                if name:
                    if log is None or log == "":
                        self.agent_thinking_logs.pop(name, None)
                    else:
                        self.agent_thinking_logs[name] = {
                            "text": log,
                            "time": time.time()
                        }

    def setup_display(self):
        self.running = True
        
        pygame.init()
        pygame.font.init()
        
        # Display window sizes (1080x720)
        self.width, self.height = 1080, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("CozyJelly Brain Simulator - 2D Visualizer")
        self.pygame_clock = pygame.time.Clock()
        
        # Initialize Korean fonts
        try:
            self.font_title = pygame.font.SysFont("malgungothic", 20, bold=True)
            self.font_body = pygame.font.SysFont("malgungothic", 14, bold=True)
            self.font_item = pygame.font.SysFont("malgungothic", 11)
            self.font_details = pygame.font.SysFont("malgungothic", 13)
            self.font_agent = pygame.font.SysFont("malgungothic", 12, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 26)
            self.font_body = pygame.font.Font(None, 18)
            self.font_item = pygame.font.Font(None, 14)
            self.font_details = pygame.font.Font(None, 16)
            self.font_agent = pygame.font.Font(None, 15)

        # Pre-populate weather particles
        self._init_particles()

    def _init_particles(self):
        self.particles = []
        for _ in range(self.max_particles):
            self.particles.append({
                "x": random.randint(20, 1060),
                "y": random.randint(120, 700),
                "speed_y": random.uniform(2.0, 5.0),
                "speed_x": random.uniform(-1.0, 1.0),
                "size": random.randint(1, 3)
            })

    def tick_once(self):
        if not self.running:
            return
            
        # Event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return
        
        # Clear screen
        self.screen.fill(self.colors["bg"])
        
        with self.lock:
            # 1. Draw weather particles (background)
            self._update_and_draw_particles()
            
            # 2. Draw UI components
            self._draw_header(self.screen)
            self._draw_map_board(self.screen)
        
        pygame.display.flip()
        self.pygame_clock.tick(30)

    def stop(self):
        if self.running:
            self.running = False
            pygame.quit()

    def _update_and_draw_particles(self):
        weather = self.world_info.get("weather", "SUNNY")
        if weather not in ["RAIN", "SNOW", "STORM"]:
            return
            
        # Subtle wind drift based on time
        wind_drift = math.sin(time.time() * 0.4) * 0.8
        
        for p in self.particles:
            # Update particle position
            p["y"] += p["speed_y"]
            p["x"] += p["speed_x"] + wind_drift
            
            # Recycle particles wrapping out of screen
            if p["y"] > 700:
                p["y"] = 120
                p["x"] = random.randint(20, 1060)
            if p["x"] < 20 or p["x"] > 1060:
                p["x"] = random.randint(20, 1060)
                
            # Draw particle
            if weather in ["RAIN", "STORM"]:
                # Draw small blue streaks
                color = (78, 120, 246, 120)
                pygame.draw.line(self.screen, color, (p["x"], p["y"]), (p["x"] + p["speed_x"]*2 + wind_drift, p["y"] + p["speed_y"]*2), 1)
            elif weather == "SNOW":
                # Draw small white circles
                color = (240, 245, 255, 180)
                pygame.draw.circle(self.screen, color, (int(p["x"]), int(p["y"])), p["size"])

    def _draw_pill_badge(self, screen, x, y, label, value, color):
        lbl_surf = self.font_details.render(label, True, self.colors["text_dark"])
        val_surf = self.font_details.render(value, True, color)
        
        lbl_w = lbl_surf.get_width()
        val_w = val_surf.get_width()
        
        total_w = lbl_w + val_w + 20
        h = 24
        
        badge_rect = pygame.Rect(x, y - 2, total_w, h)
        pygame.draw.rect(screen, (24, 26, 34), badge_rect, border_radius=6)
        pygame.draw.rect(screen, (45, 48, 62), badge_rect, width=1, border_radius=6)
        
        screen.blit(lbl_surf, (x + 8, y + 2))
        screen.blit(val_surf, (x + 12 + lbl_w, y + 2))
        return total_w

    def _draw_header(self, screen):
        header_rect = pygame.Rect(20, 20, 1040, 80)
        
        # Dynamic theme colors based on day cycle
        cycle = self.world_info.get("day_cycle", "Day").lower()
        if "morning" in cycle:
            # Sunrise orange/purple
            bg_color = (48, 30, 45)
            border_color = (220, 100, 100)
        elif "night" in cycle or "evening" in cycle:
            # Midnight blue
            bg_color = (15, 20, 38)
            border_color = (50, 100, 220)
        elif "sunset" in cycle:
            # Sunset gold/red
            bg_color = (50, 28, 20)
            border_color = (245, 120, 50)
        else:
            # Standard light slate for daytime
            bg_color = self.colors["card_bg"]
            border_color = self.colors["border"]
            
        # Draw header box
        pygame.draw.rect(screen, bg_color, header_rect, border_radius=12)
        pygame.draw.rect(screen, border_color, header_rect, width=1, border_radius=12)
        
        # Bottom decorative accent bar
        pygame.draw.rect(screen, border_color, pygame.Rect(20, 97, 1040, 3), border_bottom_left_radius=2, border_bottom_right_radius=2)
        
        # Title & Subtitle
        title_surf = self.font_title.render("COZYJELLY BRAIN", True, self.colors["text_light"])
        screen.blit(title_surf, (40, 30))
        sub_surf = self.font_item.render("SYSTEM STATUS / 2D MAP VISUALIZER", True, self.colors["text_dark"])
        screen.blit(sub_surf, (40, 56))
        
        # Weather
        weather = self.world_info.get("weather", "SUNNY")
        weather_icons = {
            "SUNNY": "맑음",
            "CLOUDY": "흐림",
            "RAIN": "비",
            "SNOW": "눈",
            "STORM": "폭풍우"
        }
        weather_str = weather_icons.get(weather, weather)
        
        # Draw Pill Badges
        pills = [
            ("DATE", self.world_info.get("date", "Day 1"), (192, 132, 252)),
            ("TIME", self.world_info.get("clock", "00:00"), (56, 189, 248)),
            ("CYCLE", self.world_info.get("day_cycle", "Morning"), (251, 146, 60)),
            ("SEASON", self.world_info.get("season", "Spring"), (74, 222, 128)),
            ("WEATHER", weather_str, (251, 113, 133) if "비" in weather_str or "폭풍" in weather_str else (250, 204, 21))
        ]
        
        start_x = 450
        badge_y = 48
        for label, val, color in pills:
            w = self._draw_pill_badge(screen, start_x, badge_y, label, val, color)
            start_x += w + 12

    def _draw_map_board(self, screen):
        map_rect = pygame.Rect(20, 120, 1040, 580)
        
        # Glassmorphic board container
        pygame.draw.rect(screen, self.colors["card_bg"], map_rect, border_radius=12)
        pygame.draw.rect(screen, self.colors["border"], map_rect, width=1, border_radius=12)
        
        # Get rooms list dynamically from agent positions
        locations = set()
        for data in self.agent_positions.values():
            loc = data.get("location")
            if loc:
                locations.add(loc)
        
        # If no positions received yet, dynamically query simulator agents' locations
        if not locations:
            try:
                if hasattr(self.engine, 'simulator') and self.engine.simulator:
                    wsm = self.engine.simulator.world_system_manager
                    if wsm and wsm.world_agents:
                        for agent in wsm.world_agents:
                            curr_loc = agent.location_delegate.get_current_location()
                            if curr_loc:
                                locations.add(curr_loc)
                            for loc in agent.location_delegate.get_available_locations():
                                locations.add(loc)
            except Exception:
                pass
                
        # If still empty, use a generic fallback
        if not locations:
            locations = {"해안가 캠프", "바위 그늘", "정찰 언덕"}
            
        loc_list = sorted(list(locations))
        
        # Layout metrics (Expanded for 1040px width)
        room_width = 225
        room_height = 230
        margin_x = 25
        margin_y = 35
        
        room_positions = {}
        for idx, loc_name in enumerate(loc_list):
            row = idx // 4
            col = idx % 4
            
            rx = map_rect.x + 30 + col * (room_width + margin_x)
            ry = map_rect.y + 40 + row * (room_height + margin_y)
            room_positions[loc_name] = (rx, ry)
            
            # Check if any agents are in this room
            agents_in_room = [name for name, data in self.agent_positions.items() if data.get("location") == loc_name]
            is_active = len(agents_in_room) > 0
            
            # Colors based on activity
            border_col = self.colors["accent"] if is_active else self.colors["border"]
            bg_col = (25, 27, 35) if is_active else self.colors["room_bg"]
            
            # 1. Draw Room Card Box Background
            r_rect = pygame.Rect(rx, ry, room_width, room_height)
            pygame.draw.rect(screen, bg_col, r_rect, border_radius=10)
            
            # Room Title Section Header (Draw first to allow outline to mask it)
            title_rect = pygame.Rect(rx, ry, room_width, 31)
            title_bg = (31, 34, 44) if is_active else (21, 23, 29)
            pygame.draw.rect(screen, title_bg, title_rect, border_top_left_radius=10, border_top_right_radius=10)
            
            # Draw Card Border Outline on top to mask corners
            pygame.draw.rect(screen, border_col, r_rect, width=1, border_radius=10)
            
            # Separator under title
            pygame.draw.line(screen, border_col, (rx, ry + 31), (rx + room_width, ry + 31), 1)
            
            # Vertical left accent bar next to title
            pygame.draw.rect(screen, border_col, pygame.Rect(rx + 8, ry + 8, 3, 14), border_radius=1)
            
            # Title text
            loc_surf = self.font_body.render(loc_name, True, self.colors["text_light"])
            screen.blit(loc_surf, (rx + 17, ry + 6))
            
            # 2. Draw inside room dots (Grid reference)
            for gx in range(1, 4):
                for gy in range(1, 4):
                    dot_x = rx + (gx * (room_width // 4))
                    dot_y = ry + 32 + (gy * ((room_height - 92 - 15) // 4)) # Adjusted spacing
                    pygame.draw.circle(screen, (34, 37, 48), (dot_x, dot_y), 1)
            
            # 3. Draw items in location from core ObjectManager
            self._draw_room_items(screen, loc_name, rx, ry, room_width, room_height)
                    
        # 4. Draw Agents with high fidelity elements
        pulse_alpha = int(127 + 127 * math.sin(time.time() * 8))  # Pulse speed
        
        mx, my = pygame.mouse.get_pos()
        hovered_agent = None

        for name, data in self.agent_positions.items():
            loc = data.get("location")
            x = data.get("x", 0)
            y = data.get("y", 0)
            is_thinking = data.get("is_thinking", False)
            health = data.get("health", 100.0)
            fatigue = data.get("fatigue", 0.0)
            hunger = data.get("hunger", 0.0)
            
            if loc in room_positions:
                rx, ry = room_positions[loc]
                
                # Logical coords mapped to room space (confined grid to prevent items overlap)
                offset_x = 35 + (x % 4) * 48
                offset_y = 50 + (y % 3) * 26
                
                pos_x = rx + offset_x
                pos_y = ry + offset_y
                
                # Check mouse hover (agent bubble has radius 15, name pill is below)
                if pos_x - 20 <= mx <= pos_x + 20 and pos_y - 18 <= my <= pos_y + 35:
                    hovered_agent = (name, data, mx, my)

                agent_color = self.colors.get(name, self.colors["UNKNOWN"])
                
                # Check for critical status (Vital Crisis)
                is_critical = health < 30.0 or fatigue >= 80.0 or hunger >= 80.0
                
                # Subtle dark shadow under agent bubble
                pygame.draw.circle(screen, (10, 11, 14), (pos_x + 1, pos_y + 2), 14)
                
                if is_critical:
                    # Pulsing crimson glow circle (64x64 surface to prevent outline clipping)
                    glow_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (self.colors["glow_warning"][0], self.colors["glow_warning"][1], self.colors["glow_warning"][2], pulse_alpha // 3), (32, 32), 22)
                    screen.blit(glow_surf, (pos_x - 32, pos_y - 32))
                    
                # Thinking Twinkling Glow (Twinkling star/light effect)
                if is_thinking:
                    # 64x64 surface to prevent outline clipping
                    glow_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                    glow_color = self.colors["glow_thinking"]
                    pulse_size = int(14 + 4 * math.sin(time.time() * 10))
                    
                    # Draw soft overlapping circles (core white + emerald halo)
                    pygame.draw.circle(glow_surf, (glow_color[0], glow_color[1], glow_color[2], 40), (32, 32), pulse_size + 6)
                    pygame.draw.circle(glow_surf, (glow_color[0], glow_color[1], glow_color[2], 90), (32, 32), pulse_size)
                    pygame.draw.circle(glow_surf, (255, 255, 255, 150), (32, 32), pulse_size - 4)
                    screen.blit(glow_surf, (pos_x - 32, pos_y - 32))
                
                # Draw outer border ring
                pygame.draw.circle(screen, self.colors["border"], (pos_x, pos_y), 15, width=1)
                
                # Draw agent core bubble
                pygame.draw.circle(screen, agent_color, (pos_x, pos_y), 12)
                
                # Draw letter initial
                initial = name[0] if name else "?"
                initial_surf = self.font_agent.render(initial, True, (255, 255, 255))
                screen.blit(initial_surf, (pos_x - 5, pos_y - 8))
                
                # Draw agent name label below (Pill Badge style)
                label_surf = self.font_agent.render(name, True, self.colors["text_light"])
                label_rect = label_surf.get_rect(center=(pos_x, pos_y + 24))
                
                pill_rect = pygame.Rect(label_rect.x - 6, label_rect.y - 3, label_rect.width + 12, label_rect.height + 6)
                pygame.draw.rect(screen, (20, 22, 28), pill_rect, border_radius=4)
                pygame.draw.rect(screen, (50, 54, 70), pill_rect, width=1, border_radius=4)
                
                screen.blit(label_surf, label_rect)
                
                # Draw single mini vital (Health) bar below name pill
                bar_y = pos_y + 35
                bar_w = 32
                bar_h = 3
                
                # Health Bar Background
                h_bg = pygame.Rect(pos_x - 16, bar_y, bar_w, bar_h)
                pygame.draw.rect(screen, (34, 37, 48), h_bg, border_radius=1)
                
                # Health Bar Fill
                h_val = int(bar_w * (health / 100.0))
                h_val = max(0, min(bar_w, h_val))
                h_color = (52, 211, 153) if health >= 50.0 else (239, 68, 68)
                if h_val > 0:
                    pygame.draw.rect(screen, h_color, pygame.Rect(pos_x - 16, bar_y, h_val, bar_h), border_radius=1)
                
                # Draw critical warning status dot
                if is_critical:
                    warn_color = self.colors["glow_warning"]
                    pygame.draw.circle(screen, warn_color, (pos_x + 12, pos_y + 12), 4)

                # Draw active thinking/action status text
                status_data = self.agent_thinking_logs.get(name)
                show_status = False
                status_text = ""
                if status_data:
                    status_text = status_data["text"]
                    elapsed = time.time() - status_data["time"]
                    # If thinking, show indefinitely. If action completed, show for 3.0 seconds
                    if is_thinking or elapsed < 3.0:
                        show_status = True
                        
                if show_status and status_text:
                    think_surf = self.font_agent.render(status_text, True, self.colors["glow_thinking"])
                    
                    # Determine vertical position based on agent row to avoid overlapping room header
                    if pos_y - 28 < ry + 34:
                        think_y = pos_y + 45
                    else:
                        think_y = pos_y - 28
                        
                    think_rect = think_surf.get_rect(center=(pos_x, think_y))
                    
                    think_bg = pygame.Rect(think_rect.x - 5, think_rect.y - 2, think_rect.width + 10, think_rect.height + 4)
                    pygame.draw.rect(screen, (15, 25, 20), think_bg, border_radius=4)
                    pygame.draw.rect(screen, (40, 100, 60), think_bg, width=1, border_radius=4)
                    
                    screen.blit(think_surf, think_rect)

        # Draw tooltip on top if hovering an agent
        if hovered_agent:
            self._draw_agent_tooltip(screen, hovered_agent[0], hovered_agent[1], hovered_agent[2], hovered_agent[3])

    def _draw_agent_tooltip(self, screen, name, data, mx, my):
        # Card size and positioning
        card_w = 260
        card_h = 370
        
        # Keep tooltip inside screen boundaries
        tx = mx + 15
        ty = my + 15
        if tx + card_w > self.width - 20:
            tx = mx - card_w - 15
        if ty + card_h > self.height - 20:
            ty = my - card_h - 15
            if ty < 20:
                ty = 20
                
        # Card container with glassmorphic dark theme
        card_rect = pygame.Rect(tx, ty, card_w, card_h)
        pygame.draw.rect(screen, (21, 23, 29), card_rect, border_radius=12)
        
        # Active border in agent's accent color
        agent_color = self.colors.get(name, self.colors["UNKNOWN"])
        pygame.draw.rect(screen, agent_color, card_rect, width=2, border_radius=12)
        
        # Header (Agent Name)
        title_surf = self.font_title.render(f"SURVIVOR: {name}", True, agent_color)
        screen.blit(title_surf, (tx + 16, ty + 16))
        
        # Subtitle (Location)
        loc = data.get("location", "UNKNOWN")
        sub_surf = self.font_item.render(f"LOCATION: {loc}", True, self.colors["text_dark"])
        screen.blit(sub_surf, (tx + 16, ty + 40))
        
        # Separator line
        pygame.draw.line(screen, (45, 48, 62), (tx + 16, ty + 56), (tx + card_w - 16, ty + 56), 1)
        
        # 1. Physical Vitals
        vy = ty + 66
        section_p = self.font_body.render("신체 상태 (PHYSICAL)", True, self.colors["text_light"])
        screen.blit(section_p, (tx + 16, vy))
        
        health = data.get("health", 100.0)
        fatigue = data.get("fatigue", 0.0)
        hunger = data.get("hunger", 0.0)
        
        # Helper to draw a small vital bar
        def draw_vital_bar(label, val, y, is_inverse=False):
            lbl_surf = self.font_item.render(label, True, self.colors["text_dark"])
            screen.blit(lbl_surf, (tx + 16, y))
            
            val_surf = self.font_item.render(f"{int(val)}%", True, self.colors["text_light"])
            screen.blit(val_surf, (tx + 100, y))
            
            # Bar bg
            bar_rect_bg = pygame.Rect(tx + 140, y + 4, 100, 6)
            pygame.draw.rect(screen, (34, 37, 48), bar_rect_bg, border_radius=2)
            
            # Bar fill
            fill_w = int(100 * (val / 100.0))
            fill_w = max(0, min(100, fill_w))
            
            # Color logic
            if is_inverse:
                color = (239, 68, 68) if val >= 70.0 else (52, 211, 153)
            else:
                color = (52, 211, 153) if val >= 50.0 else (239, 68, 68)
                
            if fill_w > 0:
                pygame.draw.rect(screen, color, pygame.Rect(tx + 140, y + 4, fill_w, 6), border_radius=2)
                
        draw_vital_bar("체력 (Health)", health, vy + 20, False)
        draw_vital_bar("피로 (Fatigue)", fatigue, vy + 38, True)
        draw_vital_bar("허기 (Hunger)", hunger, vy + 56, True)
        
        # Separator line
        pygame.draw.line(screen, (45, 48, 62), (tx + 16, ty + 148), (tx + card_w - 16, ty + 148), 1)
        
        # 2. Mental State (Personality metrics)
        my_sec = ty + 158
        section_m = self.font_body.render("정신 성향 (MENTAL)", True, self.colors["text_light"])
        screen.blit(section_m, (tx + 16, my_sec))
        
        personality = data.get("personality", {})
        logic = int(personality.get("logic_emotion", 0.5) * 100)
        decisive = int(personality.get("fear_decisive", 0.5) * 100)
        openness = int(personality.get("defensive_open", 0.5) * 100)
        
        p_text1 = f"이성향: {logic}% / 감성향: {100-logic}%"
        p_text2 = f"결단력: {decisive}% / 불안도: {100-decisive}%"
        p_text3 = f"개방성: {openness}% / 경계도: {100-openness}%"
        
        lbl_p1 = self.font_item.render(p_text1, True, self.colors["text_dark"])
        lbl_p2 = self.font_item.render(p_text2, True, self.colors["text_dark"])
        lbl_p3 = self.font_item.render(p_text3, True, self.colors["text_dark"])
        
        screen.blit(lbl_p1, (tx + 16, my_sec + 20))
        screen.blit(lbl_p2, (tx + 16, my_sec + 36))
        screen.blit(lbl_p3, (tx + 16, my_sec + 52))
        
        # Separator line
        pygame.draw.line(screen, (45, 48, 62), (tx + 16, ty + 236), (tx + card_w - 16, ty + 236), 1)
        
        # 3. Relationships
        ry_sec = ty + 246
        section_r = self.font_body.render("대인 관계 (RELATIONSHIP)", True, self.colors["text_light"])
        screen.blit(section_r, (tx + 16, ry_sec))
        
        relationships = data.get("relationships", {})
        r_y = ry_sec + 20
        if relationships:
            for rel_name, rel_score in relationships.items():
                rel_text = f"호감도 [{rel_name}]: {int(rel_score)} / 100"
                rel_surf = self.font_item.render(rel_text, True, self.colors["text_dark"])
                screen.blit(rel_surf, (tx + 16, r_y))
                r_y += 16
        else:
            rel_surf = self.font_item.render("관계 정보 없음", True, self.colors["text_dark"])
            screen.blit(rel_surf, (tx + 16, r_y))

        # Separator line
        pygame.draw.line(screen, (45, 48, 62), (tx + 16, ty + 286), (tx + card_w - 16, ty + 286), 1)

        # 4. Inventory
        inv_sec = ty + 296
        section_i = self.font_body.render("소지품 (INVENTORY)", True, self.colors["text_light"])
        screen.blit(section_i, (tx + 16, inv_sec))

        inventory = data.get("inventory", [])
        if inventory:
            # Group same items together for compact display
            from collections import Counter
            item_counts = Counter(inventory)
            inv_text = "  ".join(
                f"{item} x{cnt}" if cnt > 1 else item
                for item, cnt in item_counts.items()
            )
            # Truncate if too long
            if len(inv_text) > 30:
                inv_text = inv_text[:27] + "..."
            inv_surf = self.font_item.render(inv_text, True, (251, 191, 36))
        else:
            inv_surf = self.font_item.render("없음", True, self.colors["text_dark"])
        screen.blit(inv_surf, (tx + 16, inv_sec + 20))

    def _draw_room_items(self, screen, loc_name, rx, ry, r_w, r_h):
        # Read directly from world simulator object manager
        if not hasattr(self.engine, 'simulator') or not self.engine.simulator:
            return
        wsm = self.engine.simulator.world_system_manager
        if not wsm or not wsm.object_manager:
            return
            
        try:
            # Query items belonging to room
            items = wsm.object_manager.get_objects_by_parent_name(loc_name)
            items = [item for item in items if item.type == ObjectType.ITEM]
            
            if not items:
                return
                
            # Render item listing inside Room bottom area
            start_y = ry + r_h - 75
            line_height = 18
            
            # Background plate for items section
            items_plate = pygame.Rect(rx + 10, start_y - 5, r_w - 20, 68)
            pygame.draw.rect(screen, (16, 17, 22), items_plate, border_radius=6)
            pygame.draw.rect(screen, (34, 37, 48), items_plate, width=1, border_radius=6)
            
            # Draw ITEMS section small tag header
            tag_surf = self.font_item.render("ITEMS", True, (90, 95, 110))
            screen.blit(tag_surf, (rx + 16, start_y - 2))
            
            # Render item names with a small colored indicator circle
            for idx, item in enumerate(items[:3]):
                name = item.name
                
                # Determine dot color based on keywords (supports survival, fantasy, sci-fi)
                dot_color = (130, 135, 150) # default Slate Grey
                food_keywords = ["식량", "푸드", "물", "음료", "포션", "약초", "고기", "열매", "빵", "food", "water", "ration", "potion", "herb", "meat", "bread", "drink"]
                material_keywords = ["나무", "목재", "뗏목", "도구", "망치", "자원", "원료", "광석", "철", "금속", "배터리", "부품", "wood", "stone", "ore", "metal", "battery", "part", "tool", "gear"]
                
                name_lower = name.lower()
                if any(k in name_lower for k in food_keywords):
                    dot_color = (52, 211, 153) # Emerald Green for food/consumables
                elif any(k in name_lower for k in material_keywords):
                    dot_color = (251, 146, 60) # Amber Orange for tools/crafting/building resources
                    
                col = idx % 2
                row = idx // 2
                
                ix = rx + 16 + col * (r_w // 2 - 10)
                iy = start_y + 16 + row * line_height
                
                # Draw colored circle
                pygame.draw.circle(screen, dot_color, (ix + 5, iy + 6), 3)
                
                # Draw text next to the circle
                item_text = name
                if len(item_text) > 10:
                    item_text = item_text[:8] + ".."
                    
                item_surf = self.font_item.render(item_text, True, self.colors["text_dark"])
                screen.blit(item_surf, (ix + 14, iy - 2))
                
            # Indicator if more items
            if len(items) > 3:
                plus_surf = self.font_item.render(f"+{len(items)-3}", True, self.colors["accent"])
                screen.blit(plus_surf, (rx + r_w - 36, start_y + 24))
                
        except Exception as e:
            pass
