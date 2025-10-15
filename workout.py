import pandas
import os
#Jävla massa strul med att hitta rätt excercises.csv så fick lägga in den där långa mfen under
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "excercises.csv")
DataFrame=pandas.read_csv(csv_path)

def print_excercises(): 
    for index, row in DataFrame.iterrows():
        print(f"Exercise: {row['Name']}")
        print(f"Muscle: {row['Primary muscle']}")
        print(f"Weight Multiplier: {row['Weight Multiplier']}")
        print(f"Reps: {row['Reps']}, Weight: {row['Weight']}, 1RM: {row['1rm']}")
        print("-" * 30)

def create_workout():
    title=input("What's your workout called?\n")
    done=False
    DataFrame2 = pandas.DataFrame({
    'Name': [],
    'Primary muscle': [],  
    'Weight Multiplier': [],  
    'Reps': [],
    'Weight': [],
    '1rm': []
    })
    DataFrame2.to_csv(f'{title}.csv', index=False) #Just nu sparas alla nya workouts lokalt och inte i github
    #Fungerar bra när vi har det på laptop, men skulle vi porta det till mobil vet jag inte hur det går?
    while not done:
        current_excercise=input("Type the name of the excercise you want to do, or 1 if you're done\n")
        if current_excercise == '1':
            done=True
        else:
            for index, row in DataFrame.iterrows(): #Kollar om input finns i listan 
                found=False
                if row['Name']==current_excercise:
                    DataFrame2 = pandas.concat([DataFrame2, row.to_frame().T], ignore_index=True)
                    found=True
                    break
            if not found:
                print("Couldn't find that excercise, check your spelling")
                # Måste också lägga in en funktion för hur man lägger in nya egna här                
        
        
                
if __name__ == "__main__":
    print_excercises()
    create_workout()
