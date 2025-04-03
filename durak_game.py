import random
import os
import json
import time
import pickle
from enum import Enum
from typing import List, Dict, Tuple, Optional, Union, Any
import copy

# Константы для цветов и стилей текста
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Константы для отображения карт
CARD_WIDTH = 7
CARD_HEIGHT = 5
EMPTY_CARD = [
    '┌─────┐',
    '│     │',
    '│     │',
    '│     │',
    '└─────┘'
]

# Константы
RANKS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
SAVE_DIR = 'saves'

# Карточные символы с цветами
SUIT_COLORS = {
    '♠': Colors.BLUE,
    '♥': Colors.RED,
    '♦': Colors.RED,
    '♣': Colors.GREEN
}

# Создаем директорию для сохранений, если её нет
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

class CardSuit(Enum):
    SPADES = '♠'
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'

# Функции для отображения карты в виде ASCII графики
def generate_card_art(card):
    """Генерирует ASCII графику для карты."""
    if card is None:
        return EMPTY_CARD
    
    rank = card.rank
    suit = card.suit
    
    # Для карт 10 нужен другой формат из-за двух символов
    if rank == '10':
        lines = [
            '┌─────┐',
            f'│{rank}   │',
            f'│  {SUIT_COLORS[suit]}{suit}{Colors.END}  │',
            f'│   {rank}│',
            '└─────┘'
        ]
    else:
        lines = [
            '┌─────┐',
            f'│{rank}    │',
            f'│  {SUIT_COLORS[suit]}{suit}{Colors.END}  │',
            f'│    {rank}│',
            '└─────┘'
        ]
    
    return lines

def display_cards_horizontal(cards, indices=True):
    """Отображает карты горизонтально с номерами."""
    if not cards:
        return ""
    
    card_arts = [generate_card_art(card) for card in cards]
    result = []
    
    # Для индексов карт
    if indices:
        index_line = ' '.join([f"  {i+1}   " for i in range(len(cards))])
        result.append(index_line)
    
    # Объединение строк каждой карты
    for line_idx in range(CARD_HEIGHT):
        combined_line = ' '.join(art[line_idx] for art in card_arts)
        result.append(combined_line)
    
    return '\n'.join(result)

def display_table(table):
    """Отображает карты на столе в виде пар атака-защита."""
    if not table:
        return "Стол пуст"
    
    attacking_cards = [pair[0] for pair in table]
    defending_cards = [pair[1] for pair in table]
    
    attacking_art = [generate_card_art(card) for card in attacking_cards]
    defending_art = [generate_card_art(card) for card in defending_cards]
    
    result = []
    result.append("Атака:")
    
    # Карты атаки
    for line_idx in range(CARD_HEIGHT):
        combined_line = ' '.join(art[line_idx] for art in attacking_art)
        result.append(combined_line)
    
    result.append("\nЗащита:")
    
    # Карты защиты
    for line_idx in range(CARD_HEIGHT):
        combined_line = ' '.join(art[line_idx] for art in defending_art)
        result.append(combined_line)
    
    return '\n'.join(result)

def draw_frame(text, width=80, title=None):
    """Рисует рамку вокруг текста с заголовком."""
    lines = text.split('\n')
    result = []
    
    # Добавляем заголовок, если он есть
    if title:
        title_padding = (width - len(title) - 4) // 2
        header = '┌' + '─' * title_padding + f' {title} ' + '─' * (width - title_padding - len(title) - 3) + '┐'
    else:
        header = '┌' + '─' * (width - 2) + '┐'
    
    result.append(header)
    
    # Добавляем строки текста
    for line in lines:
        line_length = len(line)
        padding = width - line_length - 4  # -4 для '│ ' и ' │'
        result.append(f'│ {line}{" " * padding} │')
    
    # Добавляем нижнюю границу
    result.append('└' + '─' * (width - 2) + '┘')
    
    return '\n'.join(result)

def colorize(text, color):
    """Добавляет цвет к тексту."""
    return f"{color}{text}{Colors.END}"

class Card:
    """Класс, представляющий игральную карту."""
    
    def __init__(self, rank: str, suit: str):
        """
        Инициализация карты.
        
        Args:
            rank: Ранг карты ('6', '7', ..., 'A')
            suit: Масть карты ('♠', '♥', '♦', '♣')
        """
        self.rank = rank
        self.suit = suit
        
        # Числовое значение ранга для сравнения карт
        self.rank_value = RANKS.index(rank)
    
    def __str__(self) -> str:
        """Строковое представление карты."""
        color = SUIT_COLORS.get(self.suit, '')
        return f"{self.rank}{color}{self.suit}{Colors.END}"
    
    def __repr__(self) -> str:
        """Представление карты для отладки."""
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """Проверка на равенство карт."""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        """Хеш-функция для использования карт в качестве ключей."""
        return hash((self.rank, self.suit))

class Deck:
    """Класс, представляющий колоду карт."""
    
    def __init__(self, include_ranks: List[str] = None):
        """
        Инициализация колоды.
        
        Args:
            include_ranks: Список рангов, которые следует включить в колоду.
                           По умолчанию включаются все ранги.
        """
        if include_ranks is None:
            include_ranks = RANKS
            
        self.cards = [Card(rank, suit) for rank in include_ranks for suit in SUITS]
        self.trump_suit = None
        self.trump_card = None
    
    def shuffle(self) -> None:
        """Перемешивание колоды."""
        random.shuffle(self.cards)
    
    def draw(self) -> Optional[Card]:
        """
        Взятие карты из колоды.
        
        Returns:
            Карту или None, если колода пуста.
        """
        if not self.cards:
            return None
        return self.cards.pop()
    
    def set_trump(self) -> None:
        """Установка козырной масти."""
        if self.cards:
            self.trump_card = self.cards[-1]
            self.trump_suit = self.trump_card.suit
    
    def __len__(self) -> int:
        """Количество карт в колоде."""
        return len(self.cards)
    
    def __str__(self) -> str:
        """Строковое представление колоды."""
        return f"Колода: {len(self.cards)} карт, козырь: {self.trump_suit if self.trump_suit else 'не выбран'}"
    
    def __repr__(self) -> str:
        """Представление колоды для отладки."""
        return self.__str__()

class Player:
    """Класс, представляющий игрока."""
    
    def __init__(self, name: str):
        """
        Инициализация игрока.
        
        Args:
            name: Имя игрока
        """
        self.name = name
        self.hand: List[Card] = []
    
    def add_card(self, card: Card) -> None:
        """
        Добавление карты в руку игрока.
        
        Args:
            card: Добавляемая карта
        """
        if card:
            self.hand.append(card)
    
    def remove_card(self, card: Card) -> None:
        """
        Удаление карты из руки игрока.
        
        Args:
            card: Удаляемая карта
        """
        if card in self.hand:
            self.hand.remove(card)
    
    def has_card(self, card: Card) -> bool:
        """
        Проверка наличия карты в руке игрока.
        
        Args:
            card: Проверяемая карта
            
        Returns:
            True, если карта есть в руке, иначе False
        """
        return card in self.hand
    
    def has_rank(self, rank: str) -> bool:
        """
        Проверка наличия карты определенного ранга в руке игрока.
        
        Args:
            rank: Проверяемый ранг
            
        Returns:
            True, если карта с таким рангом есть в руке, иначе False
        """
        return any(card.rank == rank for card in self.hand)
    
    def get_cards_by_rank(self, rank: str) -> List[Card]:
        """
        Получение списка карт определенного ранга из руки игрока.
        
        Args:
            rank: Ранг карт
            
        Returns:
            Список карт с указанным рангом
        """
        return [card for card in self.hand if card.rank == rank]
    
    def sort_hand(self, trump_suit: str = None) -> None:
        """
        Сортировка карт в руке игрока.
        
        Args:
            trump_suit: Козырная масть
        """
        # Сортируем карты сначала по масти (не козыри, затем козыри),
        # затем по рангу (от меньшего к большему)
        self.hand.sort(key=lambda card: (
            1 if card.suit == trump_suit else 0,
            card.rank_value
        ))
    
    def __len__(self) -> int:
        """Количество карт в руке игрока."""
        return len(self.hand)
    
    def __str__(self) -> str:
        """Строковое представление игрока."""
        return f"{self.name}: {self.hand}"
    
    def __repr__(self) -> str:
        """Представление игрока для отладки."""
        return self.__str__()

class ComputerPlayer(Player):
    """Класс, представляющий компьютерного игрока."""
    
    def __init__(self, name: str = "Компьютер"):
        """
        Инициализация компьютерного игрока.
        
        Args:
            name: Имя компьютерного игрока
        """
        super().__init__(name)
        # История игры для обучения
        self.game_history: List[Dict] = []
    
    def choose_card_to_attack(self, game_state: 'GameState') -> Optional[Card]:
        """
        Выбор карты для атаки.
        
        Args:
            game_state: Текущее состояние игры
            
        Returns:
            Выбранная карта или None, если нет подходящих карт
        """
        if not self.hand:
            return None
        
        # Сортируем карты по возрастанию силы
        cards_sorted = sorted(self.hand, key=lambda c: (
            1 if c.suit == game_state.trump_suit else 0,
            c.rank_value
        ))
        
        # Список рангов карт на столе
        table_ranks = [card.rank for pair in game_state.table for card in pair if card is not None]
        
        # Выбираем карты, ранги которых уже есть на столе (если стол не пуст)
        playable_cards = [card for card in cards_sorted if table_ranks and card.rank in table_ranks]
        
        # Если нет подходящих карт или стол пуст, берем минимальную карту
        if not playable_cards and (not game_state.table or len(game_state.table) < 6):
            # Предпочитаем не козырные карты
            non_trump_cards = [card for card in cards_sorted if card.suit != game_state.trump_suit]
            if non_trump_cards:
                return non_trump_cards[0]  # Минимальная не козырная карта
            elif cards_sorted:
                return cards_sorted[0]  # Минимальная карта (возможно, козырь)
            
        # Если есть подходящие карты, выбираем минимальную из них
        if playable_cards:
            return playable_cards[0]
            
        return None
    
    def choose_card_to_defend(self, attacking_card: Card, game_state: 'GameState') -> Optional[Card]:
        """
        Выбор карты для защиты от атаки.
        
        Args:
            attacking_card: Карта, которой атакует противник
            game_state: Текущее состояние игры
            
        Returns:
            Выбранная карта или None, если нет подходящей карты
        """
        if not self.hand:
            return None
        
        # Ищем карты той же масти с большим рангом
        same_suit_cards = [card for card in self.hand 
                          if card.suit == attacking_card.suit and card.rank_value > attacking_card.rank_value]
        
        # Если таких нет, ищем козыри (если атакующая карта не козырь)
        trump_cards = []
        if attacking_card.suit != game_state.trump_suit:
            trump_cards = [card for card in self.hand if card.suit == game_state.trump_suit]
        
        # Сортируем карты по возрастанию силы
        same_suit_cards.sort(key=lambda c: c.rank_value)
        trump_cards.sort(key=lambda c: c.rank_value)
        
        # Выбираем минимально подходящую карту
        if same_suit_cards:
            return same_suit_cards[0]
        elif trump_cards:
            return trump_cards[0]
        
        return None
    
    def decide_to_take_cards(self, game_state: 'GameState') -> bool:
        """
        Решение о взятии карт.
        
        Args:
            game_state: Текущее состояние игры
            
        Returns:
            True, если компьютер решает взять карты, иначе False
        """
        # Подсчитываем количество карт, которые нужно будет взять
        cards_to_take = sum(len(pair) for pair in game_state.table)
        
        # Подсчитываем количество карт, которые мы не можем отбить
        unbeatable_cards = 0
        for attacking_card, _ in game_state.table:
            if not self.choose_card_to_defend(attacking_card, game_state):
                unbeatable_cards += 1
        
        # Если более половины карт на столе мы не можем отбить, берем все
        if unbeatable_cards > len(game_state.table) / 2:
            return True
        
        # Если в колоде мало карт и у нас будет меньше 6 карт после хода, берем
        cards_after_move = len(self.hand) - unbeatable_cards
        if len(game_state.deck) < 6 and cards_after_move < 6:
            return True
        
        # По умолчанию пытаемся отбиваться
        return False
    
    def update_game_history(self, state: Dict, action: Dict, result: Dict) -> None:
        """
        Обновление истории игры для обучения.
        
        Args:
            state: Состояние игры перед действием
            action: Выполненное действие
            result: Результат действия
        """
        self.game_history.append({
            'state': state,
            'action': action,
            'result': result
        })
    
    def save_learning_data(self, filename: str = "computer_learning.json") -> None:
        """
        Сохранение данных обучения в файл.
        
        Args:
            filename: Имя файла для сохранения
        """
        path = os.path.join(SAVE_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.game_history, f, ensure_ascii=False, indent=2)
    
    def load_learning_data(self, filename: str = "computer_learning.json") -> None:
        """
        Загрузка данных обучения из файла.
        
        Args:
            filename: Имя файла для загрузки
        """
        path = os.path.join(SAVE_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.game_history = json.load(f)

class GameState:
    """Класс, представляющий состояние игры."""
    
    def __init__(self, player1: Player, player2: Player, deck_size: int = 36):
        """
        Инициализация состояния игры.
        
        Args:
            player1: Первый игрок
            player2: Второй игрок
            deck_size: Размер колоды (36 карт по умолчанию)
        """
        self.player1 = player1
        self.player2 = player2
        
        # Определяем какие ранги включать в колоду
        if deck_size == 36:
            include_ranks = RANKS
        elif deck_size == 24:
            include_ranks = RANKS[3:]  # Начиная с 9-ки
        elif deck_size == 20:
            include_ranks = RANKS[4:]  # Начиная с 10-ки
        else:
            raise ValueError(f"Неподдерживаемый размер колоды: {deck_size}")
        
        # Создаем и перемешиваем колоду
        self.deck = Deck(include_ranks)
        self.deck.shuffle()
        self.deck.set_trump()
        
        # Козырная масть
        self.trump_suit = self.deck.trump_suit
        
        # Раздаем начальные карты
        self.deal_initial_cards()
        
        # Определяем атакующего игрока
        self.attacker = self.determine_first_player()
        self.defender = player2 if self.attacker == player1 else player1
        
        # Стол с картами - список пар (атакующая карта, защищающаяся карта или None)
        self.table: List[Tuple[Card, Optional[Card]]] = []
        
        # Игра закончена?
        self.game_over = False
        self.winner = None
    
    def deal_initial_cards(self, cards_per_player: int = 6) -> None:
        """
        Раздача начальных карт игрокам.
        
        Args:
            cards_per_player: Количество карт для каждого игрока
        """
        for _ in range(cards_per_player):
            self.player1.add_card(self.deck.draw())
            self.player2.add_card(self.deck.draw())
        
        # Сортируем карты в руках игроков
        self.player1.sort_hand(self.trump_suit)
        self.player2.sort_hand(self.trump_suit)
    
    def determine_first_player(self) -> Player:
        """
        Определение игрока, который ходит первым.
        
        В карточной игре "Дурак" первым ходит игрок с наименьшим козырем.
        Если ни у кого нет козырей, выбирается случайный игрок.
        
        Returns:
            Игрок, который ходит первым
        """
        # Находим минимальный козырь у каждого игрока
        player1_min_trump = None
        for card in self.player1.hand:
            if card.suit == self.trump_suit:
                if player1_min_trump is None or card.rank_value < player1_min_trump.rank_value:
                    player1_min_trump = card
        
        player2_min_trump = None
        for card in self.player2.hand:
            if card.suit == self.trump_suit:
                if player2_min_trump is None or card.rank_value < player2_min_trump.rank_value:
                    player2_min_trump = card
        
        # Определяем, кто ходит первым
        if player1_min_trump and player2_min_trump:
            # У обоих есть козыри, сравниваем их
            return self.player1 if player1_min_trump.rank_value < player2_min_trump.rank_value else self.player2
        elif player1_min_trump:
            # Только у первого игрока есть козырь
            return self.player1
        elif player2_min_trump:
            # Только у второго игрока есть козырь
            return self.player2
        else:
            # Ни у кого нет козырей, выбираем случайно
            return random.choice([self.player1, self.player2])
    
    def refill_hands(self) -> None:
        """Добор карт игроками до 6, начиная с атакующего."""
        # Сначала атакующий добирает карты
        while len(self.attacker.hand) < 6 and len(self.deck) > 0:
            self.attacker.add_card(self.deck.draw())
        
        # Затем защищающийся
        while len(self.defender.hand) < 6 and len(self.deck) > 0:
            self.defender.add_card(self.deck.draw())
        
        # Сортируем карты в руках игроков
        self.attacker.sort_hand(self.trump_suit)
        self.defender.sort_hand(self.trump_suit)
    
    def switch_roles(self) -> None:
        """Смена ролей игроков (атакующий становится защищающимся и наоборот)."""
        self.attacker, self.defender = self.defender, self.attacker
    
    def clear_table(self) -> None:
        """Очистка стола."""
        self.table = []
    
    def can_add_card(self, card: Card) -> bool:
        """
        Проверка возможности добавления карты на стол.
        
        Args:
            card: Проверяемая карта
            
        Returns:
            True, если карту можно добавить, иначе False
        """
        # Если стол пуст, можно положить любую карту
        if not self.table:
            return True
        
        # Иначе проверяем, есть ли на столе карта такого же ранга
        table_ranks = set()
        for attacking_card, defending_card in self.table:
            table_ranks.add(attacking_card.rank)
            if defending_card:
                table_ranks.add(defending_card.rank)
        
        return card.rank in table_ranks
    
    def can_beat_card(self, attacking_card: Card, defending_card: Card) -> bool:
        """
        Проверка возможности отбить одну карту другой.
        
        Args:
            attacking_card: Атакующая карта
            defending_card: Защищающаяся карта
            
        Returns:
            True, если карту можно отбить, иначе False
        """
        # Если масти одинаковые, то старшая карта бьет младшую
        if attacking_card.suit == defending_card.suit:
            return defending_card.rank_value > attacking_card.rank_value
        
        # Если масти разные, то только козырь может бить не козырь
        return defending_card.suit == self.trump_suit and attacking_card.suit != self.trump_suit
    
    def check_game_over(self) -> bool:
        """
        Проверка окончания игры.
        
        Returns:
            True, если игра окончена, иначе False
        """
        # Игра окончена, если у одного из игроков нет карт и колода пуста
        if (len(self.player1.hand) == 0 or len(self.player2.hand) == 0) and len(self.deck) == 0:
            self.game_over = True
            
            # Определяем победителя
            if len(self.player1.hand) == 0 and len(self.player2.hand) > 0:
                self.winner = self.player1
            elif len(self.player2.hand) == 0 and len(self.player1.hand) > 0:
                self.winner = self.player2
            else:
                # Ничья (оба игрока закончили карты одновременно)
                self.winner = None
            
            return True
        
        return False
    
    def __str__(self) -> str:
        """Строковое представление состояния игры."""
        return (
            f"Игрок 1: {self.player1}\n"
            f"Игрок 2: {self.player2}\n"
            f"Колода: {len(self.deck)} карт, козырь: {self.trump_suit}\n"
            f"Атакующий: {self.attacker.name}\n"
            f"Стол: {self.table}"
        )
    
    def serialize(self) -> Dict:
        """
        Сериализация состояния игры для сохранения.
        
        Returns:
            Словарь с данными состояния игры
        """
        return {
            'player1': {
                'name': self.player1.name,
                'hand': [(card.rank, card.suit) for card in self.player1.hand]
            },
            'player2': {
                'name': self.player2.name,
                'hand': [(card.rank, card.suit) for card in self.player2.hand]
            },
            'deck': {
                'cards': [(card.rank, card.suit) for card in self.deck.cards],
                'trump_suit': self.trump_suit
            },
            'attacker_name': self.attacker.name,
            'table': [
                [(a_card.rank, a_card.suit), (d_card.rank, d_card.suit) if d_card else None]
                for a_card, d_card in self.table
            ],
            'game_over': self.game_over,
            'winner': self.winner.name if self.winner else None
        }
    
    @classmethod
    def deserialize(cls, data: Dict) -> 'GameState':
        """
        Десериализация состояния игры из сохранения.
        
        Args:
            data: Словарь с данными состояния игры
            
        Returns:
            Восстановленное состояние игры
        """
        # Создаем игроков
        player1 = Player(data['player1']['name'])
        player2 = Player(data['player2']['name'])
        
        # Если игрок - компьютер, создаем экземпляр ComputerPlayer
        if data['player1']['name'] == "Компьютер":
            player1 = ComputerPlayer()
        if data['player2']['name'] == "Компьютер":
            player2 = ComputerPlayer()
        
        # Создаем пустое состояние игры
        game_state = cls(player1, player2, deck_size=0)
        
        # Восстанавливаем руки игроков
        player1.hand = [Card(rank, suit) for rank, suit in data['player1']['hand']]
        player2.hand = [Card(rank, suit) for rank, suit in data['player2']['hand']]
        
        # Восстанавливаем колоду
        game_state.deck = Deck()
        game_state.deck.cards = [Card(rank, suit) for rank, suit in data['deck']['cards']]
        game_state.deck.trump_suit = data['deck']['trump_suit']
        game_state.trump_suit = data['deck']['trump_suit']
        
        # Восстанавливаем атакующего игрока
        if data['attacker_name'] == player1.name:
            game_state.attacker = player1
            game_state.defender = player2
        else:
            game_state.attacker = player2
            game_state.defender = player1
        
        # Восстанавливаем стол
        game_state.table = []
        for attacking, defending in data['table']:
            a_card = Card(attacking[0], attacking[1])
            d_card = Card(defending[0], defending[1]) if defending else None
            game_state.table.append((a_card, d_card))
        
        # Восстанавливаем статус игры
        game_state.game_over = data['game_over']
        if data['winner']:
            game_state.winner = player1 if data['winner'] == player1.name else player2
        else:
            game_state.winner = None
        
        return game_state 

class DurakGame:
    """Основной класс игры, отвечающий за логику и управление игровым процессом."""
    
    def __init__(self, player_name: str = "Игрок", deck_size: int = 36, against_computer: bool = True):
        """
        Инициализация игры.
        
        Args:
            player_name: Имя игрока
            deck_size: Размер колоды (36, 24 или 20 карт)
            against_computer: Игра против компьютера (True) или другого игрока (False)
        """
        # Создаем игроков
        self.human_player = Player(player_name)
        
        if against_computer:
            self.opponent = ComputerPlayer()
            # Загружаем данные обучения компьютера, если они есть
            self.opponent.load_learning_data()
        else:
            self.opponent = Player("Игрок 2")
        
        # Создаем состояние игры
        self.state = GameState(self.human_player, self.opponent, deck_size)
        
        # Флаг игры против компьютера
        self.against_computer = against_computer
        
        # История ходов для отмены
        self.history: List[Dict] = []
    
    def attack(self, card: Card) -> bool:
        """
        Атака картой.
        
        Args:
            card: Карта для атаки
            
        Returns:
            True, если атака успешна, иначе False
        """
        # Проверяем, что карта есть у атакующего и ее можно добавить
        if not self.state.attacker.has_card(card) or not self.state.can_add_card(card):
            return False
        
        # Сохраняем текущее состояние игры в истории
        self.save_state_to_history()
        
        # Добавляем карту на стол
        self.state.attacker.remove_card(card)
        self.state.table.append((card, None))
        
        # Обновляем данные обучения компьютера
        if isinstance(self.opponent, ComputerPlayer):
            state_snapshot = self._create_state_snapshot()
            action = {'type': 'attack', 'card': (card.rank, card.suit)}
            result = {'success': True}
            self.opponent.update_game_history(state_snapshot, action, result)
        
        return True
    
    def defend(self, attacking_card: Card, defending_card: Card) -> bool:
        """
        Защита от атаки.
        
        Args:
            attacking_card: Атакующая карта
            defending_card: Карта для защиты
            
        Returns:
            True, если защита успешна, иначе False
        """
        # Проверяем, что карта есть у защищающегося и ей можно отбиться
        if not self.state.defender.has_card(defending_card):
            return False
        
        # Находим атакующую карту на столе
        for i, (a_card, d_card) in enumerate(self.state.table):
            if a_card == attacking_card and d_card is None:
                # Проверяем, можно ли отбить атакующую карту
                if not self.state.can_beat_card(a_card, defending_card):
                    return False
                
                # Сохраняем текущее состояние игры в истории
                self.save_state_to_history()
                
                # Отбиваем карту
                self.state.defender.remove_card(defending_card)
                self.state.table[i] = (a_card, defending_card)
                
                # Обновляем данные обучения компьютера
                if isinstance(self.opponent, ComputerPlayer):
                    state_snapshot = self._create_state_snapshot()
                    action = {
                        'type': 'defend', 
                        'attacking_card': (attacking_card.rank, attacking_card.suit),
                        'defending_card': (defending_card.rank, defending_card.suit)
                    }
                    result = {'success': True}
                    self.opponent.update_game_history(state_snapshot, action, result)
                
                return True
        
        return False
    
    def take_cards(self) -> None:
        """Защищающийся игрок берет все карты со стола."""
        # Сохраняем текущее состояние игры в истории
        self.save_state_to_history()
        
        # Добавляем все карты со стола в руку защищающегося
        for attacking_card, defending_card in self.state.table:
            self.state.defender.add_card(attacking_card)
            if defending_card:
                self.state.defender.add_card(defending_card)
        
        # Очищаем стол
        self.state.clear_table()
        
        # Добираем карты
        self.state.refill_hands()
        
        # Атакующий остается тем же (защищающийся взял карты)
        
        # Обновляем данные обучения компьютера
        if isinstance(self.opponent, ComputerPlayer):
            state_snapshot = self._create_state_snapshot()
            action = {'type': 'take_cards'}
            result = {'cards_taken': len(self.state.defender.hand)}
            self.opponent.update_game_history(state_snapshot, action, result)
    
    def done_attacking(self) -> None:
        """Атакующий игрок завершает атаку."""
        # Сохраняем текущее состояние игры в истории
        self.save_state_to_history()
        
        # Проверяем, все ли атаки отбиты
        all_defended = all(defending_card is not None for _, defending_card in self.state.table)
        
        # Очищаем стол
        self.state.clear_table()
        
        # Добираем карты
        self.state.refill_hands()
        
        # Меняем атакующего и защищающегося только если все атаки отбиты
        if all_defended:
            self.state.switch_roles()
        
        # Обновляем данные обучения компьютера
        if isinstance(self.opponent, ComputerPlayer):
            state_snapshot = self._create_state_snapshot()
            action = {'type': 'done_attacking'}
            result = {'all_defended': all_defended}
            self.opponent.update_game_history(state_snapshot, action, result)
    
    def computer_move(self) -> None:
        """Выполнение хода компьютером."""
        if not isinstance(self.opponent, ComputerPlayer):
            return
        
        if self.state.attacker == self.opponent:
            # Компьютер атакует
            card = self.opponent.choose_card_to_attack(self.state)
            if card:
                self.attack(card)
            else:
                self.done_attacking()
        else:
            # Компьютер защищается
            # Проверяем, есть ли на столе неотбитые атаки
            undefended_attacks = [a_card for a_card, d_card in self.state.table if d_card is None]
            
            if undefended_attacks:
                # Решаем, брать карты или отбиваться
                if self.opponent.decide_to_take_cards(self.state):
                    self.take_cards()
                else:
                    # Пытаемся отбиться от каждой атаки
                    for attacking_card in undefended_attacks:
                        defending_card = self.opponent.choose_card_to_defend(attacking_card, self.state)
                        if defending_card:
                            self.defend(attacking_card, defending_card)
                        else:
                            # Если не можем отбиться хотя бы от одной карты, берем все
                            self.take_cards()
                            break
            else:
                # Все атаки отбиты, ждем дальнейших действий игрока
                pass
    
    def check_game_over(self) -> bool:
        """
        Проверка окончания игры.
        
        Returns:
            True, если игра окончена, иначе False
        """
        return self.state.check_game_over()
    
    def save_game(self, filename: str) -> None:
        """
        Сохранение игры в файл.
        
        Args:
            filename: Имя файла для сохранения
        """
        # Создаем данные для сохранения
        save_data = {
            'game_state': self.state.serialize(),
            'against_computer': self.against_computer,
            'history': self.history
        }
        
        # Добавляем расширение .save, если оно отсутствует
        if not filename.endswith('.save'):
            filename += '.save'
        
        # Сохраняем в файл
        path = os.path.join(SAVE_DIR, filename)
        with open(path, 'wb') as f:
            pickle.dump(save_data, f)
        
        print(f"Игра сохранена в файл {path}")
    
    def load_game(self, filename: str) -> bool:
        """
        Загрузка игры из файла.
        
        Args:
            filename: Имя файла для загрузки
            
        Returns:
            True, если загрузка успешна, иначе False
        """
        # Добавляем расширение .save, если оно отсутствует
        if not filename.endswith('.save'):
            filename += '.save'
        
        path = os.path.join(SAVE_DIR, filename)
        
        # Проверяем существование файла
        if not os.path.exists(path):
            print(f"Файл {path} не найден")
            return False
        
        try:
            # Загружаем данные из файла
            with open(path, 'rb') as f:
                save_data = pickle.load(f)
            
            # Восстанавливаем состояние игры
            self.state = GameState.deserialize(save_data['game_state'])
            self.against_computer = save_data['against_computer']
            self.history = save_data.get('history', [])
            
            # Обновляем ссылки на игроков
            self.human_player = self.state.player1 if self.state.player1.name != "Компьютер" else self.state.player2
            self.opponent = self.state.player2 if self.state.player1.name != "Компьютер" else self.state.player1
            
            # Загружаем данные обучения компьютера, если это игра против компьютера
            if self.against_computer and isinstance(self.opponent, ComputerPlayer):
                self.opponent.load_learning_data()
            
            print(f"Игра загружена из файла {path}")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке игры: {e}")
            return False
    
    def undo_move(self) -> bool:
        """
        Отмена последнего хода.
        
        Returns:
            True, если отмена успешна, иначе False
        """
        if not self.history:
            print("Невозможно отменить ход: история пуста")
            return False
        
        # Восстанавливаем предыдущее состояние игры
        last_state = self.history.pop()
        self.state = GameState.deserialize(last_state)
        
        # Обновляем ссылки на игроков
        self.human_player = self.state.player1 if self.state.player1.name != "Компьютер" else self.state.player2
        self.opponent = self.state.player2 if self.state.player1.name != "Компьютер" else self.state.player1
        
        print("Ход отменен")
        return True
    
    def save_state_to_history(self) -> None:
        """Сохранение текущего состояния игры в историю."""
        self.history.append(self.state.serialize())
    
    def _create_state_snapshot(self) -> Dict:
        """
        Создание снимка состояния игры для обучения компьютера.
        
        Returns:
            Словарь с данными о состоянии игры
        """
        return {
            'hand': [(card.rank, card.suit) for card in self.opponent.hand],
            'table': [
                [(a_card.rank, a_card.suit), (d_card.rank, d_card.suit) if d_card else None]
                for a_card, d_card in self.state.table
            ],
            'trump_suit': self.state.trump_suit,
            'deck_size': len(self.state.deck),
            'opponent_cards': len(self.human_player.hand),
            'is_attacker': self.state.attacker == self.opponent
        }

class DurakGameUI:
    """Класс, отвечающий за пользовательский интерфейс игры."""
    
    def __init__(self):
        """Инициализация интерфейса."""
        self.game = None
        self.width = 100  # Ширина интерфейса
        self.show_main_menu()
    
    def show_main_menu(self) -> None:
        """Отображение главного меню."""
        self.clear_screen()
        
        title = f"{Colors.BOLD}{Colors.YELLOW}КАРТОЧНАЯ ИГРА ДУРАК{Colors.END}"
        menu_items = [
            f"{Colors.GREEN}1.{Colors.END} Новая игра",
            f"{Colors.GREEN}2.{Colors.END} Загрузить игру",
            f"{Colors.GREEN}3.{Colors.END} Правила игры",
            f"{Colors.GREEN}4.{Colors.END} О программе",
            f"{Colors.GREEN}5.{Colors.END} Выход"
        ]
        
        menu_text = f"\n{title}\n\n" + "\n".join(menu_items) + "\n\nВыберите пункт меню: "
        menu_frame = draw_frame(menu_text, self.width, "ГЛАВНОЕ МЕНЮ")
        
        print(menu_frame)
        
        choice = input()
        
        if choice == "1":
            self.start_new_game()
        elif choice == "2":
            self.load_game()
        elif choice == "3":
            self.show_rules()
        elif choice == "4":
            self.show_about()
        elif choice == "5":
            print(f"\n{Colors.YELLOW}Спасибо за игру! До свидания!{Colors.END}")
            exit(0)
        else:
            print(f"\n{Colors.RED}Неверный выбор. Попробуйте снова.{Colors.END}")
            time.sleep(1)
            self.show_main_menu()
    
    def start_new_game(self) -> None:
        """Начало новой игры."""
        self.clear_screen()
        print("=== НОВАЯ ИГРА ===")
        
        # Запрашиваем имя игрока
        player_name = input("Введите ваше имя (по умолчанию 'Игрок'): ").strip()
        if not player_name:
            player_name = "Игрок"
        
        # Запрашиваем режим игры
        print("\nВыберите режим игры:")
        print("1. Против компьютера")
        print("2. Два игрока (hot seat)")
        
        game_mode_choice = input("\nВыберите режим (1-2), по умолчанию 1: ").strip()
        against_computer = game_mode_choice != '2'
        
        # Запрашиваем размер колоды
        print("\nВыберите размер колоды:")
        print("1. 36 карт (от 6 до туза)")
        print("2. 24 карты (от 9 до туза)")
        print("3. 20 карт (от 10 до туза)")
        
        deck_size_choice = input("\nВыберите размер колоды (1-3), по умолчанию 1: ").strip()
        
        if deck_size_choice == '2':
            deck_size = 24
        elif deck_size_choice == '3':
            deck_size = 20
        else:
            deck_size = 36
        
        # Создаем игру
        self.game = DurakGame(player_name, deck_size, against_computer)
        
        # Начинаем игровой цикл
        self.game_loop()
    
    def load_game(self) -> None:
        """Загрузка сохраненной игры."""
        self.clear_screen()
        print("=== ЗАГРУЗКА ИГРЫ ===")
        
        # Получаем список файлов сохранений
        save_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.save')]
        
        if not save_files:
            input("Сохраненные игры не найдены. Нажмите Enter для возврата в меню...")
            return
        
        # Выводим список сохранений
        print("Доступные сохранения:")
        for i, filename in enumerate(save_files, 1):
            print(f"{i}. {filename}")
        
        # Запрашиваем выбор файла
        choice = input("\nВыберите номер сохранения или 0 для возврата в меню: ")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
            
            if 1 <= choice_num <= len(save_files):
                # Создаем пустую игру и загружаем в нее данные
                self.game = DurakGame()
                if self.game.load_game(save_files[choice_num - 1]):
                    self.game_loop()
            else:
                input("Некорректный выбор. Нажмите Enter для продолжения...")
        except ValueError:
            input("Введите число. Нажмите Enter для продолжения...")
    
    def game_loop(self) -> None:
        """Основной игровой цикл."""
        while True:
            # Проверяем окончание игры
            if self.game.check_game_over():
                self.show_game_over()
                break
            
            # Отображаем текущее состояние игры
            self.display_game_state()
            
            # Если сейчас ход компьютера, выполняем его
            if self.game.against_computer and self.game.state.attacker == self.game.opponent:
                print("Ход компьютера...")
                time.sleep(1)  # Пауза для лучшего восприятия
                self.game.computer_move()
                continue
            
            # Если сейчас ход защищающегося компьютера, выполняем его
            if self.game.against_computer and self.game.state.defender == self.game.opponent and self.undefended_attacks_exist():
                print("Компьютер защищается...")
                time.sleep(1)  # Пауза для лучшего восприятия
                self.game.computer_move()
                continue
            
            # Запрашиваем действие у пользователя
            self.handle_user_action()
    
    def undefended_attacks_exist(self) -> bool:
        """
        Проверка наличия неотбитых атак на столе.
        
        Returns:
            True, если есть неотбитые атаки, иначе False
        """
        return any(defending is None for _, defending in self.game.state.table)
    
    def display_game_state(self) -> None:
        """Отображение текущего состояния игры."""
        self.clear_screen()
        
        state = self.game.state
        
        # Информация о колоде
        deck_info = f"Колода: {len(state.deck.cards)} карт | Козырь: {SUIT_COLORS[state.trump_suit]}{state.trump_suit}{Colors.END}"
        
        # Информация о противнике
        opponent = self.game.opponent
        opponent_info = f"Противник: {opponent.name} [{len(opponent.hand)} карт]"
        if state.defender == opponent:
            opponent_info += f" {Colors.CYAN}(Защищается){Colors.END}"
        else:
            opponent_info += f" {Colors.MAGENTA}(Атакует){Colors.END}"
        
        # Информация о столе
        table_display = display_table(state.table)
        
        # Информация о текущем игроке
        player = self.game.human_player
        player_info = f"Ваши карты: {player.name} [{len(player.hand)} карт]"
        if state.defender == player:
            player_info += f" {Colors.CYAN}(Вы защищаетесь){Colors.END}"
        else:
            player_info += f" {Colors.MAGENTA}(Вы атакуете){Colors.END}"
        
        # Отображение карт игрока
        player_cards = display_cards_horizontal(player.hand)
        
        # Доступные команды
        commands = [
            f"{Colors.GREEN}c N{Colors.END} - положить карту N для атаки",
            f"{Colors.GREEN}c N M{Colors.END} - отбить карту N картой M",
            f"{Colors.GREEN}d{Colors.END} - завершить атаку",
            f"{Colors.GREEN}t{Colors.END} - взять карты",
            f"{Colors.GREEN}s{Colors.END} - сохранить игру",
            f"{Colors.GREEN}u{Colors.END} - отменить ход",
            f"{Colors.GREEN}q{Colors.END} - выйти в меню"
        ]
        commands_text = " | ".join(commands)
        
        # Объединение всей информации
        game_info = f"{deck_info}\n\n{opponent_info}\n\n{table_display}\n\n{player_info}\n\n{player_cards}\n\n{commands_text}"
        
        # Отображение в рамке
        game_frame = draw_frame(game_info, self.width, "ИГРА ДУРАК")
        print(game_frame)
    
    def handle_user_action(self) -> None:
        """Обработка действий пользователя."""
        action = input("\nВведите команду: ").strip().lower()
        
        if not action:
            return
        
        # Выход в меню
        if action == 'q':
            confirm = input("Вы уверены, что хотите выйти в меню? Несохраненный прогресс будет потерян (y/n): ")
            if confirm.lower() == 'y':
                return
        
        # Сохранение игры
        elif action == 's':
            filename = input("Введите имя файла для сохранения: ")
            if filename:
                self.game.save_game(filename)
                input("Нажмите Enter для продолжения...")
        
        # Отмена хода
        elif action == 'u':
            self.game.undo_move()
            input("Нажмите Enter для продолжения...")
        
        # Действия атакующего
        elif self.game.state.attacker == self.game.human_player:
            # Атака картой
            if action.startswith('c '):
                try:
                    card_index = int(action[2:]) - 1
                    if 0 <= card_index < len(self.game.human_player.hand):
                        card = self.game.human_player.hand[card_index]
                        if self.game.attack(card):
                            pass  # Успешная атака
                        else:
                            input("Невозможно атаковать этой картой. Нажмите Enter для продолжения...")
                    else:
                        input("Некорректный номер карты. Нажмите Enter для продолжения...")
                except ValueError:
                    input("Введите число после 'c'. Нажмите Enter для продолжения...")
            
            # Завершение атаки
            elif action == 'd':
                self.game.done_attacking()
        
        # Действия защищающегося
        else:
            # Отбивание карты
            if action.startswith('c '):
                parts = action.split()
                if len(parts) >= 3:
                    try:
                        attack_index = int(parts[1]) - 1
                        defend_index = int(parts[2]) - 1
                        
                        if 0 <= attack_index < len(self.game.state.table) and 0 <= defend_index < len(self.game.human_player.hand):
                            attacking_card = self.game.state.table[attack_index][0]
                            defending_card = self.game.human_player.hand[defend_index]
                            
                            if self.game.defend(attacking_card, defending_card):
                                pass  # Успешная защита
                            else:
                                input("Невозможно отбить эту карту. Нажмите Enter для продолжения...")
                        else:
                            input("Некорректные номера карт. Нажмите Enter для продолжения...")
                    except ValueError:
                        input("Введите числа после 'c'. Нажмите Enter для продолжения...")
                else:
                    input("Неверный формат команды. Используйте 'c N M'. Нажмите Enter для продолжения...")
            
            # Взятие карт
            elif action == 't':
                self.game.take_cards()
    
    def show_game_over(self) -> None:
        """Отображение окончания игры."""
        self.clear_screen()
        
        winner = self.game.state.winner
        if winner == self.game.human_player:
            result = f"{Colors.GREEN}ПОЗДРАВЛЯЕМ! ВЫ ПОБЕДИЛИ!{Colors.END}"
        else:
            result = f"{Colors.RED}К СОЖАЛЕНИЮ, ВЫ ПРОИГРАЛИ.{Colors.END}"
        
        game_over_text = f"\n{result}\n\nПобедитель: {winner.name}\n\nНажмите Enter, чтобы вернуться в главное меню..."
        game_over_frame = draw_frame(game_over_text, self.width, "ИГРА ОКОНЧЕНА")
        
        print(game_over_frame)
        input()
        self.show_main_menu()
    
    def show_rules(self) -> None:
        """Отображение правил игры."""
        self.clear_screen()
        
        rules_text = f"""
{Colors.YELLOW}Цель игры:{Colors.END}
Избавиться от всех карт. Последний игрок с картами на руках считается проигравшим ("дураком").

{Colors.YELLOW}Основные правила:{Colors.END}
1. Игра ведется колодой из 36 карт (от 6 до туза).
2. В начале игры каждому игроку раздается по 6 карт.
3. Последняя карта колоды переворачивается и определяет козырную масть.
4. Игрок с наименьшим козырем начинает игру.
5. Игроки ходят по очереди, атакуя и защищаясь.

{Colors.YELLOW}Ход игры:{Colors.END}
1. Атакующий игрок выкладывает карту на стол.
2. Защищающийся игрок должен побить карту, выложив карту старшего достоинства 
   той же масти или любую карту козырной масти.
3. Атакующий может подкинуть карты того же достоинства, что уже есть на столе.
4. Если защищающийся не может или не хочет отбиться, он забирает все карты со стола.
5. После завершения хода игроки добирают карты из колоды до 6.

{Colors.YELLOW}Управление:{Colors.END}
- c N - положить карту N из руки для атаки
- c N M - отбить карту N на столе картой M из руки
- d - завершить атаку
- t - взять карты
- s - сохранить игру
- u - отменить ход
- q - выйти в меню

Нажмите Enter, чтобы вернуться в главное меню...
"""
        rules_frame = draw_frame(rules_text, self.width, "ПРАВИЛА ИГРЫ")
        
        print(rules_frame)
        input()
        self.show_main_menu()
    
    def show_about(self) -> None:
        """Отображение информации о программе."""
        self.clear_screen()
        
        about_text = f"""
{Colors.YELLOW}Карточная игра "Дурак"{Colors.END}

Версия: 1.0

{Colors.YELLOW}Особенности:{Colors.END}
- Полная реализация правил игры "Дурак"
- Игра против компьютера или другого игрока
- Сохранение и загрузка игры
- Отмена ходов
- Обучающийся искусственный интеллект

{Colors.YELLOW}Автор:{Colors.END} AI Developer
{Colors.YELLOW}Год:{Colors.END} 2023

Полная документация доступна в файлах:
- README.md - общее описание проекта
- DOCUMENTATION.md - техническая документация
- REFERENCE.md - справочник по игре и командам

Нажмите Enter, чтобы вернуться в главное меню...
"""
        about_frame = draw_frame(about_text, self.width, "О ПРОГРАММЕ")
        
        print(about_frame)
        input()
        self.show_main_menu()
    
    @staticmethod
    def clear_screen() -> None:
        """Очистка экрана."""
        os.system('cls' if os.name == 'nt' else 'clear')

# Запуск игры при выполнении скрипта напрямую
if __name__ == "__main__":
    ui = DurakGameUI()
    ui.show_main_menu() 
