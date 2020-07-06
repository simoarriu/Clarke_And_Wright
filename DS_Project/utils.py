import math
import pprint
import parallel

# Funzione per calcolare la distanza euclidea tra due punti date le loro coordinate
def pointDistance(x1, y1, x2, y2):
    return round(math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2)), 2)


# Funzione per calcolo del saving
def saving(c1, c2, c3):
    return c1 + c2 - c3


# Funzione per prendere i customers dal file
def getCustomers(data, depotX, depotY):
    customers = []
    customersL = []
    customersB = []
    route_L = []
    route_B = []

    # Itero la lista, parto da 4 e vado fino alla fine della lista data
    # Teoricamente, visto che stiamo guardando i clienti, dovremmo usare
    # la variabile numCustomers ma possiamo cambiarlo
    for i in range(4, len(data)):
        splitStr = data[i].split("   ")  # splitto la stringa
        # Per ogni cliente inserisco nella lista un dizionario contenente
        # quattro valori: le due coordinate del cliente, la quantità da
        # consegnare e la quantità da ritirare. Questi ultimi due valori
        # sono uno nullo e l'altro diverso da zero (o viceversa)

        customer = {"id": i - 3, "xCoord": int(splitStr[0]), "yCoord": int(splitStr[1]), "delivery": int(splitStr[2]),
                    "pickup": int(splitStr[3])}
        customer["distFromDepot"] = pointDistance(
                depotX, depotY,
                customer["xCoord"],
                customer["yCoord"])

        customers.append(customer)
        if int(splitStr[2]) != 0:
            customersL.append(customer)
            route_L.append([0, i - 3, 0])
        elif int(splitStr[3]) != 0:
            customersB.append(customer)
            route_B.append([0, i - 3, 0])
    return customers, customersL, customersB, route_L, route_B


# Funzione per calcolare le distanze tra i clienti
# Viene restituita una lista di liste: ogni lista primaria indica
# un cliente, e ogni lista secondaria interna alla primaria indica
# ogni cliente successivo ad esso e quindi la distanza ad esso
# correlata. Quindi se ho 10 clienti, la lista all'indice 5 indica
# il cliente numero 6 e le liste interne ad esso saranno le distanze
# dal cliente 6 ai clienti 7, 8, 9 e 10.
def getCustomersDist(customers):
    customerDist = []
    for i in range(0, len(customers)):
        for j in range(i + 1, len(customers)):
            if j == i + 1:
                customerDist.append([{
                    "destination": j + 1,
                    "distance": pointDistance(
                        customers[i]["xCoord"],
                        customers[i]["yCoord"],
                        customers[j]["xCoord"],
                        customers[j]["yCoord"]
                    )
                }])
            else:
                customerDist[i].append({
                    "destination": j + 1,
                    "distance": pointDistance(
                        customers[i]["xCoord"],
                        customers[i]["yCoord"],
                        customers[j]["xCoord"],
                        customers[j]["yCoord"]
                    )
                })
    return customerDist


# Funzione per il calcolo dei savings
# Qua ho una lista di dizionari. Ogni dizionario indica, per ogni
# cliente, il saving che si ottiene con tutti i clienti successivi
# ad esso. Quindi se ho 5 clienti, per il cliente 1 calcolo i savings
# per cliente 2, 3, 4 e 5.
def getSavings(savings, customerDist, customers):
    for i in range(0, len(customerDist)):
        for j in range(0, len(customerDist[i])):
            tempDest = customerDist[i][j]["destination"]
            savings.append({
                "source": i + 1,
                "destination": tempDest,
                "saving": saving(
                    customers[i]["distFromDepot"],
                    customers[tempDest - 1]["distFromDepot"],
                    customerDist[i][j]["distance"]
                )
            })
    return savings


def getLH_BHSavings(LH_savings, BH_savings, savings, customers):
    print("\nStarting getting LSBH savings\n")
    for saving in savings:

        if customers[saving["source"] - 1]["delivery"] != 0 and customers[saving["destination"] - 1]["delivery"] != 0:
            LH_savings.append(saving)
        elif customers[saving["source"] - 1]["pickup"] != 0 and customers[saving["destination"] - 1]["pickup"] != 0:
            BH_savings.append(saving)

    return LH_savings, BH_savings


def getDelivery(delivery, id, customers, flagL):
    for i in range(0, len(customers)):
        if (id == customers[i]["id"]):
            if (flagL):
                if (customers[i]["delivery"]) != 0:
                    delivery = customers[i]["delivery"]
                else:
                    delivery = customers[i]["pickup"]
            else:
                if (customers[i]["pickup"]) != 0:
                    delivery = customers[i]["pickup"]
                else:
                    delivery = customers[i]["delivery"]

    return delivery


def getCapacityRoute(delivery, new_route, customers, flagL):
    for r in new_route:
        for i in range(0, len(customers)):
            if (r == customers[i]["id"]):
                if (flagL):
                    delivery += customers[i]["delivery"]
                else:
                    delivery += customers[i]["pickup"]

    return delivery


def getIdCustomer(customerList, customers):
    for i in range(0, len(customers)):
        customerList.append(customers[i]["id"])

    return customerList


def getTotalCostRoute(routesCostsLH):
    cost = 0
    for i in routesCostsLH:
        cost += i
    return cost


def getSplitRoute(route, client):
    for r in route:
        for i in range(0, len(r)):
            if r[i] == client:
                return r


# Dato un cliente r, la route lh e i savings, cerco qual è il saving migliore tra le combinazioni
# di r con la testa di ciascuna route lh
def searchBestSaving(r, routes_lh, savings, customers, vehicleCapacity):
    list_s = []
    delivery = 0
    # print("Valore bh: " + str(r))

    # Scorro le route LH
    for route in routes_lh:
        # Controllo l'elemento di testa
        for i in range(0, len(route) - 1):
            if route[i + 1] == 0:
                # Scorro tutti i saving, se trovo la combinazione r-testa o testa-r, allora aggiungo il saving alla lista
                for s in savings:
                    if ((s["source"] == r and s["destination"] == route[i]) or (
                            s["source"] == route[i] and s["destination"] == r)):
                        # Controllo che la capacità dei BH uniti venga rispettata
                        if ((getCapacityRoute(delivery, route, customers, False) + getDelivery(delivery, r, customers,
                                                                                               False)) <= vehicleCapacity):
                            list_s.append(s["saving"])
                        # Se non è rispettata, inserisco uno 0 così da non perdere l'ordine degli indici
                        else:
                            list_s.append(0)

    # print("Lista saving temp")
    # print(list_s)
    # ottengo l'indice dell'elemento massimo, che mi permette di inserire poi r nella route lh corretta
    index_max = list_s.index(max(list_s))
    # print(routes_lh[index_max])

    return index_max


# Questo metodo prende le route Lh, le Bh e la lista di saving
def merge(routes_lh, routes_bh, savings, customers, vehicleCapacity):
    # Scorro le route BH
    for i in range(0, len(routes_bh)):
        # Per ogni elemento Bh diverso dal deposito
        for r in routes_bh[i]:
            if r != 0:
                # ottengo l'indice della route LH in cui devo inserire il cliente BH, in corrispondenza del saving migliore
                index_found = searchBestSaving(r, routes_lh, savings, customers, vehicleCapacity)
                # inserisco il cliente Bh in testa
                routes_lh[index_found].insert(-1, r)

    return routes_lh


def getTotalC(merge_routes, customers, customerDist):
    routesCosts = parallel.getRoutesCosts(merge_routes, customers, customerDist)

    # print("\n")
    # print("Costi routes merge")
    # pprint.pprint(routesCosts)

    total_cost = 0
    total_cost = getTotalCostRoute(routesCosts)

    # print("\n")
    # print("Costo totale merge")
    # pprint.pprint(total_cost)

    return total_cost, routesCosts


def printFileSeq(filename, merge_routes, vehicleCapacity, numCustomers, numVehicles, single_cost_route, customers,
              elapsed_time):
    with open(filename + "outputSeq.txt", "w") as file:
        file.write("PROBLEM DETAILS:\n")
        file.write("Customers = " + str(numCustomers) + '\n')
        file.write("Max Load = " + str(vehicleCapacity) + '\n')
        file.write("Max Cost = 999999999999999\n\n")
        file.write("SOLUTION DETAILS:\n")
        file.write("Total Cost = " + str(sum(single_cost_route)) + '\n')
        file.write("Routes Of the Solution = " + str(numVehicles) + '\n')
        file.write("Computational Time = " + str(elapsed_time) + " s" '\n\n')

        for i in range(0, len(merge_routes)):
            file.write("ROUTE " + str(i) + ':\n')
            file.write("Cost = " + str(single_cost_route[i]) + '\n')
            delivery = 0
            file.write("Delivery Load = " + str(getCapacityRoute(delivery, merge_routes[i], customers, True)) + '\n')
            delivery = 0
            file.write("Pick-Up Load = " + str(getCapacityRoute(delivery, merge_routes[i], customers, False)) + '\n')
            file.write("Customers in Route = " + str(len(merge_routes[i]) - 2) + '\n')
            file.write("Vertex Sequence :\n" + str(merge_routes[i]) + '\n\n')


def printFilePar(filename, merge_routes, vehicleCapacity, numCustomers, numVehicles, single_cost_route, customers,
              elapsed_time):
    with open(filename + "outputPar.txt", "w") as file:
        file.write("PROBLEM DETAILS:\n")
        file.write("Customers = " + str(numCustomers) + '\n')
        file.write("Max Load = " + str(vehicleCapacity) + '\n')
        file.write("Max Cost = 999999999999999\n\n")
        file.write("SOLUTION DETAILS:\n")
        file.write("Total Cost = " + str(sum(single_cost_route)) + '\n')
        file.write("Routes Of the Solution = " + str(numVehicles) + '\n')
        file.write("Computational Time = " + str(elapsed_time) + " s" '\n\n')

        for i in range(0, len(merge_routes)):
            file.write("ROUTE " + str(i) + ':\n')
            file.write("Cost = " + str(single_cost_route[i]) + '\n')
            delivery = 0
            file.write("Delivery Load = " + str(getCapacityRoute(delivery, merge_routes[i], customers, True)) + '\n')
            delivery = 0
            file.write("Pick-Up Load = " + str(getCapacityRoute(delivery, merge_routes[i], customers, False)) + '\n')
            file.write("Customers in Route = " + str(len(merge_routes[i]) - 2) + '\n')
            file.write("Vertex Sequence :\n" + str(merge_routes[i]) + '\n\n')
