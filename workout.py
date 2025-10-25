import csv
import os
from datetime import date

data = {}

#Automatiskt räkna ut PB för varje set

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
            index = int(input("Chose muscle group (To exit press 0): "))
        except:
            index = -1
        if index == 0:
            return 0
        elif index > 0 and index <= len(muscle_groups):
            choosen_muscle = muscle_groups[index-1]
        else:
            print("Choose an existing muscle group")
    
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
            index = int(input("Chose exercise: "))
            print()
        except:
            index = -1
        if index > 0 and index <= len(exercises):
            choosen_exercise = exercises[index-1]
        else:
            print("Choose an existing exercise")
    return choosen_exercise

def add_exercise(workout):
    choosen_exercise = chose_exercise()
    print(choosen_exercise)
    if choosen_exercise == 0:
        return workout
    sets = log_sets()
    for set in sets:
        if set[1] > data[choosen_exercise][5]:
            data[choosen_exercise][5] = set[1]
        calculated_rm = rm_formula(set[0], set[1])
        if calculated_rm > data[choosen_exercise][6]:
            print(calculated_rm)
            data[choosen_exercise][6] = calculated_rm
    if choosen_exercise in workout:
        for set in sets:
            workout[choosen_exercise].append(set)
        print(workout[choosen_exercise])
    else:
        workout[choosen_exercise] = sets
    return workout

def log_sets():
    sets = []
    weight = -1
    reps = -1
    count_set = 1
    while reps != 0:
        if reps == -1:
            try:
                reps = int(input(f"For set {count_set}. How many reps did you do? (Press 0 if you are done): "))
            except:
                reps = -1
                print("Reps should be an integer")

        if reps == 0:
            break
        if reps != -1:
            try:
                weight = float(input(f"For set {count_set}. With how many kg?: "))
                set = (reps, weight)
                sets.append(set)
                count_set += 1
                reps = -1
            except:
                print("Weight should be a floating number")
            
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
            index = int(input("Chose muscle group (To exit press 0): "))
        except:
            index = -1
        if index == 0:
            return []
        elif index > 0 and index <= len(muscle_groups):
            choosen_muscle = muscle_groups[index-1]
        else:
            print("Choose an existing muscle group")
    w_multiplier = -1
    while w_multiplier != 0:
        try:
            w_multiplier = float(input("What's the weight multiplier? (0 for default): "))
        except:
            print("Invalid multiplier")
            w_multiplier = -1
    if w_multiplier == 0:
        w_multiplier = 1
    data[new_ex_f] = [choosen_muscle, w_multiplier, 0, 0, 0, 0, 0]

    # So that the file is saved even when no workout is logged
    workout["Added"] = []

def menu(workout):
    choice = ""
    while choice != "Q":
        print()
        print("-" * 40)
        print("A: Logga en övning")
        print("E: Editera en övning")
        print("L: Lista alla övningar")
        print("R: Se ditt 1RM")
        print("Ö: Lägg till en ny övning i listan")#TODO
        print("-: Avsluta")
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
        elif choice == "-":
            update_exercises(workout)
            break
        else: 
            print("Chose a letter from the menu!")
        

def rm_formula(reps, weight):
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
    if not workout:
        print("No exercises were logged — nothing to save.")
        return

    filename = f"workouts/{workout_name}.csv"
    fieldnames = ["Name", "Primary muscle", "Weight Multiplier", "Sets", "Reps", "Weight", "1rm", "Date"]

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
                "Date": today
            })

    print(f"Workout saved to '{filename}'!")

def calculate_rm():
    exercise = chose_exercise()
    if chose_exercise == []:
        return workout
    max_rep = data[exercise][5]
    calc_max_rep = data[exercise][6]
    haveData = True
    if max_rep == 0 and calc_max_rep == 0:
        print()
        print("No data on this exercise! Try logging a set first!")
        haveData = False
    return (exercise, max_rep, calc_max_rep, haveData)

def workout_exists(workout_name):
    folder = "workouts"
    return any(
        fname.lower() == f"{workout_name.lower()}.csv"
        for fname in os.listdir(folder)
    )

def start_app(workout):
    workout_name = input("Name of workout: ")
    while workout_exists(workout_name):
        print("Workout name already exists!")
        workout_name = input("Name of workout: ")

    menu(workout)
    save_workout(workout_name, workout)


if __name__ == "__main__":
    workout = {}
    start_app(workout)