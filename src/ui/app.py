import pygame
from src.ui.style import WINDOW_SIZE
from src.ui.scenes.menu import MenuScene
from src.ui.components.button import Button

FPS = 60
TITLE = "Truque"

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = False
        self.scene = MenuScene(self)
        self.btn_exit = Button(
            rect=(WINDOW_SIZE[0] - 100 - 10, 10, 100, 40),
            label="Salir",
            on_click=self._quit,
        )

    def _quit(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.btn_exit.handle_event(event)
            self.scene.handle_event(event)

    def _update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_exit.update(mouse_pos)
        self.scene.update(dt)

    def _render(self):
        self.scene.draw(self.screen)
        self.btn_exit.draw(self.screen)
        pygame.display.flip()

    def change_scene(self, scene):
        self.scene = scene