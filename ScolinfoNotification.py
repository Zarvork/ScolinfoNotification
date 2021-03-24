import platform
import time
from selenium import webdriver
import smtplib
import ssl
import os
from notify_run import Notify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
notify = Notify()
try:
    data_user = open("data.txt", "r")
except:
    notify.register()
    url_notify = str(notify.info())
    print("Veuillez vous abonner a cette page pour recevoir les notifications sur votre téléphone :" +  url_notify[45:103])
    identifiant = str(input("Entrez votre identifiant :"))
    mdp = str(input("Entrez votre mot de passe :"))
    email_receiver = str(input("Entrez votre adresse mail :"))
    choix_save = str(input("Etes vous sur(sauvegarde)? :"))
    if "yes" in choix_save:
        data_user = open("data.txt", "x")
        data_user.writelines([identifiant,"\n",mdp,"\n",email_receiver])
        data_user.close()
        is_there_data= True
    if "no" in choix_save:
        print("ok")
        is_there_data= False
else:
    changement_compte = str(input("Vous voulez changer de compte ?"))
    if "yes" in changement_compte:
        identifiant = str(input("Entrez votre identifiant :"))
        mdp = str(input("Entrez votre mot de passe :"))
        email_receiver = str(input("Entrez votre adresse mail :"))
        choix_save = str(input("Etes vous sur(sauvegarde)? :"))
        if "yes" in choix_save:
            data_user = open("data.txt", "w")
            data_user.writelines([identifiant,"\n",mdp,"\n",email_receiver])
            data_user.close()
        if "no" in choix_save:
            while "yes" not in choix_save:
                identifiant = str(input("Entrez votre identifiant :"))
                mdp = str(input("Entrez votre mot de passe :"))
                email_receiver = str(input("Entrez votre adresse mail :"))
                choix_save = str(input("Etes vous sur(sauvegarde)? :"))
        data_user = open("data.txt", "w")
        data_user.writelines([identifiant,"\n",mdp,"\n",email_receiver])
        data_user.close()
        is_there_data= True
first_execution = 0
if is_there_data != False:
    data_user = open("data.txt", "r")
    lignes = data_user.readlines()
    identifiant = lignes[0].rstrip()
    mdp = lignes[1].rstrip()
    email_receiver = lignes[2].rstrip()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(executable_path=r'chromedriver.exe', options=options)  #Optional argument, if not specified will search path.
browser.set_window_size(1366, 768)
browser.get("https://www.scolinfo.net/Default.aspx")
browser.find_element_by_id("LoginControl_UserName").send_keys(identifiant)
browser.find_element_by_id("LoginControl_Password").send_keys(mdp)
browser.find_element_by_id("LoginControl_LoginButton").click()
time.sleep(5)
html = browser.page_source
if 'Vie Scolaire' in html:
    print("Vous etes connecté ! ")
else:
    print("Erreur identifiant ou mot de passe")
while True:
    scrap_data = ""
    browser.get("https://www.scolinfo.net/Eleve/ConsultationReleve.aspx")
    notes = browser.find_elements_by_class_name("etendue")
    moyenne = browser.find_elements_by_class_name("cel-moyenne")
    nom_professeur = browser.find_elements_by_css_selector('td.alt')
    matière = browser.find_elements_by_xpath("//td[@style = 'width:200px;']")
    time.sleep(5)
    for f in range(0,10):
        if moyenne[f].text !="":
            scrap_data = scrap_data+ matière[f].text + " " + nom_professeur[f].text + " moyenne : " + moyenne[f].text + " notes : " + notes[f].text + '\n'
    if first_execution==0:
        scrap_data_for_comparison = scrap_data
    if first_execution ==1 and scrap_data_for_comparison!= scrap_data:
        notify.send('Des nouvelles sur Scolinfo !', 'https://www.scolinfo.net/Eleve/ConsultationReleve.aspx')
        email_address = 'alertejvc@gmail.com'
        email_password = '3TW5qx2cW'
        smtp_address = 'smtp.gmail.com'
        smtp_port = 465
        # on crée un e-mail
        message = MIMEMultipart("alternative")
        # on ajoute un sujet
        message["Subject"] = "News Scolinfo"
        # un émetteur
        message["From"] = email_address
        # un destinataire
        message["To"] = email_receiver
        # on crée un texte et sa version HTML
        # on crée deux éléments MIMEText 
        texte_mime = MIMEText(scrap_data.encode('utf-8'), _charset='utf-8')
        # on attache ces deux éléments 
        message.attach(texte_mime)
        # on crée la connexion
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            # connexion au compte
            server.login(email_address, email_password)
            # envoi du mail
            server.sendmail(email_address, email_receiver, message.as_string())
        scrap_data_for_comparison = scrap_data
    first_execution=1
    time.sleep(60)
