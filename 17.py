import os
import sys
import time
import pygame
from pygame.locals import *

# Подключаем основную логику игры
try:
    from durak_game import Card, CardSuit, DurakGame
except ImportError:
    print("Ошибка: не найден файл с логикой игры durak_game.py")
    sys.exit(1)

# Константы для интерфейса
SCREEN_WIDTH = 1224  # Увеличено на 200
SCREEN_HEIGHT = 968  # Увеличено на 200
FPS = 60
BACKGROUND_COLOR = (0, 100, 0)  # Темно-зеленый цвет стола
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Константы для карт
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 30
CARD_BACK_COLOR = (30, 50, 150)

# Символы мастей для Pygame (заменяем юникод на текстовые обозначения)
SUIT_SYMBOLS = {
    '♠': 'S',  # Пики
    '♥': 'H',  # Червы
    '♦': 'D',  # Бубны
    '♣': 'C'   # Трефы
}

SUIT_COLORS = {
    '♠': BLACK,
    '♥': RED,
    '♦': RED,
    '♣': BLACK
}

class Button:
    """Класс для создания кнопок в интерфейсе."""
    
    def __init__(self, x, y, width, height, text, color=(200, 200, 200), hover_color=(150, 150, 150), text_color=BLACK, font_size=24):
        """
        Инициализация кнопки.
        
        Args:
            x, y: координаты верхнего левого угла кнопки
            width, height: размеры кнопки
            text: текст на кнопке
            color: цвет кнопки
            hover_color: цвет кнопки при наведении
            text_color: цвет текста
            font_size: размер шрифта
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.current_color = color
        self.is_hovered = False
    
    def draw(self, screen):
        """Отрисовка кнопки на экране."""
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        font = pygame.font.Font(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        """Обновление состояния кнопки в зависимости от положения мыши."""
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.is_hovered = True
        else:
            self.current_color = self.color
            self.is_hovered = False
    
    def is_clicked(self, event):
        """Проверка, нажата ли кнопка."""
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class CardSprite:
    """Класс для графического представления игральной карты."""
    
    # Словарь для хранения загруженных изображений карт
    card_images = {}
    card_back = None
    
    @classmethod
    def load_images(cls):
        """Загрузка изображений карт."""
        # Загружаем фон карты (рубашку)
        if cls.card_back is None:
            # Создаем рубашку программно
            cls.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            cls.card_back.fill(CARD_BACK_COLOR)
            pygame.draw.rect(cls.card_back, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
            font = pygame.font.Font(None, 40)
            text = font.render("?", True, WHITE)
            text_rect = text.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
            cls.card_back.blit(text, text_rect)
        
        # Создание карт программно
        suits = {'♠': 'spades', '♥': 'hearts', '♦': 'diamonds', '♣': 'clubs'}
        ranks = {'6': '6', '7': '7', '8': '8', '9': '9', '10': '10', 
                'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
        
        for suit_symbol in suits:
            for rank_symbol in ranks:
                card_key = f"{rank_symbol}{suit_symbol}"
                if card_key not in cls.card_images:
                    # Создаем изображение карты
                    image = cls.create_card_image(rank_symbol, suit_symbol)
                    cls.card_images[card_key] = image
    
    @classmethod
    def create_card_image(cls, rank, suit):
        """Создание изображения карты."""
        image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        image.fill(WHITE)
        pygame.draw.rect(image, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
        
        font = pygame.font.Font(None, 40)
        suit_color = SUIT_COLORS.get(suit, BLACK)
        
        # Ранг в верхнем левом и нижнем правом углах
        rank_text = font.render(rank, True, suit_color)
        image.blit(rank_text, (5, 5))
        image.blit(rank_text, (CARD_WIDTH - rank_text.get_width() - 5, CARD_HEIGHT - rank_text.get_height() - 5))
        
        # Масть в центре
        font = pygame.font.Font(None, 80)
        suit_symbol = SUIT_SYMBOLS.get(suit, suit)  # Используем текстовое обозначение масти
        suit_text = font.render(suit_symbol, True, suit_color)
        suit_rect = suit_text.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
        image.blit(suit_text, suit_rect)
        
        return image
    
    def __init__(self, card=None, x=0, y=0, face_up=True):
        """
        Инициализация спрайта карты.
        
        Args:
            card: объект карты или None
            x, y: координаты левого верхнего угла
            face_up: True если карта лицом вверх, False если рубашкой
        """
        self.card = card
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.face_up = face_up
        self.dragging = False
        self.drag_offset = (0, 0)
        
        # Загружаем изображения карт при первом создании
        if not CardSprite.card_images:
            CardSprite.load_images()
    
    def draw(self, screen):
        """Отрисовка карты на экране."""
        if self.card is None:
            return
        
        if self.face_up:
            card_key = f"{self.card.rank}{self.card.suit}"
            image = CardSprite.card_images.get(card_key, CardSprite.create_card_image(self.card.rank, self.card.suit))
        else:
            image = CardSprite.card_back
        
        screen.blit(image, self.rect)
    
    def update(self, mouse_pos, is_dragging):
        """Обновление позиции карты при перетаскивании."""
        if self.dragging and is_dragging:
            self.rect.x = mouse_pos[0] - self.drag_offset[0]
            self.rect.y = mouse_pos[1] - self.drag_offset[1]
    
    def is_clicked(self, event):
        """Проверка, была ли нажата карта."""
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                return True
        return False
    
    def stop_dragging(self):
        """Прекращение перетаскивания карты."""
        self.dragging = False 

class DurakGUI:
    """Основной класс графического интерфейса игры Дурак."""
    
    def __init__(self):
        """Инициализация графического интерфейса."""
        pygame.init()
        pygame.display.set_caption("Карточная игра Дурак")
        
        # Создаем окно
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Состояние экрана (меню, игра, правила, etc.)
        self.current_screen = 'menu'
        
        # Игровая логика
        self.game = None
        
        # Спрайты карт
        self.player_cards = []
        self.opponent_cards = []
        self.table_cards = []
        self.deck_sprite = None
        self.trump_card = None
        
        # Кнопки меню
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 60, "Новая игра", color=(100, 200, 100)),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 60, "Загрузить игру", color=(100, 150, 200)),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 60, "Правила", color=(200, 200, 100)),
            Button(SCREEN_WIDTH//2 - 150, 440, 300, 60, "О программе", color=(200, 150, 100)),
            Button(SCREEN_WIDTH//2 - 150, 520, 300, 60, "Выход", color=(200, 100, 100))
        ]
        
        # Кнопки игрового процесса: перемещаем их выше, чтобы не перекрывали карты
        self.game_buttons = []
        
        # Кнопки в других экранах
        self.back_button = Button(30, 700, 120, 40, "Назад")
        
        # Фонты
        self.title_font = pygame.font.Font(None, 72)
        self.normal_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Переменные для перетаскивания карт
        self.dragging = False
        self.selected_card = None
        
        # Запуск основного цикла
        self.run()
    
    def run(self):
        """Основной игровой цикл."""
        running = True
        
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                self.handle_event(event)
            
            # Обновление
            self.update()
            
            # Отрисовка
            self.draw()
            
            # Ограничение FPS
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event):
        """Обработка событий."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Обработка кнопок в зависимости от текущего экрана
        if self.current_screen == 'menu':
            self.handle_menu_events(event)
        elif self.current_screen == 'game':
            self.handle_game_events(event)
        elif self.current_screen == 'rules':
            self.handle_rules_events(event)
        elif self.current_screen == 'about':
            self.handle_about_events(event)
        elif self.current_screen == 'game_over':
            self.handle_game_over_events(event)
        
        # Прекращение перетаскивания при отпускании кнопки мыши
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if self.dragging and self.selected_card:
                self.handle_card_drop(self.selected_card)
                self.selected_card.stop_dragging()
                self.dragging = False
                self.selected_card = None
    
    def handle_menu_events(self, event):
        """Обработка событий в меню."""
        for i, button in enumerate(self.menu_buttons):
            button.update(pygame.mouse.get_pos())
            
            if button.is_clicked(event):
                if i == 0:  # Новая игра
                    self.start_new_game()
                elif i == 1:  # Загрузить игру
                    self.load_game()
                elif i == 2:  # Правила
                    self.current_screen = 'rules'
                elif i == 3:  # О программе
                    self.current_screen = 'about'
                elif i == 4:  # Выход
                    pygame.quit()
                    sys.exit()
    
    def init_game_interface(self):
        """Инициализация игрового интерфейса."""
        # Сброс спрайтов карт
        self.clear_sprites()
        
        # Создание колоды и козыря (если есть)
        self.create_deck_and_trump_sprites()
        
        # Обновление спрайтов карт
        self.update_card_sprites()
        
        # Создание основных игровых кнопок
        button_width, button_height = 180, 60
        button_margin = 30
        
        # Располагаем кнопки ниже, чтобы не перекрывались с картами игрока
        # Располагаем кнопки в нижней части экрана, но выше чем информационная панель
        button_y = SCREEN_HEIGHT - 120
        
        take_cards_button = Button(
            SCREEN_WIDTH - button_width - button_margin,
            button_y,
            button_width,
            button_height,
            "Взять карты",
            color=(200, 100, 100),
            font_size=30
        )
        
        done_button = Button(
            SCREEN_WIDTH - 2 * (button_width + button_margin),
            button_y,
            button_width,
            button_height,
            "Бито",
            color=(100, 200, 100),
            font_size=30
        )
        
        menu_button = Button(
            button_margin,
            button_y,
            button_width,
            button_height,
            "Меню",
            color=(100, 150, 200),
            font_size=30
        )
        
        save_button = Button(
            2 * button_margin + button_width,
            button_y,
            button_width,
            button_height,
            "Сохранить",
            color=(200, 200, 100),
            font_size=30
        )
        
        self.game_buttons = [take_cards_button, done_button, menu_button, save_button]
        
        # Обновление состояния кнопок
        self.update_buttons_state()
    
    def handle_game_events(self, event):
        """Обработка событий в игре."""
        # Обновление кнопок и их доступности
        self.update_buttons_state()
        
        # Обработка кликов по кнопкам
        for i, button in enumerate(self.game_buttons):
            if button.is_clicked(event):
                if i == 0:  # Взять карты
                    if self.game and self.game.state.defender == self.game.human_player:
                        self.game.take_cards()
                        self.update_card_sprites()
                elif i == 1:  # Бито
                    if self.game:
                        if self.game.state.attacker == self.game.human_player:
                            # Атакующий завершает атаку
                            self.game.done_attacking()
                        elif self.game.state.defender == self.game.human_player:
                            # Проверяем, все ли карты отбиты
                            all_defended = True
                            for _, defend_card in self.game.state.table:
                                if defend_card is None:
                                    all_defended = False
                                    break
                            
                            if all_defended and self.game.state.table:
                                # Если все карты отбиты, завершаем защиту
                                # Очищаем стол
                                self.game.done_attacking()
                                # Выводим сообщение об успешной защите
                                self.show_message("Защита успешна! Вы атакуете.", 1500)
                        
                        self.update_card_sprites()
                elif i == 2:  # Меню
                    self.current_screen = 'menu'
                elif i == 3:  # Сохранить
                    if self.game:
                        self.game.save_game("quick_save")
                        self.show_message("Игра сохранена")
        
        # Обработка нажатий на карты
        for card_sprite in self.player_cards:
            if not self.dragging and card_sprite.is_clicked(event):
                # Проверяем возможность хода этой картой
                if self.can_play_card(card_sprite.card):
                    self.dragging = True
                    self.selected_card = card_sprite
                else:
                    # Показываем индикацию, что ход этой картой невозможен
                    self.show_message("Эту карту нельзя сейчас сыграть", 1000)
    
    def update_buttons_state(self):
        """Обновляет состояние кнопок в зависимости от текущего состояния игры."""
        if not self.game or not hasattr(self.game, 'state'):
            return
            
        # Кнопка "Взять карты" - активна только для защищающегося
        if len(self.game_buttons) >= 1:
            take_button = self.game_buttons[0]
            if self.game.state.defender == self.game.human_player:
                take_button.color = (200, 100, 100)  # Красная - активная
                take_button.hover_color = (255, 150, 150)
            else:
                take_button.color = (150, 100, 100)  # Темно-красная - неактивная
                take_button.hover_color = (180, 110, 110)
        
        # Кнопка "Бито" - активна для атакующего и для защитника, отбившего все карты
        if len(self.game_buttons) >= 2:
            done_button = self.game_buttons[1]
            
            # Проверяем, все ли карты отбиты
            all_defended = True
            if hasattr(self.game.state, 'table') and self.game.state.table:
                for _, defend_card in self.game.state.table:
                    if defend_card is None:
                        all_defended = False
                        break
            
            if (self.game.state.attacker == self.game.human_player and self.game.state.table) or \
               (self.game.state.defender == self.game.human_player and all_defended and self.game.state.table):
                done_button.color = (100, 200, 100)  # Зеленая - активная
                done_button.hover_color = (150, 255, 150)
            else:
                done_button.color = (100, 150, 100)  # Темно-зеленая - неактивная
                done_button.hover_color = (110, 180, 110)
        
        # Обновляем текущий цвет кнопок
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_buttons:
            button.update(mouse_pos)
    
    def can_play_card(self, card):
        """Проверяет, можно ли сыграть данную карту в текущей ситуации."""
        if not self.game or not card:
            return False
            
        # Если игрок атакует
        if self.game.state.attacker == self.game.human_player:
            # Проверяем, можно ли добавить эту карту на стол
            if self.game.state.can_add_card(card):
                return True
                
        # Если игрок защищается
        elif self.game.state.defender == self.game.human_player:
            # Проверяем, может ли карта отбить хоть одну атакующую карту
            for attack_pair in self.game.state.table:
                attack_card, defend_card = attack_pair
                if defend_card is None and self.game.state.can_beat_card(attack_card, card):
                    return True
                    
        return False
    
    def handle_rules_events(self, event):
        """Обработка событий в экране правил."""
        self.back_button.update(pygame.mouse.get_pos())
        if self.back_button.is_clicked(event):
            self.current_screen = 'menu'
    
    def handle_about_events(self, event):
        """Обработка событий в экране "О программе"."""
        self.back_button.update(pygame.mouse.get_pos())
        if self.back_button.is_clicked(event):
            self.current_screen = 'menu'
    
    def handle_game_over_events(self, event):
        """Обработка событий в экране окончания игры."""
        self.back_button.update(pygame.mouse.get_pos())
        if self.back_button.is_clicked(event):
            self.current_screen = 'menu'
    
    def handle_card_drop(self, card_sprite):
        """Обработка сброса карты после перетаскивания."""
        if self.game is None or card_sprite is None or card_sprite.card is None:
            return
        
        try:
            # Определение индекса карты в руке игрока
            if card_sprite.card not in self.game.human_player.hand:
                return
                
            # Проверяем, куда сбросили карту
            # Зона стола - атака или защита - увеличиваем область стола
            table_area = pygame.Rect(SCREEN_WIDTH//2 - 350, SCREEN_HEIGHT//2 - 200, 700, 400)
            
            if table_area.collidepoint(card_sprite.rect.center):
                # Если игрок атакует, просто выкладываем карту
                if self.game.state.attacker == self.game.human_player:
                    # Визуальная анимация карты перемещающейся на стол
                    target_x = SCREEN_WIDTH // 2
                    if hasattr(self.game.state, 'table') and self.game.state.table:
                        target_x = SCREEN_WIDTH // 2 - (len(self.game.state.table) * (CARD_WIDTH + CARD_SPACING) // 2)
                    target_y = SCREEN_HEIGHT // 2 - 180  # Обновлена координата соответственно новому положению
                    self.animate_card_movement(card_sprite, target_x, target_y)
                    
                    # Выполняем атаку
                    self.game.attack(card_sprite.card)
                    
                # Если игрок защищается, ищем ближайшую атакующую карту
                elif self.game.state.defender == self.game.human_player:
                    # Ищем ближайшую карту атаки
                    nearest_attack_pair = self.find_nearest_attack_card(card_sprite.rect.center)
                    if nearest_attack_pair is not None and len(nearest_attack_pair) >= 1:
                        attacking_card = nearest_attack_pair[0]  # Первый элемент пары - атакующая карта
                        if attacking_card is not None:
                            # Находим спрайт атакующей карты для анимации
                            attack_sprite = None
                            for i, sprite in enumerate(self.table_cards):
                                if i % 2 == 0 and sprite.card == attacking_card:
                                    attack_sprite = sprite
                                    break
                            
                            if attack_sprite:
                                # Визуальная анимация карты перемещающейся на позицию защиты
                                target_x = attack_sprite.rect.x
                                target_y = attack_sprite.rect.y + CARD_HEIGHT // 2  # Половина высоты карты для лучшего выравнивания
                                self.animate_card_movement(card_sprite, target_x, target_y)
                            
                            # Выполняем защиту
                            self.game.defend(attacking_card, card_sprite.card)
            
            # Обновляем спрайты карт
            self.update_card_sprites()
            
        except Exception as e:
            print(f"Ошибка при обработке сброса карты: {e}")
            self.update_card_sprites()
    
    def animate_card_movement(self, card_sprite, target_x, target_y, frames=5):
        """Анимирует перемещение карты из текущей позиции в целевую."""
        start_x, start_y = card_sprite.rect.x, card_sprite.rect.y
        dx = (target_x - start_x) / frames
        dy = (target_y - start_y) / frames
        
        for i in range(frames):
            # Обновляем положение карты
            card_sprite.rect.x = int(start_x + dx * (i + 1))
            card_sprite.rect.y = int(start_y + dy * (i + 1))
            
            # Перерисовываем экран
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_game()
            pygame.display.flip()
            
            # Небольшая задержка для эффекта анимации
            pygame.time.delay(30)
    
    def find_nearest_attack_card(self, position):
        """Находит ближайшую атакующую карту на столе."""
        min_distance = float('inf')
        nearest_pair = None
        
        # Проверка, что на столе есть карты
        if not hasattr(self.game, 'state') or not hasattr(self.game.state, 'table') or not self.game.state.table or not self.table_cards:
            return None
            
        try:
            for i, (attack_sprite, defend_sprite) in enumerate(zip(self.table_cards[::2], self.table_cards[1::2])):
                # Проверка на валидность индекса и существование неотбитой карты
                if i < len(self.game.state.table) and attack_sprite.card is not None and defend_sprite.card is None:
                    distance = ((attack_sprite.rect.centerx - position[0])**2 + 
                               (attack_sprite.rect.centery - position[1])**2)**0.5
                    if distance < min_distance:
                        min_distance = distance
                        nearest_pair = self.game.state.table[i]
        except Exception as e:
            print(f"Ошибка при поиске ближайшей карты атаки: {e}")
            return None
            
        return nearest_pair
    
    def update(self):
        """Обновление состояния игры."""
        try:
            mouse_pos = pygame.mouse.get_pos()
            
            # Обновление кнопок в зависимости от экрана
            if self.current_screen == 'menu':
                for button in self.menu_buttons:
                    button.update(mouse_pos)
            elif self.current_screen == 'game':
                for button in self.game_buttons:
                    button.update(mouse_pos)
                
                # Обновление позиции перетаскиваемой карты
                if self.selected_card:
                    self.selected_card.update(mouse_pos, self.dragging)
                
                # Проверка окончания игры
                if self.game and self.game.state.winner is not None:
                    self.current_screen = 'game_over'
                
                # Обработка ходов компьютера
                if self.game and not self.dragging:  # Не делаем ход компьютера, если игрок перетаскивает карту
                    # Проверяем, является ли компьютер атакующим или защищающимся
                    if self.game.state.attacker == self.game.opponent or self.game.state.defender == self.game.opponent:
                        # AI делает ход
                        self.game.computer_move()
                        # Обновляем отображение
                        self.update_card_sprites()
            elif self.current_screen in ['rules', 'about', 'game_over']:
                self.back_button.update(mouse_pos)
        except Exception as e:
            print(f"Ошибка в методе update: {e}")
            # Если произошла ошибка в игре, возвращаемся в меню
            if self.current_screen == 'game':
                self.current_screen = 'menu'
                self.show_message("Произошла ошибка в игре")
    
    def draw(self):
        """Отрисовка текущего экрана."""
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.current_screen == 'menu':
            self.draw_menu()
        elif self.current_screen == 'game':
            self.draw_game()
        elif self.current_screen == 'rules':
            self.draw_rules()
        elif self.current_screen == 'about':
            self.draw_about()
        elif self.current_screen == 'game_over':
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Отрисовка главного меню."""
        # Заголовок
        title_text = self.title_font.render("Карточная игра Дурак", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка кнопок
        for button in self.menu_buttons:
            button.draw(self.screen)
    
    def draw_game(self):
        """Отрисовка игрового процесса."""
        if self.game is None:
            return
        
        # Отрисовка колоды и козыря
        if self.deck_sprite:
            self.deck_sprite.draw(self.screen)
        if self.trump_card:
            self.trump_card.draw(self.screen)
        
        # Отображение информации о козыре
        trump_suit = self.game.state.trump_suit if hasattr(self.game.state, 'trump_suit') else None
        if trump_suit:
            trump_symbol = SUIT_SYMBOLS.get(trump_suit, trump_suit)
            trump_color = SUIT_COLORS.get(trump_suit, BLACK)
            trump_text = self.normal_font.render(f"Козырь: {trump_symbol}", True, trump_color)
            self.screen.blit(trump_text, (50, 50))
        
        # Отображение количества карт в колоде
        if hasattr(self.game.state, 'deck') and self.game.state.deck and hasattr(self.game.state.deck, 'cards'):
            deck_text = self.normal_font.render(f"Колода: {len(self.game.state.deck.cards)}", True, WHITE)
            self.screen.blit(deck_text, (50, 90))
        
        # Отрисовка карт противника (рубашкой вверх)
        for card in self.opponent_cards:
            card.draw(self.screen)
        
        # Информация о противнике
        opponent_text = self.normal_font.render(
            f"{self.game.opponent.name}: {len(self.game.opponent.hand)} карт", 
            True, WHITE
        )
        self.screen.blit(opponent_text, (SCREEN_WIDTH//2 - 100, 50))
        
        # Отрисовка карт на столе
        for card in self.table_cards:
            card.draw(self.screen)
        
        # Панель информации о состоянии игры (информация игрока, статус игры)
        info_panel = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        info_panel.fill((0, 70, 0, 200))  # Полупрозрачный фон, немного темнее
        
        # Информация о текущем игроке - увеличенный шрифт
        player_font = pygame.font.Font(None, 40)  # Увеличенный шрифт
        player_text = player_font.render(
            f"{self.game.human_player.name}: {len(self.game.human_player.hand)} карт", 
            True, WHITE
        )
        player_text_rect = player_text.get_rect(midleft=(50, info_panel.get_height()//2))
        info_panel.blit(player_text, player_text_rect)
        
        # Проверка всех ли карты отбиты (для статуса)
        all_defended = True
        if hasattr(self.game.state, 'table') and self.game.state.table:
            for _, defend_card in self.game.state.table:
                if defend_card is None:
                    all_defended = False
                    break
        
        # Статус (атака/защита с подробностями) - увеличенный шрифт
        status_font = pygame.font.Font(None, 40)  # Увеличенный шрифт
        status_text = ""
        if self.game.state.attacker == self.game.human_player:
            if hasattr(self.game.state, 'table') and self.game.state.table:
                status_text = "Ваш ход: можете подкинуть или завершить"
            else:
                status_text = "Ваш ход: выберите карту для атаки"
        else:
            if all_defended and hasattr(self.game.state, 'table') and self.game.state.table:
                status_text = "Все карты отбиты! Можете завершить защиту"
            elif hasattr(self.game.state, 'table') and self.game.state.table:
                status_text = "Ваш ход: отбейтесь или возьмите карты"
            else:
                status_text = "Ваш ход: ожидайте атаки"
        
        status_surface = status_font.render(status_text, True, YELLOW)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, info_panel.get_height()//2))
        info_panel.blit(status_surface, status_rect)
        
        # Добавляем панель информации внизу экрана, выше кнопок
        self.screen.blit(info_panel, (0, SCREEN_HEIGHT - 200))
        
        # Отрисовка карт игрока
        for card in self.player_cards:
            card.draw(self.screen)
        
        # Отрисовка кнопок
        for button in self.game_buttons:
            button.draw(self.screen)
    
    def draw_rules(self):
        """Отрисовка экрана с правилами."""
        # Заголовок
        title_text = self.title_font.render("Правила игры", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Текст правил
        rules = [
            "Цель игры: избавиться от всех карт в руке. Последний игрок с картами становится 'дураком'.",
            "",
            "Основные правила:",
            "• Игра ведется колодой из 36 карт (от 6 до туза).",
            "• В начале игры каждому игроку раздается по 6 карт.",
            "• Последняя карта колоды переворачивается и определяет козырную масть.",
            "• Козырная масть имеет преимущество над другими мастями.",
            "• Игрок с наименьшим козырем начинает игру в качестве атакующего.",
            "",
            "Ход игры:",
            "• Атакующий игрок выкладывает карту на стол.",
            "• Защищающийся должен побить эту карту картой той же масти, но большего достоинства,",
            "  или любой картой козырной масти (если атакующая карта не козырь).",
            "• Если защищающийся отбился, атакующий может подкинуть еще карты, но только того",
            "  достоинства, которое уже есть на столе (у атакующих или отбитых карт).",
            "• Защищающийся должен отбить все подкинутые карты или взять все карты со стола.",
            "• Если все атаки успешно отбиты, карты сбрасываются, и защищающийся становится атакующим.",
            "• За один ход можно подкинуть столько карт, сколько карт у защищающегося в руке, но не более 6.",
            "• После каждого хода игроки добирают карты из колоды до 6, начиная с атакующего.",
            "",
            "Управление в игре:",
            "• Перетащите карту на стол для атаки",
            "• Перетащите карту на атакующую карту для защиты",
            "• Кнопка 'Взять' - защищающийся берет все карты со стола",
            "• Кнопка 'Бито' - атакующий завершает атаку, карты сбрасываются"
        ]
        
        # Создаем прокручиваемую область для правил
        rules_surface = pygame.Surface((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150))
        rules_surface.fill(BACKGROUND_COLOR)
        
        y = 10
        for line in rules:
            if line == "":
                y += 20
                continue
                
            # Если строка длинная, разбиваем ее на несколько строк
            if len(line) > 70 and "•" not in line:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 70:
                        if current_line:
                            current_line += " "
                        current_line += word
                    else:
                        rule_text = self.normal_font.render(current_line, True, WHITE)
                        rules_surface.blit(rule_text, (10, y))
                        y += 30
                        current_line = word
                
                if current_line:
                    rule_text = self.normal_font.render(current_line, True, WHITE)
                    rules_surface.blit(rule_text, (10, y))
                    y += 30
            else:
                rule_text = self.normal_font.render(line, True, WHITE)
                rules_surface.blit(rule_text, (10, y))
                y += 30
        
        # Отображаем прокручиваемую область
        self.screen.blit(rules_surface, (50, 100))
        
        # Кнопка возврата
        self.back_button.draw(self.screen)
    
    def draw_about(self):
        """Отрисовка экрана "О программе"."""
        # Заголовок
        title_text = self.title_font.render("О программе", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Информация о программе
        about_lines = [
            "Карточная игра 'Дурак' - версия 1.0",
            "",
            "Особенности:",
            "• Полная реализация правил карточной игры 'Дурак'",
            "• Игра против компьютера",
            "• Графический интерфейс с перетаскиванием карт",
            "• Сохранение и загрузка состояния игры",
            "",
            "Полная документация доступна в файлах:",
            "• README.md - общее описание проекта",
            "• DOCUMENTATION.md - техническая документация",
            "• REFERENCE.md - справочник по игре и командам",
            "",
            "Автор: AI Developer",
            "Год: 2023"
        ]
        
        y = 120
        for line in about_lines:
            if line == "":
                y += 20
                continue
                
            about_text = self.normal_font.render(line, True, WHITE)
            self.screen.blit(about_text, (50, y))
            y += 30
        
        # Кнопка возврата
        self.back_button.draw(self.screen)
    
    def draw_game_over(self):
        """Отрисовка экрана окончания игры."""
        # Заголовок
        title_text = self.title_font.render("Игра окончена", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        if self.game and self.game.state and self.game.state.winner is not None:
            # Результат
            if self.game.state.winner == self.game.human_player:
                result_text = self.title_font.render("Вы победили!", True, GREEN)
            else:
                result_text = self.title_font.render("Вы проиграли!", True, RED)
            
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(result_text, result_rect)
            
            # Информация о победителе
            winner_text = self.normal_font.render(
                f"Победитель: {self.game.state.winner.name}",
                True, WHITE
            )
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(winner_text, winner_rect)
        else:
            # Если победитель не определен
            result_text = self.title_font.render("Игра завершена", True, YELLOW)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(result_text, result_rect)
        
        # Кнопка возврата в меню
        self.back_button.draw(self.screen)
    
    def start_new_game(self):
        """Начало новой игры."""
        try:
            self.game = DurakGame(player_name="Игрок", deck_size=36, against_computer=True)
            self.current_screen = 'game'
            self.init_game_interface()
        except Exception as e:
            print(f"Ошибка при создании новой игры: {e}")
            self.current_screen = 'menu'
            self.show_message("Ошибка при создании игры")
    
    def load_game(self):
        """Загрузка игры."""
        # Пока просто пытаемся загрузить последнее быстрое сохранение
        try:
            self.game = DurakGame.load_game("quick_save")
            self.current_screen = 'game'
            self.init_game_interface()
        except:
            self.show_message("Не удалось загрузить игру")
    
    def update_card_sprites(self):
        """Обновление спрайтов карт на основе текущего состояния игры."""
        if self.game is None:
            return
        
        try:
            # Обновление карт игрока
            self.player_cards = []
            player_hand = self.game.human_player.hand
            if player_hand:
                # Расчет масштаба для уменьшения карт, если их много
                max_cards_normal = (SCREEN_WIDTH - 200) // (CARD_WIDTH + CARD_SPACING)
                if len(player_hand) > max_cards_normal:
                    # Уменьшаем расстояние между картами, если их много
                    overlap = min(CARD_WIDTH * 0.7, CARD_WIDTH * 0.9 - ((len(player_hand) - max_cards_normal) * 5))
                    total_width = CARD_WIDTH + (len(player_hand) - 1) * overlap
                    x = SCREEN_WIDTH // 2 - total_width // 2
                    for i, card in enumerate(player_hand):
                        # Размещаем карты игрока выше от нижнего края экрана
                        y_pos = SCREEN_HEIGHT - CARD_HEIGHT - 230  # Увеличен отступ от нижнего края
                        self.player_cards.append(CardSprite(card, int(x), y_pos, True))
                        x += overlap
                else:
                    # Стандартное расположение
                    x = SCREEN_WIDTH // 2 - (len(player_hand) * CARD_WIDTH + 
                                          (len(player_hand) - 1) * CARD_SPACING) // 2
                    for card in player_hand:
                        # Размещаем карты игрока выше от нижнего края экрана
                        y_pos = SCREEN_HEIGHT - CARD_HEIGHT - 230  # Увеличен отступ от нижнего края
                        self.player_cards.append(CardSprite(card, x, y_pos, True))
                        x += CARD_WIDTH + CARD_SPACING
            
            # Обновление карт противника
            self.opponent_cards = []
            opponent_hand = self.game.opponent.hand
            if opponent_hand:
                # Расчет масштаба для уменьшения карт, если их много
                max_cards_normal = (SCREEN_WIDTH - 200) // (CARD_WIDTH + CARD_SPACING)
                if len(opponent_hand) > max_cards_normal:
                    # Уменьшаем расстояние между картами, если их много
                    overlap = min(CARD_WIDTH * 0.7, CARD_WIDTH * 0.9 - ((len(opponent_hand) - max_cards_normal) * 5))
                    total_width = CARD_WIDTH + (len(opponent_hand) - 1) * overlap
                    x = SCREEN_WIDTH // 2 - total_width // 2
                    for i in range(len(opponent_hand)):
                        self.opponent_cards.append(CardSprite(None, int(x), 40, False))  # Увеличен отступ сверху
                        x += overlap
                else:
                    # Стандартное расположение
                    x = SCREEN_WIDTH // 2 - (len(opponent_hand) * CARD_WIDTH + 
                                        (len(opponent_hand) - 1) * CARD_SPACING) // 2
                    for _ in range(len(opponent_hand)):
                        self.opponent_cards.append(CardSprite(None, x, 40, False))  # Увеличен отступ сверху
                        x += CARD_WIDTH + CARD_SPACING
            
            # Обновление карт на столе
            self.table_cards = []
            table = self.game.state.table
            if table:
                # Расчет положения карт на столе - размещаем по центру экрана
                table_width = len(table) * (CARD_WIDTH + CARD_SPACING) // 2
                x_attack = SCREEN_WIDTH // 2 - table_width // 2
                x_defend = x_attack
                # Позиции карт атаки и защиты на столе
                y_attack = SCREEN_HEIGHT // 2 - 180  # Приподнято выше к центру
                y_defend = SCREEN_HEIGHT // 2 - 80   # Приподнято выше к центру
                
                for attack_card, defend_card in table:
                    # Добавляем атакующую карту
                    if attack_card is not None:
                        self.table_cards.append(CardSprite(attack_card, x_attack, y_attack, True))
                    else:
                        self.table_cards.append(CardSprite(None, 0, 0, True))
                    
                    # Добавляем защищающуюся карту
                    if defend_card is not None:
                        self.table_cards.append(CardSprite(defend_card, x_defend, y_defend, True))
                    else:
                        self.table_cards.append(CardSprite(None, 0, 0, True))
                    
                    # Смещаем координаты для следующей пары карт
                    x_attack += CARD_WIDTH + CARD_SPACING
                    x_defend += CARD_WIDTH + CARD_SPACING
                
        except Exception as e:
            print(f"Ошибка при обновлении спрайтов карт: {e}")
            # В случае ошибки очищаем все спрайты
            self.clear_sprites()
            
        # Обновляем состояние кнопок игрового процесса
        self.update_buttons_state()
        
    def clear_sprites(self):
        """Очистка всех спрайтов карт."""
        self.player_cards = []
        self.opponent_cards = []
        self.table_cards = []
        self.deck_sprite = None
        self.trump_card = None
        
    def create_deck_and_trump_sprites(self):
        """Создание спрайтов колоды и козырной карты."""
        if self.game is None or self.game.state is None:
            return
            
        try:
            # Создание спрайта колоды - перемещаем правее из-за расширения экрана
            if self.game.state.deck and len(self.game.state.deck.cards) > 0:
                self.deck_sprite = CardSprite(None, 
                                             SCREEN_WIDTH - CARD_WIDTH - 80, 
                                             SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2 - 50, 
                                             False)
                
                # Создание спрайта козырной карты - перемещаем вместе с колодой
                if self.game.state.trump_suit:
                    trump_suit = self.game.state.trump_suit
                    trump_rank = '6'  # Просто для отображения
                    try:
                        trump_card = Card(trump_rank, trump_suit)
                        self.trump_card = CardSprite(
                            trump_card, 
                            SCREEN_WIDTH - CARD_WIDTH - 80 + 30, 
                            SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2 - 50 + 30,
                            True
                        )
                    except Exception as e:
                        print(f"Ошибка создания козырной карты: {e}")
                        self.trump_card = None
                else:
                    self.trump_card = None
            else:
                self.deck_sprite = None
                self.trump_card = None
        except Exception as e:
            print(f"Ошибка при создании спрайтов колоды и козыря: {e}")
            self.deck_sprite = None
            self.trump_card = None
    
    def show_message(self, message, duration=2000):
        """Показывает сообщение на экране."""
        message_surface = self.normal_font.render(message, True, WHITE)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        # Сохраняем текущий экран
        old_screen = self.screen.copy()
        
        # Полупрозрачный фон для сообщения
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Фон сообщения
        pygame.draw.rect(self.screen, (50, 50, 50), 
                         (message_rect.x - 20, message_rect.y - 10, 
                          message_rect.width + 40, message_rect.height + 20),
                         border_radius=10)
        
        # Текст сообщения
        self.screen.blit(message_surface, message_rect)
        pygame.display.flip()
        
        # Пауза
        pygame.time.wait(duration)
        
        # Восстановление предыдущего экрана
        self.screen.blit(old_screen, (0, 0))
        pygame.display.flip()

# Запуск игры
if __name__ == "__main__":
    DurakGUI() 
