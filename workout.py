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
    
    def load_score(self):
        try:
            with open('settings.csv', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.score = int(row['score'])
                    self.goal = int(row['goal'])
        except FileNotFoundError:
            self.score = 0
            self.goal = 0
    
    def load_data(self):
        try:
            with open('exercises.csv', newline='', encoding='utf-8') as csvfile:
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
            print(f"Loaded {len(self.data)} exercises")
        except FileNotFoundError:
            self.create_default_exercises()
    
    def create_default_exercises(self):
        default_exercises = {
            "Bench Press": ["Chest", "Triceps", 1.0, 0, 0, 0, 0, 0],
            "Squats": ["Legs", "Core", 1.0, 0, 0, 0, 0, 0],
            "Pull-ups": ["Back", "Biceps", 1.0, 0, 0, 0, 0, 0]
        }
        self.data = default_exercises
    
    def get_weekly_summary(self):
        try:
            weekly_score = 0
            muscle_sets = {}
            
            workouts_folder = "workouts"
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
    # Configure the app for proper mobile support
    page.title = "Workout"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 15
    
    app = WorkoutApp()
    
    # Global variables for current exercise tracking
    current_exercise = "Bench Press"
    current_set = 1
    current_reps = ft.TextField(value="8", text_size=24, text_align=ft.TextAlign.CENTER, border="none")
    current_weight = ft.TextField(value="65", text_size=24, text_align=ft.TextAlign.CENTER, border="none")
    
    # PB Star indicator
    pb_stars = ft.Text("", size=20, color=ft.Colors.YELLOW)
    
    # DASHBOARD SCREEN
    def build_dashboard():
        weekly_score, muscle_sets = app.get_weekly_summary()
        
        # Goal toggle
        goal_text = "Strength" if app.goal == 0 else "Hypertrophy"
        goal_icon = ft.Icons.FITNESS_CENTER if app.goal == 0 else ft.Icons.SPEED
        
        goal_toggle = ft.Container(
            content=ft.Row([
                ft.Icon(goal_icon, color=ft.Colors.BLUE_400, size=20),
                ft.Text(goal_text, color=ft.Colors.WHITE, size=14),
            ], tight=True),
            on_click=toggle_goal,
            padding=8,
            border_radius=10,
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("🏋️ Workout", size=24, weight=ft.FontWeight.BOLD, expand=True),
                goal_toggle,
            ]),
            
            # Current score
            ft.Container(
                content=ft.Column([
                    ft.Text("CURRENT SCORE", size=16, color=ft.Colors.WHITE54),
                    ft.Text(f"🏆 {app.score}", size=48, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=20,
            ),
            
            # Start workout button
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PLAY_ARROW, size=48, color=ft.Colors.WHITE),
                    ft.Text("START WORKOUT", size=20, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.BLUE_600,
                padding=30,
                border_radius=15,
                on_click=lambda e: page.go("/exercise-selection"),
                margin=ft.margin.only(bottom=15),
            ),
            
            # Secondary buttons
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.EDIT, color=ft.Colors.WHITE, size=24),
                        ft.Text("EDIT", size=12, color=ft.Colors.WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.GREY_900,
                    padding=20,
                    border_radius=10,
                    on_click=lambda e: show_edit_exercises(),
                    expand=True,
                ),
                ft.Container(width=10),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.WHITE, size=24),
                        ft.Text("PROGRESS", size=12, color=ft.Colors.WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.GREY_900,
                    padding=20,
                    border_radius=10,
                    on_click=lambda e: show_progress(),
                    expand=True,
                ),
            ]),
            
            # Weekly summary
            ft.Container(
                content=build_weekly_summary(weekly_score, muscle_sets),
                bgcolor=ft.Colors.GREY_900,
                padding=20,
                border_radius=10,
                margin=ft.margin.only(top=20),
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE)
    
    def build_weekly_summary(weekly_score, muscle_sets):
        content = [
            ft.Row([
                ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.WHITE),
                ft.Text("WEEKLY SUMMARY", size=16, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(color=ft.Colors.GREY_800),
        ]
        
        for muscle, sets in list(muscle_sets.items())[:4]:
            bar_length = min(int(sets), 12)
            content.append(ft.Text(f"{muscle}: {'█' * bar_length} {sets:.1f} sets", 
                                size=14, color=ft.Colors.WHITE))
        
        content.append(ft.Text(f"Weekly Score: ⭐ {weekly_score}", 
                            size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD))
        
        return ft.Column(content, spacing=8)
    
    # EXERCISE SELECTION SCREEN
    def build_exercise_selection():
        muscle_groups = sorted(list(set([exercise_data[0] for exercise_data in app.data.values()])))
        
        muscle_grid = ft.GridView(
            expand=1,
            runs_count=2,
            spacing=10,
            run_spacing=10,
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
                        ft.Text(emoji, size=32),
                        ft.Text(muscle, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"({exercise_count})", size=12, color=ft.Colors.WHITE54),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    bgcolor=ft.Colors.GREY_900,
                    padding=20,
                    border_radius=10,
                    on_click=lambda e, m=muscle: select_muscle_group(m),
                )
            )
        
        return ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/")),
                ft.Text("Select Muscle Group", size=20, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            ft.Container(
                content=ft.TextField(hint_text="🔍 Search exercises...", border_color=ft.Colors.GREY_700),
                margin=ft.margin.only(bottom=10)
            ),
            muscle_grid,
        ])
    
    def start_exercise_logging(exercise_name):
        nonlocal current_exercise, current_set
        current_exercise = exercise_name
        current_set = 1
        current_reps.value = "8"
        current_weight.value = "65"
        page.go("/set-logging")
    
    # SET LOGGING SCREEN  
    def build_set_logging():
        return ft.Column([
            ft.Row([
                pb_stars,
                ft.Text(current_exercise, size=20, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Set {current_set}", size=16, color=ft.Colors.WHITE54),
            ]),
            
            # Input fields
            ft.Container(
                content=ft.Column([
                    ft.Text("REPS", size=16, color=ft.Colors.WHITE54),
                    current_reps,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_900,
                padding=25,
                border_radius=15,
                margin=ft.margin.only(bottom=15),
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("WEIGHT (kg)", size=16, color=ft.Colors.WHITE54),
                    current_weight,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_900,
                padding=25,
                border_radius=15,
                margin=ft.margin.only(bottom=15),
            ),
            
            # Dropset button
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WATER_DROP, color=ft.Colors.BLUE_300),
                    ft.Text("SWITCH TO DROPSET", color=ft.Colors.BLUE_300),
                ], alignment=ft.MainAxisAlignment.CENTER),
                on_click=toggle_dropset,
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.BLUE_300),
                margin=ft.margin.only(bottom=20),
            ),
            
            # Action buttons
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE),
                        ft.Text("ADD SET", color=ft.Colors.WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.GREEN_600,
                    padding=20,
                    border_radius=10,
                    on_click=add_set,
                    expand=True,
                ),
                ft.Container(width=10),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SKIP_NEXT, color=ft.Colors.WHITE),
                        ft.Text("NEXT EXERCISE", color=ft.Colors.WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.BLUE_600,
                    padding=20,
                    border_radius=10,
                    on_click=lambda e: page.go("/exercise-selection"),
                    expand=True,
                ),
            ]),
        ], scroll=ft.ScrollMode.ADAPTIVE)
    
    # WORKOUT SUMMARY SCREEN
    def build_workout_summary():
        return ft.Column([
            ft.Row([
                pb_stars,
                ft.Text("Workout Complete!", size=24, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
            ]),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("TODAY'S SCORE", size=16, color=ft.Colors.WHITE54),
                    ft.Text(f"+{app.sessionscore} ⭐", size=32, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.margin.only(bottom=30, top=20),
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Exercises Completed:", weight=ft.FontWeight.BOLD),
                    ft.Text(f"• {current_exercise}: {current_set-1} sets ✓"),
                ]),
                bgcolor=ft.Colors.GREY_900,
                padding=20,
                border_radius=10,
                margin=ft.margin.only(bottom=30),
            ),
            
            # Primary action
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ADD, size=32, color=ft.Colors.WHITE),
                    ft.Text("ADD MORE EXERCISES", size=16, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.BLUE_600,
                padding=25,
                border_radius=10,
                on_click=lambda e: page.go("/exercise-selection"),
                margin=ft.margin.only(bottom=10),
            ),
            
            # Secondary action
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE),
                    ft.Text("FINISH WORKOUT", color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_700,
                padding=15,
                border_radius=10,
                on_click=lambda e: page.go("/"),
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE)
    
    # EDIT EXERCISES SCREEN
    def build_edit_exercises():
        exercises_list = ft.ListView(expand=1, spacing=10)
        
        for exercise_name, exercise_data in app.data.items():
            exercises_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(exercise_name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{exercise_data[0]} → {exercise_data[1]}", size=12, color=ft.Colors.WHITE54),
                        ft.Text(f"Sets: {exercise_data[3]}, 1RM: {exercise_data[6]}kg", size=12, color=ft.Colors.WHITE54),
                    ]),
                    bgcolor=ft.Colors.GREY_900,
                    padding=15,
                    border_radius=10,
                )
            )
        
        return ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/")),
                ft.Text("Edit Exercises", size=20, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            exercises_list,
        ])
    
    # PROGRESS SCREEN
    def build_progress():
        return ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/")),
                ft.Text("Progress Analytics", size=20, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            ft.Container(
                content=ft.Column([
                    ft.Text("1RM Progress", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(color=ft.Colors.GREY_700),
                    *[ft.Text(f"• {ex}: {data[6]}kg (calc: {data[7]}kg)", size=14) 
                      for ex, data in list(app.data.items())[:8]],
                ]),
                bgcolor=ft.Colors.GREY_900,
                padding=20,
                border_radius=10,
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE)
    
    # Navigation functions
    def toggle_goal():
        app.goal = 1 - app.goal
        page.update()
    
    def select_muscle_group(selected_muscle):
        exercises = [name for name, data in app.data.items() if data[0] == selected_muscle]
        
        exercise_options = []
        for ex in exercises:
            exercise_options.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(ex, size=16, expand=True),
                        ft.Text(f"{app.data[ex][3]} sets", size=12, color=ft.Colors.WHITE54),
                    ]),
                    bgcolor=ft.Colors.GREY_800,
                    padding=15,
                    border_radius=8,
                    on_click=lambda e, ex_name=ex: start_exercise_logging(ex_name),
                )
            )
        
        page.views.append(
            ft.View(
                "/exercise-list",
                [
                    ft.Row([
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/exercise-selection")),
                        ft.Text(f"{selected_muscle} Exercises", size=20, weight=ft.FontWeight.BOLD, expand=True),
                    ]),
                    ft.Column(exercise_options, scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
                ]
            )
        )
        page.update()
    
    def show_edit_exercises():
        page.views.append(ft.View("/edit-exercises", [build_edit_exercises()]))
        page.update()
    
    def show_progress():
        page.views.append(ft.View("/progress", [build_progress()]))
        page.update()
    
    def toggle_dropset():
        # Simple dropset toggle
        if "💧" in pb_stars.value:
            pb_stars.value = pb_stars.value.replace("💧", "")
        else:
            pb_stars.value += "💧"
        page.update()
    
    def add_set():
        nonlocal current_set
        try:
            reps = int(current_reps.value)
            weight = float(current_weight.value)
            
            # Simple scoring based on your original logic
            current_set += 1
            app.pb_count += 1
            pb_stars.value = "★" * app.pb_count
            
            # Clear for next set
            current_reps.value = "8"
            current_weight.value = str(weight + 5)  # Auto-increment weight
            
            page.update()
        except ValueError:
            # Handle invalid input
            pass
    
    # Route handler - SIMPLIFIED
    def route_change(e):
        troute = ft.TemplateRoute(page.route)
        page.views.clear()
        
        if troute.match("/"):
            page.views.append(ft.View("/", [build_dashboard()]))
        elif troute.match("/exercise-selection"):
            page.views.append(ft.View("/exercise-selection", [build_exercise_selection()]))
        elif troute.match("/set-logging"):
            page.views.append(ft.View("/set-logging", [build_set_logging()]))
        elif troute.match("/workout-summary"):
            page.views.append(ft.View("/workout-summary", [build_workout_summary()]))
        elif troute.match("/edit-exercises"):
            page.views.append(ft.View("/edit-exercises", [build_edit_exercises()]))
        elif troute.match("/progress"):
            page.views.append(ft.View("/progress", [build_progress()]))
        
        page.update()
    
    def view_pop(e):
        page.views.pop()
        if page.views:
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            page.go("/")
    
    # Set up event handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Initialize with dashboard
    page.go("/")

# Run the app with NATIVE view to get QR codes
if __name__ == "__main__":
    ft.app(target=main, port=8550)