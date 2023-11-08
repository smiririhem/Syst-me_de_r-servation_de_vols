#Importation des bibliothèques nécessaires
import threading
import time
import sys 
from socket import *
from threading import *
#Déclaration des verrous pour chaque section critique
lockVols= Lock()
lockHistorique = Lock()
lockFacture = Lock()   
#Création de la socket du serveur pour écouter les connexions des agences
server = socket(AF_INET, SOCK_STREAM)

#Définition de l'adresse IP et du port du serveur
host = '192.168.1.93'
port = 2023
adrs = (host, port)

#Attribution de l'adresse IP et du port au serveur pour qu'il puisse écouter les connexions des clients
server.bind(adrs)


def transaction(conn, adrs):
    print(f"****************AGENCE CONNECTE****************")
    while True :
            data = conn.recv(1024).decode('ascii') #écoute les données entrantes sur la connexion de socket
            
            if len(data)<2 : #demande une facture spécifique
               facture = open("facture.txt", "r")
               lockFacture.acquire() #verouillage
               all_lines = facture.readlines()
               index = 0
               for line in all_lines:
                     if line[0]  == data: #reference_agence
                           conn.send(line.encode('ascii'))   #envoi somme à payer au agence    

                           index = index + 1
                     else:
                         line="pas de facture"
                         conn.send(line.encode('ascii'))
                         
                
               facture.close()
               lockFacture.release() #deverouillage
                
            else : #demande d'anullation ou reservation : donneé >2
                l = data.split()
                numAgen = l[0]
                nbPlace = int(l[1])
                refVol= l[2]
                trans = l[3]
                print(numAgen,nbPlace,refVol,trans)
                
                vols = open("vols.txt", "r+")  #recherche de correspandance de vol     

                lockVols.acquire()

                liste = []
                print("[################COMPAGNIES DATA################]")
                index = 0
                all_lines = vols.readlines()
                for line in all_lines:
                     ref, destination, old_nb, prix = line.split()
                     if ref == refVol:
                         liste.append(ref)
                         liste.append(destination)
                         liste.append(old_nb)
                         liste.append(prix)
                         break
            
                lockVols.release()
                vols.close()
            







                if trans=='reserver':
                     if int(liste[2])>=nbPlace: #nb place demandé < dispo
                          vols = open("vols.txt", "r")
                          lockFileVols.acquire()
                          all_lines = vols.readlines()
                          index = 0
                          for line in all_lines: #lecture de toute les lignes + comparaison
                               if line[0] + line[1] + line[2] + line[3] == liste[0]:
                                    all_lines[index] = liste[0] + "        " +liste[1] + "        " + str(int(liste[2])-nbPlace  ) + "        " + liste[3] + '\n'
                               index = index + 1
                          lockFileVols.release()
                          vols.close()
                          # Mise à jour vols (nb place demandé)
                          vols = open("vols.txt", "w")
                          lockFileVols.acquire()
                          vols.writelines(all_lines)
                          lockFileVols.release()
                          vols.close()
                          # mise a jour historique
                          histo = open("histo.txt", "a")
                          lockHistorique.acquire()
                          ligne_histo = liste[0] + "        " + numAgen + "        " + trans + "        " + str(nbPlace) + "        " + "succes" 
                          histo.write(  str(ligne_histo)+"\n")
                          lockHistorique.release()
                          histo.close()
                          total =nbPlace*int(liste[3])
                          facture = open("facture.txt", "r+")

                          lockFacture.acquire()

                          liste1 = []
                
                          print("[################Données du compagnie########################]")
                          index = 0
                          for line in facture.readlines():
                              ref, total1= line.split("        ",2)
                              if ref == numAgen:
                                  liste1.append(ref)
                                  liste1.append(total1)
                                  index +=1
                                  break
                    
                          lockFacture.release()
                          facture.close()
                          facture = open("facture.txt", "r")
                          lockFacture.acquire()
                          all_lines = facture.readlines()
                          if len(liste1)!=0:
                                    all_lines[index] = liste1[0]+"        " + str(float(liste1[1])+total) +'\n'
                        
                          else :
                              all_lines.append(numAgen+"        " + str(total)+'\n')
                          lockFacture.release()
                          facture.close()
                          # MODIFIER LA FACTURE
                          facture = open("facture.txt", "w")
                          lockFacture.acquire()
                          facture.writelines(all_lines)
                          lockFacture.release()
                          facture.close()
                          
            
                     else: #  Vérifier si le vol est disponible nbPlaceDispo < nbPlace
                         # Ajouter la transaction à l'historique
                          histo = open("histo.txt", "a")
                          lockHistorique.acquire()
                          ligne_histo = liste[0] + "        " + numAgen + "        " + trans + "        " + str(nbPlace) + "        " + "impossible" 
                          histo.write(str(ligne_histo)+"\n")
                          lockHistorique.release()
                          histo.close()

                else : #annulation
                     #Lire l'historique pour calculer le nombre total de places réservées
                      s=0
                      histo = open("histo.txt", "r")
                      lockHistorique.acquire()
                      all_lines = histo.readlines()
                      for line in all_lines:
         
                            m=line.split("        ")
                           
                            
                            if m[0]==liste[0] and m[1]==numAgen and m[4][0]=="s" :        
                                if  m[2]=="reserver":
                                     s+=int(m[3])
                                else :
                                
                                     s-=int(m[3])
                                print(s) 
                            
                      lockHistorique.release()
                      histo.close()











                      if s>=nbPlace:
                      
                          vols = open("vols.txt", "r")
                          lockVols.acquire()
                          all_lines = vols.readlines()
                          index = 0
                          for line in all_lines:
                                if line[0] + line[1] + line[2] + line[3] == liste[0]:
                                    
                                    all_lines[index] = liste[0] + "        " +liste[1] + "        " + str(int(liste[2])+nbPlace  ) + "        " + liste[3] + '\n'
                                    break
                                index = index + 1
                          lockVols.release()
                          vols.close()
                       # MODIFIER LE FICHIER VOLS 
                          vols = open("vols.txt", "w")
                          lockVols.acquire()
                          vols.writelines(all_lines)
                          lockVols.release()
                          vols.close()
                        # NOTER LA MODIFICATION DANS HISTO
                          histo = open("histo.txt", "a")
                          lockHistorique.acquire()
                          ligne_histo = liste[0] + "        " + numAgen + "        " + trans + "        " + str(nbPlace) + "        " + "succes" 
                          histo.write(str(ligne_histo)+"\n")
                          lockHistorique.release()
                          histo.close() 
                          #MODIFIER LA FACTURE AUSSI
                          total =nbPlace*int(liste[3])*(-0.9)
                          facture = open("facture.txt", "r+")
                          lockFacture.acquire()
                          liste1 = []
                          index = 0
                          all_lines = facture.readlines()
                          for line in all_lines:
                              ref, total1= line.split()
                              if ref == numAgen:
                                  liste1.append(ref)
                                  liste1.append(total1)
                                  break
                              index +=1
                    
                   
                          lockFacture.release()
                          facture.close()
                
                          facture = open("facture.txt", "r")
                          lockFacture.acquire()
                          if len(liste1)!=0:
                                        all_lines[index] = liste1[0]+"        " + str(float(liste1[1])+total) +'\n'
                        
                         
                          lockFacture.release()
                          facture.close()
                        

                          facture = open("facture.txt", "w")
                          lockFacture.acquire()
                          facture.writelines(all_lines)
                          lockFacture.release()
                          facture.close() 
                        # s< nbPlace  
                      else :
                          histo = open("histo.txt", "a")
                          lockHistorique.acquire()
                          ligne_histo = liste[0] + "        " + numAgen + "        " + trans + "        " + str(nbPlace) + "        " + "impossible" 
                          histo.write(str(ligne_histo)+"\n")
                          lockHistorique.release()
                          histo.close()  
                

def start():
    while True:
        conn, adrs = server.accept()
        thread = Thread(target=transaction, args=(conn, adrs))
        thread.start()
        

def consult_historic_transactions():
    print("###########################Histrorique des transactions :########################### \n \n")
    
    histo = open("histo.txt", "r")
    all_lines = histo.readlines()
    for line in all_lines:
        print(line)
        print("------------------------------------------------------------------------\n \n \n ")
    histo.close()
    return 0








if __name__ == "__main__":          
    server.listen()
    print("####################Le serveur est prete #############\n \n ")
    ACCEPT_THREAD = Thread(target=start)
    ACCEPT_THREAD.start()
    consult_historic_transactions()
    ACCEPT_THREAD.join() 
    server.close()
