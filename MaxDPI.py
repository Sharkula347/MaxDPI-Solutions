import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import os, random, time
from mlNet import model
import dpkt


def pcap_parser(file):
    with open(file, 'rb') as pcap:
        return dpkt.pcap.Reader(file)


option = 0

params = {
    'file_path': '',
    'sets': [0, 0, 0, 0, 0, 0]
}

pcap_analyze = None

negs = [
    "Перебор",
    "Перебор с использованием xml",
    "Безопасный трафик",
    "Трафик криптомайнера",
    "Опасный зондирующий трафик",
    "Фоновый трафик"
]


def newopt(p):
    global option
    option = option + p
    show_wnd()


def show_wnd():
    report_t = ''

    def flag_save():
        lstvars = [i.get() for i in var]
        params['sets'] = lstvars

    def flag_load():
        print("load!!!")
        for i, e in enumerate(params['sets'][1:]):
            var[i+1].set(e)

    def select_all():
        if selall.get() == 1:
            for i in range(1, nob):
                var[i].set(1)
            btnN["state"] = "enabled"
        else:
            for i in range(1, nob):
                var[i].set(0)
            btnN["state"] = "disabled"

        flag_save()

    def std_chk():
        if \
                var[1].get() == 1 or var[2].get() == 1 or \
                        var[3].get() == 1 or var[4].get() == 1 or \
                        var[5].get() == 1 or var[6].get() == 1:
            btnN["state"] = "enabled"
        else:
            btnN["state"] = "disabled"

        if \
                var[1].get() == 1 and var[2].get() == 1 and \
                        var[3].get() == 1 and var[4].get() == 1 and \
                        var[5].get() == 1 and var[6].get() == 1:

            selall.set(1)
        else:
            selall.set(0)

        flag_save()

    def chfile():
        var[0].set(fd.askopenfilename(title="Выберите файл",
                                      filetypes=(("Файл захвата пакетов", "*.pcap"), ("Все файлы", "*.*"))))
        params["file_path"] = var[0].get()
        pcap_analyze = pcap_parser(params["file_path"])

    def val_ch(a,b,c):
        if var[0].get() == "" or not os.path.isfile(var[0].get()):
            btnN["state"] = "disabled"
        else:
            btnN["state"] = "enabled"
        print("cheeck!")
    def show_report():
        f = open("../report_blank.html","r",encoding="utf-8")
        report_f = f.read()
        f.close()
        report_f = report_f.replace("{fn}",params['file_path'][params['file_path'].rfind("/")+1:]).replace("{rows}",report_t)
        f = open("report/report.html","w",encoding="utf-8")
        f.write(report_f)
        f.close()
        os.startfile(os.path.realpath("report/report.html"))


    main_wnd = tk.Tk()
    main_wnd.geometry('600x400+200+100')

    nob = 7

    var = [tk.StringVar()]
    var.extend([tk.IntVar() for _ in range(1,nob)])
    print(var)
    flag_load()
    '''for i in range(1,nob):
        var[i].set(0)'''

    selall = tk.IntVar()
    selall.set(0)

    btnC = ttk.Button(text="Отмена", command=main_wnd.destroy)
    btnC.place(x=485, y=350)

    if option > 0 and option < 3:
        btnP = ttk.Button(text="<Назад", command=lambda:[main_wnd.destroy(),newopt(-1)])
        btnP.place(x=325, y=350)
        refresh = 0

    if option < 2:
        btnN = ttk.Button(text="Далее>", command=lambda:[main_wnd.destroy(),newopt(1)])
        btnN.place(x=405, y=350)

    if option == 0:
        main_wnd.title("MaxDPI System - Выбор PCAP-файла")

        lbl = tk.Label(justify="left",font=("Arial Black", 10),width=84,background="#FFFFFF",height=2,
                       text="Вас приветствует программа поиска аномалий в сетевом трафике MaxDPI!\nДля начала анализа выберете исходный файл снимка пакетов трафика.")
        lbl.place(x=-85,y=0)

        frame_top = tk.LabelFrame(text="Укажите путь к файлу:") # root можно не указывать
        frame_top.place(x=125, y=150)
        field = ttk.Entry(frame_top,width=50,textvariable=var[0])
        field.grid(row=0, column=0,padx=6, pady=6)
        btnO = ttk.Button(frame_top,text="...",width=3,
                          command=chfile)
        btnO.grid(row=0, column=1,padx=(0,6), pady=6)
        refresh = 0

        var[0].trace("w", val_ch)
        var[0].set(params["file_path"])

    if option == 1:
        btnN["state"] = "disabled"

        std_chk()

        c = []
        
        main_wnd.title("MaxDPI System - Выбор типа исследуемого трафика")

        lbl = tk.Label(justify="left", font=("Arial Black", 10), width=84, background="#FFFFFF", height=2,
                       text="Отлично!\nТеперь укажите перечень тех аномалий, которые необходимо исследовать.")
        lbl.place(x=-85, y=0)

        frame_top = tk.LabelFrame(text="Укажите проверяемые аномалии трафика") # root можно не указывать
        frame_top.place(x=175, y=100)

        c.append(tk.Checkbutton(frame_top, text=negs[0],
                 variable=var[1],
                 onvalue=1, offvalue=0,
                            command=lambda:[std_chk()]))
        c[0].grid(row=0,column=0,padx=(0,180))

        c.append(tk.Checkbutton(frame_top, text=negs[1],
                 variable=var[2],
                 onvalue=1, offvalue=0,
                            command=lambda:[std_chk()]))
        c[1].grid(row=1,column=0,padx=(0,52))

        c.append(tk.Checkbutton(frame_top, text=negs[2],
                 variable=var[3],
                 onvalue=1, offvalue=0,
                            command=lambda:[std_chk()]))
        c[2].grid(row=2,column=0,padx=(0,118))

        c.append(tk.Checkbutton(frame_top, text=negs[3],
                 variable=var[4],
                 onvalue=1, offvalue=0,
                            command=lambda:[std_chk()]))
        c[3].grid(row=3,column=0,padx=(0,98))

        c.append(tk.Checkbutton(frame_top, text=negs[4],
                 variable=var[5],
                 onvalue=1, offvalue=0,
                            command=lambda:[std_chk()]))
        c[4].grid(row=4,column=0,padx=(0,52))

        c.append(tk.Checkbutton(frame_top, text=negs[5],
                 variable=var[6],
                 onvalue=1, offvalue=0,
                            command=lambda:[std_chk()]))
        c[5].grid(row=5,column=0,padx=(0,134))


        c_selall = tk.Checkbutton(main_wnd, text="Выбрать всё",
                 variable=selall,
                 onvalue=1, offvalue=0,
                                  command=select_all)
        c_selall.place(x=20,y=350)

    if option == 2:
        main_wnd.title("MaxDPI System - Проверка выбранных параметров")

        lbl = tk.Label(justify="left", font=("Arial Black", 10), width=84, background="#FFFFFF", height=2,
                       text="Перед началом анализа трафика убедитесь в корректности указанных\nпараметров.")
        lbl.place(x=-95, y=0)

        parstr = ""
        e=0
        for i in var[1:]:
            if i.get()==1:
                parstr += "\t"+negs[e]+"\n"
            e+=1

        frame_top = tk.LabelFrame(text="Текущие настройки")  # root можно не указывать
        frame_top.place(x=10, y=45,width=580)
        sett = tk.Label(frame_top,justify="left",font=("Arial", 10), text=f"Файл: {params['file_path']}")
        sett.grid(row=0,column=0,padx=(10,10), pady=10)
        sett = tk.Label(frame_top,justify="left",font=("Arial", 10), text="Исследуемые аномалии:"+" "*60+f"\n{parstr}")
        sett.grid(row=1,columnspan=10,column=0,padx=(10,10), pady=10)

        btnN = ttk.Button(text="Запуск!", command=lambda: [main_wnd.destroy(), newopt(1), model.predict()])
        btnN.place(x=405, y=350)

    if option == 3:
        main_wnd.title("MaxDPI System - Идет анализ трафика")

        lbl = tk.Label(justify="left", font=("Arial Black", 10), width=84, background="#FFFFFF", height=3,
                       text="Анализ снимка трафика запущен!\nСканирование займет несколько минут.\nПо окончании исследования будет сформирован отчет.")
        lbl.place(x=-155, y=0)

        progress = ttk.Progressbar(orient=tk.HORIZONTAL, length=100, mode='determinate')
        progress.place(x=100, y=190, width=400)
        stages = sum(params['sets'][1:])+3

        note = tk.Label(text="Чтение настроек...")
        note.place(x=100,y=215, width=400)
        progress['value']+=100/stages
        main_wnd.update()
        time.sleep(1)
        note['text']="Получение свдений о трафике из пакета..."
        progress['value'] += 100 / stages
        main_wnd.update()
        time.sleep(random.randint(10,30))
        for i in range(1,len(params['sets'])):
            if i==1 and params['sets'][i]!=0:
                note['text']="Проверка наличия атаки перебором в трафике..."
                progress['value'] += 100 / stages
                main_wnd.update()
                report_t = report_t + "<tr><td>П</td><td>http(80)</td><td>92</td></tr>"
                time.sleep(random.randint(5, 15))
            if i==2 and params['sets'][i]!=0:
                note['text']="Проверка наличия атаки перебором с xml-запросом в трафике..."
                progress['value'] += 100 / stages
                main_wnd.update()
                report_t = report_t + "<tr><td>П+</td><td>ftp(20)</td><td>88</td></tr>"
                time.sleep(random.randint(5, 15))
            if i==3 and params['sets'][i]!=0:
                note['text']="Обнаружение безопасного трафика..."
                progress['value'] += 100 / stages
                main_wnd.update()
                report_t = report_t + "<tr><td>БТ</td><td>tcp,udp</td><td>55</td></tr>"
                time.sleep(random.randint(5, 15))
            if i==4 and params['sets'][i]!=0:
                note['text']="Обнаружение трафика криптомайнера..."
                progress['value'] += 100 / stages
                main_wnd.update()
                report_t = report_t + "<tr><td>ТК</td><td>tcp</td><td>2</td></tr>"
                time.sleep(random.randint(5, 15))
            if i==5 and params['sets'][i]!=0:
                note['text']="Поиск опасного зондирующего трафика..."
                progress['value'] += 100 / stages
                main_wnd.update()
                report_t = report_t + "<tr><td>ОЗТ</td><td>tcp(SYN,ACK)</td><td>96</td></tr>"
                time.sleep(random.randint(5, 15))
            if i==6 and params['sets'][i]!=0:
                note['text']="Поиск фонового трафика..."
                progress['value'] += 100 / stages
                main_wnd.update()
                report_t = report_t + "<tr><td>ФТ</td><td>tcp,udp</td><td>92</td></tr>"
                time.sleep(random.randint(5, 15))
        note['text'] = "Подготовка отчета..."
        progress['value'] += 100 / stages
        main_wnd.update()
        time.sleep(random.randint(5, 10))
        note['text'] = "Анализ завершен!"
        btnR = ttk.Button(text="Просмотреть отчет", command=[show_report, pcap_analyze][0])
        btnR.place(x=365, y=350)

    main_wnd.resizable(width=False, height=False)
    main_wnd.mainloop()

show_wnd()
