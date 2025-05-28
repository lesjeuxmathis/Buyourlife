import pygame
import sys
import random
import time
import os
import tkinter as tk
from tkinter import filedialog

# Initialisation de Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 670
GAME_WIDTH = 800
GAME_HEIGHT = 600
FPS = 60
GRAVITY = 0.5

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
PINK = (255, 192, 203)
GOLD = (255, 215, 0)
DIAMOND = (185, 242, 255)
BROWN = (165 , 45, 45) 
BILL_WIDTH = 65
BILL_HEIGHT = 50
# Dimension des images redimensionnées
COIN_SIZE = 30
BAG_WIDTH = 110
BAG_HEIGHT = 90


# Configuration des pièces et billets
MONEY_CONFIG = {
    "10cent": {"value": 0.1, "speed": 3, "color": YELLOW, "count": 1000},
    "20cent": {"value": 0.2, "speed": 4, "color": YELLOW, "count": 500},
    "50cent": {"value": 0.5, "speed": 5, "color": YELLOW, "count": 200},
    "1euro": {"value": 1.0, "speed": 6, "color": YELLOW, "count": 100},
    "2euro": {"value": 2.0, "speed": 7, "color": YELLOW, "count": 50},
    "5euro": {"value": 5.0, "speed": 8, "color": GREEN, "count": 20},
    "10euro": {"value": 10.0, "speed": 9, "color": GREEN, "count": 10},
    "20euro": {"value": 20.0, "speed": 10, "color": GREEN, "count": 5},
    "50euro": {"value": 50.0, "speed": 11, "color": GREEN, "count": 2},
    "100euro": {"value": 100.0, "speed": 12, "color": GREEN, "count": 1}
}

# Objectifs par niveau
LEVEL_GOALS = {
    1: 200,
    2: 300,
    3: 400,
    4: 500,
    5: 700
}

# Skins disponibles et leurs couleurs
SKINS = {
    "default": BROWN,
    "pink": PINK,
    "gold": GOLD,
    "diamond": DIAMOND
}

# Dictionnaire pour stocker les images chargées
MONEY_IMAGES = {}

# Fonction pour charger les images
# À modifier dans la fonction load_money_images()
def load_money_images():
    for money_type in MONEY_CONFIG.keys():
        image_path = os.path.join("images", f"{money_type}.png")
        try:
            # Charger l'image et la redimensionner selon le type
            original_image = pygame.image.load(image_path)
            
            # Si c'est un billet (5€ ou plus), le rendre rectangulaire
            if MONEY_CONFIG[money_type]["value"] >= 5.0:
                MONEY_IMAGES[money_type] = pygame.transform.scale(original_image, (BILL_WIDTH, BILL_HEIGHT))
            else:
                MONEY_IMAGES[money_type] = pygame.transform.scale(original_image, (COIN_SIZE, COIN_SIZE))
        except pygame.error:
            print(f"Impossible de charger l'image {image_path}")
            # Créer une image de substitution
            if MONEY_CONFIG[money_type]["value"] >= 5.0:
                img = pygame.Surface((BILL_WIDTH, BILL_HEIGHT))
            else:
                img = pygame.Surface((COIN_SIZE, COIN_SIZE))
            img.fill(MONEY_CONFIG[money_type]["color"])
            font = pygame.font.Font(None, 20)
            text = font.render(f"{MONEY_CONFIG[money_type]['value']}€", True, BLACK)
            text_rect = text.get_rect(center=(img.get_width()//2, img.get_height()//2))
            img.blit(text, text_rect)
            MONEY_IMAGES[money_type] = img

# Classe pour les pièces et billets
class Money(pygame.sprite.Sprite):
    def __init__(self, money_type, x, speed_multiplier=1.0, gravity_multiplier=1.0, size_multiplier=1.0):
        super().__init__()
        config = MONEY_CONFIG[money_type]
        self.money_type = money_type
        self.value = config["value"]
        self.speed = config["speed"] * speed_multiplier
        self.gravity_multiplier = gravity_multiplier
        
        # Calcul des tailles selon le multiplicateur
        coin_size = int(COIN_SIZE * size_multiplier)
        bill_width = int(BILL_WIDTH * size_multiplier)
        bill_height = int(BILL_HEIGHT * size_multiplier)
    
        # Utilisation de l'image chargée avec redimensionnement
        if money_type in MONEY_IMAGES:
            original_image = MONEY_IMAGES[money_type]
            if self.value >= 5.0:  # C'est un billet
                self.image = pygame.transform.scale(original_image, (bill_width, bill_height))
            else:  # C'est une pièce
                self.image = pygame.transform.scale(original_image, (coin_size, coin_size))
        else:
            # Fallback si l'image n'est pas disponible
            if self.value >= 5.0:  # C'est un billet
                self.image = pygame.Surface((bill_width, bill_height))
            else:  # C'est une pièce
                self.image = pygame.Surface((coin_size, coin_size))
            self.image.fill(config["color"])
            
            # Ajout du texte de la valeur
            font_size = max(12, int(20 * size_multiplier))
            font = pygame.font.Font(None, font_size)
            text = font.render(f"{self.value}€", True, BLACK)
            text_rect = text.get_rect(center=(self.image.get_width()//2, self.image.get_height()//2))
            self.image.blit(text, text_rect)
    
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.rect.height
    
        # Variables pour la physique
        self.velocity_y = random.uniform(0.5, 2.0)
    
    def update(self):
        # Applique la gravité modifiée pour un mouvement plus naturel
        self.velocity_y += GRAVITY * self.gravity_multiplier * 0.1
        self.rect.y += self.velocity_y * self.speed

        # Supprime la pièce si elle sort de l'écran
        if self.rect.y > GAME_HEIGHT:
            self.kill()

# Classe pour le sac
# À modifier à la classe Bag complète
class Bag(pygame.sprite.Sprite):
    def __init__(self, skin="default", speed_multiplier=1.0):
        super().__init__()
        self.skin = skin
        self.color = SKINS.get(skin, BLUE)
        
        # Chargement de l'image du sac (reste identique jusqu'à self.rect.y)
        try:
            self.original_image = pygame.image.load(os.path.join("images", "bag.png"))
            self.original_image = pygame.transform.scale(self.original_image, (BAG_WIDTH, BAG_HEIGHT))
            
            # Application du filtre de couleur selon le skin
            self.image = self.apply_color_filter(self.original_image, self.color)
            
        except pygame.error:
            # Fallback si l'image n'est pas disponible
            self.image = pygame.Surface((BAG_WIDTH, BAG_HEIGHT))
            self.image.fill(self.color)
            # Ajout d'une bordure pour le style
            pygame.draw.rect(self.image, BLACK, (0, 0, BAG_WIDTH, BAG_HEIGHT), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = GAME_WIDTH // 2 - BAG_WIDTH // 2
        self.rect.y = GAME_HEIGHT - BAG_HEIGHT - 20
        self.speed = int(16 * speed_multiplier)  # Application du multiplicateur 
    
    def apply_color_filter(self, surface, color):
        """Applique un filtre de couleur à une surface"""
        # Créer une copie de l'image
        result = surface.copy()
        
        # Créer un overlay de la couleur désirée
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((color[0], color[1], color[2], 128))  # Alpha à 128 pour semi-transparence
        
        # Appliquer l'overlay sur l'image
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        return result
    
    def update(self, keys):
        # Déplacement du sac
        if keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # Limites de l'écran
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > GAME_WIDTH - self.rect.width:
            self.rect.x = GAME_WIDTH - self.rect.width

# Classe principale du jeu
# Classe principale du jeu
class BuyourlifeSimulator:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Buyourlife Simulator")
        self.clock = pygame.time.Clock()
        self.speed_multiplier = 1.0
        self.gravity_multiplier = 1.0
        self.size_multiplier = 1.0
        self.bag_speed_multiplier = 1.0
        self.running = True
        self.custom_background = None
        self.default_background = BLACK
        
        # Charger les images des pièces et billets
        load_money_images()
        
        # Surface de jeu (séparée de l'interface)
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        
        # État du jeu
        self.state = "menu"  # menu, playing, pause, game_over, skins
        self.current_level = 1
        self.money_collected = 0
        self.time_left = 60
        self.countdown = 0
        self.is_paused = False
        
        # Groupes de sprites
        self.all_sprites = pygame.sprite.Group()
        self.money_sprites = pygame.sprite.Group()
        
        # Joueur
        self.bag = None
        self.selected_skin = "default"
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.ui_font = pygame.font.Font(None, 36)
        
        # Timer pour la génération d'argent
        self.last_money_spawn = 0
        self.money_spawn_delay = 500  # millisecondes
        
        # System for coin spawning
        self.coins_remaining = {}
        self.level_start_time = 0
        self.pause_start_time = 0
        
        # Menu variables
        self.menu_items = ["Mode Facile", "Mode Normal", "Mode Difficile", "Skins", "Fond", "Quitter"]
        self.selected_menu_item = 0
        
        # Setup des pièces pour le niveau
        self.setup_money_for_level()

    def load_custom_background(self):
        """Charge un fond personnalisé depuis un fichier"""
        import tkinter as tk
        from tkinter import filedialog
    
        # Créer une fenêtre temporaire pour le dialog
        root = tk.Tk()
        root.withdraw()  # Cache la fenêtre principale
        
        # Ouvre le dialog de sélection de fichier
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image de fond",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Tous les fichiers", "*.*")
            ]
        )
    
        root.destroy()  # Ferme la fenêtre temporaire
    
        if file_path:
            try:
                # Charge et redimensionne l'image
                background_image = pygame.image.load(file_path)
                self.custom_background = pygame.transform.scale(background_image, (GAME_WIDTH, GAME_HEIGHT))
                print(f"Fond personnalisé chargé: {file_path}")
            except pygame.error as e:
                print(f"Erreur lors du chargement du fond: {e}")
                self.custom_background = None

    def reset_custom_background(self):
        """Remet le fond par défaut"""
        self.custom_background = None
    
    def setup_money_for_level(self):
        """Configure l'argent à faire tomber pour le niveau actuel"""
        self.coins_remaining = {}
        for money_type, config in MONEY_CONFIG.items():
            self.coins_remaining[money_type] = config["count"]
    
    def spawn_money(self):
        """Fait apparaître de l'argent aléatoirement"""
        current_time = pygame.time.get_ticks()

        if current_time - self.last_money_spawn > self.money_spawn_delay:
            available_types = [money_type for money_type, count in self.coins_remaining.items() if count > 0]
            
            if available_types:
                money_type = random.choice(available_types)
                x = random.randint(0, GAME_WIDTH - int(COIN_SIZE * self.size_multiplier))
        
                money = Money(money_type, x, self.speed_multiplier, self.gravity_multiplier, self.size_multiplier)
                self.all_sprites.add(money)
                self.money_sprites.add(money)
            
                self.coins_remaining[money_type] -= 1
                self.last_money_spawn = current_time
    
    def spawn_multiple_money(self, count=3):
        """Fait apparaître plusieurs pièces/billets à la fois"""
        for _ in range(count):
            available_types = [money_type for money_type, count in self.coins_remaining.items() if count > 0]
            if available_types:
                money_type = random.choice(available_types)
                x = random.randint(0, GAME_WIDTH - int(COIN_SIZE * self.size_multiplier))
                
                money = Money(money_type, x, self.speed_multiplier, self.gravity_multiplier, self.size_multiplier)
                self.all_sprites.add(money)
                self.money_sprites.add(money)
            
                self.coins_remaining[money_type] -= 1
        
    def draw_menu(self):
        """Affiche le menu principal"""
        self.screen.fill(BLACK)
        
        # Titre
        title = self.title_font.render("BUYOURLIFE SIMULATOR", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Options du menu avec sélection par clavier et souris
        mouse_pos = pygame.mouse.get_pos()
        
        for i, item in enumerate(self.menu_items):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250 + i * 60, 300, 50)
            
            # Choix de la couleur selon la sélection ou le survol
            if i == self.selected_menu_item or rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GREEN, rect)
                text_color = BLACK
            else:
                pygame.draw.rect(self.screen, WHITE, rect, 2)
                text_color = WHITE
            
            text = self.menu_font.render(item, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_skin_menu(self):
        """Affiche le menu de sélection des skins"""
        self.screen.fill(BLACK)
        
        title = self.title_font.render("Sélection du Skin", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Affichage des skins
        skin_index = 0
        mouse_pos = pygame.mouse.get_pos()
        
        for skin_name, skin_color in SKINS.items():
            col = skin_index % 2
            row = skin_index // 2
            
            x = SCREEN_WIDTH // 4 + col * SCREEN_WIDTH // 2
            y = 200 + row * 120
            
            rect = pygame.Rect(x - 75, y - 50, 150, 100)
            pygame.draw.rect(self.screen, skin_color, rect)
            
            # Indique le skin sélectionné
            if skin_name == self.selected_skin:
                pygame.draw.rect(self.screen, WHITE, rect, 3)
            elif rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GREEN, rect, 2)
            
            text = self.menu_font.render(skin_name.title(), True, BLACK)
            text_rect = text.get_rect(center=(x, y + 70))
            self.screen.blit(text, text_rect)
            
            skin_index += 1
        
        # Bouton retour
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
        
        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, RED, back_rect)
            text_color = WHITE
        else:
            pygame.draw.rect(self.screen, WHITE, back_rect, 2)
            text_color = WHITE
            
        back_text = self.menu_font.render("Retour", True, text_color)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
    
    def draw_game(self):
        """Affiche l'écran de jeu avec l'interface"""
        self.screen.fill(BLACK)
        
        # Utilise le fond personnalisé ou le fond par défaut
        if self.custom_background:
            self.game_surface.blit(self.custom_background, (0, 0))
        else:
            self.game_surface.fill(self.default_background)
        
        # Dessine les sprites sur la surface de jeu
        self.all_sprites.draw(self.game_surface)
        
        # Affiche la surface de jeu
        game_x = (SCREEN_WIDTH - GAME_WIDTH) // 2
        game_y = 0
        self.screen.blit(self.game_surface, (game_x, game_y))
        
        # Interface utilisateur
        # Niveau
        level_text = self.ui_font.render(f"Niveau: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (20, 20))
    
        # Argent collecté / Objectif
        money_text = self.ui_font.render(f"€{self.money_collected:.2f} / €{LEVEL_GOALS[self.current_level]}", True, GREEN)
        self.screen.blit(money_text, (20, 60))
    
        # Temps restant
        if self.countdown > 0:
            time_text = self.ui_font.render(f"{int(self.countdown)}", True, RED)
            time_text_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(time_text, time_text_rect)
        else:
            time_text = self.ui_font.render(f"Temps: {int(self.time_left)}s", True, WHITE)
            self.screen.blit(time_text, (SCREEN_WIDTH - 200, 20))
        
        # Message de pause
        if self.is_paused:
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 128))
            self.screen.blit(pause_overlay, (0, 0))
        
            pause_text = self.title_font.render("PAUSE", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
        
            continue_text = self.menu_font.render("Appuyez sur ÉCHAP pour continuer", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            self.screen.blit(continue_text, continue_rect)
    
    def draw_game_over(self):
        """Affiche l'écran de fin de partie"""
        self.screen.fill(BLACK)
        
        if self.current_level > 5:
            title = self.title_font.render("VICTOIRE!", True, GREEN)
            message = "Vous avez terminé tous les niveaux!"
        else:
            title = self.title_font.render("GAME OVER", True, RED)
            if self.money_collected >= LEVEL_GOALS[self.current_level]:
                message = f"Niveau {self.current_level} terminé avec succès!"
            else:
                message = f"Vous n'avez pas atteint l'objectif du niveau"
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        message_text = self.menu_font.render(message, True, WHITE)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(message_text, message_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Bouton rejouer
        replay_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 60)
        if replay_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GREEN, replay_rect)
            replay_color = BLACK
        else:
            pygame.draw.rect(self.screen, GREEN, replay_rect, 2)
            replay_color = GREEN
            
        replay_text = self.menu_font.render("Rejouer", True, replay_color)
        replay_text_rect = replay_text.get_rect(center=replay_rect.center)
        self.screen.blit(replay_text, replay_text_rect)
        
        # Bouton menu
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 480, 300, 60)
        if menu_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BLUE, menu_rect)
            menu_color = WHITE
        else:
            pygame.draw.rect(self.screen, BLUE, menu_rect, 2)
            menu_color = BLUE
            
        menu_text = self.menu_font.render("Menu", True, menu_color)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
    
    def handle_menu_click(self, pos):
        """Gère les clics dans le menu principal"""
        for i, item in enumerate(self.menu_items):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250 + i * 60, 300, 50)
            if rect.collidepoint(pos):
                if i == 0:  # Mode facile
                    self.start_game("easy")
                elif i == 1:  # Mode Normal
                    self.start_game("normal")
                elif i == 2:  # Mode Difficile
                    self.start_game("hard")
                elif i == 3:  # Skins
                    self.state = "skins"
                elif i == 4:  # Fond
                    self.state = "background"
                elif i == 5:  # Quitter
                    self.running = False

    def draw_background_menu(self):
        """Affiche le menu de sélection du fond"""
        self.screen.fill(BLACK)
        
        title = self.title_font.render("Personnaliser le Fond", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Bouton charger fond
        load_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 60)
        if load_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GREEN, load_rect)
            load_color = BLACK
        else:
            pygame.draw.rect(self.screen, GREEN, load_rect, 2)
            load_color = GREEN
            
        load_text = self.menu_font.render("Charger une image", True, load_color)
        load_text_rect = load_text.get_rect(center=load_rect.center)
        self.screen.blit(load_text, load_text_rect)
    
        # Bouton reset fond
        reset_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 280, 300, 60)
        if reset_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BLUE, reset_rect)
            reset_color = WHITE
        else:
            pygame.draw.rect(self.screen, BLUE, reset_rect, 2)
            reset_color = BLUE
        
        reset_text = self.menu_font.render("Fond par défaut", True, reset_color)
        reset_text_rect = reset_text.get_rect(center=reset_rect.center)
        self.screen.blit(reset_text, reset_text_rect)
    
        # Aperçu du fond actuel
        preview_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 360, 200, 120)
        if self.custom_background:
            preview_bg = pygame.transform.scale(self.custom_background, (200, 120))
            self.screen.blit(preview_bg, preview_rect)
        else:
            pygame.draw.rect(self.screen, self.default_background, preview_rect)
        pygame.draw.rect(self.screen, WHITE, preview_rect, 2)
    
        preview_label = self.ui_font.render("Aperçu", True, WHITE)
        preview_label_rect = preview_label.get_rect(center=(SCREEN_WIDTH // 2, 340))
        self.screen.blit(preview_label, preview_label_rect)
    
        # Bouton retour
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, RED, back_rect)
            back_color = WHITE
        else:
            pygame.draw.rect(self.screen, WHITE, back_rect, 2)
            back_color = WHITE
        
        back_text = self.menu_font.render("Retour", True, back_color)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

    def handle_background_click(self, pos):
        """Gère les clics dans le menu de fond"""
        # Bouton charger
        load_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 60)
        if load_rect.collidepoint(pos):
            self.load_custom_background()
            return
    
        # Bouton reset
        reset_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 280, 300, 60)
        if reset_rect.collidepoint(pos):
            self.reset_custom_background()
            return
    
        # Bouton retour
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
        if back_rect.collidepoint(pos):
            self.state = "menu"
    
    def handle_skin_click(self, pos):
        """Gère les clics dans le menu des skins"""
        # Sélection des skins
        skin_index = 0
        for skin_name in SKINS:
            col = skin_index % 2
            row = skin_index // 2
            
            x = SCREEN_WIDTH // 4 + col * SCREEN_WIDTH // 2
            y = 200 + row * 120
            
            rect = pygame.Rect(x - 75, y - 50, 150, 100)
            if rect.collidepoint(pos):
                self.selected_skin = skin_name
                return
            
            skin_index += 1
        
        # Bouton retour
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50)
        if back_rect.collidepoint(pos):
            self.state = "menu"
    
    def handle_game_over_click(self, pos):
        """Gère les clics dans l'écran game over"""
        # Rejouer
        replay_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 60)
        if replay_rect.collidepoint(pos):
            if self.current_level > 5:
                self.current_level = 1
            self.start_game("run")
        
        # Menu
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 480, 300, 60)
        if menu_rect.collidepoint(pos):
            self.state = "menu"
    
    def start_game(self, mode="normal"):
        """Démarre une nouvelle partie"""
        self.state = "playing"
        self.money_collected = 0
        self.time_left = 60
        self.countdown = 3
        self.is_paused = False
        self.game_mode = mode
        
        # Difficulté basée sur le mode
        if mode == "easy":
            self.money_spawn_delay = 300
            self.speed_multiplier = 0.5
            self.gravity_multiplier = 0.2  # Gravité réduite (0.5 * 0.2 = 0.1)
            self.size_multiplier = 1.5     # Taille augmentée
            self.bag_speed_multiplier = 1.2
        elif mode == "normal":
            self.money_spawn_delay = 500
            self.speed_multiplier = 1
            self.gravity_multiplier = 1.0   # Gravité normale (0.5 * 1.0 = 0.5)
            self.size_multiplier = 1.0      # Taille normale
            self.bag_speed_multiplier = 1.0
        elif mode == "hard":
            self.money_spawn_delay = 700
            self.speed_multiplier = 1.0
            self.gravity_multiplier = 1.4   # Gravité augmentée (0.5 * 1.4 = 0.7)
            self.size_multiplier = 0.8      # Taille réduite
            self.bag_speed_multiplier = 1.0
        else:  
            self.money_spawn_delay = 500
            self.speed_multiplier = 1.5
            self.gravity_multiplier = 1.0
            self.size_multiplier = 1.0
            self.bag_speed_multiplier = 1.0
        
        # Réinitialise les sprites
        self.all_sprites.empty()
        self.money_sprites.empty()
        
        # Crée le sac du joueur
        self.bag = Bag(self.selected_skin, self.bag_speed_multiplier)
        self.all_sprites.add(self.bag)
        
        # Configure l'argent pour le niveau
        self.setup_money_for_level()
        
        # Spawn initial de pièces
        self.spawn_multiple_money(5)
        
        # Initialise le temps de départ
        self.level_start_time = time.time()
    
    def check_collisions(self):
        """Vérifie les collisions entre le sac et l'argent"""
        hits = pygame.sprite.spritecollide(self.bag, self.money_sprites, True)
        for hit in hits:
            self.money_collected += hit.value
    
    def update_timer(self, dt):
        """Met à jour les timers du jeu"""
        if self.countdown > 0:
            self.countdown -= dt
            if self.countdown <= 0:
                self.countdown = 0
        elif not self.is_paused:
            self.time_left -= dt
            
            # Countdown effect at the end
            if int(self.time_left) <= 5 and int(self.time_left) >= 1:
                # Highlight the timer on whole seconds
                if int(self.time_left) != int(self.time_left + dt):
                    countdown_text = self.title_font.render(str(int(self.time_left)), True, RED)
                    countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    self.screen.blit(countdown_text, countdown_rect)
                    pygame.display.flip()
                    pygame.time.delay(200)  # Pause briefly to emphasize the countdown
            
            if self.time_left <= 0:
                self.time_left = 0
                self.check_level_complete()
    
    def check_level_complete(self):
        """Vérifie si le niveau est terminé"""
        if self.money_collected >= LEVEL_GOALS[self.current_level]:
            # Niveau réussi
            self.current_level += 1
            
            if self.current_level > 5:
                # Jeu terminé
                self.state = "game_over"
            else:
                # Niveau suivant
                self.money_collected = 0
                self.time_left = 60
                self.countdown = 3
                self.setup_money_for_level()
                
                # Initialise le temps de départ
                self.level_start_time = time.time()
        else:
            # Niveau échoué
            self.current_level = 1
            self.state = "game_over"
    
    def handle_events(self):
        """Gère les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_UP:
                        self.selected_menu_item = (self.selected_menu_item - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_menu_item = (self.selected_menu_item + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        item = self.menu_items[self.selected_menu_item]
                        if item == "Mode Facile":
                            self.start_game("easy")
                        elif item == "Mode Normal":
                            self.start_game("normal")
                        elif item == "Mode Difficile":
                            self.start_game("hard")
                        elif item == "Skins":
                            self.state = "skins"
                        elif item == "Fond":
                            self.state = "background"
                        elif item == "Quitter":
                            self.running = False
                
                elif event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.is_paused = not self.is_paused
                    elif self.state == "skins":
                        self.state = "menu"
                    elif self.state == "background":
                        self.state = "menu"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    if self.state == "menu":
                        self.handle_menu_click(event.pos)
                    elif self.state == "skins":
                        self.handle_skin_click(event.pos)
                    elif self.state == "game_over":
                        self.handle_game_over_click(event.pos)
                    elif self.state == "background":
                        self.handle_background_click(event.pos)
    
    def update(self):
        """Met à jour l'état du jeu"""
        dt = self.clock.tick(FPS) / 1000.0  # Delta time en secondes
        
        if self.state == "playing" and not self.is_paused and self.countdown <= 0:
            # Mise à jour des sprites
            keys = pygame.key.get_pressed()
            self.bag.update(keys)
            self.money_sprites.update()
            
            # Vérification des collisions
            self.check_collisions()
            
            # Spawn de l'argent
            self.spawn_money()
            
            # Mise à jour du timer
            self.update_timer(dt)
        elif self.state == "playing" and not self.is_paused:
            # Countdown avant de commencer le niveau
            self.update_timer(dt)
    
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            self.handle_events()
            self.update()
            
            # Affichage selon l'état
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "skins":
                self.draw_skin_menu()
            elif self.state == "background":
                self.draw_background_menu()
            elif self.state == "playing":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
# Lancement du jeu
if __name__ == "__main__":
    game = BuyourlifeSimulator()
    game.run()
