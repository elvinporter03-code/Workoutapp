import csv
import os
import ast
from datetime import date, datetime, timedelta

goal = 0
score = 0
sessionscore = 0
data = {}

#Automatiskt räkna ut PB för varje set

def read_score():
    global score, goal
    with open('settings.csv', newline='', encoding='utf-8',) as f:
        reader=csv.DictReader(f)
        for row in reader:
            score=row['score']
            goal=row['goal']
        score=int(score)
        goal=int(goal)
    return goal

goal = read_score()


with open("exercises.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row["Name"]
        primary_muscle = row["Primary muscle"]
        weight_multiplier = float(row["Weight Multiplier"])
        sets = int(row["Sets"])
        reps = int(row["Reps"])
        weight = float(row["Weight"])
        one_rm = float(row["1rm"])
        calc_rm = int(row["calculated1rm"])

        data[name] = [primary_muscle, weight_multiplier, sets, reps, weight, one_rm, calc_rm]



def print_exercises():
    for ex in data.keys():
        print("-" * 35)
        print(f'Exercise: {ex}')
        print(f'Muscle: {data[ex][0]}')
        print(f'Weight multiplier: {data[ex][1]}')
        print(f'Sets: {data[ex][2]} Reps: {data[ex][3]}, Weight: {data[ex][4]}, 1RM: {data[ex][5]}, Calc 1RM: {data[ex][6]}')


def chose_exercise():
    choosen_muscle = ""
    muscle_groups = []
    for ex in data.keys():
        if data[ex][0] not in muscle_groups:
            muscle_groups.append(data[ex][0])
    while choosen_muscle not in muscle_groups:
        count = 1
        print()
        for m in muscle_groups:
            print(f'{count}. {m}')
            count += 1
        print()
        try:
            index = int(input("Välj muskelgruppp (0 för att avsluta): "))
        except:
            index = -1
        if index == 0:
            return 0
        elif index > 0 and index <= len(muscle_groups):
            choosen_muscle = muscle_groups[index-1]
        else:
            print("Välj en existerande muskelgrupp")
    
    choosen_exercise = ""
    exercises = []
    for ex in data.keys():
        if data[ex][0] == choosen_muscle:
            exercises.append(ex)

    while choosen_exercise not in exercises:
        count = 1
        print()
        for ex in exercises:
            print(f'{count}. {ex}')
            count += 1
        print()
        try:
            index = int(input("Välj övning : "))
            print()
        except:
            index = -1
        if index > 0 and index <= len(exercises):
            choosen_exercise = exercises[index-1]
        else:
            print("Välj en existerande övning eller lägg till en egen: ")
    return choosen_exercise

def add_exercise(workout):
    choosen_exercise = chose_exercise()
    print(choosen_exercise)
    if choosen_exercise == 0:
        return workout
    sets = log_sets(choosen_exercise)
    for set in sets:
        if set[1] > data[choosen_exercise][5]:
            data[choosen_exercise][5] = set[1]
        calculated_rm = rm_formula(set[0], set[1])
        if calculated_rm > data[choosen_exercise][6]:
            data[choosen_exercise][6] = calculated_rm
    if choosen_exercise in workout:
        for set in sets:
            workout[choosen_exercise].append(set)
    else:
        workout[choosen_exercise] = sets
    return workout

def log_sets(exercise):
    sets = []
    weight = -1
    reps = -1
    count_set = 1
    temp=False
    while reps != 0:
        if reps == -1:
            if not temp:
                expected=calculate_expected_1rm(exercise, count_set)
            try:
                
                reps = int(input(f"I set {count_set}. Hur många reps gjorde du? (tryck 0 om du är klar): "))
            except:
                reps = -1
                print("Ange reps som integers")

        if reps == 0:
            break
        if reps != -1:  
            try:
                weight = float(input(f"I set {count_set}. Hur mycket vikt lyfte du?: "))
                print()
                set = (reps, weight)
                sets.append(set)
                count_set += 1
                check_score(expected, rm_formula(reps,weight))
                if expected == 0:
                    expected=rm_formula(reps,weight)
                    temp=True
                reps = -1  
                
            except:
                print("Ange vikt som en siffra! ")
                
        

    return sets
    

def create_exercise(workout):
    new_ex = input("Name of the exercise you want to add: ")
    new_ex_f = new_ex.title()

    choosen_muscle = ""
    muscle_groups = []
    for ex in data.keys():
        if ex == new_ex_f:
            print("Exercise already exists")
            return
        if data[ex][0] not in muscle_groups:
            muscle_groups.append(data[ex][0])
    while choosen_muscle not in muscle_groups:
        count = 1
        print()
        for m in muscle_groups:
            print(f'{count}. {m}')
            count += 1
        print()
        try:
            index = int(input("Välj en muskelgrupp (0 för att avsluta): "))
        except:
            index = -1
        if index == 0:
            return []
        elif index > 0 and index <= len(muscle_groups):
            choosen_muscle = muscle_groups[index-1]
        else:
            print("Välj en existerande muskelgrupp")
    w_multiplier = -1
    while w_multiplier != 0:
        try:
            w_multiplier = float(input("Vikt multiplikator? (0 för standard): "))
        except:
            print("Invalid multiplier")
            w_multiplier = -1
    if w_multiplier == 0:
        w_multiplier = 1
    data[new_ex_f] = [choosen_muscle, w_multiplier, 0, 0, 0, 0, 0]

    # So that the file is saved even when no workout is logged
    workout["Added"] = []

def edit_exercise():
    exercise = chose_exercise()
    choice = ""
    while choice != "Q":
        print("-" * 40)
        print(f"Vad vill du ändra på {exercise}?")
        print("N: Namn")
        print("M: Muskelgrupp")
        print("W: Weight Multiplier")
        print("Q: Klar")
        print("-" * 40)
        choice = input("Vad vill du redigera?: ").upper()
        if choice == "N":
            edit_helper(exercise, -1)
        elif choice == "M":
            edit_helper(exercise, 0)
        elif choice == "W":
            edit_helper(exercise, 1)
        elif choice == "Q":
            return
        else:
            print("Välj en bokstav från menyn!")

def edit_helper(exercise, index):
    new_input = ""
    while new_input == "":
        if index == 1:
            try:
                new_input = float(input("Ny multiplier: "))
                data[exercise][index] = new_input 
            except:
                print("Multipliern måste vara ett flyttal")
        elif index == 0:
            print()
            muscle_groups = []
            for ex in data.keys():
                if data[ex][0] not in muscle_groups:
                    muscle_groups.append(data[ex][0])
            while new_input not in muscle_groups:
                count = 1
                print()
                for m in muscle_groups:
                    print(f'{count}. {m}')
                    count += 1
                print()
                try:
                    index2 = int(input("Ny muskelgrupp (Tryck 0 för att lämna): "))
                except:
                    index2 = -1
                if index2 == 0:
                    return 0
                elif index2 > 0 and index2 <= len(muscle_groups):
                    new_input = muscle_groups[index2-1]
                else:
                    print("Välj en existerande muskelgrupp") 
            data[exercise][0] = new_input
        else:
            new_input = input("Nytt namn: ")
            new_input = new_input.title()
            data[new_input] = data.pop(exercise)
    workout["Added"] = ""


def menu(workout):
    choice = ""
    while choice != "Q":
        print()
        print("-" * 40)
        print("A: Logga en övning")
        print("E: Editera en övning")
        print("I: Inställningar")
        print("L: Lista alla övningar")
        print("R: Se ditt 1RM")
        print("Ö: Lägg till en ny övning i listan")#TODO
        print("S: Se din weekly summary")
        print("Q: Avsluta")
        print("-" * 40)

        choice = input("Välj från menyn: ").upper()
        if choice == "A":
            add_exercise(workout)
        elif choice == "R":
            rm = calculate_rm()
            if rm[3]:
                width = 40
                print("-" * width)

                text = f"1 Rep Max för {rm[0]}:"
                print(text.center(width))
                print()
                if rm[1] != 0:
                    text = f"- Faktiska: {rm[1]}"
                    print(text.center(width))
                if rm[2] != 0:
                    text = f"- Uppskattade: {rm[2]}"
                    print(text.center(width))
                print()
                text = "Bra jobbat!"
                print(text.center(width))

        elif choice == "L":
            print_exercises()
        elif choice == "Ö": 
            create_exercise(workout)
        elif choice == "E":
            edit_exercise()
        elif choice == "I":
            change_goal()
        elif choice == "S":
            get_last_week()
        elif choice == "Q":
            update_exercises(workout)
            break
        else: 
            print("Välj en bokstav från menyn!")
        

def rm_formula(reps, weight):
    #Return the actual weight if it's a real 1RM.
    if reps == 1:
        return weight

    #Epley's formula
    return int(weight * (1 + reps/30))

def update_exercises(workout):
    if not workout:
        return

    for ex_name, sets_list in workout.items():
        if ex_name not in data:
            continue

        primary_muscle, weight_multiplier, prev_sets, prev_reps, prev_weight, one_rm, calc_rm = data[ex_name]

        sets_this = len(sets_list)
        reps_this = sum(r for (r, w) in sets_list)
        weight_this = sum(r * w * weight_multiplier for (r, w) in sets_list)

        new_sets = prev_sets + sets_this
        new_reps = prev_reps + reps_this
        new_weight = prev_weight + weight_this

        data[ex_name] = [primary_muscle, weight_multiplier, new_sets, new_reps, new_weight, one_rm, calc_rm]

    fieldnames = ["Name", "Primary muscle", "Weight Multiplier", "Sets", "Reps", "Weight", "1rm", "calculated1rm"]
    with open("exercises.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for name, vals in data.items():
            writer.writerow({
                "Name": name,
                "Primary muscle": vals[0],
                "Weight Multiplier": vals[1],
                "Sets": vals[2],
                "Reps": vals[3],
                "Weight": vals[4],
                "1rm": vals[5],
                "calculated1rm": vals[6],
            })

def save_workout(workout_name, workout):
    keys = list(workout.keys())
    if not workout or (len(keys) == 1 and keys[0] == "Added"):
        print("Inga övningar loggade, inget att spara.")
        return

    filename = f"workouts/{workout_name}.csv"
    fieldnames = ["Name", "Primary muscle", "Weight Multiplier", "Sets", "Reps", "Weight", "1rm", "Date", "Score"]

    today = date.today().isoformat()

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for ex_name, sets_list in workout.items():
            if ex_name not in data:
                continue

            primary_muscle, weight_multiplier, _, _, _, _, calc_rm = data[ex_name]
            one_rm = 0
            for set in sets_list:
                if set[1] > one_rm:
                    one_rm = set[1]

            total_reps = sum(r for (r, w) in sets_list)
            total_weight = sum(r * w * weight_multiplier for (r, w) in sets_list)

            writer.writerow({
                "Name": ex_name,
                "Primary muscle": primary_muscle,
                "Weight Multiplier": weight_multiplier,
                "Sets": str(sets_list),
                "Reps": total_reps,
                "Weight": total_weight,
                "1rm": one_rm,
                "Date": today,
                "Score": sessionscore
            })

    print(f"Workout sparad till '{filename}'!")

def calculate_rm():
    exercise = chose_exercise()
    if chose_exercise == []:
        return workout
    max_rep = data[exercise][5]
    calc_max_rep = data[exercise][6]
    haveData = True
    if max_rep == 0 and calc_max_rep == 0:
        print()
        print(f"Ingen data finns för {exercise}! Logga ett set först!")
        haveData = False
    return (exercise, max_rep, calc_max_rep, haveData)

def workout_exists(workout_name):
    folder = "workouts"
    return any(
        fname.lower() == f"{workout_name.lower()}.csv"
        for fname in os.listdir(folder)
    )

def start_app(workout):
    workout_name = input("Namn på passet (lämna tomt för dagens datum): ")
    while workout_exists(workout_name):
        print("Workoutnamnet finns redan!")
        workout_name = input("Namn på passet (lämna tomt för dagens datum): ")
    if workout_name == "":
        workout_name = datetime.now().strftime("%Y-%m-%d_%H.%M")
    menu(workout)
    save_workout(workout_name, workout)
    
def calculate_expected_1rm(exercise, setcount):
    lastworkouts=[]
    workouts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workouts")
    for filename in os.listdir(workouts_folder):
        path = os.path.join(workouts_folder, filename)
        with open(path, 'r', newline='', encoding='utf-8') as csvfile:
            past_workout=csv.DictReader(csvfile)
            for row in past_workout:
                if row['Name'] == exercise:
                    sets=row['Sets']
                    try: 
                        sets=ast.literal_eval(sets)
                        if sets and len(sets) > 0:
                            lastworkouts.append(rm_formula(sets[0][0],sets[0][1]))
                    except (ValueError, SyntaxError) as e:
                        print(e)
    if len(lastworkouts) > 0:
        erm = erm_calc(lastworkouts)
        erm *= (0.95**(setcount-1))
        print(f"1RM att slå: {data[exercise][5]}kg")

        if goal==0:
            strength=erm*0.85
            
            print(f"För träning med fokus på styrka, gör: {round_reps(reverse_epley(erm, round_kgs(strength)))} reps med {round_kgs(strength)}kg")
            print()
            erm=rm_formula(round_reps(reverse_epley(erm,round_kgs(strength))), round_kgs(strength))
        else:
            hypertrophy =erm*0.7
            print(f"För träning med fokus på hypertrofi, gör: {round_reps(reverse_epley(erm, round_kgs(hypertrophy)))} reps med {round_kgs(hypertrophy)}kg")
            print()
            erm=rm_formula(round_reps(reverse_epley(erm,round_kgs(hypertrophy))), round_kgs(hypertrophy))

        return erm
    return 0
                 
def erm_calc(sets):   #Tar snittökningen minus minsta värdet + största för att få ett expected 1rm   
    erm=sum(sets)
    erm=erm/len(sets) 
    erm-=min(sets)
    erm+=max(sets)
    return erm
    
def reverse_epley(erm, weight): #inverterar epleys formel
    suggested_reps=erm/weight
    suggested_reps-=1
    suggested_reps*=30
    return suggested_reps


def write_score(change):
    global score, goal, sessionscore
    read_score()
    fields=['score', 'goal']
    with open('settings.csv', 'w', newline='', encoding='utf-8') as f:
        writer=csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        score+=change
        sessionscore+=change
        writer.writerow({
                "score" : score,
                "goal" : goal
            })     
    print(f"Du har nu: {score} poäng!")   


def check_score(expected, actual):
    if actual>expected:
        print("Snyggt jobbat! Du slog förväntningarna!")
        write_score(1)
    elif actual==expected:
        print("Helt okej")
        return
    elif actual<expected:
        print("Bättre kan du!")
        write_score(-1)

def round_kgs(kg):
    r=kg%5
    if r>=2.5:
        kg = kg//5
        kg*=5
        kg+=5
    else:
        kg-=r
    return kg

def round_reps(reps):
    return int(reps+1)

def change_goal():
    global goal
    if goal == 0:
        mode = "styrka"
    else:
        mode = "hypertrofi"

    print(f"Ditt nuvarande träningssätt är {mode}")
    print("Sätt nytt mål (0 för att avbryta)")
    local_goal = -1
    while local_goal != 0:
        try:
            local_goal = int(input("Skriv 1 för styrka, eller 2 för hypertrofi: ")) - 1
            if local_goal == 1 or local_goal == 0:
                goal = local_goal
                break
        except:
            print("Skriv in en siffra!")
        print("Välj antingen 1 eller 2!")
        
    
def is_within_past_week(given_date):
    given_date = datetime.strptime(given_date, '%Y-%m-%d').date() 
    today = date.today()
    one_week_ago = today - timedelta(days=7)
    return one_week_ago <= given_date <= today

def get_last_week():
    weeklyscore=0
    muscle_sets = {}
    workouts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workouts")
    for filename in os.listdir(workouts_folder):
        path = os.path.join(workouts_folder, filename)
        with open(path, 'r', newline='', encoding='utf-8') as csvfile:
            past_workout=csv.DictReader(csvfile)
            for row in past_workout:
                if is_within_past_week(row['Date']):
                    sets_list = ast.literal_eval(row['Sets'])
                    num_sets = len(sets_list)
                    muscle = row["Primary muscle"]
                    if muscle in muscle_sets:
                        muscle_sets[muscle] += num_sets
                    else:
                        muscle_sets[muscle] = num_sets
                    weeklyscore+=int(row["Score"])
    for i in muscle_sets:
        print(i)
    print(weeklyscore)
    
if __name__ == "__main__":
    workout = {}
    start_app(workout)