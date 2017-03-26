# Marco Casillas
# Final Project
# Python 2.7.12

########################################################################################################################
# Imports
########################################################################################################################
import random  # Import random for random integer generation
import sys  # Import sys so that we can pass argv to QApplication
import os  # Import os to make calls to OS resources
import sqlite3  # Import sqlite3 so we can work with the app DB

from PyQt4 import QtCore, QtGui  # Import the PyQt4 modules

import hangman_layout  # This file holds the Qt MainWindow and all design related things.

########################################################################################################################
# Class definition
########################################################################################################################
class HangmanApp(QtGui.QMainWindow, hangman_layout.Ui_MainWindow):
    list_of_words = ("psych",
                     "rhubarb",
                     "broadside",
                     "punctual",
                     "television",
                     "january",
                     "february",
                     "march",
                     "april",
                     "may",
                     "june",
                     "july",
                     "august",
                     "september",
                     "november",
                     "december",
                     "monday",
                     "tuesday",
                     "wednesday",
                     "thursday",
                     "friday",
                     "saturday")

    word_to_guess = list_of_words[random.randint(0, 21)]
    misses = ''
    number_of_guesses_remaining = 6
    masked_word = "_" * len(word_to_guess)
    masked_word_as_list = list(masked_word)
    user_name = ""
    consecutive_games_won_this_session = 0
    conn = sqlite3.connect(os.path.join(os.getcwd(), "resources", "hangman_data.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    def __init__(self, parent=None):
        """Initialize game window and all widgets"""
        super(self.__class__, self).__init__(parent)

        self.setupUi(self)
        self.actionQuit.triggered.connect(self.close)
        self.actionLoad_custom_word_list.triggered.connect(self.load_custom_word_list)
        self.actionClear_previous_scores.triggered.connect(self.clear_previous_scores)
        self.actionView_Previous_Scores.triggered.connect(self.display_scores)
        self.new_game()

    def new_game(self):
        """Initialize game window for a new game"""
        if not self.user_name:
            self.get_name()
        self.word_to_guess = self.list_of_words[random.randint(0, (len(self.list_of_words) - 1))].upper()
        if len(self.word_to_guess) > 10:
            while self.word_to_guess > 10:
                self.word_to_guess = self.list_of_words[random.randint(0, (len(self.list_of_words) - 1))].upper()
        self.misses = ''
        self.number_of_guesses_remaining = 6
        self.masked_word = "_" * len(self.word_to_guess)
        self.masked_word_as_list = list(self.masked_word)
        self.lbl_masked_word.setText(str.upper(' '.join(letter for letter in self.masked_word)))
        self.lbl_missed_letters.setText(self.misses)
        self.btn_guess.clicked.connect(self.guess)
        self.lbl_guesses_remaining.setText(str(self.number_of_guesses_remaining))
        self.lbl_hangman_drawing.setPixmap(QtGui.QPixmap(os.path.join(os.getcwd(), "resources", "6.gif")))

        return None

    def load_custom_word_list(self):
        """Use a File Dialog to load a textfile of words for import"""
        word_file_path = QtGui.QFileDialog.getOpenFileName(self, "Pick a word list you'd like to use", os.getcwd(),
                                                           "Text Files (*.txt)")
        print word_file_path
        if word_file_path:
            self.list_of_words = list()
            word_file = open(word_file_path, "r")
            for word in word_file:
                self.list_of_words.append(word.rstrip().upper())
        self.new_game()
        return None

    def clear_previous_scores(self):
        """Purge all scores from the database"""
        self.conn.execute("DELETE FROM user_scores")
        self.conn.commit()
        return None

    def closeEvent(self, event):
        """Override default closeEvent method provided by PyQt4 to prompt user about exiting, and append score to database if they say yes"""
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           quit_msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            if self.consecutive_games_won_this_session:
                self.add_score_to_db()
        else:
            event.ignore()
        return None

    def get_name(self):
        """Prompt the user for their name"""
        name, ok = QtGui.QInputDialog.getText(self, "User's Name", "Enter your name so we can track your score:")
        if ok:
            if name:
                self.user_name = str(name)
            else:
                self.get_name()
        if not ok:
            raise SystemExit
        return None

    def guess(self):
        """Read the user's guess from the linedit box in the guessing frame"""
        guess = str.upper(str(self.lineEdit_guess.text()))
        self.lineEdit_guess.setText("")
        self.check_guess(guess)
        return None

    def check_guess(self, guess):
        """Check the guess submitted by the user"""
        if len(guess) > 1:
            if guess == self.word_to_guess:
                self.winner()
            else:
                self.loser()
        elif guess in self.word_to_guess:
            self.correct_guess(guess)
        else:
            self.incorrect_guess(guess)
        return None

    def correct_guess(self, guess):
        """Process a correct guess input by the user"""
        for ind, letter in enumerate(self.word_to_guess):
            if guess == letter:
                self.masked_word_as_list[ind] = (guess)
            elif not self.masked_word_as_list[ind] == '_ ':
                continue
            else:
                self.masked_word_as_list[ind] = "_ "
        self.masked_word = ''.join(self.masked_word_as_list)
        self.lbl_masked_word.setText(str.upper(' '.join((letter for letter in self.masked_word))))

        if self.masked_word == self.word_to_guess:
            self.winner()
        return None

    def incorrect_guess(self, guess):
        """Process an incorrect guess input by the user"""
        if self.misses == '':
            self.misses = str.upper(guess)
        else:
            self.misses += " " + str.upper(guess)
        self.lbl_missed_letters.setText(self.misses)
        self.decrement_guesses_left()
        return None

    def decrement_guesses_left(self):
        """If the user guesses incorrectly decrement the amount of guesses left
            End the game if the user guesses incorrectly too many times"""
        self.number_of_guesses_remaining -= 1
        self.lbl_hangman_drawing.setPixmap(QtGui.QPixmap(
            os.path.join(os.getcwd(), "resources", "{}.gif".format(self.number_of_guesses_remaining))))
        if self.number_of_guesses_remaining == 0:
            self.lbl_guesses_remaining.setText("You are out of guesses")
            self.loser()
        else:
            self.lbl_guesses_remaining.setText(str(self.number_of_guesses_remaining))

        return None

    def winner(self):
        """If the user wins begin executing winning logic"""
        self.consecutive_games_won_this_session += 1
        self.display_message(True)
        return None

    def loser(self):
        """If the user loses begin executing winning logic"""
        self.add_score_to_db()
        self.consecutive_games_won_this_session = 0
        self.display_message(False)

    def add_score_to_db(self):
        """When the user is ending the session append their score to the database"""
        with self.conn:
            self.conn.execute("INSERT INTO user_scores VALUES (?,?)",
                              (self.user_name, self.consecutive_games_won_this_session))
            self.conn.commit()
        return None

    def pull_scores_from_db(self):
        """Poll the database for the last 5 player scores"""
        with self.conn:

            score_data = self.cursor.execute("SELECT * FROM user_scores").fetchall()
            score_data = sorted(score_data, reverse=True)
            row_count = len(score_data)
            score_data_string = ""
            count = 0
            for row in score_data:
                score_data_string += "%s\t%s\n" % (row["user_name"], row["consecutive_games_won"])
                count += 1
                if count == 5:
                    break
            return score_data_string

    def display_scores(self):
        """Display the scores when executed from the menu entry"""
        msgBox = QtGui.QMessageBox(self)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.setWindowTitle("Previous Player Scores")
        msgBox.setText("Last 5 Scores\n\n" + self.pull_scores_from_db())
        msgBox.exec_()
        return None

    def display_message(self, winner):
        """Process winning and losing messages depending on game state"""
        msgBox = QtGui.QMessageBox(self)
        msgBox.setIcon(QtGui.QMessageBox.Information)

        if winner:
            msgBox.setWindowTitle("Winner!")
            msgBox.setText(
                "<center>You guessed the word \"{}\" correctly!\nWould you like to play again?</center>".format(
                    self.word_to_guess))
        else:
            msgBox.setWindowTitle("Loser!")
            msgBox.setText("<center>Sorry! You Lost!</center>" +
                           "\n" +
                           "<center>The word was \"{}\"</center>".format(self.word_to_guess) +
                           "\n" +
                           "<center>Would you like to play again?</center>")

        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        play_again = msgBox.exec_()

        if play_again == QtGui.QMessageBox.Yes:
            self.new_game()

        else:
            self.close()

        return None


########################################################################################################################
# Functions and Main
########################################################################################################################
def main():
    """Execute the app"""
    app = QtGui.QApplication(sys.argv)
    form = HangmanApp()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
