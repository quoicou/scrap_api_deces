from datetime import datetime
from scipy import stats
from sklearn.metrics import r2_score
from unidecode import unidecode
import requests
import matplotlib.pyplot as plt
import numpy

def input_nom_pnom_date():
    sortie = 0

    while sortie != 1:
        nom = input("\nSaisissez un nom de famille (Rentrez 0 si vous ne souhaitez pas saisir de nom)\n\nNom : ")

        nom = unidecode(nom.replace(" ", "%20"))

        pnom = input("\nSaisissez un prénom (Rentrez 0 si vous ne souhaitez pas saisir de prénom)\n\nPrénom : ")

        pnom = unidecode(pnom)

        date = input("\nSaisissez un date de décès (Rentrez 0 si vous ne souhaitez pas saisir de date) - Format jj/mm/aaaa\n\nDate : ")

        if nom == "0" and pnom == "0" and date == "0":
            sortie = 0

        else:
            sortie = 1

    if nom != "0" and pnom != "0" and date != "0":
        nom_pnom_date = nom.strip().lower() + "+" + pnom.strip().lower() + "+" + date
    elif nom != "0" and pnom != "0" and date == "0":
        nom_pnom_date = nom.strip().lower() + "+" + pnom.strip().lower()
    elif nom != "0" and pnom == "0" and date != "0":
        nom_pnom_date = nom.strip().lower() + "+" + date
    elif nom == "0" and pnom != "0" and date != "0":
        nom_pnom_date = pnom.strip().lower() + "+" + date
    elif nom != "0" and pnom == "0" and date == "0":
        nom_pnom_date = nom.strip().lower()
    elif nom == "0" and pnom != "0" and date == "0":
        nom_pnom_date = pnom.strip().lower()
    elif nom == "0" and pnom == "0" and date != "0":
        nom_pnom_date = date

    return nom_pnom_date

def input_sexe():
    choix = int(input("\nVoulez-vous saisir un sexe ?\n1) Oui\n2) Non\n\nChoix : "))

    while choix not in [1, 2]:
        choix = int(input("\nERREUR DE SAISIE\n\nVoulez-vous saisir un sexe ?\n1) Oui\n2) Non\n\nChoix : "))

    if choix == 1:
        choix_sexe = int(input("\nChoisissez un sexe\n1) F\n2) M\n\nChoix : "))

        while choix_sexe not in [1, 2]:
            choix_sexe = int(input("\nERREUR DE SAISIE\n\nChoisissez un sexe\n1) F\n2) M\n\nChoix : "))

        if choix_sexe == 1:
            return "F"
        else:
            return "M"

    else:
        return None

def token():
    token = "INSERER TOKEN"
    
    return token

def lien_api(nom_pnom_date, sexe, nb_page):
    if sexe == None:
        url = f"https://deces.matchid.io/deces/api/v1/search?q={nom_pnom_date}&size=500&page={nb_page}"
    else:
        url = f"https://deces.matchid.io/deces/api/v1/search?q={nom_pnom_date}&sexe={sexe}&size=500&page={nb_page}"

    return url

def lien_api_aggs(nom_pnom_date, sexe, choix_type_aggs):
    if sexe == None:
        url_aggs = f"https://deces.matchid.io/deces/api/v1/agg?q={nom_pnom_date}&aggs={choix_type_aggs}"
    else:
        url_aggs = f"https://deces.matchid.io/deces/api/v1/agg?q={nom_pnom_date}&sexe={sexe}&aggs={choix_type_aggs}"

    return url_aggs

def date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        date_formatted = date_obj.strftime("%Y/%m/%d")

    except:
        date_formatted = "00/00/0000"

    return date_formatted

def input_total():
    nom_pnom_date = input_nom_pnom_date()

    sexe = input_sexe()

    return nom_pnom_date, sexe

def recherche_nom_pnom_date_sexe():
    i=0

    nb_page = 1

    dict_date = {}

    nom_pnom_date, sexe = input_total()

    url = lien_api(nom_pnom_date, sexe, nb_page)
    print(url)

    response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token())})

    while response.status_code == 200:

        url = lien_api(nom_pnom_date, sexe, nb_page)

        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token())})

        if response.status_code == 200:

            data = response.json()
            results = data["response"]["persons"]

            for result in results:
                date_str = result["death"]["date"].replace("....", "$3/$2/$1")
                date_formatted = date_format(date_str)
                print(f"Nom : {result['name']['last']} - Prénom : {result['name']['first'][0]} - Décès : {date_formatted}")

                if date_formatted != "00/00/0000":
                    date_annee = int(date_formatted[:4])

                    if date_annee not in dict_date:
                        dict_date[date_annee] = 1
                    elif date_annee in dict_date:
                        dict_date[date_annee] += 1

                """ TRAITEMENT DE FICHIER .TXT
                chemin_fichier = "C:\\Users\\Asus\\Documents\\deces\\deces.txt"

                with open(chemin_fichier, "a") as f:
                    f.write(f"\n[[{result['name']['last']}][{result['name']['first'][0]}][{date_formatted}]]")

                
                with open(chemin_fichier, "r") as f:
                    #liste_action = re.search(r'\[\[(.*?)\]\]')
                    transactions = f.readlines()
                """

                i+=1

        nb_page += 1

    print(f"\n{i} occurrences trouvées\n\n###Fin du scrapping###")

    if i != 0:

        choix_aggs = int(input("\nSouhaitez-vous classer ces données par aggrégations ?\n1) Oui\n2) Non\n\nChoix : "))

        while choix_aggs not in [1, 2]:
            choix_aggs = int(input("\nERREUR DE SAISIE\n\nSouhaitez-vous classer ces données par aggrégations ?\n1) Oui\n2) Non\n\nChoix : "))

        if choix_aggs == 1:
            return dict_date, choix_aggs, nom_pnom_date, sexe

        else:
            return dict_date, None, None, None

def type_aggs():
    choix_type_aggs = int(input("\nPar quel type d'aggrégation souhaitez-vous classer ces données ?\n1) Par pays de décès\n2) Par ville de décès\n3) Par sexe\n4) Par âge de décès\n\nChoix : "))

    while choix_type_aggs not in [1, 2, 3, 4]:
        choix_type_aggs = int(input("\nERREUR DE SAISIE\n\nPar quel type d'aggrégation souhaitez-vous classer ces données ?\n1) Par pays de décès\n2) Par ville de décès\n3) Par sexe\n4) Par âge de décès\n\nChoix : "))

    if choix_type_aggs == 1:
        return "deathCountry", "Pays de décès"
    elif choix_type_aggs == 2:
        return "deathCity", "Ville de décès"
    elif choix_type_aggs == 3:
        return "sex", "Sexe"
    elif choix_type_aggs == 4:
        return "deathAge", "Âge de décès"

def recherche_aggs(nom_pnom_date, sexe):
    choix_type_aggs, key_affichage = type_aggs()

    url_aggs = lien_api_aggs(nom_pnom_date, sexe, choix_type_aggs)

    response = requests.get(url_aggs, headers={'Authorization': 'Bearer {}'.format(token())})

    print("\n")

    if response.status_code == 200:
        data = response.json()
        results = data["response"]["aggregations"]

        for result in results:
            print(f"{key_affichage} : {result['key']} - Nombre : {result['doc_count']}")

def stat(dict_date, nom_pnom_date, sexe):
    dict_date = {k: dict_date[k] for k in sorted(dict_date.keys())}

    x = []
    y = []

    for nombre, annee in dict_date.items():
        x.append(nombre)
        y.append(annee)

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    if r < -0.5 or r > 0.5:
        print(f"\nConditions réunies pour faire une régression linéaire : {r}")

        def myfunc(x):
            return slope * x + intercept

        mymodel = list(map(myfunc, x))

        plt.scatter(x, y)
        plt.plot(x, mymodel)
        plt.suptitle("Nombre de mort par année")
        plt.title(f"Pour {nom_pnom_date}, {sexe}")
        plt.show()

    else:
        print(f"\nConditions non-réunies pour faire une régression linéaire : {r}")

        mymodel = numpy.poly1d(numpy.polyfit(x, y, 3))

        if r2_score(y, mymodel(x)) > 0.5:

            myline = numpy.linspace(next(iter(dict_date)), list(dict_date.keys())[-1], max(dict_date.values()))

            plt.scatter(x, y)
            plt.plot(myline, mymodel(myline))
            plt.suptitle("Nombre de mort par année")
            plt.title(f"Pour {nom_pnom_date}, {sexe}")
            plt.show()

        else:
            print(f"\nConditions non-réunies pour faire une régression polynomiale : {r}")
            plt.scatter(x, y)
            plt.suptitle("Nombre de mort par année")
            plt.title(f"Pour {nom_pnom_date}, {sexe}")
            plt.show()



if __name__ == '__main__':
    dict_date, choix_aggs, nom_pnom_date, sexe = recherche_nom_pnom_date_sexe()
    if choix_aggs != None:
        recherche_aggs(nom_pnom_date, sexe)

    stat(dict_date, nom_pnom_date, sexe)


"""
- Recherche exacte nom, prénom
- Mettre Token dans fichier .txt
"""
