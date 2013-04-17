import kivy
kivy.require('1.5.1')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.listview import ListView
from pyswip import Prolog
from kivy.properties import StringProperty
from kivy.adapters.simplelistadapter import SimpleListAdapter

prolog = Prolog()
prolog.consult("tic.pl")
sm = ScreenManager(transition=SwapTransition())

#NOTE: Module pyswip has many bugs, eg. for some readon I can't take query if is already taken in same context :(
# Very very buggy module, and that is reason why code maybe looky little strange (global variables, etc.)

class PrologHelper():
    def addScore(self, score):
        #res = prolog.query("addScore(4)")
        res = prolog.query("addScore(%s)" % score)
        for sol in res:
            print sol

ph = PrologHelper()

class HighScoresScreen(Screen):

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        kwargs['size_hint'] = (1.0, 1.0)
        super(HighScoresScreen, self).__init__(**kwargs)
                
        response = prolog.query("getScores(Scores)")
        for sol in response:
            result = sol["Scores"]

        if(result[0] != "["):
            simple_list_adapter = SimpleListAdapter(
                data=["Player score: {0}".format(i) for i in result],
                cls=Label)
        else:
            message = ["No avabile high scores!"]
            simple_list_adapter = SimpleListAdapter(
                data=message,
                cls=Label)
        
        list_view = ListView(adapter=simple_list_adapter)
        
        self.add_widget(list_view)
        
    def click(self):
        sm.current = "menu"

hsScreen = HighScoresScreen(name="highScores")

class GameplayScreen(Screen):

    box = StringProperty()
    view = ModalView(size_hint=(None, None), size=(300, 100))
    turn = 'x'
    points = 0
    gameOver = 0
    
    def __init__(self, **kwargs):
        super(GameplayScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        Detect pressed key
        '''
        # when user press escape key
        self.view.dismiss()
        if(keycode[0] == 27):
            self.showMenuModal(self)
        return -1

    def showMenu(self, kwargs):
        '''
        Method for showing main menu
        '''
        self.view.dismiss()

        try:
            sm.get_screen("highScores")
            sm.remove_widget(hsScreen)
        except:
            pass
        
        sm.current = "menu"

    def newGame(self, kwargs):
        '''
        Clear table and begin new game
        '''
        # clear table
        for linearLayout in self.children:
            for linear in linearLayout.children:
                for button in linear.children:
                    button.text = ""

        if(self.gameOver == 1):
            #ph.addScore(self.points)
            self.gameOver = 0
            self.points = 0
                    
        # hide modal
        self.view.dismiss()


    def nextLevel(self, kwargs):
        '''
        If is remi of user is win, goto next level (we will play again -> score++)
        '''
        self.newGame(kwargs)
        if(self.turn == 'o'):
            response = prolog.query("play(o, _, Result)")
            self.drawTable(kwargs, response)

    def changeBeginMove(self):
        '''
        Switch turns
        '''
        if(self.turn == 'x'):
            self.turn = 'o'
            
        elif(self.turn == 'o'):
            self.turn = 'x'
            

    def showMenuModal(self, winner):
        '''
        When we have winner, or all squares are filled
        '''
        if(winner == 'o'):
            message = "Computer wins. You collect " + str(self.points) + " points!"
            self.gameOver = 1

        elif(winner == -1):
            message = "Remi"
            self.changeBeginMove()
            self.points += 1

        elif(winner == 'x'):
            message = "User wins"
            self.changeBeginMove()
            self.points += 2

        else:
            message = "Pause"

        boxlayout = BoxLayout(orientation='vertical')
        boxlayout.add_widget(Label(text=message))
        buttonLayout = BoxLayout(orientation='horizontal')

        if((winner == 'x') | (winner == -1)):
            buttonLayout.add_widget(Button(text="Next level", on_press=self.nextLevel))

        if(winner == 'o'):
            buttonLayout.add_widget(Button(text="Save score", on_press=lambda save: ph.addScore(self.points)))
            
        buttonLayout.add_widget(Button(text="New Game", on_press=self.newGame))
        buttonLayout.add_widget(Button(text="Main Menu", on_press=self.showMenu))
        boxlayout.add_widget(buttonLayout)

        self.view = ModalView(size_hint=(None, None), size=(300, 100))
        
        self.view.add_widget(boxlayout)
        self.view.open()

    def drawTable(self, kwargs, response):
        '''
        Draw table by response from prolog
        '''
        for sol in response:
            if((sol["Result"] == 'x') | (sol["Result"] == 'o') | (sol["Result"] == -1)):
                squares = sol["Result"]
                break
            else:
                squares = list((sol["Result"]))
                
        if((squares == 'x') | (squares == 'o') | (squares == -1)):
            self.showMenuModal(squares)

        else:
            i = len(squares) - 1
            for linearLayout in self.children:
                for linear in linearLayout.children:
                    for button in linear.children:
                        if squares[i] != "N":
                            button.text = squares[i]
                        i -= 1
    def btn_click(self, args):
        '''
        When user click on some box...
        '''
        if((args.text == "x") | (args.text == "o")):
            Logger.info("Square occupied")
            
        else:
            response = prolog.query("playy(%s, Result)" % self.box)
            self.drawTable(args, response)
            Logger.info("User has click on button")
            
        
class MenuScreen(Screen):

    def newGame(self, args):
        sm.current = "game"

    def highScores(self, args):
        global hsScreen
        hsScreen = HighScoresScreen(name="highScores")
        sm.add_widget(hsScreen)
        sm.current = "highScores"
            
class TicTacToe(App):
    
    def build(self):
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameplayScreen(name='game'))
        return sm

if __name__ == '__main__':
    TicTacToe().run()

    
