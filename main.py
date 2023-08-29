import webbrowser
from kivy.app import App
import re
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from datetime import datetime
from datetime import date
import sqlite3

try:
    conn = sqlite3.connect('BD-kapsula.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT, tema TEXT)''')
    conn.commit()
    cursor.execute("SELECT tema FROM settings")
    n_tema = cursor.fetchone()
    if n_tema == ('Светлая',):
        dtem = (1, 1, 1, 1)
        ltem = (0, 0, 0, 1)
        btem = (0.128, 0.128, 0.128, 0.5)
        ttem = (0.128, 0.128, 0.128, 0.2)
        s_tema = "Светлая"
    elif n_tema == ('Темная',):
        ltem = (1, 1, 1, 1)
        dtem = (0, 0, 0, 1)
        btem = (0.9, 0.918, 0.9, 1)
        ttem = (1, 1, 1, 1)
        s_tema = "Темная"
    elif n_tema == None:
        ltem = (1, 1, 1, 1)
        dtem = (0, 0, 0, 1)
        btem = (0.9, 0.918, 0.9, 1)
        ttem = (1, 1, 1, 1)
        s_tema = "Темная"
        #conn = sqlite3.connect('BD-kapsula.db')
        #cursor = conn.cursor()
        cursor.execute("INSERT INTO settings (tema) VALUES (?)", (s_tema,))
        conn.commit()
        conn.close()
    else:
        popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                      content=Label(text='Ошибка смены темы :(' + '\n' + str(n_tema)), size_hint=(0.7, 0.3))
        popup.open()
        dtem = (1, 0, 0, 1)
        ltem = (1, 1, 1, 1)
        btem = (0.9, 0.918, 0.9, 1)
        ttem = (1, 1, 1, 1)
        s_tema = "Темная"
    conn.close()
except:
    popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                  content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
    popup.open()
today_date = date.today()
adm = 0

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = dtem
        self.sm = ScreenManager()
        self.add_widget(self.sm)
        layout = BoxLayout(orientation='vertical')
        self.sr_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        root = ScrollView(size_hint=(1, 1))
        niz_layout = BoxLayout(size_hint=(1, None))
        header_layout = BoxLayout(size_hint=(1, None))
        header_layout.add_widget(Label(text='Капсула времени', color=ltem, font_size=50, size_hint=(0.7, 0.8)))
        set_button = Button(text='...', color=ltem, background_color=btem, size_hint=(0.2, 0.8), font_size=50,
                            pos_hint={'center_x': 0.5})
        set_button.bind(on_press=self.settings_screen)
        header_layout.add_widget(set_button)
        plus_button = Button(text='+', color=ltem, background_color=btem, size_hint=(0.3, None), font_size=50,
                             pos_hint={'center_x': 0.5})
        plus_button.bind(on_press=self.new_capsule_screen)
        niz_layout.add_widget(plus_button)
        layout.add_widget(header_layout)
        root.add_widget(self.sr_layout)
        layout.add_widget(root)
        layout.add_widget(niz_layout)
        self.add_widget(layout)
    def open_capsule(self, row):
        self.manager.current = 'capsule'
        self.manager.get_screen('capsule').date_label.text = 'Капсула заложена: ' + row[1]
        self.manager.get_screen('capsule').description_label.text = row[2]
        self.manager.transition.direction = 'left'
    def close_capsule(self, row, razn_date):
        popup = Popup(title='Капсула закрыта', title_align='center', title_color=[1, 0, 0, 1], size_hint=(0.7, 0.3),
                      content=Label(text='Капсула закрыта до ' + row[3] + '\nОсталось дней: ' + razn_date,
                                    size_hint=(1, 1)))
        popup.open()
    def new_capsule_screen(self, instance):
        self.manager.current = 'new_capsule'
        self.manager.transition.direction = 'left'
    def settings_screen(self, instance):
        self.manager.current = 'settings'
        self.manager.transition.direction = 'left'
    def on_pre_enter(self):
        try:
            self.sr_layout.clear_widgets()
            conn = sqlite3.connect('BD-kapsula.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS kapsul
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, date_s TEXT, description TEXT, date_do TEXT)''')
            conn.commit()
            cursor.execute("SELECT * FROM kapsul")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                date_doo = datetime.strptime(row[3], "%d.%m.%Y")
                if today_date >= datetime.date(date_doo):
                    button = Button(text="Капсула открыта с " + row[3], color=ltem, background_color=btem,
                                    size_hint=(0.9, None), pos_hint={'center_x': 0.5, 'y': 0.8})
                    button.bind(on_press=lambda instance, row=row: self.open_capsule(row))
                    self.sr_layout.add_widget(button)
                elif today_date < datetime.date(date_doo):
                    razn_date = str(datetime.date(date_doo) - today_date).split()[:-2][0]
                    button = Button(text="Капсула закрыта до " + row[3], color=ltem, background_color=btem,
                                    size_hint=(0.9, None), pos_hint={'center_x': 0.5, 'y': 0.8})
                    button.bind(on_press=lambda instance, row=row, razn_data=razn_date: self.close_capsule(row, razn_data))
                    self.sr_layout.add_widget(button)
            if len(rows) == 0:
                self.sr_layout.add_widget(
                    Label(text='Вселенская пустота... \nДобавьте первую капсулу', color=ltem, size_hint=(1, None),
                          pos_hint={'center_y': 0.5, 'center_x': 0.5}, font_size=45))
            self.sr_layout.bind(minimum_height=self.sr_layout.setter('height'))
        except:
            popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                      content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
            popup.open()
class NewCapsuleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = dtem
        layout = BoxLayout(orientation='vertical')
        header_layout = BoxLayout(size_hint=(1, None))
        back_button = Button(text='<-', color=ltem, background_color=btem, size_hint=(0.2, 0.8), font_size=40)
        back_button.bind(on_press=self.back_to_start_screen)
        header_layout.add_widget(back_button)
        header_layout.add_widget(Label(text='Новая капсула', color=ltem, size_hint=(0.7, 0.8)))
        layout.add_widget(header_layout)
        layout.add_widget(Label(text='Дата', color=ltem, size_hint=(1, 0.3), height=60))
        self.date_input = TextInput(multiline=False, hint_text="01.01.2001", background_active="", size_hint=(1, 0.15),
                                    background_color=ttem)
        self.date_input.bind(text=self.validate_date)
        layout.add_widget(self.date_input)
        layout.add_widget(Label(text='Текст капсулы', color=ltem, size_hint=(1, 0.3), height=60))
        self.description_input = TextInput(multiline=True, background_color=ttem, background_active="",
                                           hint_text="А помнишь...", size_hint=(1, 1))
        layout.add_widget(self.description_input)
        self.description_input.bind(text=self.char_limit)
        layout.add_widget(Widget(size_hint=(1, 0.3)))
        save_button = Button(text='Сохранить', color=ltem, background_color=btem, size_hint=(1, 0.2), height=110)
        save_button.bind(on_press=self.save_capsule)
        layout.add_widget(save_button)
        self.add_widget(layout)
    def back_to_start_screen(self, instance):
        self.manager.current = 'start'
        self.manager.transition.direction = 'right'
    def validate_date(self, instance, value):
        valid_text = re.sub(r'[^.\d]', '', instance.text)
        valid_text = valid_text[:10]
        instance.text = valid_text
    def char_limit(self, instance, value):
        if len(value) > 1500:
            instance.text = value[:1500]
    def save_capsule(self, instance):
        date = self.date_input.text
        description = self.description_input.text
        today_data = datetime.strptime(str(today_date), '%Y-%m-%d').strftime('%d.%m.%y')
        try:
            valid_data = datetime.strptime(date, "%d.%m.%Y")
            if description.strip() == "":
                popup = Popup(title='Ошибка', title_align='center', title_color=[1, 0, 0, 1], size_hint=(0.7, 0.3),
                              content=Label(text='Напишите что-то'))
                popup.open()
            else:
                if today_date > datetime.date(valid_data):  # переделать в >= перед заливк в прод!!!!!!
                    popup = Popup(title='Ошибка', title_align='center', title_color=[1, 0, 0, 1], size_hint=(0.7, 0.3),
                                  content=Label(text='Дата должна быть\nбольше сегодняшней'))
                    popup.open()
                else:
                    try:
                        conn = sqlite3.connect('BD-kapsula.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO kapsul (date_s, description, date_do) VALUES (?, ?, ?)",
                                       (today_data, description, date))
                        conn.commit()
                        conn.close()
                        self.description_input.text = ""
                        self.date_input.text = ""
                        popup = Popup(title='Успешно сохранено', title_align='center', title_color=[0, 1, 0, 1],
                                      content=Label(text='Капсула сохранена успешно'), size_hint=(0.7, 0.3))
                        popup.open()
                        self.manager.current = 'start'
                        self.manager.transition.direction = 'right'
                    except:
                        popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                                      content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
                        popup.open()
        except:
            popup = Popup(title='Ошибка', title_align='center', title_color=[1, 0, 0, 1], size_hint=(0.7, 0.3),
                          content=Label(text='Дата должна быть\nв формате dd.mm.yyyy'))
            popup.open()
class CapsuleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = dtem
        layout = BoxLayout(orientation='vertical')
        root = ScrollView(size_hint=(1, 1))
        header_layout = BoxLayout(size_hint=(1, None))
        sr_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        sr_layout.bind(minimum_height=sr_layout.setter('height'))
        back_button = Button(text='<-', color=ltem, background_color=btem, size_hint=(0.2, 0.8), font_size=40)
        back_button.bind(on_press=self.back_to_start_screen)
        header_layout.add_widget(back_button)
        header_layout.add_widget(Label(text='Капсула', color=ltem, size_hint=(0.7, 0.8)))
        layout.add_widget(header_layout)
        self.date_label = Label(text='', color=ltem, pos_hint={'x': 0, 'y': 0.9}, size_hint=(1, None), height=50)
        sr_layout.add_widget(self.date_label)
        self.description_label = Label(text='', color=ltem, size_hint=(0.9, None), text_size=(Window.width - 100, None))
        self.description_label.bind(texture_size=self.description_label.setter('size'))
        sr_layout.add_widget(self.description_label)
        root.add_widget(sr_layout)
        layout.add_widget(root)
        self.add_widget(layout)
    def back_to_start_screen(self, instance):
        self.manager.current = 'start'
        self.manager.transition.direction = 'right'

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        self.adm=0
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        Window.clearcolor = dtem
        self.add_widget(layout)
        header_layout = BoxLayout(size_hint=(1, None))
        back_button = Button(text='<-', color=ltem, background_color=btem, size_hint=(0.2, 0.8), font_size=40)
        back_button.bind(on_press=self.back_to_start_screen)
        header_layout.add_widget(back_button)
        header_layout.add_widget(Label(text='Настройки', color=ltem, size_hint=(0.7, 0.8)))
        layout.add_widget(header_layout)
        sred_layout = BoxLayout(size_hint=(1, 1))
        sred_layout.add_widget(Label(text='Тема\n'
                                          '[color=#5E5E5E]Требуется перезапуск[/color]',
                                     color=ltem, size_hint=(0.5, None), pos_hint={'top': 1}, markup=True))
        dropdown = DropDown()
        dark_btn = Button(text='Темная', color=ltem, background_color=btem, size_hint=(0.45, None))
        dark_btn.bind(on_release=lambda btn: dropdown.select(btn.text))
        dropdown.add_widget(dark_btn)
        light_btn = Button(text='Светлая', color=ltem, background_color=btem, size_hint=(0.45, None))
        light_btn.bind(on_release=lambda btn: dropdown.select(btn.text))
        dropdown.add_widget(light_btn)
        self.dropdown_btn = Button(text=s_tema, color=ltem, background_color=btem, pos_hint={'top': 1},
                                   size_hint=(0.45, None))
        self.dropdown_btn.bind(on_release=dropdown.open)
        sred_layout.add_widget(self.dropdown_btn)
        dropdown.bind(on_select=self.save_settings)
        del_button = Button(text='Очистить данные', color=ltem, background_color=btem, size_hint=(0.45, None),
                            pos_hint={'center_x': 0.5})
        del_button.bind(on_press=self.pop_up)
        sr2_layout = BoxLayout(size_hint=(1, None))
        sr2_layout.add_widget(Label(text='Удалить все капсулы', color=ltem, size_hint=(0.5, None),
                                    pos_hint={'center_x': 0.5}))
        sr2_layout.add_widget(del_button)
        layout.add_widget(sr2_layout)
        info_button = Button(text='Информация', color=ltem, background_color=btem, size_hint=(0.45, None))
        info_button.bind(on_press=self.information)
        sr3_layout = BoxLayout(size_hint=(1, None))
        sr3_layout.add_widget(Label(text='Подробнее о приложении', color=ltem, size_hint=(0.5, None)))
        sr3_layout.add_widget(info_button)
        layout.add_widget(sr3_layout)
        layout.add_widget(sred_layout)
        Window.softinput_mode = 'below_target'
    def back_to_start_screen(self, instance):
        self.manager.current = 'start'
        self.manager.transition.direction = 'right'
    def information(self, instance):
        p_layout = BoxLayout(orientation="vertical")
        infotext = Label(text='Создатель: [ref=ranon]Анонимный[/ref]\n'
                                       'Поддержка: [ref=rbot][color=#00BFFF]ТГ бот[/color][/ref]\n'
                                       'Версия: 1.0', markup=True)
        infotext.bind(on_ref_press=self.refinfo)
        p_layout.add_widget(infotext)
        popup = Popup(title='Информация', title_align='center', title_color=[0, 0, 1, 1],
                      content=p_layout, size_hint=(0.8, 0.4))
        cl_button = Button(text='Закрыть', pos_hint={'center_x': 0.5}, size_hint=(0.5, None))
        p_layout.add_widget(cl_button)
        cl_button.bind(on_press=popup.dismiss)
        popup.open()
    def refinfo(self, instance, *args):
        if args[0]=='ranon':
            self.adm+=1
            if self.adm>=10:
                popup = Popup(title='Пасхалка', title_align='center', title_color=[1, 1, 1, 1],
                              content=Label(text='Ну как же без пасхалки?)'), size_hint=(0.7, 0.3))
                popup.open()
                self.adm=0
        elif args[0]=="rbot":
            try:
                webbrowser.open('https://t.me/capsule_vremeni_bot', new=2)
            except:
                popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                        content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
                popup.open()
        else:
            popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                          content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
            popup.open()
    def pop_up(self, instance):
        pop1_layout = BoxLayout(orientation="vertical")
        pop2_layout = BoxLayout(size_hint=(1, None))
        pop1_layout.add_widget(Label(text='Вы уверены,\nчто хотите удалить капсулы?'))
        ok_button = Button(text='Да', size_hint=(0.5, 1))
        pop2_layout.add_widget(ok_button)
        cl_button = Button(text='Закрыть', size_hint=(0.5, 1))
        pop2_layout.add_widget(cl_button)
        ok_button.bind(on_press=self.delete_capsule)
        pop1_layout.add_widget(pop2_layout)
        self.popup1 = Popup(title='Уведомление', content=pop1_layout, title_align='center',
                      title_color=[0, 0, 1, 1], size_hint=(0.8, 0.4))
        cl_button.bind(on_press=self.popup1.dismiss)
        self.popup1.open()
    def delete_capsule(self, instance):
        try:
            conn = sqlite3.connect('BD-kapsula.db')
            cursor = conn.cursor()
            cursor.execute("DROP TABLE kapsul")
            conn.close()
            self.popup1.dismiss()
            popup = Popup(title='Успешно удалено', title_align='center', title_color=[0, 1, 0, 1],
                          content=Label(text='Данные удалены успешно'), size_hint=(0.7, 0.3))
            popup.open()
        except:
            popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                          content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
            popup.open()
    def save_settings(self, instance, value):
        self.dropdown_btn.text = value
        val_tema = self.dropdown_btn.text
        try:
            conn = sqlite3.connect('BD-kapsula.db')
            cursor = conn.cursor()
            cursor.execute("Update settings set tema = (?) where id=1", (val_tema,))
            conn.commit()
            conn.close()
            popup = Popup(title='Настройки сохранены успешно', title_align='center', title_color=[0, 1, 0, 1],
                          content=Label(text='Перезапустите приложение\nдля применения'),
                          size_hint=(0.7, 0.3))
            popup.open()
            self.manager.current = 'start'
            self.manager.transition.direction = 'right'
        except:
            popup = Popup(title='Ошибка', title_align='center', title_color=[1, 0, 0, 1], size_hint=(0.7, 0.3),
                          content=Label(text='Ошибка сохранения'))
            popup.open()

class CapsulesApp(App):
    def build(self):
        try:
            self.title = 'Капсула времени'
            conn = sqlite3.connect('BD-kapsula.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS kapsul
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, date_s TEXT, description TEXT, date_do TEXT)''')
            conn.commit()
            #conn.close()
        except:
            popup = Popup(title='Что-то пошло не так...', title_align='center', title_color=[1, 0, 0, 1],
                          content=Label(text='Произошла системная ошибка :('), size_hint=(0.7, 0.3))
            popup.open()
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(NewCapsuleScreen(name='new_capsule'))
        sm.add_widget(CapsuleScreen(name='capsule'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    CapsulesApp().run()