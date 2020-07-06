import pprint
import time
import utils
import parallel
import sequential

# Il pprint serve per stampare la roba sul terminale in modo più decente
# perchè altrimenti le liste vengono fatte tutte su una riga, invece
# pprint le fa con un elemento per riga.

# Apro il file e metto tutto in una lista, ogni stringa è una linea del file
filepath = input("Insert the name of the instance you want to run: ")
with open("Instances/" + filepath + ".txt", 'r') as file:
    data = [el.replace("\n", "") for el in list(file)]

# La prima riga contiene il numero totale di clienti
numCustomers = int(data[0])

# La seconda è sempre 1
# La terza contiene il numero di veicoli
numVehicles = int(data[2])

print("Number of customers: " + str(numCustomers))
print("Number of vehicles: " + str(numVehicles))

# La quarta riga contiene quattro valori ma di questi ce ne servono solo tre
# Il primo e il secondo valore sono le coordinate del deposito
depotX, depotY = data[3].split("   ")[0:2]
depotX = int(depotX)
depotY = int(depotY)

# Il terzo valore è sempre 0
# Il quarto valore è la capacità del deposito
vehicleCapacity = int(data[3].split("   ")[3])

print("The deposit is on the point " + str(depotX) + ":" + str(depotY))
print("The capacity of each vehicle is " + str(vehicleCapacity))

# Creo una nuova lista che conterrà tutti i dati dei clienti
# Creo una lista dei clienti linehaul e clienti backhaul.
# Creo inoltre due liste: una conterrà delle route base di tipo 0 - LH - 0
# mentre l'altra conterrà route base del tipo 0 - BH - 0
customers, customersL, customersB, route_L, route_B = utils.getCustomers(data, depotX, depotY)

# Ora devo calcolare le distanze tra clienti fra di loro
# Ricorda che customerDist indica i nodi da 1 a 25, perchè
# lo zero è il deposito e non lo contiamo
customerDist = utils.getCustomersDist(customers)

# Distanze clienti linehaul
customerDistL = utils.getCustomersDist(customersL)

# Distanze clienti backhaul
customerDistB = utils.getCustomersDist(customersB)


# print("\nNow we print the distances for the clients\n")

# pprint.pprint(customerDist)

# Per tenere conto dei savings, preferisco usare una lista
# in modo tale da poter effettuare poi un ordinamento
# sull'intera lista in modo più semplice, ordinamento che
# mi sarà poi utile nella creazione dell'algoritmo
# Clark & Wright

savings = []
savings = utils.getSavings(savings, customerDist, customers)

# Ordino i savings in base al valore del saving ottenuto.
# Uso una lambda per risparmiare spazio poichè la funzione
# è piuttosto semplice. Inoltre pongo reverse = true
# perchè voglio prima i valori più grandi.

savings.sort(key=lambda obj: obj["saving"], reverse=True)

# Creo due nuove liste: LH_savings conterrà i saving in cui sia
# sorgente che destinazione sono dei nodi di delivery, mentre
# BH_savings conterrà i savings in cui sia sorgente che destinazione
# sono di pickup.



# Creo anche una terza lista che contiene i savings in cui uno
# dei nodi è di delivery e l'altro è di pickup. Mi servirà per
# effettuare l'unione.

LH_savings = []
BH_savings = []

LH_savings, BH_savings = utils.getLH_BHSavings(LH_savings, BH_savings, savings, customers)

# print("\nLHSavings: \n")

# pprint.pprint(LH_savings)

# print("\nBHSavings: \n")

# pprint.pprint(BH_savings)

# testInput.inputTest(savings, customers, customerDist)

# Qua si fanno partire entrambi gli algoritmi, sia parallelo che sequenziale
flagLinehaul = True
start_time = time.time()
route_LH = sequential.mainSequential(
    LH_savings, route_L, numVehicles, customersL,
    customerDistL, vehicleCapacity, flagLinehaul)
flagLinehaul = False
route_BH = sequential.mainSequential(
    BH_savings, route_B, numVehicles, customersB,
    customerDistB, vehicleCapacity, flagLinehaul)

parallelPack = {
    "savings": savings,
    "LH_savings": LH_savings,
    "BH_savings": BH_savings,
    "numCustomers": numCustomers,
    "numVehicles": numVehicles,
    "vehicleCapacity": vehicleCapacity,
    "customers": customers,
    "customerDist": customerDist
}

route_LH_par, route_BH_par = parallel.mainParallel(parallelPack)


#Merge tra route LH e BH
merge_routes = utils.merge(
    route_LH, route_BH, savings,
    customers, vehicleCapacity)

merge_routes_par = utils.merge(
    route_LH_par, route_BH_par, savings,
    customers, vehicleCapacity)

elapsed_time = time.time() - start_time

print("Liste finali seq")
pprint.pprint(merge_routes)

print("Liste finali par")
pprint.pprint(merge_routes_par)

single_cost_route = parallel.getRoutesCosts(merge_routes, customers, customerDist)

single_cost_route_par = parallel.getRoutesCosts(merge_routes_par, customers, customerDist)

utils.printFileSeq(
    filepath.split('\\')[-1], merge_routes, vehicleCapacity,
    numCustomers, numVehicles, single_cost_route, customers, elapsed_time
)

utils.printFilePar(
    filepath.split('\\')[-1], merge_routes_par, vehicleCapacity,
    numCustomers, numVehicles, single_cost_route_par, customers, elapsed_time
)