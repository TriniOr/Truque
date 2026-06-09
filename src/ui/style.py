import pygame
_font_cache = {}

def get_font(size: str) -> pygame.font.Font:
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font("src/ui/fonts/Silkscreen/Silkscreen-Regular.ttf", size)
    return _font_cache[size]

# --- Colores ---
COLOR_BG         = (4, 98, 56)
COLOR_PRIMARY    = (30, 30, 30)
COLOR_HOVER      = (60,60,60)
COLOR_SELECTED   = (0,30,60)
COLOR_FORBIDDEN  = (120,120,120)
COLOR_TEXT       = (255, 255, 255)
COLOR_TEXT_HIGH  = (130, 255, 200)
COLOR_TEXT_DIM   = (160, 160, 160)
COLOR_EQUIPO1    = (255, 150, 150)
COLOR_EQUIPO2    = (150, 150, 255)
COLOR_MANO       = (200, 170, 50)

# --- Tamaños de fuente ---
FONT_SM = 16
FONT_MD = 22
FONT_LG = 32
FONT_XL = 48

# --- Layout ---
WINDOW_SIZE      = (1920, 1080)
PADDING          = 20
BUTTON_H         = 48
BUTTON_W         = 350
LINE_H           = 60

# --- Cartas ---
CARD_SIZE       = (73, 113)
CARD_SIZE_SM    = (36,56)
CARD_SIZE_LG    = (146, 226)
CARD_HOVER      = (255, 220, 50)

NOMBRES_PUEBLO = [
    "IKER", "ALEX", "JAVI", "NINI", "CARLOS", "K", "ESTRELLA", "JULIA", "ISAIAS", "ALCALDE"
]