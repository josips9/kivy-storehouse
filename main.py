import kivy
import sqlite3
import os
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config

Config.set('graphics', 'width', '340')
Config.set('graphics', 'height', '500')


def connect_to_database(path):
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        create_table_productos(cursor)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def create_table_productos(cursor):
    cursor.execute(
        """
        CREATE TABLE Productos(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Naziv TEXT NOT NULL,
        Oznaka TEXT NOT NULL,
        Cijena FLOAT NOT NULL,
        Kolicina TEXT NOT NULL
        )
        """
    )


class MainWid(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # connect to database
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH + '/my_database.db'

        self.StartWid = StartWid(self)
        wid = Screen(name='start')
        wid.add_widget(self.StartWid)
        self.add_widget(wid)

        self.DatabaseWid = DatabaseWid(self)
        wid = Screen(name='database')
        wid.add_widget(self.DatabaseWid)
        self.add_widget(wid)

        self.InsertDataWid = InsertDataWid(self)
        wid = Screen(name='insertdata')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)

        self.UpdateDataWid = UpdateDataWid(self, data_id="0")
        wid = Screen(name='updatedata')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)

        self.Popup = MessagePopup()

        self.goto_start()

    def goto_start(self):
        self.current = 'start'

    def goto_database(self):
        self.DatabaseWid.check_memory()
        self.current = 'database'

    def goto_insertdata(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'insertdata'

    def goto_updatedata(self, data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self, data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'updatedata'


class StartWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()


class DatabaseWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def check_memory(self):
        self.ids.container.clear_widgets()

        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID, Naziv, Oznaka, Cijena, Kolicina FROM Productos')
        for element in cursor:
            wid = DataWid(self.mainwid)
            r1 = str(element[0]) + '\n'
            r2 = element[1] + '\n'
            r3 = 'cijena po jedinici ' + str(element[3]) + '\n'
            r4 = 'količina ' + str(element[4]) + '\n'
            wid.data_id = str(element[0])
            wid.data = r1 + r2 + r3 + r4
            self.ids.container.add_widget(wid)

        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid)


class NewDataButton(Button):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def create_new_product(self):
        print("proizvod kreiran")
        self.mainwid.goto_insertdata()


class InsertDataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def insert_data(self):
        print("metoda za insert")
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()
        d1 = self.ids.ti_naziv.text
        d2 = self.ids.ti_oznaka.text
        d3 = self.ids.ti_cijena.text
        d4 = self.ids.ti_kolicina.text

        a1 = (d1, d2, d3, d4)
        s1 = 'INSERT INTO Productos(Naziv, Oznaka, Cijena, Kolicina)'
        s2 = 'VALUES("%s", "%s", %s, %s)' % a1

        try:
            cursor.execute(s1 + " " + s2)
            conn.commit()
            conn.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Greška u bazi"
            if "" in a1:
                message.text = "Niste unijeli sve podatke"
            else:
                message.text = str(e)

    def back_to_dbw(self):
        self.mainwid.goto_database()


class MessagePopup(Popup):
    pass


class DataWid(BoxLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid

    def update_data(self, data_id):
        self.mainwid.goto_updatedata(data_id)


class UpdateDataWid(BoxLayout):
    def __init__(self, data_id, mainwid, **kwargs):
        super().__init__(**kwargs)
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()

    def check_memory(self):
        conn = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = conn.cursor()
        s = 'SELECT Naziv, Oznaka, Cijena, Kolicina FROM Productos WHERE ID = %s'
        cursor.execute(s + self.data_id)
        for element in cursor:
            self.ids.ti_naziv.text = str(element[0])
            self.ids.ti_oznaka.text = str(element[1])
            self.ids.ti_cijena.text = str(element[2])
            self.ids.ti_kolicina.text = str(element[3])
        conn.close()

    def update_data(self):
        pass

    def delete_data(self):
        pass

    def back_to_dbw(self):
        self.mainwid.goto_database()


class MainApp(App):
    title = "jednostavno skladište"

    def build(self):
        return MainWid()


MainApp().run()
