
import os
import datetime as dt
import time
import threading
# библиотека Tkinter установлена в Python в качестве стандартного модуля
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext
import tkinter.messagebox
import tkinter.filedialog

# библиотеки requests и bs4 нужно устанавливать отдельно
import requests
from bs4 import BeautifulSoup

"""
у потоков общая память, поэтому они могут менять глобальные переменные не напрягаясь
хотя это и создает проблему целостности (или релевантности, корректности) памяти
(т.е. информации в ней)
ниже: списки - для хранения словарей, результатов работы скрапинга gismeteo,
логические переменные - флаги, устанавливаются потоком когда скрапинг завершен
"""
one_day_dict = list()
ten_days_dict = list()
one_flag = False
ten_flag = False

def one_day():
    """
    Функция потока получает данные от gismeteo для сегодняшней даты
    и для населенных пунктов, для которых url'ы перечислены в списке url,
    формирует словарь и добавляет его в конец списка one_day_dict
    """
    file = open(os.path.dirname(__file__) + "\\one.txt", "a")
    file.write(f"Start 'one' thread at {dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')}\n")
    global one_day_dict, one_flag
    url = ["https://www.gismeteo.ru/weather-chelyabinsk-4565/", \
           "https://www.gismeteo.ru/weather-bulzi-234546/"]
    headers_ = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    for city in url:
        # пауза, чтобы сайт-цель не заподозрил неладное :)
        time.sleep(0.5)
        # словарь, который будет хранить нужные данные
        result = dict()
        res_main = requests.get(city, headers = headers_)
    # создаем объект BeautifulSoup, в конструктор передаем два аргумента: строку - 
    # html-документ или результат requests.get(...) или просто python-строку 
    # и название html парсера
        soup_main = BeautifulSoup(res_main.text, "html.parser")
        result["status_code"] = res_main.status_code
        if result["status_code"] != 200:
            one_day_dict.append(result)
            continue
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
        one_day_dict.append(result)
    one_flag = True
    file.write("Finish 'one' thread...\n")
    file.close()

def ten_days():
    """
    Функция потока получает данные от gismeteo на 10 дней
    для населенных пунктов, для которых url'ы перечислены в списке url,
    формирует словарь и добавляет его в конец списка one_day_dict
    """
    file = open(os.path.dirname(__file__) + "\\ten.txt", "a")
    file.write(f"Start 'ten' thread at {dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')}\n")
    global ten_days_dict, ten_flag
    url = ["https://www.gismeteo.ru/weather-chelyabinsk-4565/10-days/", \
           "https://www.gismeteo.ru/weather-bulzi-234546/10-days/"]
    headers_ = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    for city in url:
        # пауза, чтобы сайт-цель не заподозрил неладное :)
        time.sleep(0.5)
        # словарь, который будет хранить нужные данные
        result = dict()
        res_main = requests.get(city, headers = headers_)
        # создаем объект BeautifulSoup, в конструктор передаем два аргумента: строку - 
        # html-документ или результат requests.get(...) или просто python-строку 
        # и название html парсера
        soup_main = BeautifulSoup(res_main.text, "html.parser")
        result["status_code"] = res_main.status_code
        if result["status_code"] != 200:
            ten_days_dict.append(result)
            continue
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
        ten_days_dict.append(result)
    ten_flag = True
    file.write("Finish 'ten' thread...\n")
    file.close()

class App(tk.Tk):
    global one_day_dict, ten_days_dict, one_flag, ten_flag
    # defaults settings
    X_POSITION_WINDOW = "10"
    Y_POSITION_WINDOW = "10"
    WIDTH_WINDOW  = "640"
    HEIGHT_WINDOW = "480"

    # state of main window
    state = dict()
    state["x_position_window"] = X_POSITION_WINDOW
    state["y_position_window"] = Y_POSITION_WINDOW
    state["width_window"] = WIDTH_WINDOW
    state["height_window"] = HEIGHT_WINDOW

    # цвет неактивной надписи
    fg_na = "#666666"
    # цвет активной надписи
    fg_a = "#000000"

    def __init__(self):
        super().__init__()
        one = threading.Thread(target = one_day)
        one.start()
        ten = threading.Thread(target = ten_days)
        ten.start()
        self.LoadInitialSettings()
        self.InitMainWindow()
        
        # Связь между Radiobutton устанавливается через общую переменную, разные значения которой соответствуют включению разных радиокнопок группы.
        # У всех кнопок одной группы свойство variable устанавливается в одно и то же значение – связанную с группой переменную.
        # А свойству value присваиваются разные значения этой переменной.
        # В Tkinter нельзя использовать любую переменную для хранения состояний виджетов. Для этих целей предусмотрены специальные
        # классы-переменные пакета tkinter – BooleanVar, IntVar, DoubleVar, StringVar. Первый класс позволяет принимать своим экземплярам 
        # только булевы значения (0 или 1 и True или False), второй – целые, третий – дробные, четвертый – строковые.
        self.r_var = tk.IntVar()
        self.r_var.set(0)
        
        # чтобы метка Челябинск и соответствующая Radiobutton упаковщиком воспринимались как одно
        # помещаем их на Frame со своей сеткой
        self.frame = ttk.Frame(self, width = 114)
        self.lbl_city0 = tk.Label(self.frame, font = ("Arial", 12), text = "Челябинск", fg = self.fg_a)
        self.lbl_city0.bind("<Button-1>", self.clk_Radiobutton)
        self.city0 = tk.Radiobutton(self.frame, font = ("Arial", 12), text = "", value = 0, variable = self.r_var, command = self.clk_Radiobutton)
        self.city1 = tk.Radiobutton(self.frame, font = ("Arial", 10), text = "Булзи", fg = self.fg_na, value = 1, variable = self.r_var, command = self.clk_Radiobutton)
        self.lbl_city0.grid(row = 0, column = 0)
        self.city0.grid(row = 0, column = 1)
        self.city1.grid(row = 0, column = 2)
        
        self.date = tk.Label(self, font = ("Arial", 12), text = self.date_to_russian())
        test_one_datas_text = "Данные получены" if one_flag and one_day_dict[0]["status_code"] == 200 and one_day_dict[1]["status_code"] == 200 else "Что-то не так"
        self.test_one_datas = tk.Label(self, font = ("Arial", 10, "italic"), text = test_one_datas_text)
        self.lbls_times = list()
        self.lbls_temp = list()
        self.lbls_precipitation_one = list()
        self.lbls_days = list()
        self.lbls_maxt = list()
        self.lbls_mint = list()
        self.lbls_precipitation = list()
        # создаем метки для прогнозов текущего дня
        for i in range(0, 8):
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_times.append(l)
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_temp.append(l)
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_precipitation_one.append(l)
        # создаем метки для прогнозов на 10 дней
        for i in range(0, 10):
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_days.append(l)
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_maxt.append(l)
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_mint.append(l)
            l = tk.Label(self, font = ("Arial", 12), text = "")
            self.lbls_precipitation.append(l)
        
        self.frame.grid(row = 0, column = 0)
        self.date.grid(row = 0, column = 2, pady = 10, columnspan = 4)
        self.test_one_datas.grid(row = 0, column = 8, columnspan = 3)
        for i in range(0, 8):
            self.lbls_times[i].grid(row = 1, column = i+2)
        tk.Label(self, font = ("Arial", 10), text = "Температура", justify = "left").grid(row = 2, column = 0)
        for i in range(0, 8):
            self.lbls_temp[i].grid(row = 2, column = i+2)
        tk.Label(self, font = ("Arial", 10), text = "Осадки, мм", justify = "left").grid(row = 3, column = 0)
        for i in range(0, 8):
            self.lbls_precipitation_one[i].grid(row = 3, column = i+2)
        tk.Label(self, font = ("Arial", 12), text = "Прогноз на 10 дней").grid(row = 4, column = 0, pady = 10, columnspan = 11)
        for i in range(0, 10):
            self.lbls_days[i].grid(row = 5, column = i+1)
        tk.Label(self, font = ("Arial", 10), text = " Максимальная  температура ", justify = "left").grid(row = 6, column = 0)
        for i in range(0, 10):
            self.lbls_maxt[i].grid(row = 6, column = i+1)
        tk.Label(self, font = ("Arial", 10), text = "Минимальная  температура", justify = "left").grid(row = 7, column = 0)
        for i in range(0, 10):
            self.lbls_mint[i].grid(row = 7, column = i+1)
        tk.Label(self, font = ("Arial", 10), text = "Осадки, мм", justify = "left").grid(row = 8, column = 0)
        for i in range(0, 10):
            self.lbls_precipitation[i].grid(row = 8, column = i+1)

        # вызываем функцию, которая проверяет, закончили-ли работу все потоки,
        # если да, то выводим данные на экран,
        # если нет, то опять вызываем эту же функцию через 100 мс
        self.check_threads_finished()

    def check_threads_finished(self):
        if self.is_threads_finished():
            test_one_datas_text = "Данные получены" if one_day_dict[0]["status_code"] == 200 and one_day_dict[1]["status_code"] == 200 else "Что-то не так"
            self.test_one_datas["text"] = test_one_datas_text
            self.city_datas(0)
        else:
            self.after(100, self.check_threads_finished)
    
    def is_threads_finished(self):
        return one_flag and ten_flag

    def city_datas(self, city: int = 0):
        for i in range(0, 8):
            self.lbls_times[i]["text"] = one_day_dict[city]["times"][i]
            self.lbls_temp[i]["text"] = one_day_dict[city]["temperatures"][i]
            self.lbls_precipitation_one[i]["text"] = one_day_dict[city]["precipitation"][i]
        for i in range(0, 10):
            self.lbls_days[i]["text"] = ten_days_dict[city]["days"][i]
            self.lbls_maxt[i]["text"] = ten_days_dict[city]["maxt"][i]
            self.lbls_mint[i]["text"] = ten_days_dict[city]["mint"][i]
            self.lbls_precipitation[i]["text"] = ten_days_dict[city]["precipitation"][i]

    def clk_Radiobutton(self, event = None):
        if not self.is_threads_finished():
            return
        b = self.r_var.get()
        #if type(event.widget) == tkinter.Label or b == 0:
        if event is not None or b == 0:
            self.r_var.set(0)
            self.lbl_city0["fg"] = self.fg_a
            self.lbl_city0["font"] = ("Arial", 12)
            self.city1["fg"] = self.fg_na
            self.city1["font"] = ("Arial", 10)
            self.city_datas(0)
        else:
            self.lbl_city0["fg"] = self.fg_na
            self.lbl_city0["font"] = ("Arial", 10)
            self.city1["fg"] = self.fg_a
            self.city1["font"] = ("Arial", 12)
            self.city_datas(1)

    def LoadInitialSettings(self):
        cfg = open("init.cfg")
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
        #self.resizable(False, False)
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
        conf = open("init.cfg", "w")
        conf.write("# window settings\n")
        conf.write(f"x_position_window = {self.state['x_position_window']}\n")
        conf.write(f"y_position_window = {self.state['y_position_window']}\n")
        conf.write(f"width_window  = {self.state['width_window']}\n")
        conf.write(f"height_window = {self.state['height_window']}\n")
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



if __name__ == "__main__":
    try:
        app = App()
        # бесконечный цикл окна, поэтому окно будет ждать любого взаимодействия с 
        # пользователем, пока не будет закрыто
        # Если ее не использовать, то окно сразу закроется, и пользователь ничего не увидит
        app.mainloop()
    except Exception as e:
        tk.messagebox.showerror("Ошибка", e)

