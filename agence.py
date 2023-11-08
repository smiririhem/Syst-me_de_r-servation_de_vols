import socket                    # importation de la bibliothèque socket pour la communication entre 2 processus
import sys                        # importation de la bibliothèque sys pour accéder à certaines variables et fonctions liées à l'interpréteur Python
# définition de l'adresse IP et du port du serveur
host = '192.168.1.93'
port = 2023             
import socket, sys, threading       # importation de la bibliothèque threading pour exécuter des tâches en parallèle
from tkinter import*               # importation de la bibliothèque tkinter pour créer des interfaces graphiques

# définition de la classe Agc qui hérite de la classe Thread de threading
class Agc(threading.Thread):
 
 
    verif = True   # variable de classe verif initialisée à True
    def __init__(self, conn):
 
        threading.Thread.__init__(self)
 
        self.connexion = conn           # attribut de l'objet Agc qui stocke le socket de connexion
  # méthode pour effectuer une réservation ou une annulation selon tran
    def resOannul(self,numagc,trans,nbPlace,refVol):
        msg = numagc + ' ' + str(nbPlace) + ' ' + refVol + ' ' + trans  
        self.connexion.send(msg.encode('ascii')) 
   
    # méthode pour demander la facture selon num   agence  	
    def demdFact(self,numagc):
        msg = numagc            # création du message à envoyer au serveur
        self.connexion.send(msg.encode('ascii'))    # envoi du message encodé en ASCII
        data = self.connexion.recv(1024).decode('ascii')9856    # réception de la réponse du serveur
        print(data) # affichage de la réponse
        print("succés de la reception du données")
        return 0

# création du socket de connexion
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
verif = True
# tentative de connexion au serveur  
try:
 
    connexion.connect((host, port))
 
except socket.error:
 
    print ("pas de connexion avec le serveur.")
 
    sys.exit()
 
print ("Connexion avec le serveur.")
 
 
# création d'un objet Agc qui va s'occuper des échanges avec le serveur
th_R = Agc(connexion)


 # dictionnaire qui associe à chaque option une fonction lambda correspondante
while th_R.verif:
    print("Pour faire une reservation tapez 1")
    print("Pour faire une annulation tapez 2")
    print("Pour demander la facture tapez 3")
    print("Pour quitter tapez 4")
    
    choice = input()
    
    switcher = {
        '1': lambda: th_R.resOannul('1', 'reserver', 15, '4000'),
        '2': lambda: th_R.resOannul('2', 'annuler', 5, '1000'),
        '3': lambda: th_R.demdFact('1'),
        '4': lambda: setattr(th_R, "verif", False),
    }
        # exécution de la fonction lambda correspond
    switcher.get(choice, lambda: print("\n Verifier votre choix"))()
    
    