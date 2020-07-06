import pprint
import utils
import parallel

def mainSequential(savings, routenn, numVehicles, customers, customerDist,vehicleCapacity,flagLinehaul):

    #Creo la lista di routes
    routes = []
    #Clienti inseriti nelle routes
    customersInRoutes = []
    #Clienti che stanno in mezzo alla route
    middleCustomers = []

    #customersServed = []
    #print("SAVING CORRENTI")
    #p#print.p#print(savings)
    #print("CUSTOMERS CORRENTI")
    #p#print.p#print(customers)
    #Lista di clienti da servire
    customerList = []
    customerList = utils.getIdCustomer(customerList,customers)
    ##print("Lista clienti da servire: " + str(customerList))
    #flag per la creazione di una nuova route
    flagNewRoute = False


    #Ciclo finchè non ho finito di servire tutti i clienti
    while(customerList):

        #Capacità del percorso
        cap_route = 0
        #Capacità di un singolo cliente (richiesta quantità)
        delivery = 0

        #print("NUOVA ITERAZIONE")

        middleCustomers.clear()

        #Ciclo i savings
        for s in savings:
            #print()
            #print("Analizzo saving - Source: " + str(s["source"]) + " Destination: " + str(s["destination"]))
            customersInRoutes.sort()
            middleCustomers.sort()
            #print("Customers already served: " + str(customersInRoutes))
            #print("Middle customers: " + str(middleCustomers))
            #Se la lista di route è vuota o se il flag è False
            if not routes or flagNewRoute:
                #print(" Ancora nessuna routes, controllo se sono entrambi clienti da servire")
                #Forse questo if è da modificare, non lo so però
                if((s["source"] in customerList) and (s["destination"] in customerList)):
                    #print("Sono entrambi da servire")
                    #La somma di ciò che richiedono i clienti non deve essere superiore alla capacità del veicolo
                    if(utils.getDelivery(delivery, int(s["source"]), customers,flagLinehaul)+utils.getDelivery(delivery, int(s["destination"]), customers,flagLinehaul) <= vehicleCapacity):
                        #print("Ok posso aggiungere, la capacità del percorso è " + str(utils.getDelivery(delivery, int(s["source"]), customers,flagLinehaul)+utils.getDelivery(delivery, int(s["destination"]), customers,flagLinehaul)))
                        #print("Capacità rimanente veicolo " + str(vehicleCapacity-utils.getDelivery(delivery, int(s["source"]), customers,flagLinehaul)-utils.getDelivery(delivery, int(s["destination"]), customers,flagLinehaul)))
                        #Creo una nuova route e la aggiungo alla lista
                        new_route = [0, s["source"], s["destination"], 0]
                        routes.append(new_route)
                        customersInRoutes.append(s["source"])
                        customersInRoutes.append(s["destination"])
                        #Flag settato a false, così alla prossima iterazione entra nel terzo else successivo
                        flagNewRoute=False
                        ##print("Route corrente: " + str(new_route))
                        ##print(str(routes[0][1]))
                    #else:
                        #print("Supero la capacità del veicolo, devo creare un'altra route")
                #else:
                    #print("Uno dei due o entrambi sono già servitiiiiiiiiiiii")

            else:
                #Ho già una route, quindi devo vedere se analizzando il saving corrente posso aggiungere qualche altra destinazione al percorso
                foundRoute = False
                #print("Ho già una route " + str(new_route))
                cap_route = utils.getCapacityRoute(delivery, new_route, customers,flagLinehaul)
                #print("Capacità: " + str(cap_route))
                #print("Clienti da servire: " + str(customerList))

                #Ora scorro la route attuale per vedere se ho la stessa sorgente del saving per poter accodare eventualmente la destinazione alla route
                for i in range(0, len(new_route)):
                    #print()
                    #Se la sorgente è nella route
                    if new_route[i] == s["source"]:
                        #Se la destinazione non è già stata servita, se l'i-esimo elemento della route non è in mezzo alla route e se è invece coda (l'elemento successivo è lo 0)
                        if s["destination"] not in customersInRoutes and new_route[i] not in middleCustomers and new_route[i+1] == 0:
                            #print("Posso aggiungere la destinazione alla fine")
                            #Controllo se un'evetuale aggiunta del nodo mi crea problemi di capacità
                            if((cap_route + utils.getDelivery(delivery, int(s["destination"]), customers,flagLinehaul)<=vehicleCapacity)):
                                foundRoute = True
                                #print("Ok posso aggiungere, la capacità del percorso è " + str(cap_route + utils.getDelivery(delivery, int(s["destination"]),customers,flagLinehaul)))
                                #print("Capacità rimanente veicolo " + str(vehicleCapacity - cap_route - utils.getDelivery(delivery, int(s["destination"]),customers,flagLinehaul)))
                                #Aggiungo la destinazione alla route e shifto lo 0 a destra
                                middleCustomers.append(new_route[i])
                                new_route.insert(-1, s["destination"])
                                customersInRoutes.append(s["destination"])
                            #else:
                                #print("Supero il carico, non aggiungo nulla")
                        # Se la destinazione non è già stata servita, se l'i-esimo elemento della route non è in mezzo alla route e se è invece testa (l'elemento precedente è lo 0)
                        elif s["destination"] not in customersInRoutes and new_route[i] not in middleCustomers and new_route[i-1] == 0:
                            #print("Posso aggiungere la destinazione all'inizio")
                            if ((cap_route + utils.getDelivery(delivery, int(s["destination"]), customers,flagLinehaul) <= vehicleCapacity)):
                                foundRoute = True
                                #print("Ok posso aggiungere, la capacità del percorso è " + str(cap_route + utils.getDelivery(delivery, int(s["destination"]), customers,flagLinehaul)))
                                #print("Capacità rimanente veicolo " + str(vehicleCapacity - cap_route - utils.getDelivery(delivery, int(s["destination"]),customers, flagLinehaul)))
                                # Aggiungo la destinazione alla route e shifto lo 0 a destra
                                middleCustomers.append(new_route[i])
                                new_route.insert(i, s["destination"])
                                customersInRoutes.append(s["destination"])
                            #else:
                                #print("Supero il carico, non aggiungo nulla")
                        break

                    #Stessa cosa dell'if precedente, ma stavolta prendo in considerazione la sorgente
                    elif new_route[i] == s["destination"]:
                        #Se la sorgente non è già stata servita, se l'i-esimo elemento della route non è in mezzo alla route e se è invece coda (l'elemento successivo è lo 0)
                        if s["source"] not in customersInRoutes and new_route[i] not in middleCustomers and new_route[i+1] == 0:
                            #print("Posso aggiungere la sorgente alla fine")
                            #Controllo se un'evetuale aggiunta del nodo mi crea problemi di capacità
                            if((cap_route + utils.getDelivery(delivery, int(s["source"]), customers,flagLinehaul)<=vehicleCapacity)):
                                foundRoute = True
                                #print("Ok posso aggiungere, la capacità del percorso è " + str(cap_route + utils.getDelivery(delivery, int(s["source"]),customers,flagLinehaul)))
                                #print("Capacità rimanente veicolo " + str(vehicleCapacity - cap_route - utils.getDelivery(delivery, int(s["source"]),customers,flagLinehaul)))
                                #Aggiungo la destinazione alla route e shifto lo 0 a destra
                                middleCustomers.append(new_route[i])
                                new_route.insert(-1, s["source"])
                                customersInRoutes.append(s["source"])
                            #else:
                                #print("Supero il carico, non aggiungo nulla")
                        # Se la sorgente non è già stata servita, se l'i-esimo elemento della route non è in mezzo alla route e se è invece testa (l'elemento precedente è lo 0)
                        elif s["source"] not in customersInRoutes and new_route[i] not in middleCustomers and new_route[i-1] == 0:
                            #print("Posso aggiungere la sorgente all'inizio")
                            if ((cap_route + utils.getDelivery(delivery, int(s["source"]), customers,flagLinehaul) <= vehicleCapacity)):
                                foundRoute = True
                                #print("Ok posso aggiungere, la capacità del percorso è " + str(cap_route + utils.getDelivery(delivery, int(s["source"]), customers,flagLinehaul)))
                                #print("Capacità rimanente veicolo " + str(vehicleCapacity - cap_route - utils.getDelivery(delivery, int(s["source"]),customers, flagLinehaul)))
                                # Aggiungo la destinazione alla route e shifto lo 0 a destra
                                middleCustomers.append(new_route[i])
                                new_route.insert(i, s["source"])
                                customersInRoutes.append(s["source"])
                            #else:
                                #print("Supero il carico, non aggiungo nulla")
                        break


                    #elif (s["destination"] in middleCustomers or s["source"] in middleCustomers):
                        #print("Uno degli elementi già inserito")



        #Ok ora ho guardato tutti i savings e ho creato la mia route
        #print("Ho creato la route " + str(new_route))
        #print()
        #print("Clienti serviti: " + str(customersInRoutes))
        # Rimuovo dalla lista dei clienti da servire quelli che sono dentro la route e che quindi sono già serviti
        customerList = [x for x in customerList if x not in customersInRoutes]
        #print("Clienti rimasti: " + str(customerList))
        # setto questo flag a True così da poter entrare nel primo if e creare una nuova route
        flagNewRoute = True

        #Se mi rimane un solo cliente da servire e non trovo saving a cui accodarlo in testa o in coda, creo una nuova route con quel cliente

        if (len(customerList) == 1):
            #print("Solo uno da servire")
            routes.append([0,customerList[0],0])
            customersInRoutes.append(customerList[0])
            customersInRoutes.sort()
            customerList.clear()

            break

    checked = []
    i=0
    # Se ho meno route del numero di veicoli, splitto una route in due
    if (flagLinehaul):
        #if (len(routes) < numVehicles):
        while(len(routes)!=numVehicles):
            if (len(routes) < numVehicles):

                print("Bisogna splittare una route in 2")
                print(len(routes))

                # Il criterio che scelgo è quello di isolare il cliente che dista meno del deposito, creando una route [0-cliente-0]
                # ordino la lista dei clienti (solo LH) in maniera crescente, così ho il valore più piccolo all'indice 0
                customers.sort(key=lambda obj: obj["distFromDepot"], reverse=False)
                print(customers)
                if(customers[i]["id"] not in checked):
                    clientSplit = customers[i]["id"]

                    #print(clientSplit)
                    # una volta che ottengo il cliente,  tramite questo metodo ottengo la route che dovrà essere splittata
                    split_route = utils.getSplitRoute(routes, clientSplit)
                    #print("Route contenente cliente con costo minimo: " + str(split_route))

                    # Creo la prima route isolando il cliente
                    split_1 = [0, clientSplit, 0]
                    # Creo la seconda route inserendo tutti gli elementi della route originare eccetto il cliente che ho isolato prima
                    split_2 = [x for x in split_route if x != clientSplit]

                    #print()
                    #print("Liste create")
                    #print(split_1)
                    #print(split_2)

                    # Rimuovo la route vecchia e inserisco le due nuove
                    routes.remove(split_route)
                    routes.insert(0, split_1)
                    routes.insert(1, split_2)

                    #print("Route Linehaul: ")
                    #print.p#print(routes)
                i += 1


            elif (len(routes) > numVehicles):

                delivery = 0
                # il cliente si trova in mezzo alla route [0-cliente-0] che voglio eliminare
                client = routes[len(routes) - 1][1]
                # Rimuovo la route in più (l'ultima nella lista)
                routes.remove(routes[len(routes) - 1])
                # mi calcolo le capacità di ogni route, perchè voglio inserire il cliente nella route che ha più spazio
                capacity_route = []
                for r in routes:
                    capacity_route.append(utils.getCapacityRoute(delivery, r, customers, True))

                #print(capacity_route)
                # Ricavo l'indice della route con capacità minore
                index_min = capacity_route.index(min(capacity_route))
                # Uso l'indice per inserire il cliente alla fine della route
                routes[index_min].insert(len(routes[index_min]) - 1, client)


    return routes


