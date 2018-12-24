import requests
import time
import sqlite3
import datetime
import api_credentials
import smtplib
import os

updateDelay = 5*60
maxDaysOldRequest = 100


def init():
    """
        Initialize the program.
    """
    print("[i] Initialization started.")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    conn = sqlite3.connect("API.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS emwiu(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, url TEXT, email TEXT, ip TEXT, starttime TEXT)"
    )
    # emwiu (stands for "email me when it's up"):
    # | id | url | email | ip | starttime |
    conn.commit()
    conn.close()
    print("[i] Initialization done.")


def scanTheDatabase():
    """
        This is the main loop in the program :
        It :
            - scans the database
            - checks website's status
            - removes old users and notify them
            - notifies the ones who have their website up 
    """
    print("[i] Main loop engaged.")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    while True:
        conn = sqlite3.connect("API.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM emwiu""")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            checkResults = checkWebsite(row[1])
            if checkResults != False:
                sendMail(row, checkResults)
                deleteFromDatabase(row[0])
            else:
                if tooOldRequest(row[4]):
                    sendMail(row, "old")
                    deleteFromDatabase(row[0])
        time.sleep(updateDelay)
        

def sendMail(row, checkResults):
    """
        Notifies the user about something important.
    """
    print("[i] Sending the email.")
    date = str(datetime.datetime.now())
    login = api_credentials.creds["gmail"]["user"]
    password = api_credentials.creds["gmail"]["password"]
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    subject = "EMWIU - "
    content = "Bonjour !\n\n"
    if (checkResults != "old"):
        subject += "Le site est en ligne !"
        content += "Le site " + \
            row[1] + " que vous nous avez demande de surveiller est visiblement en ligne !\n"
        content += "Sa reponse a ete le code : " + str(checkResults) + " !"
    else:
        subject += "Ce n'est qu'un au revoir..."
        content += "Nous contactons pour vous annoncer une mauvaise nouvelle...\n"
        content += "Cela fait maintenant 100 jours que vous avez demande a avoir des nouvelles du site " + \
            row[1] + ", et toujours pas de nouvelles aujourd'hui...\n"
        content += "Nous devons faire un nettoyage regulier de notre Base de Donnee pour s'assurer que l'API ne souffre d'aucun ralentissement.\n"
        content += "C'est donc pour cette raison que vous en avez ete retire automatiquement. Vous pouvez tout de meme vous reinscrire !"
    content += "\n\nCordialement,\nL'API EMWIU (Email Me When It's Up!) du site https://louis-vallat.xyz."
    content += "\nMail genere le : " + date
    message = 'Subject: {}\n\n{}'.format(subject, content)
    mail.login(login, password)
    mail.sendmail(login, row[2], message)
    mail.quit()
    print("[i] E-mail sent.")


def deleteFromDatabase(rowId):
    """
        Delete a row from the database based on its id.
    """
    print("[i] Deleting a row from database.")
    conn = sqlite3.connect("API.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emwiu WHERE id =?", (rowId, ))
    conn.commit()
    conn.close()
    print("[i] Row deleted.")


def checkWebsite(url):
    """
        Checks if a website is up based on its URL.
        Return False if the website is down, the request code if it's up.
    """
    try:
        r = requests.get(str(url))
        return r.status_code
    except requests.exceptions.ConnectionError:
        return False


def dropTabe():
    """
        Drop the table.
    """
    print("[i] Dropping table.")
    conn = sqlite3.connect("API.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE emwiu")
    conn.commit()
    conn.close()
    print("[i] Table dropped.")


def tooOldRequest(requestDate):
    """
        Check if the age of a request
    """
    todaysDate = datetime.datetime.strptime(
        str(datetime.date.today()), "%Y-%m-%d")
    requestDate = datetime.datetime.strptime(str(requestDate), "%Y-%m-%d")
    return (abs((todaysDate - requestDate).days) >= maxDaysOldRequest)


init()
scanTheDatabase()
