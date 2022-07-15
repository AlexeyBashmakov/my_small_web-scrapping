import os
import sys
import datetime as dt
# библиотека Tkinter установлена в Python в качестве стандартного модуля
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext
import tkinter.messagebox
import tkinter.filedialog

import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import datetime

class App(tk.Tk):
    # defaults settings
    X_POSITION_WINDOW = "10"
    Y_POSITION_WINDOW = "10"
    WIDTH_WINDOW  = "640"
    HEIGHT_WINDOW = "480"
    LEFT_PANEL = os.path.dirname(__file__)
    RIGHT_PANEL = os.path.dirname(__file__)

    # state of main window
    state = dict()
    state["x_position_window"] = X_POSITION_WINDOW
    state["y_position_window"] = Y_POSITION_WINDOW
    state["width_window"] = WIDTH_WINDOW
    state["height_window"] = HEIGHT_WINDOW
    state["left_panel"]  = LEFT_PANEL
    state["right_panel"] = RIGHT_PANEL

    MAIN_BUTTON_WIDTH  = 80
    MAIN_BUTTON_HEIGHT = 25

    def __init__(self):
        super().__init__()
        self.LoadInitialSettings()
        self.InitMainWindow()
        
        self.nb = ttk.Notebook(self)
        self.page = list()
        self.date_one = list()
        self.one_day_dict = list()
        self.test_one_datas = list()
        self.lbls_times = list()
        self.lbls_temp = list()
        self.lbls_precipitation_one = list()
        self.ten_days_dict = list()
        self.lbls_days = list()
        self.lbls_maxt = list()
        self.lbls_mint = list()
        self.lbls_precipitation = list()
        for p in [0, 1]:
            # пауза, чтобы сайт-цель не заподозрил неладное :)
            time.sleep(0.36)
            self.page.append(ttk.Frame(self.nb))
            self.date_one.append(tk.Label(self.page[p], font = ("Arial", 12), text = self.date_to_russian()).grid(row = 1, column = 0))
            self.one_day_dict.append(one_day(p))
            test_one_datas_text = "Данные получены" if self.one_day_dict[p]["status_code"] == 200 else "Что-то не так"
            self.test_one_datas.append(tk.Label(self.page[p], font = ("Arial", 10, "italic"), text = test_one_datas_text).grid(row = 1, column = 8, columnspan = 3))
            # если данные с gismeteo пришли, то создаем метки для прогнозов
            if self.one_day_dict[p]["status_code"] == 200:
                for i, t in enumerate(self.one_day_dict[p]["times"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 2, column = i+1)
                    self.lbls_times.append(l)
                tk.Label(self.page[p], font = ("Arial", 10), text = "Температура", justify = "left").grid(row = 3, column = 0)#, columnspan = 2)
                for i, t in enumerate(self.one_day_dict[p]["temperatures"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 3, column = i+1)
                    self.lbls_temp.append(l)
                tk.Label(self.page[p], font = ("Arial", 10), text = "Осадки, мм", justify = "left").grid(row = 4, column = 0)#, columnspan = 2)
                for i, t in enumerate(self.one_day_dict[p]["precipitation"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 4, column = i+1)
                    self.lbls_precipitation_one.append(l)
            # пауза, чтобы сайт-цель не заподозрил неладное :)
            time.sleep(0.36)    
            self.ten_days_dict.append(ten_days(p))
            if self.ten_days_dict[p]["status_code"] == 200:
                tk.Label(self.page[p], font = ("Arial", 12), text = "Прогноз на 10 дней").grid(row = 5, column = 0, pady = 10)#, columnspan = 10)
                for i, t in enumerate(self.ten_days_dict[p]["days"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 6, column = i+1)
                    self.lbls_days.append(l)
                tk.Label(self.page[p], font = ("Arial", 10), text = "Максимальная температура", justify = "left").grid(row = 7, column = 0, columnspan = 2)
                for i, t in enumerate(self.ten_days_dict[p]["maxt"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 8, column = i+1)
                    self.lbls_maxt.append(l)
                tk.Label(self.page[p], font = ("Arial", 10), text = "Минимальная температура", justify = "left").grid(row = 9, column = 0, columnspan = 2)
                for i, t in enumerate(self.ten_days_dict[p]["mint"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 10, column = i+1)
                    self.lbls_mint.append(l)
                tk.Label(self.page[p], font = ("Arial", 10), text = "Осадки, мм", justify = "left").grid(row = 11, column = 0)#, columnspan = 2)
                for i, t in enumerate(self.ten_days_dict[p]["precipitation"]):
                    l = tk.Label(self.page[p], font = ("Arial", 12), text = t).grid(row = 12, column = i+1)
                    self.lbls_precipitation.append(l)

        
        self.nb.add(self.page[0], text = "Челябинск")
        self.nb.add(self.page[1], text = "Булзи")
        self.nb.pack(expand = 1, fill = "both")
        

    def LoadInitialSettings(self):
        cfg = open("init_old.cfg")
        for l in cfg:
            if l[0] == "#":
                continue
            line = l.split("=")
            if (line[0].strip() in self.state) and (len(line[1]) > 2):
                self.state[line[0].strip()] = line[1].strip(" \n")
                
        cfg.close()

    def InitMainWindow(self):
        # заголовок окна
        self.title("Gismeteo")
        
        # размер окна
        self.geometry(self.state["width_window"] + "x" + self.state["height_window"] + "+"
                        +self.state["x_position_window"] + "+" + self.state["y_position_window"])
    # geometry - устанавливает геометрию окна в формате ширинаxвысота+x+y
    # (пример: geometry("600x400+40+80") - поместить окно в точку с координатам 40,80
    # и установить размер в 600x400). Размер или координаты могут быть опущены
    # (geometry("600x400") - только изменить размер, geometry("+40+80") - только переместить окно).
        self.bind("<Configure>", self.window_resize)
        self.bind("<Escape>", self.window_deleted)
        self.resizable(False, False)
        # protocol = wm_protocol(self, name=None, func=None)
        # Bind function FUNC to command NAME for this widget.
        # Return the function bound to NAME if None is given. NAME could be
        # e.g. "WM_SAVE_YOURSELF" or "WM_DELETE_WINDOW".
        self.protocol("WM_DELETE_WINDOW", self.window_deleted)

    def getWindowGeometry(self):
        geometry_window = self.geometry()
        list_ = geometry_window.split("+")
        self.state["x_position_window"] = list_[1]
        self.state["y_position_window"] = list_[2]
        [self.state["width_window"], self.state["height_window"]] = list_[0].split("x")

    def window_resize(self, event):
        self.getWindowGeometry()

        # или так
        #h = event.height
        #w = event.width

    def window_deleted(self, event = None):
        #x = window.winfo_screenwidth() ширина экрана
        #y = window.winfo_screenheight() высота экрана
        self.getWindowGeometry()
        conf = open("init_old.cfg", "w")
        conf.write("# window settings\n")
        conf.write(f"x_position_window = {self.state['x_position_window']}\n")
        conf.write(f"y_position_window = {self.state['y_position_window']}\n")
        conf.write(f"width_window  = {self.state['width_window']}\n")
        conf.write(f"height_window = {self.state['height_window']}\n")
        conf.write("# working directory settings\n")
        conf.write(f"left_panel  = {self.state['left_panel']}\n")
        conf.write(f"right_panel = {self.state['right_panel']}\n")
        conf.close()
        self.destroy() # явное указание на выход из программы
        print("Окно закрыто")

    def date_to_russian(self) -> str:
        """
        Функция возвращает строку с датой на русском языке
        """
        months = {1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля", \
                  5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа", \
                  9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"}
        td = dt.date.today()
        y, m, d = td.year, td.month, td.day
        return f"{d} {months[m]} {y} года"

def one_day(city: int = 0) -> dict:
    """
    Функция получает данные для Челябинска от gismeteo для сегодняшней даты
    """
    # словарь, который будет хранить нужные данные
    result = dict()
    url = ["https://www.gismeteo.ru/weather-chelyabinsk-4565/", \
           "https://www.gismeteo.ru/weather-bulzi-234546/"]
    headers_ = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    res_main = requests.get(url[city], headers = headers_)
# создаем объект BeautifulSoup, в конструктор передаем два аргумента: строку - 
# html-документ или результат requests.get(...) или просто python-строку 
# и название html парсера
    soup_main = BeautifulSoup(res_main.text, "html.parser")
    result["status_code"] = res_main.status_code
    if result["status_code"] != 200:
        return result["status_code"]
    row_time = soup_main.find_all("div", class_ = "widget-row widget-row-time")
    # список моментов времени прогнозов
    times = list()
    time_format = lambda x: f"0{x}" if x < 10 else f"{x}"
    format2 = "Фактические данные от: %Y-%m-%d %H:%M:%S (UTC)"
    for item in row_time[0].contents:
        if item["title"].split()[0] == "Фактические":
            full_dt = dt.datetime.strptime(item["title"], format2) + dt.timedelta(hours = 5)
            times.append(f"{time_format(full_dt.hour)}:{time_format(full_dt.minute)}")
        elif item["title"].split()[0] == "Прогноз":
            format3 = item["title"].split(",")[0]
            full_dt = dt.datetime.strptime(item["title"], format3 + ", UTC: %Y-%m-%d %H:%M:%S") + dt.timedelta(hours = 5)
            times.append(f"{time_format(full_dt.hour)}:{time_format(full_dt.minute)}")
    result["times"] = times
    row_temperature = soup_main.find_all("div", class_ = "widget-row-chart widget-row-chart-temperature")
    # список прогнозов
    temperatures = list()
    for item in row_temperature[0].contents[0].find_all("span", class_ = "unit unit_temperature_c"):
        temperatures.append(item.text)
    result["temperatures"] = temperatures
    row_precipitation = soup_main.find_all("div", class_ = "widget-row widget-row-precipitation-bars row-with-caption")
    # список осадков
    precipitation = list()
    for item in row_precipitation[0].find_all("div", class_ = "item-unit"):
        precipitation.append(item.text)
    result["precipitation"] = precipitation
    return result

def ten_days(city: int = 0) -> dict:
    """
    Функция получает данные для Челябинска от gismeteo для сегодняшней даты
    """
    # словарь, который будет хранить нужные данные
    result = dict()
    url = ["https://www.gismeteo.ru/weather-chelyabinsk-4565/10-days/", \
           "https://www.gismeteo.ru/weather-bulzi-234546/10-days/"]
    headers_ = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    res_main = requests.get(url[city], headers = headers_)
# создаем объект BeautifulSoup, в конструктор передаем два аргумента: строку - 
# html-документ или результат requests.get(...) или просто python-строку 
# и название html парсера
    soup_main = BeautifulSoup(res_main.text, "html.parser")
    result["status_code"] = res_main.status_code
    if result["status_code"] != 200:
        return result["status_code"]
    row_day = soup_main.find_all("div", class_ = "widget-row widget-row-days-date")
    # список дней прогнозов
    days = list()
    for item in row_day[0].contents:
        days.append(f"{item.contents[0].text}\n{item.contents[1].text}")
    result["days"] = days
    max_temperature = soup_main.find_all("div", class_ = "maxt")
    # список максимальной температуры
    maxt = list()
    for item in max_temperature:
        t = item.find_all("span", class_ = "unit unit_temperature_c")
        if len(t) > 0:
            maxt.append(t[0].text)
        else:
            break
    result["maxt"] = maxt
    min_temperature = soup_main.find_all("div", class_ = "mint")
    # список минимальной температуры
    mint = list()
    for item in min_temperature:
        t = item.find_all("span", class_ = "unit unit_temperature_c")
        if len(t) > 0:
            mint.append(t[0].text)
        else:
            break
    result["mint"] = mint
    row_precipitation = soup_main.find_all("div", class_ = "widget-row widget-row-precipitation-bars row-with-caption")
    # список осадков
    precipitation = list()
    for item in row_precipitation[0].find_all("div", class_ = "item-unit"):
        precipitation.append(item.text)
    result["precipitation"] = precipitation
    return result




# Можно менять не отдельные виджеты, а целиком тему оформления приложения.
# С помощью методов theme_names и theme_use можно выяснить список тем (который зависит от вашей ОС) и текущую тему:
#style = ttk.Style()
#tuple_theme_names = style.theme_names()
#print(tuple_theme_names)
#print(style.theme_use())
#style.theme_use(tuple_theme_names[-1])
#print(style.theme_use())

if __name__ == "__main__":
    try:
        app = App()
        # бесконечный цикл окна, поэтому окно будет ждать любого взаимодействия с 
        # пользователем, пока не будет закрыто
        # Если ее не использовать, то окно сразу закроется, и пользователь ничего не увидит
        app.mainloop()
    except Exception as e:
        tk.messagebox.showerror("Ошибка", e)

