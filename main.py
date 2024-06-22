import tkinter as tk
from PIL import Image, ImageTk
import random
import os
from colorama import init, Back, Fore, Style

class Deck:
    def __init__(self):
        self.cards = [value + suit for suit in 'CDHS' for value in '23456789TJQKA']
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            if card[0] in 'TJQK':
                value += 10
            elif card[0] == 'A':
                aces += 1
                value += 11
            else:
                value += int(card[0])
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

class BlackjackGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Blackjack with Dealer Bot")
        self.deck = Deck()
        self.player_hand = Hand()
        self.split_hand = None
        self.dealer_hand = Hand()
        self.double_down = False
        self.split_mode = False
        self.active_hand = 'player'
        self.balance = 1000
        self.bet = 0
        self.double_bet = False
        self.background_image = ImageTk.PhotoImage(file='background.jpg')
        self.background_label = tk.Label(master, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.deal_button = tk.Button(self.buttons_frame, text="Deal", command=self.deal)
        self.deal_button.pack(fill=tk.X)

        self.hit_button = tk.Button(self.buttons_frame, text="Hit", command=self.hit, state=tk.DISABLED)
        self.hit_button.pack(fill=tk.X)

        self.stand_button = tk.Button(self.buttons_frame, text="Stand", command=self.stand, state=tk.DISABLED)
        self.stand_button.pack(fill=tk.X)

        self.double_button = tk.Button(self.buttons_frame, text="Double", command=self.double, state=tk.DISABLED)
        self.double_button.pack(fill=tk.X)

        self.split_button = tk.Button(self.buttons_frame, text="Split", command=self.split, state=tk.DISABLED)
        self.split_button.pack(fill=tk.X)

        self.switch_hand_button = tk.Button(self.buttons_frame, text="Switch Hand", command=self.switch_hand, state=tk.DISABLED)
        self.switch_hand_button.pack(fill=tk.X)

        self.bet_label = tk.Label(self.buttons_frame, text="Bet:")
        self.bet_label.pack()
        self.bet_entry = tk.Entry(self.buttons_frame)
        self.bet_entry.pack()

        self.balance_label = tk.Label(self.buttons_frame, text=f"Balance: ${self.balance}")
        self.balance_label.pack()

        self.message = tk.Label(master, text="", font=("Arial", 18))
        self.message.pack()

        self.dealer_frame = tk.Frame(master)
        self.dealer_frame.pack(pady=10)

        self.dealer_label = tk.Label(self.dealer_frame, text="Dealer", font=("Arial", 14), fg='black')
        self.dealer_label.pack()

        self.dealer_cards_frame = tk.Frame(self.dealer_frame)
        self.dealer_cards_frame.pack()

        self.player_frame = tk.Frame(master)
        self.player_frame.pack(pady=10)

        self.player_label = tk.Label(self.player_frame, text="Player", font=("Arial", 14), fg='black')
        self.player_label.pack()

        self.player_cards_frame = tk.Frame(self.player_frame)
        self.player_cards_frame.pack()

        self.split_frame = tk.Frame(master)
        self.split_frame.pack(pady=10)

        self.split_label = tk.Label(self.split_frame, text="Split Hand", font=("Arial", 14), fg='black')
        self.split_label.pack()

        self.split_cards_frame = tk.Frame(self.split_frame)
        self.split_cards_frame.pack()

        self.points_label = tk.Label(master, text="", font=("Arial", 14))
        self.points_label.pack()

        self.deck_image = ImageTk.PhotoImage(Image.open(os.path.join('cards', 'phone.png')))
        self.deck_label = tk.Label(master, image=self.deck_image)
        self.deck_label.pack(side=tk.RIGHT, padx=10, pady=10)

        self.card_images = self.load_card_images()

    def load_card_images(self):
        card_images = {}
        for card in [value + suit for suit in 'CDHS' for value in '23456789TJQKA']:
            image = Image.open(os.path.join('cards', f"{card}.png"))
            card_images[card] = ImageTk.PhotoImage(image)
        return card_images

    def deal(self):
        if self.balance <= 0:
            self.message.config(text="You have no money left. You lost everything!")
            return

        try:
            self.bet = int(self.bet_entry.get())
            if self.bet > self.balance or self.bet <= 0:
                self.message.config(text="Invalid bet amount!")
                return
        except ValueError:
            self.message.config(text="Please enter a valid bet amount!")
            return

        self.balance -= self.bet
        self.update_balance()

        self.deck = Deck()
        self.player_hand = Hand()
        self.split_hand = None
        self.dealer_hand = Hand()
        self.double_down = False
        self.split_mode = False
        self.active_hand = 'player'
        self.double_bet = False

        # Reset split hand frame
        for widget in self.split_cards_frame.winfo_children():
            widget.destroy()

        self.split_frame.config(width=200, height=100)  # Reset size of split hand frame

        self.player_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

        self.hidden_card = self.dealer_hand.cards[1]  # Remember the hidden card
        self.update_display()
        self.enable_buttons()

    def update_display(self):
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.split_cards_frame.winfo_children():
            widget.destroy()

        for card in self.player_hand.cards:
            label = tk.Label(self.player_cards_frame, image=self.card_images[card])
            label.pack(side=tk.LEFT, padx=5)  # Add space between cards

        if self.split_hand:
            for card in self.split_hand.cards:
                label = tk.Label(self.split_cards_frame, image=self.card_images[card])
                label.pack(side=tk.LEFT, padx=5)  # Add space between cards

        for i, card in enumerate(self.dealer_hand.cards):
            if i == 1 and not self.double_bet:  # Hide one card of the dealer
                label = tk.Label(self.dealer_cards_frame, image=self.deck_image)
            else:
                label = tk.Label(self.dealer_cards_frame, image=self.card_images[card])
            label.pack(side=tk.LEFT, padx=5)  # Add space between cards

        self.points_label.config(text=f"Player: {self.player_hand.get_value()} Dealer: {self.dealer_hand.get_value() if self.double_bet else '??'}")

        if self.player_hand.get_value() > 21:
            self.message.config(text="Player busts!")
            self.disable_buttons()
            self.check_winner()
        elif self.split_hand and self.split_hand.get_value() > 21:
            self.message.config(text="Split hand busts!")
            self.disable_buttons()
            self.check_winner()

    def hit(self):
        if self.active_hand == 'split' and self.split_hand:
            self.split_hand.add_card(self.deck.deal())
            self.update_display()
            if self.split_hand.get_value() > 21:
                self.message.config(text="Split hand busts!")
                self.disable_buttons()
                self.check_winner()
        else:
            self.player_hand.add_card(self.deck.deal())
            self.update_display()
            if self.player_hand.get_value() > 21:
                self.message.config(text="Player busts!")
                self.disable_buttons()
                self.check_winner()

    def stand(self):
        if self.split_hand and self.active_hand == 'player':
            self.active_hand = 'split'
            self.message.config(text="Switching to split hand")
            self.switch_hand_button.config(state=tk.DISABLED)
        else:
            self.double_bet = True
            self.update_display()
            self.disable_buttons()
            self.dealer_play()
            # Make split hand frame smaller after stand
            if self.split_hand:
                self.split_frame.config(width=100, height=50)
                for widget in self.split_cards_frame.winfo_children():
                    widget.pack_forget()  # Hide cards

    def double(self):
        if not self.double_down and self.bet * 2 <= self.balance:
            self.double_down = True
            self.balance -= self.bet
            self.bet *= 2
            self.update_balance()

            if self.active_hand == 'split' and self.split_hand:
                self.split_hand.add_card(self.deck.deal())
            else:
                self.player_hand.add_card(self.deck.deal())
            self.update_display()
            if self.active_hand == 'split' and self.split_hand.get_value() > 21:
                self.message.config(text="Split hand busts!")
                self.disable_buttons()
                self.check_winner()
            elif self.player_hand.get_value() > 21:
                self.message.config(text="Player busts!")
                self.disable_buttons()
                self.check_winner()
            else:
                self.stand()

    def split(self):
        if len(self.player_hand.cards) == 2 and self.player_hand.cards[0][0] == self.player_hand.cards[1][0] and self.bet * 2 <= self.balance:
            self.balance -= self.bet
            self.update_balance()

            self.split_hand = Hand()
            self.split_hand.add_card(self.player_hand.cards.pop())
            self.player_hand.add_card(self.deck.deal())
            self.split_hand.add_card(self.deck.deal())
            self.split_mode = True
            self.update_display()
            self.switch_hand_button.config(state=tk.NORMAL)

    def switch_hand(self):
        if self.split_hand:
            self.active_hand = 'split' if self.active_hand == 'player' else 'player'
            self.message.config(text=f"Active hand: {'Split hand' if self.active_hand == 'split' else 'Player hand'}")

    def dealer_play(self):
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
        self.update_display()
        self.check_winner()

    def check_winner(self):
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        split_value = self.split_hand.get_value() if self.split_hand else None

        winner = None
        if player_value > 21:
            winner = "Dealer wins!"
        elif dealer_value > 21:
            winner = "Player wins!"
            self.balance += self.bet * 2
        elif dealer_value == player_value:
            winner = "Push! It's a tie."
            self.balance += self.bet
        elif dealer_value >= player_value:
            winner = "Dealer wins!"
        else:
            winner = "Player wins!"
            self.balance += self.bet * 2

        if split_value:
            if split_value > 21:
                winner += "\nDealer wins on split hand!"
            elif dealer_value > 21 or split_value > dealer_value:
                winner += "\nPlayer wins on split hand!"
                self.balance += self.bet * 2

        self.message.config(text=winner)
        self.update_balance()

    def disable_buttons(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.double_button.config(state=tk.DISABLED)
        self.split_button.config(state=tk.DISABLED)
        self.switch_hand_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.double_button.config(state=tk.NORMAL)
        self.split_button.config(state=tk.NORMAL)
        if self.split_hand:
            self.switch_hand_button.config(state=tk.NORMAL)

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ${self.balance}")

root = tk.Tk()
game = BlackjackGame(root)
root.mainloop()
