
import random

from reportlab import rl_config
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from typing import List, Tuple

rl_config.TTFSearchPath.append("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))


def has_bingo(
        board_words: List[str], 
        marked_words: List[str], 
        size: int
    ) -> bool:
    board = [board_words[i*size:(i+1)*size] for i in range(size)] # reshape
    # rows and columns
    for i in range(size):
        if all(word in marked_words for word in board[i]): # row
            return True
        if all(board[j][i] in marked_words for j in range(size)):  # column
            return True
    # diagonals
    if all(board[i][i] in marked_words for i in range(size)):
        return True
    if all(board[i][size-i-1] in marked_words for i in range(size)):
        return True
    return False


def generate_word_bingo_cards(
    word_desc_pairs: List[Tuple[str, str]],
    board_size: int,
    num_players: int,
    min_turns: int,
    max_turns: int,
    max_attempts: int = 1000
) -> Tuple[List[List[str]], List[Tuple[str, str]]]:
    words = [wd[0] for wd in word_desc_pairs]
    word_to_desc = dict(word_desc_pairs)

    if len(words) < board_size * board_size:
        raise ValueError("Málo slov na zaplnenie hracej plochy.")

    for attempt in range(max_attempts):
        # readding order shuffle
        shuffled_words = random.sample(words, len(words))
        shuffled_pairs = [(w, word_to_desc[w]) for w in shuffled_words]
        
        # generate player boards
        boards = []
        for _ in range(num_players):
            board_words = random.sample(words, board_size * board_size)
            boards.append(board_words)
        
        # simulate when each player would win
        winners = []
        for board in boards:
            marks = set()
            for turn, word in enumerate(shuffled_words):
                if word in board:
                    marks.add(word)
                if has_bingo(board, marks, board_size):
                    winners.append(turn + 1)
                    break
            else:
                winners.append(None)
        
        # pacing constraints check
        early_win = any(w is not None and w < min_turns for w in winners)
        late_win = any(w is not None and w <= max_turns for w in winners)
        
        if not early_win and late_win:
            print(winners)
            for i in range(len(winners)):
                if winners[i] is None:
                    print(f"Player {i+1} did not win.")
                else:
                    print(f"Player {i+1} won on turn {winners[i]}.")
            return boards, shuffled_pairs
    
    raise RuntimeError("Nepodarilo sa vytvoriť plochy za daný počet pokusov.")


def export_bingo_cards_to_pdf_grid(
        cards: List[List[str]], 
        board_size: int, 
        cards_per_row: int=2, 
        cards_per_col: int=2, 
        filename: str="bingo_cards.pdf"
    ) -> None:
    c = canvas.Canvas(filename, pagesize=A4)
    page_width, page_height = A4

    cards_per_page = cards_per_row * cards_per_col
    total_pages = (len(cards) + cards_per_page - 1) // cards_per_page

    # dynamic cell size based on grid layout
    max_card_width = (page_width - 4 * cm) / cards_per_row
    max_card_height = (page_height - 4 * cm) / cards_per_col
    cell_size = min(max_card_width, max_card_height) / board_size

    margin_x = 2 * cm
    margin_y = 2 * cm

    for page in range(total_pages):
        for i in range(cards_per_page):
            card_idx = page * cards_per_page + i
            if card_idx >= len(cards):
                break

            card = cards[card_idx]

            # determine card grid position on the page
            grid_row = i // cards_per_row
            grid_col = i % cards_per_row

            card_origin_x = margin_x + grid_col * (cell_size * board_size + cm)
            card_origin_y = page_height - margin_y - (grid_row + 1) * (cell_size * board_size + cm)

            # draw grid
            c.setFont("Arial", 12)
            for row in range(board_size):
                for col in range(board_size):
                    word = card[row * board_size + col]
                    x = card_origin_x + col * cell_size
                    y = card_origin_y + (board_size - row - 1) * cell_size
                    c.rect(x, y, cell_size, cell_size)
                    c.drawCentredString(x + cell_size / 2, y + cell_size / 2 - 3, word)

        c.showPage()

    c.save()
    print(f"Do {filename} bolo uložených {len(cards)} hracích bingo plánov.")


def export_description_script_pdf(
        pairs: List[Tuple[str, str]], 
        filename: str="bingo_script.pdf"
    ) -> None:

    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Arial", 12)
    width, height = A4
    margin_x = 2 * cm
    margin_y = 2 * cm
    line_height = 0.8 * cm

    y = height - margin_y

    c.drawString(margin_x, y, "Poradie čítania inštrukcií (pre učiteľa):")
    y -= line_height

    for i, (word, description) in enumerate(pairs, start=1):
        line = f"{i}. {description} [{word}]"
        if y < margin_y:
            c.showPage()
            y = height - margin_y
            c.setFont("Helvetica", 11)
        c.drawString(margin_x, y, line)
        y -= line_height

    c.save()
    print(f"V {filename} sú uložené inštrukcie pre poradie čítania slov.")

# Príklad použitia
# Premenná pre testovanie
words_expanded = [
    ("nakreslí", "sloveso, 3. osoba, jednotné číslo, budúci čas"),
    ("sedíš", "sloveso, 2. osoba, jednotné číslo, prítomný čas"),
    ("tešili", "sloveso, 3. osoba, množné číslo, minulý čas"),
    ("urobila", "sloveso, 1. osoba, jednotné číslo, minulý čas"),
    ("písal", "sloveso, 2. osoba, jednotné číslo, minulý čas"),
    ("dvadsať", "číslovka, základná"),
    ("prvý", "číslovka, radová"),
    ("ono", "zámeno, osobné, tretia osoba, jednotné číslo, nominatív"),
    ("my", "zámeno, osobné, nominativ"),
    ("ňou", "zámeno, osobné, tretia osoba, jednotné číslo, inštrumentál"),
    ("školy", "podstatné meno, ženský rod, jednotné číslo, genitív"),
    ("kamarátmi", "podstatné meno, mužský rod, množné číslo, inštrumentál"),
    ("srdci", "podstatné meno, stredný rod, jednotné číslo, lokál"),
    ("dievčatám", "podstatné meno, ženský rod, množné číslo, datív"),
    ("štvrták", "podstatné meno, mužský rod, jednotné číslo, nominativ"),
    ("základnej", "prídavné meno, ženský rod, jednotné číslo, genitív"),
    ("dobrými", "prídavné meno, mužský rod, množné číslo, inštrumentál"),
    ("úprimnom", "prídavné meno, stredný rod, jednotné číslo, lokál"),
    ("šikovných", "prídavné meno, mužský rod, množné číslo, genitív"),
    ("usilovný", "prídavné meno, mužský rod, jednotné číslo, nominativ"),
    ('rozmýšľať', 'sloveso, základný tvar - neurčitok')
]

cards, reading_order = generate_word_bingo_cards(
    word_desc_pairs=words_expanded,
    board_size=4,
    num_players=11,
    min_turns=7,
    max_turns=15
)

export_bingo_cards_to_pdf_grid(cards, board_size=4, filename='bingo_test.pdf')
export_description_script_pdf(reading_order, filename='script_test.pdf')
