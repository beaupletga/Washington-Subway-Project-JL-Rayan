#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter
import pickle
import ttk
import glob
from Tkinter import *
import PIL
from PIL import ImageTk, Image
import httplib, urllib, base64
from scipy import *
import networkx as nx
import numpy as np
from lxml import etree
import xml.etree.ElementTree as ET

global api_key
api_key='6b700f7ea9db408e9745c207da7ca827'

global thedata
thedata = np.genfromtxt(
'tab.csv',           # file name
skip_header=0,          # lines to skip at the top
skip_footer=0,          # lines to skip at the bottom
delimiter=',',          # column delimiter
dtype='float32',        # data type
filling_values=0)

window = Tk()

l= PanedWindow(window, orient=VERTICAL)
c= PanedWindow(window, orient=VERTICAL)
r=PanedWindow(window, orient=VERTICAL)
l.pack(side=LEFT, fill=BOTH, pady=2, padx=2)
r.pack(side=RIGHT,expand=N, fill=BOTH, pady=2, padx=2)
c.pack(side=RIGHT,expand=Y, fill=BOTH, pady=2, padx=2)

global liste_stations,liste_code_stations
liste_code_stations=[]
liste_stations=[]
headers = {'api_key': api_key}
try:
    conn = httplib.HTTPSConnection('api.wmata.com')
    conn.request("GET", "/Rail.svc/Stations?", "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    root=ET.fromstring(data)
    #print data

    premier=root[0]
    for i in range(0,len(premier)):
        tmp=premier[i]
        liste_code_stations.append(tmp[1].text)
        liste_stations.append(tmp[8].text)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))


def afficher_carte():
    image = Image.open("map2.png").resize((1000,900))
    photo = ImageTk.PhotoImage(image)

    canvas = Canvas(r, width = image.size[0], height = image.size[1])
    canvas.create_image(0,0, anchor = NW, image=photo)
    canvas.grid()
    window.mainloop()

def get_code_from_name(name):
    for i in range(0,len(liste_stations)):
        if (liste_stations[i]==name):
            return liste_code_stations[i]

def temps_entre_deux_stations(station1,station2):
    headers = {'api_key': api_key,}
    params = urllib.urlencode({'FromStationCode': station1,'ToStationCode': station2,})
    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/Rail.svc/SrcStationToDstStationInfo?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        #print data

        root=ET.fromstring(data)
        #child=root.find('.//RailTime')
        caca=root[0]
        deux=caca[0]
        quatre=deux[3].text
        return quatre
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_indice(liste,arret):
    for i in range(0,len(liste)):
        if (liste[i]==arret):
            return i


def affecter_matrice(station1,station2,tab,liste):
    temps=temps_entre_deux_stations(station1,station2)
    indice_station1=get_indice(liste,station1)
    indice_station2=get_indice(liste,station2)
    tab[indice_station1][indice_station2]=temps
    print "1"


def definir_graphe(station1,station2,liste):
    headers = {'api_key': api_key,}
    params = urllib.urlencode({'FromStationCode': station1,'ToStationCode': station2,})

    try:
        conn = httplib.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/Rail.svc/Path?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        root=ET.fromstring(data)
        premier=root[0]
        for i in range(0,len(premier)):
            deux=premier[i]
            quatre=deux[4].text
            liste.append(quatre)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))



def symetrique(tab):
    for i in range(0,len(tab)):
        for j in range(0,len(tab)):
            if (tab[j][i]!=0 and tab[i][j]==0):
                tab[i][j]=tab[j][i]
            if (tab[i][j]!=0 and tab[j][i]==0):
                tab[j][i]=tab[i][j]
            if (tab[i][j]!=0 and tab[j][i]!=0):
                if (tab[i][j]>tab[j][i]):
                    tab[i][j]=tab[j][i]
                else:
                    tab[j][i]=tab[i][j]



def envoyer(liste1,liste2,liste3,liste4,liste5,liste6):
    definir_graphe('N06','G05',liste1)
    definir_graphe('B11','A15',liste2)
    definir_graphe('K08','D13',liste3)
    definir_graphe('G05','J03',liste4)
    definir_graphe('C15','E06',liste5)
    definir_graphe('E10','F11',liste6)

global tab

def define():
    dimension=len(liste_stations)
    tab=zeros((dimension, dimension))
    liste1=[]#SV
    liste2=[]#RD
    liste3=[]#OR
    liste4=[]#BL
    liste5=[]#YL
    liste6=[]#GR
    envoyer(liste1,liste2,liste3,liste4,liste5,liste6)
    for i in range(0,len(liste1)-1):
        tmp1=get_code_from_name(liste1[i])
        tmp2=get_code_from_name(liste1[i+1])
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste2)-1):
        tmp1=get_code_from_name(liste2[i])
        tmp2=get_code_from_name(liste2[i+1])
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste3)-1):
        tmp1=get_code_from_name(liste3[i])
        tmp2=get_code_from_name(liste3[i+1])
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste4)-1):
        tmp1=get_code_from_name(liste4[i])
        tmp2=get_code_from_name(liste4[i+1])
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste5)-1):
        tmp1=get_code_from_name(liste5[i])
        tmp2=get_code_from_name(liste5[i+1])
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    for i in range(0,len(liste6)-1):
        tmp1=get_code_from_name(liste6[i])
        tmp2=get_code_from_name(liste6[i+1])
        affecter_matrice(tmp1,tmp2,tab,liste_code_stations)

    symetrique(tab)


    np.savetxt(
    'tab.csv',           # file name
    tab,                # array to save
    fmt='%.2f',             # formatting, 2 digits in this case
    delimiter=',',          # column delimiter
    newline='\n',           # new line character
    footer='end of file',   # file footer
    comments='# ',          # character to use for comments
    header='Data generated by numpy')

def affichage_trajet():
    liste_stations_tmp=[]
    liste_stations_tmp=liste_stations
    var1= saisir1.get()
    var2= saisir2.get()
    var3= saisir3.get()
    try :
        bb=get_indice(liste_stations,var3)
        del liste_stations_tmp[bb]
        M=np.delete(thedata, bb, 0)
        N=np.delete(M, bb, 1)
        G = nx.from_numpy_matrix(N, create_using=nx.DiGraph())
        cc=get_indice(liste_stations,var2)
        dd=get_indice(liste_stations,var1)
        resultat=nx.dijkstra_path(G, dd, cc)
        Label(c,text="Numéros").grid(row=0,column=0)
        Label(c,text="Stations").grid(row=0,column=1)
        compteur2=0
        for i in resultat:
            compteur2+=1
            Label(c,text=compteur2).grid(row=compteur2+1,column=0)
            Label(c,text=liste_stations[i]).grid(row=compteur2+1,column=1)
        a=nx.dijkstra_path_length(G,dd,cc)
        Label(c,text="Temps mis :",font=("Helvetica", 16),fg="red").grid(row=compteur2+2,column=0)
        Label(c,text=a,font=("Helvetica", 16),fg="red").grid(row=compteur2+2,column=1)
        Label(c,text="min",font=("Helvetica", 16),fg="red").grid(row=compteur2+2,column=2)
    except:
        Label(c,text="Mauvaise saisie",fg="green").grid()


def trajet_bis():
    global saisir1,saisir2,saisir3
    saisir1=StringVar() # prevoir la variable pour recevoir le texte saisi
    saisir2=StringVar() # prevoir la variable pour recevoir le texte saisi
    saisir3=StringVar() # prevoir la variable pour recevoir le texte saisi
    saisir1.set("Entrez Départ")
    saisir2.set("Entrez arrivé")
    saisir3.set("Saisir l'arret à éviter")
    saisie1=Entry(l,textvariable=saisir1, width=50,justify=CENTER).pack()
    saisie2=Entry(l,textvariable=saisir2, width=50,justify=CENTER).pack()
    saisie3=Entry(l,textvariable=saisir3, width=50,justify=CENTER).pack()
    valider=Button(l,text='OK',command=affichage_trajet).pack()


compteur=0
def determiner_trajet(evt):
    global var1,var2
    global compteur
    compteur+=1
    try:
        i=l1.curselection()  ## Récupération de l'index de l'élément sélectionné
        var1= l1.get(i)  ## On retourne l'élément (un string) sélectionné
    except:
        i=l2.curselection()  ## Récupération de l'index de l'élément sélectionné
        var2=l2.get(i)
        G = nx.from_numpy_matrix(thedata, create_using=nx.DiGraph())
        var1_int=get_indice(liste_stations,var1)
        var2_int=get_indice(liste_stations,var2)
        resultat=nx.dijkstra_path(G, var1_int, var2_int)
        Label(c,text="Numéros").grid(row=0,column=0)
        Label(c,text="Stations").grid(row=0,column=1)
        compteur2=0
        for i in resultat:
            compteur2+=1
            Label(c,text=compteur2).grid(row=i+1,column=0)
            Label(c,text=liste_stations[i]).grid(row=i+1,column=1)
        a=nx.dijkstra_path_length(G,var1_int,var2_int)
        Label(c,text="Temps mis :",font=("Helvetica", 16),fg="red").grid(row=i+2,column=0)
        Label(c,text=a,font=("Helvetica", 16),fg="red").grid(row=i+2,column=1)
        Label(c,text="min",font=("Helvetica", 16),fg="red").grid(row=i+2,column=2)
        window.mainloop()

def trajet():
    global l1,l2
    liste_stations_tmp=[]
    liste_stations_tmp=liste_stations
    liste_stations_tmp.sort()
    compteur=0
    f1 = Frame(l)
    s1 = Scrollbar(f1)
    l1 = Listbox(f1)
    l1.bind('<ButtonRelease-1>',determiner_trajet)

    s2 = Scrollbar(f1)
    l2= Listbox(f1)
    l2.bind('<ButtonRelease-1>',determiner_trajet)
    for user in liste_stations:
        compteur+=1
        l1.insert(compteur, user)
        l2.insert(compteur, user)
    s1.config(command = l1.yview)
    l1.config(yscrollcommand = s1.set)
    l1.pack(side = LEFT, fill = Y)
    s1.pack(side = RIGHT, fill = Y)

    s2.config(command = l2.yview)
    l2.config(yscrollcommand = s2.set)
    l2.pack(side = LEFT, fill = Y)
    s2.pack(side = RIGHT, fill = Y)
    f1.pack()



def boutons():
    bouton3=Button(l, text="Construire le graphe",command=define,bd=5)
    bouton4=Button(l, text="Afficher la carte",command=afficher_carte,bd=5)
    bouton2=Button(l, text="Trouver itinéraire",command=trajet,bd=5)
    bouton5=Button(l, text="Trouver itinéraire bis",command=trajet_bis,bd=5)
    bouton2.pack()
    bouton5.pack()
    bouton3.pack()
    bouton4.pack()
    window.mainloop()

def changer():
    api_key= e.get()

def changer_api():
    global e
    seconde=Tk()
    window.title("API")
    window.configure(background='grey')
    Label(seconde, text="API-key").grid(row=0)
    e = Entry(seconde).grid(row=0,column=1)
    b = Button(seconde, text="Valider", width=10, command=changer).grid(row=0,column=2)
    seconde.mainloop()

def about():
    about=Tk()
    about.title("Help")
    texte="Version Alpha\r Distributeurs : Mendes Ryan - Ezvan Jean-Loup  \rMails:mendesryan@eisti.eu - ezvanjeanl@eisti.eu"
    label = Label(about, text=texte)
    label.pack()


menubar = Menu(window)
menu1=Menu(menubar)
menu1.add_command(label="API_Key",command=changer_api)
menu1.add_command(label="Exit",command=window.quit)

menu2=Menu(menubar)
menu2.add_command(label="About",command=about)

menubar.add_cascade(label="File",menu=menu1)
menubar.add_cascade(label="Help",menu=menu2)
window.config(menu = menubar)

window.title("Metro")
window.geometry("1920x1920")
window.configure(background='grey')

boutons()
