import random
import numpy as np
import math 
from random import choice
import statistics 
import time

# Enregistrer le temps de début
start_time = time.time()

sudoku_initial = """
                    024007000
                    600000000
                    003680415
                    431005000
                    500000032
                    790000060
                    209710800
                    040093000
                    310004750
                """

sudoku = np.array([[int(i) for i in ligne] for ligne in sudoku_initial.split()])

def afficher_sudoku(sudoku):
    print("\n")
    for i in range(len(sudoku)):
        ligne = ""
        if i == 3 or i == 6:
            print("---------------------")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                ligne += "| "
            ligne += str(sudoku[i,j])+" "
        print(ligne)


def fixer_valeurs_sudoku(sudoku_fixe):
    for i in range (0,9):
        for j in range (0,9):
            if sudoku_fixe[i,j] != 0:
                sudoku_fixe[i,j] = 1
    
    return(sudoku_fixe)

def calculer_nb_erreurs(sudoku):
    nb_erreurs = 0 
    for i in range (0,9):
        nb_erreurs += calculer_nb_erreurs_ligne_colonne(i ,i ,sudoku)
    return(nb_erreurs)

def calculer_nb_erreurs_ligne_colonne(ligne, colonne, sudoku):
    nb_erreurs = (9 - len(np.unique(sudoku[:,colonne]))) + (9 - len(np.unique(sudoku[ligne,:])))
    return(nb_erreurs)

def creer_blocs_3x3():
    liste_blocs = []
    for r in range (0,9):
        tmpListe = []
        bloc1 = [i + 3*((r)%3) for i in range(0,3)]
        bloc2 = [i + 3*math.trunc((r)/3) for i in range(0,3)]
        for x in bloc1:
            for y in bloc2:
                tmpListe.append([x,y])
        liste_blocs.append(tmpListe)
    return(liste_blocs)



def remplir_blocs_3x3_aleatoirement(sudoku, liste_blocs):
    for bloc in liste_blocs:
        for case in bloc:
            if sudoku[case[0],case[1]] == 0:
                bloc_courant = sudoku[bloc[0][0]:(bloc[-1][0]+1),bloc[0][1]:(bloc[-1][1]+1)]
                sudoku[case[0],case[1]] = choice([i for i in range(1,10) if i not in bloc_courant])
    return sudoku

def somme_bloc(sudoku, bloc):
    somme_finale = 0
    for case in bloc:
        somme_finale += sudoku[case[0], case[1]]
    return(somme_finale)

def deux_cases_aleatoires_dans_bloc(sudoku_fixe, bloc):
    while (1):
        premiere_case = random.choice(bloc)
        deuxieme_case = choice([case for case in bloc if case is not premiere_case ])

        if sudoku_fixe[premiere_case[0], premiere_case[1]] != 1 and sudoku_fixe[deuxieme_case[0], deuxieme_case[1]] != 1:
            return([premiere_case, deuxieme_case])

def echanger_cases(sudoku, cases_a_echanger):
    sudoku_propose = np.copy(sudoku)
    place_holder = sudoku_propose[cases_a_echanger[0][0], cases_a_echanger[0][1]]
    sudoku_propose[cases_a_echanger[0][0], cases_a_echanger[0][1]] = sudoku_propose[cases_a_echanger[1][0], cases_a_echanger[1][1]]
    sudoku_propose[cases_a_echanger[1][0], cases_a_echanger[1][1]] = place_holder
    return (sudoku_propose)

def etat_propose(sudoku, sudoku_fixe, liste_blocs):
    bloc_aleatoire = random.choice(liste_blocs)

    if somme_bloc(sudoku_fixe, bloc_aleatoire) > 6:  
        return(sudoku, 1, 1)
    cases_a_echanger = deux_cases_aleatoires_dans_bloc(sudoku_fixe, bloc_aleatoire)
    sudoku_propose = echanger_cases(sudoku,  cases_a_echanger)
    return([sudoku_propose, cases_a_echanger])

def choisir_nouvel_etat(sudoku_courant, sudoku_fixe, liste_blocs, sigma):
    proposition = etat_propose(sudoku_courant, sudoku_fixe, liste_blocs)
    nouveau_sudoku = proposition[0]
    cases_a_verifier = proposition[1]
    cout_courant = calculer_nb_erreurs_ligne_colonne(cases_a_verifier[0][0], cases_a_verifier[0][1], sudoku_courant) + calculer_nb_erreurs_ligne_colonne(cases_a_verifier[1][0], cases_a_verifier[1][1], sudoku_courant)
    nouveau_cout = calculer_nb_erreurs_ligne_colonne(cases_a_verifier[0][0], cases_a_verifier[0][1], nouveau_sudoku) + calculer_nb_erreurs_ligne_colonne(cases_a_verifier[1][0], cases_a_verifier[1][1], nouveau_sudoku)
    difference_cout = nouveau_cout - cout_courant
    rho = math.exp(-difference_cout/sigma)
    if(np.random.uniform(1,0,1) < rho):
        return([nouveau_sudoku, difference_cout])
    return([sudoku_courant, 0])

def choisir_nb_iterations(sudoku_fixe):
    nb_iterations = 0
    for i in range (0,9):
        for j in range (0,9):
            if sudoku_fixe[i,j] != 0:
                nb_iterations += 1
    return nb_iterations

def calculer_sigma_initial(sudoku, sudoku_fixe, liste_blocs):
    liste_differences = []
    tmp_sudoku = sudoku
    for i in range(1,10):
        tmp_sudoku = etat_propose(tmp_sudoku, sudoku_fixe, liste_blocs)[0]
        liste_differences.append(calculer_nb_erreurs(tmp_sudoku))
    return (statistics.pstdev(liste_differences))

def resoudre_sudoku(sudoku):
    solution_trouvee = 0
    while (solution_trouvee == 0):
        facteur_decrement = 0.99
        compteur_bloque = 0
        sudoku_fixe = np.copy(sudoku)
        afficher_sudoku(sudoku)
        fixer_valeurs_sudoku(sudoku_fixe)
        liste_blocs = creer_blocs_3x3()
        sudoku_temporaire = remplir_blocs_3x3_aleatoirement(sudoku, liste_blocs)
        afficher_sudoku(sudoku_temporaire)
        sigma = calculer_sigma_initial(sudoku, sudoku_fixe, liste_blocs)
        score = calculer_nb_erreurs(sudoku_temporaire)
        iterations = choisir_nb_iterations(sudoku_fixe)
        if score <= 0:
            solution_trouvee = 1

        while solution_trouvee == 0:
            score_precedent = score
            for i in range (0, iterations):
                nouvel_etat = choisir_nouvel_etat(sudoku_temporaire, sudoku_fixe, liste_blocs, sigma)
                sudoku_temporaire = nouvel_etat[0]
                difference_score = nouvel_etat[1]
                score += difference_score
                print(score)
                if score <= 0:
                    solution_trouvee = 1
                    break

            sigma *= facteur_decrement
            if score <= 0:
                solution_trouvee = 1
                break
            if score >= score_precedent:
                compteur_bloque += 1
            else:
                compteur_bloque = 0
            if (compteur_bloque > 80):
                sigma += 2
            if(calculer_nb_erreurs(sudoku_temporaire)==0):
                afficher_sudoku(sudoku_temporaire)
                break
    return(sudoku_temporaire)

solution = resoudre_sudoku(sudoku)
afficher_sudoku(solution)

end_time = time.time()

# Calculer la durée d'exécution
execution_time = end_time - start_time
print("Le code a pris {} secondes pour s'exécuter.".format(execution_time))
