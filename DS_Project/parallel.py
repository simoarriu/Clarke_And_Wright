import pprint

# Funzione da richiamare dal main. Genera le due route LH e BH.
def mainParallel(pack):

    # Parallel saving: si parte dall'inizio della lista di saving (ordinata).
    # Prendo il primo saving e lo metto nelle routes come 0-i-j-0 dove
    # i e j sono i due indici del saving. Poi proseguo con gli altri: se trovo
    # un saving che contiene la "coda" del saving appena salvato (cioè j) allora
    # lo unisco al saving esistente (ottenenendo 0-i-j-k-0 dove k è l'indice
    # dell'ultimo saving controllato). Se contiene la testa (cioè i) vado avanti.
    # Se invece non contiene nè testa nè coda vado a creare una nuova route con
    # i valori di quel saving (ottenendo 0-k-l-0 dove k e l sono gli indici del
    # nuovo saving).

    # Riprendo i dati dal pack

    savings = pack["savings"]
    LH_savings = pack["LH_savings"]
    BH_savings = pack["BH_savings"]
    numCustomers = pack["numCustomers"]
    numVehicles = pack["numVehicles"]
    vehicleCapacity = pack["vehicleCapacity"]
    customers = pack["customers"]
    customerDist = pack["customerDist"]

    # Mi prendo il numero di clienti LH e clienti BH

    numLH, numBH = getNumberLH_BH(customers)

    # Creo la lista di routes

    LH_routes = getRoutes({
        "savings": LH_savings,
        "numCustomers": numLH,
        "numVehicles": numVehicles,
        "vehicleCapacity": vehicleCapacity,
        "customers": customers
    }, 1)
    BH_routes = getRoutes({
        "savings": BH_savings,
        "numCustomers": numBH,
        "numVehicles": numVehicles,
        "vehicleCapacity": vehicleCapacity,
        "customers": customers
    }, 2)

    print("\nLH ROUTES: ")
    pprint.pprint(LH_routes)
    print("\nBH ROUTES: ")
    pprint.pprint(BH_routes)

    if len(LH_routes) <= numVehicles:
        print("\nLH routes numero giusto")
    else:
        print("\nLH routes numero errato")

    print("\nCost of LH routes: " + str(getRoutesCosts(LH_routes, customers, customerDist)))
    print("\nCost of BH routes: " + str(getRoutesCosts(BH_routes, customers, customerDist)))

    print("\nTotal cost of LH routes: " + str(getTotalCost(getRoutesCosts(LH_routes, customers, customerDist))))

    print("\nCapacity of LH routes: " + str(getRoutesCapacities(LH_routes, customers, 1)))
    print("\nCapacity of BH routes: " + str(getRoutesCapacities(BH_routes, customers, 2)))

    return LH_routes, BH_routes

# Funzione principale per la creazione della route, che scorre
# i savings e li inserisce nelle routes tramite vari controlli
def getRoutes(pack, flag):
    # Il parametro flag lo uso per capire se sto calcolando le routes
    # per i Linehaul o per i Bachkaul. Se flag è uguale a 1 vuol dire
    # LH, se uguale a 2 vuol dire BH. Potrei usare il valore zero per
    # indicare la creazione di routes unite LH-BH ma lo lascio per dopo.

    savings = pack["savings"]
    numCustomers = pack["numCustomers"]
    vehicleCapacity = pack["vehicleCapacity"]
    numVehicles = pack["numVehicles"]
    customers = pack["customers"]

    routes = []

    # La variabile servedCustomers è una lista, ogni volta che inserisco un
    # nodo nelle routes lo aggiungo a questa lista in modo da tenere traccia
    # di quelli che ho aggiunto.
    servedCustomers = []

    for saving in savings:
        servedCustomers.sort()
        print("\nSaving: s - " + str(saving["source"]) + "  d - " + str(saving["destination"]) + "\n")
        # Se non abbiamo ancora ruotes
        if not routes:
            # Se l'aggiunta dei due clienti non eccede la capacità del veicolo
            if checkCapacityNewRoute(
                    customers, saving["source"],
                    saving["destination"], vehicleCapacity, flag):
                # Aggiungo alle route una nuova route composta da source e destination del saving
                appendRoute(routes, [saving["source"],
                                     saving["destination"]], servedCustomers)
        # Se abbiamo già inserito routes
        else:
            # Mi salvo gli indici dei node nella lista dei customer già serviti
            savIndices = {
                "source": -1,
                "destination": -1
            }
            if saving["source"] in servedCustomers:
                savIndices["source"] = servedCustomers.index(saving["source"])
            if saving["destination"] in servedCustomers:
                savIndices["destination"] = servedCustomers.index(saving["destination"])

            # Se almeno uno di loro non è inserito, posso procedere
            if not (savIndices["source"] != -1 and savIndices["destination"] != -1):
                foundRoute = False
                # Scorro le route
                for route in routes:
                    # Il metodo createRoute va ad aggiungere il saving ad una route
                    # se è possibile, e se lo aggiunge restituisce true
                    foundRoute = createRoute(
                            saving, route, customers,
                            servedCustomers, savIndices,
                            vehicleCapacity, flag)
                    if foundRoute:
                        print("FoundRoute")
                        break
                # Se non ho potuto aggiungere il nodo, devo creare una nuova route,
                # tenendo presente che non posso eccedere il numero di veicoli
                if not foundRoute and len(routes) < numVehicles:
                    # Controllo sempre che il vincolo di capacità sia soddisfatto
                    if checkCapacityNewRoute(
                            customers, saving["source"], saving["destination"],
                            vehicleCapacity, flag) and len(routes) < numVehicles:
                        # Aggiungo nuova route
                        appendRoute(routes, [saving["source"],
                                             saving["destination"]], servedCustomers)
    return routes

# Funzione per la gestione della route. Vengono controllate
# testa e coda della route e confrontate con i valori del saving
# passato come parametro
def createRoute(saving, route, customers, servedCustomers, savIndices, vehicleCapacity, flag):
    routeCapacity = getRouteCapacity(route, customers, flag)
    foundRoute = False
    leftover = -1
    savSource = saving["source"]
    savDest = saving["destination"]
    sourceIndex = savIndices["source"]
    destIndex = savIndices["destination"]

    print("  The route is " + str(route))
    print("  savSource: " + str(savSource))
    print("  savDest: " + str(savDest))
    print("  first item route: " + str(route[1]))
    print("  last item route: " + str(route[-2]))

    # Se il source del saving è uguale all'ultimo nodo visitato dalla route,
    # allora posso fare l'unione inserendo la destinazione del saving dopo
    # tale nodo
    if route[-2] == savSource and destIndex == -1:
        foundRoute = True
        print("First if")
        if checkCapacity(customers, routeCapacity, savDest, vehicleCapacity, flag):
            route.insert(-1, savDest)
            servedCustomers.append(savDest)
        else:
            print("Superato limite veicolo")
    # Se la destination del saving è uguale all'ultimo nodo visitato dalla route,
    # allora posso fare l'unione inserendo la source del saving dopo tale nodo
    elif route[-2] == savDest and sourceIndex == -1:
        foundRoute = True
        print("Second if")
        if checkCapacity(customers, routeCapacity, savSource, vehicleCapacity, flag):
            route.insert(-1, savSource)
            servedCustomers.append(savSource)
        else:
            print("Superato limite veicolo")
    # Se la source del saving è uguale al primo nodo visitato dalla route,
    # allora posso fare l'unione inserendo la destination del saving prima di
    # tale nodo
    elif route[1] == savSource and destIndex == -1:
        foundRoute = True
        print("Third if")
        if checkCapacity(customers, routeCapacity, savDest, vehicleCapacity, flag):
            route.insert(1, savDest)
            servedCustomers.append(savDest)
        else:
            print("Superato limite veicolo")
    # Se la destination del saving è uguale al primo nodo visitato dalla route,
    # allora posso fare l'unione inserendo la destination del saving dopo tale nodo
    elif route[1] == savDest and sourceIndex == -1:
        foundRoute = True
        print("Fourth if")
        if checkCapacity(customers, routeCapacity, savSource, vehicleCapacity, flag):
            route.insert(-1, savSource)
            servedCustomers.append(savSource)
        else:
            print("Superato limite veicolo")
    return foundRoute

# Crea una nuova route da zero, quindi otterrò una nuova route
# di tipo (0 - val - val - 0) oppure (0 - val - 0)
def appendRoute(routes, values, servedCustomers):
    # Creo la testa della route
    route = [0]
    # Inserisco i valori passati come parametri
    for value in values:
        route.append(value)
        servedCustomers.append(value)
    # Inserisco la coda della route
    route.append(0)
    # Inserisco la route intera nella lista delle routes
    routes.append(route)


def getRouteCost(route, customers, customerDist):
    routeCost = 0
    for node in range(0, len(route) - 1):
        # Ricorda che le distanze per i customers sono messe in ordine e
        # ogni customer ha la distanza per tutti i nodi successivi ad esso.
        # Quindi mi basta prendere il minore tra i due, cercarlo nella lista
        # e prendere la sua distanza
        minNode = min(route[node], route[node + 1])
        maxNode = max(route[node], route[node + 1])
        if minNode == 0:
            # Le distanze tra nodi e deposito sono inserite nella lista dei customers.
            routeCost = routeCost + customers[maxNode-1]["distFromDepot"]
        else:
            # Prendo la distanza dalla lista delle distanze tra clienti (customerDist).
            index = maxNode - minNode - 1
            routeCost = routeCost + customerDist[minNode - 1][index]["distance"]
    return routeCost


def getRoutesCosts(routes, customers, customerDist):
    routesCosts = []
    for route in routes:
        routesCosts.append(getRouteCost(route, customers, customerDist))
    return routesCosts


def getTotalCost(list):
    total = 0
    for item in list:
        total += item
    return total


def getRouteCapacity(route, customers, flag):
    # Uso sempre un flag per sapere se tutti i nodi della route
    # sono LH, tutti BH o misti
    routeCapacity = 0

    # Ricorda che il primo e ultimo nodo sono 0 (il deposito) quindi
    # non hanno delivery o pickup. Scorro i nodi della route dal secondo
    # al penultimo.
    # Ricorda anche che i customers partono dal primo customer, quindi
    # l'indice zero corrisponde al cliente 1, l'indice 1 al cliente 2
    # e così via. Siccome nella route avrò un valore, devo incrementarlo
    # di uno.
    for node in range(1, len(route) - 1):
        thisNode = route[node]
        # print("     This is the iteration " + str(node) + " of getRouteCap")
        # print("     The actual route cap is " + str(routeCapacity))
        # print("     We are checking the node " + str(node))
        # pprint.pprint(customers[thisNode - 1])
        # print("     The node has cap " + str(customers[thisNode - 1]["delivery"]))
        if flag == 1:
            # print("flag1")
            routeCapacity += customers[thisNode - 1]["delivery"]
        if flag == 2:
            # print("flag2")
            routeCapacity += customers[thisNode - 1]["pickup"]
    return routeCapacity


def getRoutesCapacities(routes, customers, flag):
    routesCapacities = []
    for route in routes:
        routesCapacities.append(getRouteCapacity(route, customers, flag))
    return routesCapacities


def getNumberLH_BH(customers):
    numLH = 0
    numBH = 0
    for cust in customers:
        if cust["delivery"] != 0:
            numLH += 1
        else:
            numBH += 1
    return numLH, numBH


def checkCapacity(customers, routeCapacity, value, vehicleCapacity, flag):
    if flag == 1:
        if routeCapacity + customers[value - 1]["delivery"] <= vehicleCapacity:
            return True
    elif flag == 2:
        if routeCapacity + customers[value - 1]["pickup"] <= vehicleCapacity:
            return True
    return False


def checkCapacityNewRoute(customers, firstValue, secondValue, vehicleCapacity, flag):
    if flag == 1:
        if customers[firstValue - 1]["delivery"] + customers[secondValue - 1]["delivery"] <= vehicleCapacity:
            return True
    elif flag == 2:
        if customers[firstValue - 1]["pickup"] + customers[secondValue - 1]["pickup"] <= vehicleCapacity:
            return True
    return False