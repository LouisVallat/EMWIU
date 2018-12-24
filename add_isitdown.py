import sqlite3, sys, datetime, api_credentials, smtplib, os

# Usage :
# python3 add_isitdown.py -u <url> -e <email> -i <ip>

os.chdir(os.path.dirname(os.path.abspath(__file__)))
items = {"url": "", "email": "", "ip": "", "starttime": ""}

def sendMail(url, email, code):
    date = str(datetime.datetime.now())
    login = api_credentials.creds["gmail"]["user"]
    password = api_credentials.creds["gmail"]["password"]
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    subject = "EMWIU - "
    content = "Bonjour !\n\n"
    if (code == "new"):
        subject += "Confirmation de votre inscription"
        content += "Nous vous confirmons, de par ce mail, votre inscription a notre service. Nous surveillons des maintenant l'URL " + str(url) +  " !\n"
    elif (code == "old"):
        subject += "Vous etes deja inscrit..."
        content += "Nous avons trouve dans notre base de donnee que vous avez deja demande a surveiller l'URL " + url + " !\n"
        content += "Vous ne pouvez pas vous inscrire deux fois pour la meme URL. Desole !"
    content += "\n\nCordialement,\nL'API EMWIU (Email Me When It's Up!) du site https://louis-vallat.xyz."
    content += "\nMail genere le : " + date
    message = 'Subject: {}\n\n{}'.format(subject, content)
    mail.login(login, password)
    mail.sendmail(login, email, message)
    mail.quit()

for i in range(len(sys.argv)):
    if (sys.argv[i] == "-u" and items["url"] == ""):
        items["url"] = sys.argv[i+1]
    if (sys.argv[i] == "-e" and items["email"] == ""):
        items["email"] = sys.argv[i+1]
    if (sys.argv[i] == "-i" and items["ip"] == ""):
        items["ip"] = sys.argv[i+1]

if (items["url"] != "" and items["email"] != "" and items["ip"] != ""):
    items["starttime"] = str(datetime.date.today())
    conn = sqlite3.connect("API.db")
    cursor = conn.cursor()
    cursor.execute(
    "CREATE TABLE IF NOT EXISTS emwiu(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, url TEXT, email TEXT, ip TEXT, starttime TEXT)"
    )
    conn.commit()
    cursor.execute("""SELECT * FROM emwiu WHERE url = :url AND email = :email""", items)
    rows = cursor.fetchall()
    conn.close()
    if (len(rows) > 0):
        sendMail(items["url"], items["email"], "old")        
    else:
        conn = sqlite3.connect("API.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO emwiu(url, email, ip, starttime) VALUES(:url, :email, :ip, :starttime)", items)
        conn.commit()
        conn.close()
        sendMail(items["url"], items["email"], "new") 
else:
    print("Not enough arguments.")

