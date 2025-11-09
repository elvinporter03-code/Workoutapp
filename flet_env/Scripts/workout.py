import flet as ft
import csv
import os
import ast
from datetime import date, datetime, timedelta

class WorkoutApp:
    def __init__(self):
        self.goal = 0
        self.score = 0
        self.sessionscore = 0
        self.data = {}
        self.current_workout = {}
        self.pb_count = 0
        self.load_data()
        self.load_score()
    
    def get_data_path(self, filename):
        """Get the correct path for data files - look in project directory"""
        venv_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_dir = os.path.dirname(venv_dir)
        project_path = os.path.join(project_dir, filename)
        if os.path.exists(project_path):
            return project_path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, filename)
    
    def load_score(self):
        try:
            file_path = self.get_data_path('settings.csv')
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.score = int(row['score'])
                    self.goal = int(row['goal'])
        except FileNotFoundError:
            self.score = 0
            self.goal = 0
    
    def load_data(self):
        try:
            file_path = self.get_data_path('exercises.csv')
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row["Name"]
                    self.data[name] = [
                        row["Primary muscle"],
                        row["Secondary muscle"],
                        float(row["Weight Multiplier"]),
                        int(row["Sets"]),
                        int(row["Reps"]),
                        float(row["Weight"]),
                        float(row["1rm"]),
                        int(row["calculated1rm"])
                    ]
        except FileNotFoundError:
            self.data = {}
    
    def save_score(self):
        try:
            file_path = self.get_data_path('settings.csv')
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['score', 'goal'])
                writer.writeheader()
                writer.writerow({'score': self.score, 'goal': self.goal})
        except Exception as e:
            print(f"Error saving score: {e}")
    
    def save_exercises(self):
        """Save exercises to CSV file"""
        try:
            file_path = self.get_data_path('exercises.csv')
            fieldnames = ["Name", "Primary muscle", "Secondary muscle", "Weight Multiplier", 
                         "Sets", "Reps", "Weight", "1rm", "calculated1rm"]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for name, data in self.data.items():
                    writer.writerow({
                        "Name": name,
                        "Primary muscle": data[0],
                        "Secondary muscle": data[1],
                        "Weight Multiplier": data[2],
                        "Sets": data[3],
                        "Reps": data[4],
                        "Weight": data[5],
                        "1rm": data[6],
                        "calculated1rm": data[7]
                    })
        except Exception as e:
            print(f"Error saving exercises: {e}")
    
    def save_workout(self, workout_name, workout_data):
        """Save workout data to workouts folder"""
        try:
            workouts_folder = self.get_data_path("workouts")
            os.makedirs(workouts_folder, exist_ok=True)
            
            filename = f"{workout_name}.csv"
            file_path = os.path.join(workouts_folder, filename)
            
            fieldnames = ["Name", "Primary muscle", "Secondary muscle", "Weight Multiplier", 
                         "Sets", "Reps", "Weight", "1rm", "Date", "Score"]
            
            today = date.today().isoformat()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for exercise_name, sets_data in workout_data.items():
                    if exercise_name not in self.data:
                        continue
                    
                    exercise_info = self.data[exercise_name]
                    total_reps = sum(reps for reps, weight in sets_data)
                    total_weight = sum(reps * weight * exercise_info[2] for reps, weight in sets_data)
                    best_1rm = max(weight for reps, weight in sets_data) if sets_data else 0
                    
                    writer.writerow({
                        "Name": exercise_name,
                        "Primary muscle": exercise_info[0],
                        "Secondary muscle": exercise_info[1],
                        "Weight Multiplier": exercise_info[2],
                        "Sets": str(sets_data),  # Store actual sets as string
                        "Reps": total_reps,
                        "Weight": total_weight,
                        "1rm": best_1rm,
                        "Date": today,
                        "Score": self.sessionscore
                    })
            
            print(f"Workout saved to '{file_path}'!")
            return True
            
        except Exception as e:
            print(f"Error saving workout: {e}")
            return False
    
    def save_active_workout(self, workout_data):
        """Save active workout to active_workout.csv"""
        try:
            file_path = self.get_data_path('active_workout.csv')
            fieldnames = ["Exercise", "Set", "Reps", "Weight", "Date", "Time"]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for exercise_name, sets_data in workout_data.items():
                    for i, (reps, weight) in enumerate(sets_data, 1):
                        now = datetime.now()
                        writer.writerow({
                            "Exercise": exercise_name,
                            "Set": i,
                            "Reps": reps,
                            "Weight": weight,
                            "Date": now.strftime('%Y-%m-%d'),
                            "Time": now.strftime('%H:%M:%S')
                        })
            
            return True
        except Exception as e:
            print(f"Error saving active workout: {e}")
            return False
    
    def load_active_workout(self):
        """Load active workout from CSV"""
        try:
            file_path = self.get_data_path('active_workout.csv')
            workout_data = {}
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    exercise = row["Exercise"]
                    reps = int(row["Reps"])
                    weight = float(row["Weight"])
                    
                    if exercise not in workout_data:
                        workout_data[exercise] = []
                    
                    workout_data[exercise].append((reps, weight))
            
            return workout_data
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading active workout: {e}")
            return {}
    
    def clear_active_workout(self):
        """Clear the active workout file"""
        try:
            file_path = self.get_data_path('active_workout.csv')
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error clearing active workout: {e}")
            return False

    def create_exercise(self, name, primary_muscle, secondary_muscle, weight_multiplier=1.0):
        """Create a new exercise"""
        name_title = name.title()
        if name_title in self.data:
            return False, "Exercise already exists"
        
        self.data[name_title] = [
            primary_muscle,
            secondary_muscle,
            weight_multiplier,
            0,  # sets
            0,  # reps
            0,  # weight
            0,  # 1rm
            0   # calculated1rm
        ]
        self.save_exercises()
        return True, "Exercise created successfully"
    
    def edit_exercise(self, old_name, new_name=None, primary_muscle=None, secondary_muscle=None, weight_multiplier=None):
        """Edit an existing exercise"""
        if old_name not in self.data:
            return False, "Exercise not found"
        
        if new_name and new_name != old_name:
            self.data[new_name] = self.data.pop(old_name)
            old_name = new_name
        
        if primary_muscle:
            self.data[old_name][0] = primary_muscle
        if secondary_muscle:
            self.data[old_name][1] = secondary_muscle
        if weight_multiplier:
            self.data[old_name][2] = weight_multiplier
        
        self.save_exercises()
        return True, "Exercise updated successfully"
    
    def calculate_1rm(self, exercise_name):
        """Calculate 1RM for an exercise"""
        if exercise_name not in self.data:
            return None, None, False
        
        actual_1rm = self.data[exercise_name][6]
        calculated_1rm = self.data[exercise_name][7]
        has_data = actual_1rm > 0 or calculated_1rm > 0
        
        return actual_1rm, calculated_1rm, has_data
    
    # YOUR ORIGINAL LOGIC FUNCTIONS
    def rm_formula(self, reps, weight):
        """Return the actual weight if it's a real 1RM."""
        if reps == 1:
            return weight
        # Epley's formula
        return int(weight * (1 + reps/30))
    
    def reverse_epley(self, erm, weight):
        """Inverterar epleys formel"""
        suggested_reps = erm / weight
        suggested_reps -= 1
        suggested_reps *= 30
        return suggested_reps
    
    def round_kgs(self, kg):
        r = kg % 5
        if r >= 2.5:
            kg = kg // 5
            kg *= 5
            kg += 5
        else:
            kg -= r
        return kg
    
    def round_reps(self, reps):
        return int(reps + 1)
    
    def calculate_expected_1rm(self, exercise, setcount):
        """Calculate expected 1RM based on previous workouts"""
        try:
            lastworkouts = []
            workouts_folder = self.get_data_path("workouts")
            
            if not os.path.exists(workouts_folder):
                return 0
                
            for filename in os.listdir(workouts_folder):
                path = os.path.join(workouts_folder, filename)
                with open(path, 'r', newline='', encoding='utf-8') as csvfile:
                    past_workout = csv.DictReader(csvfile)
                    for row in past_workout:
                        if row['Name'] == exercise:
                            sets = row['Sets']
                            try: 
                                sets = ast.literal_eval(sets)
                                if sets and len(sets) > 0:
                                    lastworkouts.append(self.rm_formula(sets[0][0], sets[0][1]))
                            except (ValueError, SyntaxError) as e:
                                print(e)
            
            if len(lastworkouts) > 0:
                erm = self.erm_calc(lastworkouts)
                erm *= (0.95**(setcount-1))
                return erm
            return 0
        except Exception as e:
            print(f"Error calculating expected 1RM: {e}")
            return 0
    
    def erm_calc(self, sets):
        """Tar snittökningen minus minsta värdet + största för att få ett expected 1rm"""
        if not sets:
            return 0
        erm = sum(sets)
        erm = erm / len(sets) 
        erm -= min(sets)
        erm += max(sets)
        return erm
    
    def get_suggested_workout(self, exercise_name, set_number):
        """Get suggested reps and weight based on your original algorithm"""
        expected_rm = self.calculate_expected_1rm(exercise_name, set_number)
        
        if expected_rm == 0:
            # No previous data, return defaults
            return 8, 65
        
        if self.goal == 0:  # Strength
            strength_weight = expected_rm * 0.85
            rounded_weight = self.round_kgs(strength_weight)
            suggested_reps = self.round_reps(self.reverse_epley(expected_rm, rounded_weight))
        else:  # Hypertrophy
            hypertrophy_weight = expected_rm * 0.7
            rounded_weight = self.round_kgs(hypertrophy_weight)
            suggested_reps = self.round_reps(self.reverse_epley(expected_rm, rounded_weight))
        
        return suggested_reps, rounded_weight
    
    def write_score(self, change):
        """Your original scoring logic"""
        self.load_score()
        self.score += change
        self.sessionscore += change
        self.save_score()
        return self.score
    
    def check_score(self, expected, actual, dropset):
        """Your original scoring logic"""
        if dropset and self.goal == 1:
            self.write_score(1)
        else:
            if actual > expected:
                print("Snyggt jobbat!")
                self.write_score(2)
            elif actual == expected:
                print("Helt okej")
                return
            elif actual < expected:
                print("Bättre kan du!")
                self.write_score(-2)
    
    def get_weekly_summary(self):
        try:
            weekly_score = 0
            muscle_sets = {}
            
            workouts_folder = self.get_data_path("workouts")
            if not os.path.exists(workouts_folder):
                return weekly_score, muscle_sets
            
            for filename in os.listdir(workouts_folder):
                if filename.endswith('.csv'):
                    path = os.path.join(workouts_folder, filename)
                    with open(path, 'r', newline='', encoding='utf-8') as csvfile:
                        past_workout = csv.DictReader(csvfile)
                        for row in past_workout:
                            workout_date = row.get('Date', '')
                            if self.is_within_past_week(workout_date):
                                try:
                                    sets_list = ast.literal_eval(row['Sets'])
                                    num_sets = len(sets_list)
                                    muscle = row["Primary muscle"]
                                    smuscle = row["Secondary muscle"]
                                    
                                    if muscle in muscle_sets:
                                        muscle_sets[muscle] += num_sets
                                    else:
                                        muscle_sets[muscle] = num_sets
                                    
                                    if smuscle in muscle_sets:
                                        muscle_sets[smuscle] += (0.5 * num_sets)
                                    else:
                                        muscle_sets[smuscle] = (0.5 * num_sets)
                                    
                                    weekly_score += int(row.get("Score", 0))
                                except:
                                    continue
            return weekly_score, muscle_sets
        except Exception as e:
            print(f"Error loading weekly summary: {e}")
            return 0, {}
    
    def is_within_past_week(self, given_date):
        try:
            given_date = datetime.strptime(given_date, '%Y-%m-%d').date()
            today = date.today()
            one_week_ago = today - timedelta(days=7)
            return one_week_ago <= given_date <= today
        except:
            return False

def main(page: ft.Page):
    # Configure the app for responsive design
    page.title = "Workout"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.spacing = 0
    
    app = WorkoutApp()
    
    # Global variables
    current_exercise = ""
    current_set = 1
    is_dropset = False
    current_expected_rm = 0
    pb_stars_text = ""
    workout_data = app.load_active_workout()  # Load active workout if exists
    
    # Store UI components for real-time updates
    current_reps_field = None
    current_weight_field = None
    current_goal_toggle = None
    current_dropset_button = None
    
    # Responsive scaling functions
    def get_padding():
        base_padding = max(10, min(20, page.width * 0.03))
        return base_padding
    
    def get_font_size(size_type):
        base_size = page.width * 0.04
        sizes = {
            "h1": max(24, min(36, base_size * 1.2)),
            "h2": max(18, min(24, base_size * 0.9)),
            "h3": max(14, min(18, base_size * 0.7)),
            "body": max(12, min(16, base_size * 0.6)),
            "small": max(10, min(12, base_size * 0.5)),
        }
        return sizes.get(size_type, sizes["body"])
    
    def get_container_padding():
        return max(15, min(30, page.width * 0.05))
    
    def get_grid_spacing():
        return max(8, min(15, page.width * 0.02))
    
    def update_suggestions():
        """Update the suggestion fields with current values"""
        if current_exercise and current_reps_field and current_weight_field:
            suggested_reps, suggested_weight = app.get_suggested_workout(current_exercise, current_set)
            current_reps_field.value = str(suggested_reps)
            current_weight_field.value = str(suggested_weight)
            page.update()
    
    def update_goal_display():
        """Update goal toggle display"""
        if current_goal_toggle:
            goal_text = "Strength" if app.goal == 0 else "Hypertrophy"
            goal_icon = ft.Icons.FITNESS_CENTER if app.goal == 0 else ft.Icons.SPEED
            goal_color = ft.Colors.BLUE_400 if app.goal == 0 else ft.Colors.PURPLE_400
            
            current_goal_toggle.content = ft.Row([
                ft.Icon(goal_icon, color=goal_color, size=get_font_size("h3")),
                ft.Text(goal_text, color=ft.Colors.WHITE, size=get_font_size("body")),
            ], tight=True)
            page.update()
    
    def update_dropset_display():
        """Update dropset button display"""
        if current_dropset_button:
            dropset_text = "💧 DROPSET ACTIVE" if is_dropset else "💧 SWITCH TO DROPSET"
            dropset_color = ft.Colors.GREEN_300 if is_dropset else ft.Colors.BLUE_300
            dropset_bgcolor = ft.Colors.GREEN_900 if is_dropset else ft.Colors.TRANSPARENT
            
            current_dropset_button.content = ft.Row([
                ft.Icon(ft.Icons.WATER_DROP, color=dropset_color, size=get_font_size("h3")),
                ft.Text(dropset_text, size=get_font_size("body"), color=dropset_color, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER)
            current_dropset_button.bgcolor = dropset_bgcolor
            current_dropset_button.border = ft.border.all(2, dropset_color)
            page.update()
    
    # DASHBOARD SCREEN - UPDATED WITH ACTIVE WORKOUT BUTTON
    def build_dashboard():
        weekly_score, muscle_sets = app.get_weekly_summary()
        padding = get_padding()
        
        # Check if there's an active workout
        has_active_workout = len(workout_data) > 0
        
        # Goal toggle - NOW WITH REAL-TIME UPDATES
        goal_text = "Strength" if app.goal == 0 else "Hypertrophy"
        goal_icon = ft.Icons.FITNESS_CENTER if app.goal == 0 else ft.Icons.SPEED
        
        goal_toggle = ft.Container(
            content=ft.Row([
                ft.Icon(goal_icon, color=ft.Colors.BLUE_400, size=get_font_size("h3")),
                ft.Text(goal_text, color=ft.Colors.WHITE, size=get_font_size("body")),
            ], tight=True),
            on_click=lambda e: toggle_goal(e),
            padding=get_padding(),
            border_radius=10,
        )
        
        # Active workout button if there's an active workout
        active_workout_button = None
        if has_active_workout:
            total_sets = sum(len(sets) for sets in workout_data.values())
            active_workout_button = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FITNESS_CENTER, size=get_font_size("h2"), color=ft.Colors.ORANGE),
                    ft.Column([
                        ft.Text("ACTIVE WORKOUT", size=get_font_size("h3"), weight=ft.FontWeight.BOLD),
                        ft.Text(f"{len(workout_data)} exercises, {total_sets} sets", 
                               size=get_font_size("small"), color=ft.Colors.WHITE70),
                    ], expand=True),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=get_font_size("h3"), color=ft.Colors.WHITE54),
                ]),
                bgcolor=ft.Colors.ORANGE_900,
                padding=get_container_padding(),
                border_radius=15,
                on_click=lambda e: page.go("/active-workout"),
                margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
            )
        
        dashboard_content = [
            ft.Container(
                content=ft.Row([
                    ft.Text("🏋️ Workout", size=get_font_size("h1"), weight=ft.FontWeight.BOLD, expand=True),
                    goal_toggle,
                ]),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("CURRENT SCORE", size=get_font_size("h3"), color=ft.Colors.WHITE54),
                    ft.Text(f"🏆 {app.score}", size=get_font_size("h1"), weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=padding,
            ),
        ]
        
        # Add active workout button if there's an active workout
        if active_workout_button:
            dashboard_content.append(active_workout_button)
        
        dashboard_content.extend([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PLAY_ARROW, size=get_font_size("h1"), color=ft.Colors.WHITE),
                    ft.Text("START WORKOUT", size=get_font_size("h2"), weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                bgcolor=ft.Colors.BLUE_600,
                padding=get_container_padding(),
                border_radius=15,
                on_click=lambda e: page.go("/exercise-selection"),
                margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
            ),
            
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.EDIT, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("EDIT", size=get_font_size("body"), color=ft.Colors.WHITE),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        bgcolor=ft.Colors.GREY_900,
                        padding=get_container_padding(),
                        border_radius=10,
                        on_click=lambda e: page.go("/edit-exercises"),
                        expand=True,
                    ),
                    ft.Container(width=get_grid_spacing()),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("PROGRESS", size=get_font_size("body"), color=ft.Colors.WHITE),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        bgcolor=ft.Colors.GREY_900,
                        padding=get_container_padding(),
                        border_radius=10,
                        on_click=lambda e: page.go("/progress"),
                        expand=True,
                    ),
                ]),
                padding=ft.padding.symmetric(horizontal=padding),
            ),
            
            ft.Container(
                content=build_weekly_summary(weekly_score, muscle_sets),
                bgcolor=ft.Colors.GREY_900,
                padding=get_container_padding(),
                border_radius=10,
                margin=ft.margin.all(padding),
            ),
        ])
        
        return ft.Column(dashboard_content, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    def build_weekly_summary(weekly_score, muscle_sets):
        content = [
            ft.Row([
                ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.WHITE, size=get_font_size("h2")),
                ft.Text("WEEKLY SUMMARY", size=get_font_size("h2"), weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(color=ft.Colors.GREY_800),
        ]
        
        if muscle_sets:
            for muscle, sets in list(muscle_sets.items())[:4]:
                bar_length = min(int(sets), 12)
                content.append(ft.Text(f"{muscle}: {'█' * bar_length} {sets:.1f} sets", 
                                    size=get_font_size("body"), color=ft.Colors.WHITE))
            content.append(ft.Text(f"Weekly Score: ⭐ {weekly_score}", 
                                size=get_font_size("body"), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD))
        else:
            content.append(ft.Text("No workouts this week", 
                                size=get_font_size("body"), color=ft.Colors.WHITE54))
        
        return ft.Column(content, spacing=8)
    
    # EXERCISE SELECTION SCREEN - UPDATED WITH SMALLER BUTTONS
    def build_exercise_selection():
        muscle_groups = sorted(list(set([exercise_data[0] for exercise_data in app.data.values()])))
        padding = get_padding()
        grid_spacing = get_grid_spacing()
        
        muscle_grid = ft.GridView(
            expand=True,
            runs_count=3,  # Increased from 2 to 3 for smaller buttons
            spacing=grid_spacing,
            run_spacing=grid_spacing,
            padding=padding,
        )
        
        muscle_emojis = {
            "Chest": "💪", "Back": "🦵", "Legs": "🦵🏽", "Shoulders": "🏋️",
            "Biceps": "💪", "Triceps": "💪", "Forearms": "🤏", "Core": "🏃", "Abs": "🏃"
        }
        
        for muscle in muscle_groups:
            exercise_count = sum(1 for ex_data in app.data.values() if ex_data[0] == muscle)
            emoji = muscle_emojis.get(muscle, "🏋️")
            
            muscle_grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(emoji, size=get_font_size("h2")),  # Smaller emoji
                        ft.Text(muscle, size=get_font_size("small"), weight=ft.FontWeight.BOLD),  # Smaller text
                        ft.Text(f"({exercise_count})", size=get_font_size("small"), color=ft.Colors.WHITE54),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),  # Reduced spacing
                    bgcolor=ft.Colors.GREY_900,
                    padding=10,  # Reduced padding for smaller buttons
                    border_radius=8,
                    on_click=lambda e, m=muscle: select_muscle_group(m),
                )
            )
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.ARROW_BACK, 
                        on_click=lambda e: page.go("/"),
                        icon_size=get_font_size("h2")
                    ),
                    ft.Text("Select Muscle Group", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                ]),
                padding=padding,
            ),
            muscle_grid,
        ], expand=True)
    
    def select_muscle_group(selected_muscle):
        exercises = [name for name, data in app.data.items() if data[0] == selected_muscle]
        
        exercise_options = []
        for ex in exercises:
            exercise_data = app.data[ex]
            exercise_options.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(ex, size=get_font_size("h3"), weight=ft.FontWeight.BOLD),
                            ft.Text(f"Secondary: {exercise_data[1]}", 
                                   size=get_font_size("small"), color=ft.Colors.WHITE54),
                        ], expand=True),
                        ft.Text(f"{exercise_data[3]} sets", 
                               size=get_font_size("small"), color=ft.Colors.WHITE54),
                    ]),
                    bgcolor=ft.Colors.GREY_800,
                    padding=get_container_padding(),
                    border_radius=8,
                    on_click=lambda e, ex_name=ex: start_exercise_logging(ex_name),
                )
            )
        
        exercise_list_view = ft.View(
            "/exercise-list",
            [
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK, 
                            on_click=lambda e: page.go("/exercise-selection"),
                            icon_size=get_font_size("h2")
                        ),
                        ft.Text(f"{selected_muscle} Exercises", 
                               size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                    ]),
                    padding=get_padding(),
                ),
                ft.Container(
                    content=ft.Column(
                        exercise_options, 
                        scroll=ft.ScrollMode.ADAPTIVE, 
                        spacing=get_grid_spacing()
                    ),
                    padding=get_padding(),
                    expand=True,
                )
            ]
        )
        
        page.views.append(exercise_list_view)
        page.update()
    
    def start_exercise_logging(exercise_name):
        nonlocal current_exercise, current_set, is_dropset, current_expected_rm
        current_exercise = exercise_name
        current_set = 1
        is_dropset = False
        # Initialize workout data for this exercise if not exists
        if current_exercise not in workout_data:
            workout_data[current_exercise] = []
        # Calculate expected 1RM for suggestions
        current_expected_rm = app.calculate_expected_1rm(exercise_name, current_set)
        page.go("/set-logging")
    
    # SET LOGGING SCREEN - UPDATED WITH REAL-TIME UPDATES
    def build_set_logging():
        if not current_exercise:
            page.go("/exercise-selection")
            return ft.Text("Loading...")
            
        padding = get_padding()
        container_padding = get_container_padding()
        
        # Get suggested reps and weight based on your algorithm - UPDATED TO USE CURRENT STATE
        suggested_reps, suggested_weight = app.get_suggested_workout(current_exercise, current_set)
        
        # Create responsive text fields with suggested values
        nonlocal current_reps_field, current_weight_field
        current_reps_field = ft.TextField(
            value=str(suggested_reps), 
            text_size=get_font_size("h1"), 
            text_align=ft.TextAlign.CENTER, 
            border="none",
            content_padding=container_padding
        )
        
        current_weight_field = ft.TextField(
            value=str(suggested_weight), 
            text_size=get_font_size("h1"), 
            text_align=ft.TextAlign.CENTER, 
            border="none",
            content_padding=container_padding
        )
        
        # Dropset button with enhanced visual indicators - UPDATED FOR REAL-TIME
        dropset_text = "💧 DROPSET ACTIVE" if is_dropset else "💧 SWITCH TO DROPSET"
        dropset_color = ft.Colors.GREEN_300 if is_dropset else ft.Colors.BLUE_300
        dropset_bgcolor = ft.Colors.GREEN_900 if is_dropset else ft.Colors.TRANSPARENT
        
        nonlocal current_dropset_button
        current_dropset_button = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WATER_DROP, color=dropset_color, size=get_font_size("h3")),
                ft.Text(dropset_text, size=get_font_size("body"), color=dropset_color, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            on_click=lambda e: toggle_dropset(e),
            padding=container_padding,
            border_radius=10,
            border=ft.border.all(2, dropset_color),
            bgcolor=dropset_bgcolor,
            margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
        )
        
        # Goal toggle for set logging screen - UPDATED FOR REAL-TIME
        goal_text = "Strength" if app.goal == 0 else "Hypertrophy"
        goal_icon = ft.Icons.FITNESS_CENTER if app.goal == 0 else ft.Icons.SPEED
        goal_color = ft.Colors.BLUE_400 if app.goal == 0 else ft.Colors.PURPLE_400
        
        nonlocal current_goal_toggle
        current_goal_toggle = ft.Container(
            content=ft.Row([
                ft.Icon(goal_icon, color=goal_color, size=get_font_size("h3")),
                ft.Text(goal_text, color=ft.Colors.WHITE, size=get_font_size("body")),
            ], tight=True),
            on_click=lambda e: toggle_goal(e),
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.GREY_800,
        )
        
        # PB stars display
        pb_stars_display = ft.Text(pb_stars_text, size=20, color=ft.Colors.YELLOW)
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    pb_stars_display,
                    ft.Text(current_exercise, size=get_font_size("h2"), weight=ft.FontWeight.BOLD, 
                           expand=True, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Set {current_set}", size=get_font_size("h3"), color=ft.Colors.WHITE54),
                ]),
                padding=padding,
            ),
            
            # Goal toggle and 1RM info
            ft.Container(
                content=ft.Row([
                    current_goal_toggle,
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"1RM to beat: {current_expected_rm:.0f}kg", 
                                   size=get_font_size("body"), color=ft.Colors.WHITE54, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True,
                    ),
                ]),
                padding=padding//2,
            ) if current_expected_rm > 0 else ft.Container(
                content=ft.Row([
                    current_goal_toggle,
                    ft.Container(expand=True),
                ]),
                padding=padding//2,
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("REPS", size=get_font_size("h3"), color=ft.Colors.WHITE54),
                    current_reps_field,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_900,
                padding=container_padding,
                border_radius=15,
                margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("WEIGHT (kg)", size=get_font_size("h3"), color=ft.Colors.WHITE54),
                    current_weight_field,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_900,
                padding=container_padding,
                border_radius=15,
                margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
            ),
            
            # Dropset button
            current_dropset_button,
            
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("ADD SET", size=get_font_size("body"), color=ft.Colors.WHITE),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        bgcolor=ft.Colors.GREEN_600,
                        padding=container_padding,
                        border_radius=10,
                        on_click=lambda e: add_set(current_reps_field.value, current_weight_field.value),
                        expand=True,
                    ),
                    ft.Container(width=get_grid_spacing()),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.SKIP_NEXT, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("NEXT EXERCISE", size=get_font_size("body"), color=ft.Colors.WHITE),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        bgcolor=ft.Colors.BLUE_600,
                        padding=container_padding,
                        border_radius=10,
                        on_click=lambda e: page.go("/exercise-selection"),
                        expand=True,
                    ),
                ]),
                padding=ft.padding.symmetric(horizontal=padding),
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    # ACTIVE WORKOUT SCREEN - NEW SCREEN TO VIEW ACTIVE WORKOUT
    def build_active_workout():
        padding = get_padding()
        container_padding = get_container_padding()
        
        if not workout_data:
            content = [
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK, 
                            on_click=lambda e: page.go("/"),
                            icon_size=get_font_size("h2")
                        ),
                        ft.Text("Active Workout", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                    ]),
                    padding=padding,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FITNESS_CENTER, size=get_font_size("h1"), color=ft.Colors.WHITE54),
                        ft.Text("No Active Workout", size=get_font_size("h2"), color=ft.Colors.WHITE54),
                        ft.Text("Start a workout to see your progress here", 
                               size=get_font_size("body"), color=ft.Colors.WHITE54),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=container_padding,
                    expand=True,
                ),
            ]
        else:
            exercises_list = []
            total_sets = 0
            
            for exercise_name, sets in workout_data.items():
                total_sets += len(sets)
                set_details = []
                for i, (reps, weight) in enumerate(sets, 1):
                    set_details.append(ft.Text(f"Set {i}: {reps} reps × {weight}kg", 
                                             size=get_font_size("small"), color=ft.Colors.WHITE70))
                
                exercises_list.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(exercise_name, size=get_font_size("h3"), weight=ft.FontWeight.BOLD),
                            ft.Column(set_details, spacing=2),
                        ]),
                        bgcolor=ft.Colors.GREY_900,
                        padding=container_padding,
                        border_radius=10,
                        margin=ft.margin.only(bottom=padding//2),
                    )
                )
            
            content = [
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK, 
                            on_click=lambda e: page.go("/"),
                            icon_size=get_font_size("h2")
                        ),
                        ft.Text("Active Workout", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                    ]),
                    padding=padding,
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"{len(workout_data)}", size=get_font_size("h1"), weight=ft.FontWeight.BOLD),
                            ft.Text("Exercises", size=get_font_size("small"), color=ft.Colors.WHITE54),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        ft.Column([
                            ft.Text(f"{total_sets}", size=get_font_size("h1"), weight=ft.FontWeight.BOLD),
                            ft.Text("Sets", size=get_font_size("small"), color=ft.Colors.WHITE54),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=container_padding,
                    border_radius=10,
                    margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Exercises", size=get_font_size("h3"), weight=ft.FontWeight.BOLD),
                        ft.Divider(color=ft.Colors.GREY_700),
                        *exercises_list
                    ]),
                    padding=padding,
                    expand=True,
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=get_font_size("h2")),
                                ft.Text("ADD MORE", size=get_font_size("body"), color=ft.Colors.WHITE),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            bgcolor=ft.Colors.BLUE_600,
                            padding=container_padding,
                            border_radius=10,
                            on_click=lambda e: page.go("/exercise-selection"),
                            expand=True,
                        ),
                        ft.Container(width=get_grid_spacing()),
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=get_font_size("h2")),
                                ft.Text("FINISH", size=get_font_size("body"), color=ft.Colors.WHITE),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            bgcolor=ft.Colors.GREEN_600,
                            padding=container_padding,
                            border_radius=10,
                            on_click=lambda e: save_and_finish_workout(e),
                            expand=True,
                        ),
                    ]),
                    padding=ft.padding.symmetric(horizontal=padding, vertical=padding),
                ),
            ]
        
        return ft.Column(content, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    # CREATE EXERCISE SCREEN - NEW SCREEN
    def build_create_exercise():
        padding = get_padding()
        container_padding = get_container_padding()
        
        # Form fields
        name_field = ft.TextField(label="Exercise Name", text_size=get_font_size("body"))
        multiplier_field = ft.TextField(label="Weight Multiplier (default: 1.0)", value="1.0", text_size=get_font_size("body"))
        
        # Muscle group selection
        muscle_groups = sorted(list(set([exercise_data[0] for exercise_data in app.data.values()])))
        primary_dropdown = ft.Dropdown(
            label="Primary Muscle",
            options=[ft.dropdown.Option(m) for m in muscle_groups],
            text_size=get_font_size("body")
        )
        secondary_dropdown = ft.Dropdown(
            label="Secondary Muscle", 
            options=[ft.dropdown.Option(m) for m in muscle_groups],
            text_size=get_font_size("body")
        )
        
        def create_exercise_handler(e):
            if not name_field.value or not primary_dropdown.value or not secondary_dropdown.value:
                page.snack_bar = ft.SnackBar(content=ft.Text("Please fill all fields"))
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                multiplier = float(multiplier_field.value)
            except:
                multiplier = 1.0
            
            success, message = app.create_exercise(
                name_field.value,
                primary_dropdown.value,
                secondary_dropdown.value,
                multiplier
            )
            
            page.snack_bar = ft.SnackBar(content=ft.Text(message))
            page.snack_bar.open = True
            page.update()
            
            if success:
                page.go("/edit-exercises")
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.ARROW_BACK, 
                        on_click=lambda e: page.go("/edit-exercises"),
                        icon_size=get_font_size("h2")
                    ),
                    ft.Text("Create New Exercise", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                ]),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column([
                    name_field,
                    primary_dropdown,
                    secondary_dropdown,
                    multiplier_field,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("CREATE EXERCISE", size=get_font_size("h3"), color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=ft.Colors.GREEN_600,
                        padding=container_padding,
                        border_radius=10,
                        on_click=create_exercise_handler,
                        margin=ft.margin.only(top=padding),
                    ),
                ]),
                padding=padding,
                expand=True,
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    # 1RM CALCULATION SCREEN - NEW SCREEN
    def build_1rm_calculation():
        padding = get_padding()
        container_padding = get_container_padding()
        
        # Exercise selection
        exercises = list(app.data.keys())
        exercise_dropdown = ft.Dropdown(
            label="Select Exercise",
            options=[ft.dropdown.Option(ex) for ex in exercises],
            text_size=get_font_size("body")
        )
        
        result_display = ft.Column()
        
        def calculate_1rm_handler(e):
            if not exercise_dropdown.value:
                return
            
            actual_1rm, calculated_1rm, has_data = app.calculate_1rm(exercise_dropdown.value)
            
            result_display.controls.clear()
            
            if not has_data:
                result_display.controls.append(
                    ft.Text(f"No data available for {exercise_dropdown.value}", 
                           size=get_font_size("body"), color=ft.Colors.WHITE54)
                )
            else:
                result_display.controls.append(
                    ft.Text(f"1 Rep Max for {exercise_dropdown.value}:", 
                           size=get_font_size("h3"), weight=ft.FontWeight.BOLD)
                )
                
                if actual_1rm > 0:
                    result_display.controls.append(
                        ft.Text(f"Actual: {actual_1rm}kg", 
                               size=get_font_size("body"), color=ft.Colors.WHITE)
                    )
                
                if calculated_1rm > 0:
                    result_display.controls.append(
                        ft.Text(f"Calculated: {calculated_1rm}kg", 
                               size=get_font_size("body"), color=ft.Colors.WHITE)
                    )
                
                result_display.controls.append(
                    ft.Text("Great job!", 
                           size=get_font_size("body"), color=ft.Colors.GREEN,
                           weight=ft.FontWeight.BOLD)
                )
            
            page.update()
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.ARROW_BACK, 
                        on_click=lambda e: page.go("/"),
                        icon_size=get_font_size("h2")
                    ),
                    ft.Text("1RM Calculator", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                ]),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column([
                    exercise_dropdown,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CALCULATE, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("CALCULATE 1RM", size=get_font_size("h3"), color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=ft.Colors.BLUE_600,
                        padding=container_padding,
                        border_radius=10,
                        on_click=calculate_1rm_handler,
                        margin=ft.margin.only(top=padding, bottom=padding),
                    ),
                    result_display,
                ]),
                padding=padding,
                expand=True,
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    # WORKOUT SUMMARY SCREEN - UPDATED WITH WORKOUT SAVING
    def build_workout_summary():
        padding = get_padding()
        container_padding = get_container_padding()
        
        exercises_completed = []
        if workout_data:
            for exercise_name, sets in workout_data.items():
                if sets:  # Only show exercises with completed sets
                    exercises_completed.append(f"{exercise_name}: {len(sets)} sets ✓")
        
        exercises_column_content = []
        if exercises_completed:
            exercises_column_content.append(ft.Text("Exercises Completed:", size=get_font_size("h3"), weight=ft.FontWeight.BOLD))
            for ex in exercises_completed:
                exercises_column_content.append(ft.Text(ex, size=get_font_size("body")))
        else:
            exercises_column_content.append(ft.Text("No exercises completed", size=get_font_size("body"), color=ft.Colors.WHITE54))
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(pb_stars_text, size=20, color=ft.Colors.YELLOW),
                    ft.Text("Workout Complete!", size=get_font_size("h1"), weight=ft.FontWeight.BOLD, 
                           expand=True, text_align=ft.TextAlign.CENTER),
                ]),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("TODAY'S SCORE", size=get_font_size("h3"), color=ft.Colors.WHITE54),
                    ft.Text(f"+{app.sessionscore} ⭐", size=get_font_size("h1"), weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column(exercises_column_content),
                bgcolor=ft.Colors.GREY_900,
                padding=container_padding,
                border_radius=10,
                margin=ft.margin.symmetric(horizontal=padding, vertical=padding//2),
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ADD, size=get_font_size("h1"), color=ft.Colors.WHITE),
                            ft.Text("ADD MORE EXERCISES", size=get_font_size("h2"), weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        bgcolor=ft.Colors.BLUE_600,
                        padding=container_padding,
                        border_radius=10,
                        on_click=lambda e: page.go("/exercise-selection"),
                    ),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("SAVE & FINISH WORKOUT", size=get_font_size("h3"), color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=ft.Colors.GREEN_600,
                        padding=container_padding,
                        border_radius=10,
                        on_click=lambda e: save_and_finish_workout(e),
                        margin=ft.margin.only(top=padding//2),
                    ),
                ]),
                padding=padding,
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    # EDIT EXERCISES SCREEN - UPDATED WITH CREATE EXERCISE BUTTON
    def build_edit_exercises():
        padding = get_padding()
        
        exercises_list = ft.ListView(expand=1, spacing=get_grid_spacing())
        
        for exercise_name, exercise_data in app.data.items():
            exercises_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(exercise_name, size=get_font_size("h3"), weight=ft.FontWeight.BOLD),
                        ft.Text(f"Primary: {exercise_data[0]} | Secondary: {exercise_data[1]}", 
                               size=get_font_size("small"), color=ft.Colors.WHITE54),
                        ft.Text(f"Sets: {exercise_data[3]} | Reps: {exercise_data[4]} | 1RM: {exercise_data[6]}kg", 
                               size=get_font_size("small"), color=ft.Colors.WHITE54),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=get_container_padding(),
                    border_radius=10,
                )
            )
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.ARROW_BACK, 
                        on_click=lambda e: page.go("/"),
                        icon_size=get_font_size("h2")
                    ),
                    ft.Text("All Exercises", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                ]),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=get_font_size("h2")),
                            ft.Text("CREATE NEW EXERCISE", size=get_font_size("h3"), color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=ft.Colors.GREEN_600,
                        padding=get_container_padding(),
                        border_radius=10,
                        on_click=lambda e: page.go("/create-exercise"),
                        margin=ft.margin.only(bottom=padding),
                    ),
                    exercises_list,
                ]),
                padding=padding,
                expand=True,
            ),
        ], expand=True)
    
    # PROGRESS SCREEN
    def build_progress():
        padding = get_padding()
        container_padding = get_container_padding()
        
        progress_items = []
        for ex, data in app.data.items():
            if data[6] > 0 or data[7] > 0:
                progress_items.append(
                    ft.Text(f"• {ex}: {data[6]}kg (calc: {data[7]}kg)", size=get_font_size("body"))
                )
        
        progress_column_content = [
            ft.Text("1RM Progress", size=get_font_size("h2"), weight=ft.FontWeight.BOLD),
            ft.Divider(color=ft.Colors.GREY_700),
        ]
        
        if progress_items:
            for item in progress_items:
                progress_column_content.append(item)
        else:
            progress_column_content.append(ft.Text("No progress data yet", size=get_font_size("body"), color=ft.Colors.WHITE54))
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.ARROW_BACK, 
                        on_click=lambda e: page.go("/"),
                        icon_size=get_font_size("h2")
                    ),
                    ft.Text("Progress Analytics", size=get_font_size("h2"), weight=ft.FontWeight.BOLD, expand=True),
                ]),
                padding=padding,
            ),
            
            ft.Container(
                content=ft.Column(progress_column_content, scroll=ft.ScrollMode.ADAPTIVE),
                bgcolor=ft.Colors.GREY_900,
                padding=container_padding,
                border_radius=10,
                margin=padding,
                expand=True,
            ),
        ], expand=True)
    
    # NAVIGATION FUNCTIONS - UPDATED WITH WORKOUT SAVING AND REAL-TIME UPDATES
    def toggle_goal(e):
        app.goal = 1 - app.goal
        app.save_score()
        print(f"Goal changed to: {'Strength' if app.goal == 0 else 'Hypertrophy'}")
        # Update UI components in real-time
        update_goal_display()
        update_suggestions()
    
    def toggle_dropset(e):
        nonlocal is_dropset
        is_dropset = not is_dropset
        print(f"Dropset {'activated' if is_dropset else 'deactivated'}")
        # Update UI components in real-time
        update_dropset_display()
    
    def add_set(reps, weight):
        nonlocal current_set, pb_stars_text, current_expected_rm, workout_data
        try:
            reps_val = int(reps)
            weight_val = float(weight)
            
            # Store the set data
            if current_exercise in workout_data:
                workout_data[current_exercise].append((reps_val, weight_val))
            else:
                workout_data[current_exercise] = [(reps_val, weight_val)]
            
            # Save to active workout CSV
            app.save_active_workout(workout_data)
            
            # Calculate actual 1RM for scoring
            actual_rm = app.rm_formula(reps_val, weight_val)
            
            # Use your original scoring logic
            app.check_score(current_expected_rm, actual_rm, is_dropset)
            
            # Update UI
            current_set += 1
            app.pb_count += 1
            pb_stars_text = "★" * app.pb_count
            
            # Recalculate expected 1RM for next set
            current_expected_rm = app.calculate_expected_1rm(current_exercise, current_set)
            
            print(f"Added set: {reps_val} reps x {weight_val}kg for {current_exercise}")
            print(f"Total sets for {current_exercise}: {len(workout_data[current_exercise])}")
            
            # Update suggestions for next set
            update_suggestions()
            
        except ValueError:
            print("Invalid input for reps or weight")
    
    def save_and_finish_workout(e):
        nonlocal current_exercise, current_set, pb_stars_text, is_dropset, workout_data
        
        if workout_data:
            # Generate workout name with timestamp
            workout_name = datetime.now().strftime("%Y-%m-%d_%H.%M")
            
            # Save the workout to workouts folder
            success = app.save_workout(workout_name, workout_data)
            
            if success:
                print(f"Workout saved successfully as '{workout_name}'")
            else:
                print("Failed to save workout")
            
            # Clear active workout
            app.clear_active_workout()
        
        # Reset workout state
        current_exercise = ""
        current_set = 1
        app.sessionscore = 0
        pb_stars_text = ""
        is_dropset = False
        workout_data = {}
        
        page.go("/")
    
    def finish_workout(e):
        # This is now handled by save_and_finish_workout
        save_and_finish_workout(e)
    
    # Route handler - UPDATED WITH NEW ROUTES
    def route_change(e):
        troute = ft.TemplateRoute(page.route)
        
        if troute.match("/"):
            page.views.clear()
            page.views.append(ft.View("/", [build_dashboard()], padding=0))
        elif troute.match("/exercise-selection"):
            if not page.views or page.views[-1].route != "/exercise-selection":
                page.views.append(ft.View("/exercise-selection", [build_exercise_selection()], padding=0))
        elif troute.match("/set-logging"):
            if not page.views or page.views[-1].route != "/set-logging":
                page.views.append(ft.View("/set-logging", [build_set_logging()], padding=0))
        elif troute.match("/workout-summary"):
            if not page.views or page.views[-1].route != "/workout-summary":
                page.views.append(ft.View("/workout-summary", [build_workout_summary()], padding=0))
        elif troute.match("/edit-exercises"):
            if not page.views or page.views[-1].route != "/edit-exercises":
                page.views.append(ft.View("/edit-exercises", [build_edit_exercises()], padding=0))
        elif troute.match("/create-exercise"):
            if not page.views or page.views[-1].route != "/create-exercise":
                page.views.append(ft.View("/create-exercise", [build_create_exercise()], padding=0))
        elif troute.match("/progress"):
            if not page.views or page.views[-1].route != "/progress":
                page.views.append(ft.View("/progress", [build_progress()], padding=0))
        elif troute.match("/active-workout"):
            if not page.views or page.views[-1].route != "/active-workout":
                page.views.append(ft.View("/active-workout", [build_active_workout()], padding=0))
        elif troute.match("/1rm-calculator"):
            if not page.views or page.views[-1].route != "/1rm-calculator":
                page.views.append(ft.View("/1rm-calculator", [build_1rm_calculation()], padding=0))
        elif troute.match("/exercise-list"):
            pass
        
        page.update()
    
    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            page.go("/")
    
    # Set up event handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    def page_resize(e):
        page.update()
    
    page.on_resize = page_resize
    
    # Initialize with dashboard
    page.go("/")

# Run the app
if __name__ == "__main__":
    ft.app(target=main)