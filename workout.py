import pandas
DataFrame=pandas.read_csv("excercises.csv")

def get_excercises():
    for index, row in DataFrame.iterrows():
        print(f"Exercise: {row['Name']}")
        print(f"Muscle: {row['Primary muscle']}")
        print(f"Weight Multiplier: {row['Weight Multiplier']}")
        print(f"Reps: {row['Reps']}, Weight: {row['Weight']}, 1RM: {row['1rm']}")
        print("-" * 40)

if __name__ == "__main__":
    get_excercises()