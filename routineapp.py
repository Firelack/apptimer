import os
import json
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty

# Disable default multitouch behavior on desktop (e.g. prevents red dot on right-click)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

def resource_path(relative_path):
    """Return absolute path to resource, compatible with PyInstaller or normal execution."""
    try:
        # If bundled with PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # In normal execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AutoResizeLabel(Label):
    """Label that adjusts its text size to fit the parent widget's width."""

    text_property = StringProperty()  # Custom property for use in Kivy or Python

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Trigger size adjustment when the widget resizes
        self.bind(size=self._on_size)

    def _on_size(self, instance, value):
        """Update text size to match parent width with margin."""
        if self.parent:
            self.text_size = (self.parent.width - 20, None)  # Apply horizontal margin
            self.texture_update()  # Recalculate texture for rendering

    def on_parent(self, instance, parent):
        """Adjust size immediately when added to a parent widget."""
        if parent:
            self._on_size(parent, parent.size)

class MyTextInput(TextInput):
    def __init__(self, max_length=50, **kwargs):
        """Custom TextInput with max length and dynamic background on focus."""
        super().__init__(**kwargs)
        self.max_length = max_length  # Maximum number of characters allowed

        # Layout and style configuration
        self.size_hint_x = 0.7
        self.size_hint_y = None
        self.height = 40
        self.pos_hint = {'center_x': 0.5}
        self.background_color = (0.7, 0.7, 0.7, 0.6)  # Default background (semi-transparent)
        self.foreground_color = (1, 1, 1, 1)

        # Center text both horizontally and vertically
        self.halign = 'center'
        self.valign = 'middle'
        self.multiline = False  # Single-line input

        # Recalculate padding when size or text changes
        self.bind(size=self.update_padding, text=self.update_padding)
        self.update_padding()

        # Listen for focus events to change background opacity
        self.bind(on_focus=self.on_focus)

    def update_padding(self, *args):
        """Adjust vertical padding to center text within the input box."""
        self.padding = [10, (self.height - self.line_height) / 2]  # [horizontal, vertical]

    def on_focus(self, instance, value):
        """Change background opacity when input gains or loses focus."""
        if value:
            self.background_color = (0.7, 0.7, 0.7, 1)  # Fully opaque when focused
        else:
            self.background_color = (0.7, 0.7, 0.7, 0.6)  # Semi-transparent when unfocused

    def insert_text(self, substring, from_undo=False):
        """Limit input length to max_length."""
        if len(self.text) < self.max_length or substring == "":
            super().insert_text(substring, from_undo=from_undo)
            
class FocusableForm(BoxLayout):
    def __init__(self, **kwargs):
        """BoxLayout that manages focus switching with TAB and triggering with ENTER."""
        super().__init__(**kwargs)
        self.widgets_list = []  # Stores widgets that can receive focus
        Window.bind(on_key_down=self._on_key_down)  # Listen for keyboard input

    def register_focusable(self, widget):
        """Register a widget as focusable with TAB."""
        self.widgets_list.append(widget)

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        """Handle TAB to cycle focus and ENTER to trigger buttons."""
        if key == 9:  # TAB key
            # Only consider widgets that are enabled and have focus capability
            enabled_widgets = [w for w in self.widgets_list if hasattr(w, 'focus') and not getattr(w, 'disabled', False)]

            # Find the currently focused widget
            focused = next((i for i, w in enumerate(enabled_widgets) if w.focus), None)

            if focused is None:
                # No widget has focus: focus the first active button if available
                first_button = next((w for w in enabled_widgets if isinstance(w, Button)), None)
                if first_button:
                    first_button.focus = True
                return True

            # Move focus to the next or previous widget based on SHIFT key
            enabled_widgets[focused].focus = False
            next_index = (focused - 1 if 'shift' in modifiers else focused + 1) % len(enabled_widgets)
            enabled_widgets[next_index].focus = True
            return True

        elif key == 13:  # ENTER key
            # Trigger the focused button if any
            focused_btn = next((w for w in self.widgets_list if isinstance(w, Button) and w.focus), None)
            if focused_btn:
                focused_btn.trigger_action(duration=0)
                return True

        return False

class HoverBehavior:
    hovered = BooleanProperty(False)  # Tracks whether the mouse is over the widget
    border_point = None  # Optional: used for additional hover logic (not implemented here)

    def __init__(self, **kwargs):
        """Base class to detect mouse hover over a widget."""
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)  # Bind mouse movement to handler

    def on_mouse_pos(self, *args):
        """Update hovered state based on mouse position."""
        if not self.get_root_window():
            return  # Ignore if widget is not displayed

        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))  # Check if mouse is inside widget bounds
        self.hovered = inside
        self.on_hover(inside)  # Trigger hover callback

    def on_hover(self, hovered):
        """Called when hover state changes; override to customize behavior."""
        pass

class StyledButton(FocusBehavior, HoverBehavior, Button):
    def __init__(self, opacity=0.6, **kwargs):
        """Custom button with hover/focus visual feedback and rounded border."""
        super().__init__(**kwargs)
        self.opacity_normal = opacity
        self.opacity_focus = 1.0
        self.opacity_hover = 0.85
        self.selected = False  # Used to highlight a selected button
        
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Fully transparent default background

        # Draw custom background and border
        with self.canvas.before:
            self.bg_color = Color(0.7, 0.7, 0.7, self.opacity_normal)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[30])
            self.border_color = Color(0, 0, 0, 1)
            self.border_line = Line(width=1.5)

        # Update visuals on relevant changes
        self.bind(pos=self.update_graphics, size=self.update_graphics,
                  focus=self.on_focus, hovered=self.on_hover)

    def update_graphics(self, *args):
        """Update shape and position of background and border."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (
            self.x, self.y, self.width, self.height, 30
        )

    def on_focus(self, instance, value):
        """Adjust opacity when focus changes."""
        self.update_opacity()

    def on_hover(self, *args):
        """Adjust opacity when hover state changes."""
        self.update_opacity()

    def update_opacity(self):
        """Set background opacity based on selection, focus, or hover."""
        if self.selected:  # Priority: selected state overrides others
            self.bg_color.a = self.opacity_focus
        elif self.focus:
            self.bg_color.a = self.opacity_focus
        elif self.hovered:
            self.bg_color.a = self.opacity_hover
        else:
            self.bg_color.a = self.opacity_normal

class RoutineApp(App):
    FILE_PATH = "necessary/routinesV3.json"

    with open("necessary/language.json", 'r', encoding='utf-8') as f:
        dictlanguage = json.load(f)

    def build(self):
        """Initialize the interface using routines and language data."""
        self.routines_data = self.charger_routines()
        self.routines = self.routines_data.get("routines", {})
        self.current_language = self.routines_data["language"]

        self.root = FloatLayout()
        self.background_image = Image(allow_stretch=True, keep_ratio=False)
        self.root.add_widget(self.background_image)

        self.content_container = BoxLayout()
        self.root.add_widget(self.content_container)

        if self.routines_data.get("first_time", True):
            self.set_root_content(self.page_bienvenue())
            self.routines_data["first_time"] = False
            self.sauvegarder_routines()
        else:
            self.set_root_content(self.page_accueil())

        Window.bind(size=self.update_background_image)
        self.update_background_image()
        Window.bind(size=self.update_lang_button_text)
        Window.bind(size=lambda *args: self.update_dropdown_language_buttons())

        return self.root

    def set_root_content(self, new_content):
        """Replace the central content with a new widget."""
        self.content_container.clear_widgets()
        self.content_container.add_widget(new_content)

    def page_bienvenue(self):
        """Display the welcome page."""
        layout = FloatLayout()
        box = BoxLayout(orientation="vertical", padding=10)
        label = Label(text=self.dictlanguage[self.current_language]["welcome_page"],
                      font_size=24, halign="center", valign="middle")
        label.bind(size=label.setter('text_size'))
        box.add_widget(label)
        layout.add_widget(box)
        layout.bind(on_touch_down=lambda *args: self.set_root_content(self.page_accueil()))
        return layout

    def update_background_image(self, *args):
        """Adjust background image based on orientation."""
        img = 'fondportraitbienvenue.jpg' if Window.height > Window.width else 'fondpaysagebienvenue.png'
        self.background_image.source = resource_path(f'necessary/images/{img}')

    def update_lang_button_text(self, *args):
        """Shorten or display the full language button text."""
        lang = self.routines_data["language"]
        self.main_lang_btn.text = lang[:2] if Window.width < Window.height else lang

    def update_dropdown_language_buttons(self):
        """Update the labels of the language dropdown buttons."""
        if not hasattr(self, 'dropdown_buttons'):
            return
        for btn in self.dropdown_buttons:
            lang = btn.full_text
            btn.text = lang[:2] if Window.width < Window.height else lang

    def adjust_button_text(self, text):
        """Shorten long button texts when in portrait mode."""
        words = text.split()
        return ' '.join(words[:2]) if len(words) > 2 and Window.width < Window.height else text

    def on_window_resize(self, instance, width, height):
        """Adjust the text of routine buttons upon window resizing."""
        if hasattr(self, "routine_buttons"):
            for btn, name in self.routine_buttons:
                btn.text = self.adjust_button_text(name)

    def changer_langue(self, langue):
        """Change the app language and save the settings."""
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["language"] = langue
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        self.current_language = langue
        self.set_root_content(self.page_accueil())

    def page_accueil(self):
        """
        Create the main home page including:
        - a dropdown menu for language selection,
        - a button to add a new routine,
        - a help button,
        - a scrollable list of routines with options (rename, copy, delete),
        - handles resizing and keyboard navigation.
        """
        layout = FloatLayout()

        # Main vertical container with focus management
        content = FocusableForm(orientation="vertical", spacing=10, padding=10, size_hint=(1, 1))

        # --- Top bar: language selection + add routine + help ---
        top_buttons = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)

        # Main button showing current language and opening dropdown menu
        self.main_lang_btn = StyledButton(text="", size_hint=(0.1, 1))
        self.update_lang_button_text()

        dropdown = DropDown()
        self.dropdown_buttons = []  # List of language buttons in the dropdown

        for lang in self.dictlanguage:
            btn = StyledButton(text="", size_hint_y=None, height=44, opacity=1)
            btn.full_text = lang

            def on_lang_select(btn_instance, dropdown=dropdown):
                # Language change: update, save, and reload home page
                selected_lang = btn_instance.full_text
                self.routines_data["language"] = selected_lang
                self.current_language = selected_lang
                self.sauvegarder_routines()
                self.update_lang_button_text()
                self.update_dropdown_language_buttons()
                dropdown.dismiss()
                Clock.schedule_once(lambda dt: self.set_root_content(self.page_accueil()), 0.1)

            btn.bind(on_release=on_lang_select)
            dropdown.add_widget(btn)
            self.dropdown_buttons.append(btn)

        self.update_dropdown_language_buttons()
        self.main_lang_btn.bind(on_release=lambda btn: Clock.schedule_once(lambda dt: dropdown.open(btn), 0.01))
        top_buttons.add_widget(self.main_lang_btn)

        # "Add a routine" button
        btn2 = StyledButton(text=self.dictlanguage[self.current_language]["home_page"][0], size_hint=(0.8, 1))
        btn2.bind(on_press=lambda *args: self.set_root_content(self.page_ajouter_routine()))
        top_buttons.add_widget(btn2)

        # Help "?" button
        helpbtn = StyledButton(text="?", size_hint=(0.1, 1))
        helpbtn.bind(on_press=lambda *args: self.set_root_content(self.help_page()))
        top_buttons.add_widget(helpbtn)

        content.add_widget(top_buttons)

        # --- Scroll view containing the routines list ---
        scroll = ScrollView(size_hint=(1, 0.8))
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        routine_layout.bind(minimum_height=routine_layout.setter("height"))

        self.routine_buttons = []  # Store routine buttons to handle resizing

        routines_list = list(self.routines.items())
        for index, (name, _) in enumerate(routines_list):
            routine_box = BoxLayout(size_hint_y=None, height=50, spacing=10)

            # Main routine button
            btn = StyledButton(text=self.adjust_button_text(name), size_hint=(0.7, 1))
            btn.bind(on_press=lambda instance, r=name: self.set_root_content(self.page_routine(r)))
            routine_box.add_widget(btn)
            content.register_focusable(btn)

            self.routine_buttons.append((btn, name))

            # Up/down movement buttons
            up_btn = StyledButton(text="↑", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, -1))
            routine_box.add_widget(up_btn)

            down_btn = StyledButton(text="↓", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, 1))
            routine_box.add_widget(down_btn)

            # Dropdown options: rename, copy, delete (30% of window width)
            dropdown2 = DropDown(auto_width=False)
            dropdown_width = Window.width * 0.3
            dropdown2.width = dropdown_width

            rename_btn = StyledButton(
                text=self.dictlanguage[self.current_language]["home_page"][2],
                size_hint=(None, None),
                size=(dropdown_width, 50),
                opacity=1
            )
            rename_btn.bind(on_release=lambda instance, r=name, dd=dropdown2: (
                self.set_root_content(self.page_renommer_routine(r)),
                dd.dismiss()
            ))
            dropdown2.add_widget(rename_btn)

            copy_btn = StyledButton(
                text=self.dictlanguage[self.current_language]["home_page"][3],
                size_hint=(None, None),
                size=(dropdown_width, 50),
                opacity=1
            )
            copy_btn.bind(on_release=lambda instance, r=name, dd=dropdown2: (
                self.set_root_content(self.copy_routine(r)),
                dd.dismiss()
            ))
            dropdown2.add_widget(copy_btn)

            delete_btn = StyledButton(
                text=self.dictlanguage[self.current_language]["home_page"][1],
                size_hint=(None, None),
                size=(dropdown_width, 50),
                opacity=1
            )
            delete_btn.bind(on_release=lambda instance, r=name, dd=dropdown2: (
                self.confirmer_suppression_routine(r),
                dd.dismiss()
            ))
            dropdown2.add_widget(delete_btn)

            # Button opening the options dropdown
            more_btn = StyledButton(text="...", size_hint=(0.1, 1))
            more_btn.bind(on_release=lambda btn, dd=dropdown2: dd.open(btn))
            routine_box.add_widget(more_btn)

            routine_layout.add_widget(routine_box)

        # Adapt dropdown options width on window resize
        def update_dropdown_width(*args):
            new_width = Window.width * 0.3
            dropdown2.width = new_width
            rename_btn.size = (new_width, 50)
            delete_btn.size = (new_width, 50)

        Window.bind(on_resize=update_dropdown_width)

        scroll.add_widget(routine_layout)
        content.add_widget(scroll)

        layout.add_widget(content)

        # Register buttons for tab navigation
        content.register_focusable(self.main_lang_btn)
        content.register_focusable(btn2)

        # Manage global resizing
        Window.unbind(on_resize=self.on_window_resize)
        Window.bind(on_resize=self.on_window_resize)

        return layout
    
    def copy_routine(self, name):
        """Copy a routine and add it with '(copy)' suffix."""
        routine = self.routines[name]
        new_routine_name = f"{routine['name']} (copy)"
        new_routine = {"name": new_routine_name, "fonctions": routine["fonctions"][:]}
        self.routines[new_routine_name] = new_routine
        self.sauvegarder_routines()
        return self.page_accueil()
    
    def help_page(self):
        """Create the help page layout with scrollable instructions and return button."""
        layout = FocusableForm(orientation="vertical", spacing=10, padding=10)

        # Title label
        title = self.dictlanguage[self.current_language]["helppage"][1]
        title_label = AutoResizeLabel(
            text=title,
            font_size=30,
            size_hint=(1, 0.2),
            height=40,
            halign="center",
            valign="middle"
        )
        title_label.bind(size=title_label.setter('text_size'))
        layout.add_widget(title_label)

        # Help text inside a scrollview
        help_text = self.dictlanguage[self.current_language]["helppage"][0]
        scroll = ScrollView(size_hint=(1, 1))
        help_label = AutoResizeLabel(
            text=help_text,
            size_hint_y=None,
            halign="center",
            valign="middle",
            font_size=16
        )
        help_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        scroll.add_widget(help_label)
        layout.add_widget(scroll)

        # Small spacer
        layout.add_widget(Widget(size_hint=(1, None), height=10))

        # Return button
        back_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["routine_page"][6],  # "Back"
            size_hint=(1, None),
            height=50
        )
        layout.register_focusable(back_btn)
        back_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))
        layout.add_widget(back_btn)

        return layout

    def deplacer_routine(self, index, direction):
        """Move a routine up or down in the list."""
        routines_list = list(self.routines.items())
        new_index = index + direction
        if 0 <= new_index < len(routines_list):
            routines_list[index], routines_list[new_index] = routines_list[new_index], routines_list[index]
            self.routines = {name: data for name, data in routines_list}
            self.sauvegarder_routines()
            self.set_root_content(self.page_accueil())

    def confirmer_suppression_routine(self, name):
        """Show a confirmation popup to delete a routine."""
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        popup_layout.add_widget(
            AutoResizeLabel(
                text=f"{self.dictlanguage[self.current_language]['confirmation'][1]} {name} ?",
                halign="center",
                valign="middle",
                font_size=20
            )
        )
        btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        popup = Popup(
            title=self.dictlanguage[self.current_language]["confirmation"][0],
            content=popup_layout,
            size_hint=(0.8, 0.4)
        )

        yes_btn = StyledButton(text=self.dictlanguage[self.current_language]["confirmation"][2])
        yes_btn.bind(on_press=lambda *args: self.supprimer_routine(name, popup))
        no_btn = StyledButton(text=self.dictlanguage[self.current_language]["confirmation"][3])
        no_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        popup_layout.add_widget(btn_layout)

        popup.open()

    def supprimer_routine(self, name, popup):
        """Delete a routine and close the confirmation popup."""
        if name in self.routines:
            del self.routines[name]
            self.sauvegarder_routines()
        popup.dismiss()
        self.set_root_content(self.page_accueil())

    def page_ajouter_routine(self, error_message=""):
        """Create layout to add a new routine with optional error message."""
        layout = FocusableForm(orientation="vertical", spacing=10, padding=10)
        layout.add_widget(Widget(size_hint=(1, 0.1)))

        label = Label(
            text=self.dictlanguage[self.current_language]["add_routine"][0],
            font_size=30,
            size_hint=(1, None),
            height=40,
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))
        layout.add_widget(label)

        routine_name_input = MyTextInput(size_hint=(1, None), max_length=20, height=40)
        layout.register_focusable(routine_name_input)
        layout.add_widget(routine_name_input)

        # Show error message if provided
        if error_message:
            error_label = Label(
                text=error_message,
                color=(1, 1, 1, 1),  # Red
                size_hint=(1, None),
                height=30,
                halign="center",
                valign="middle"
            )
            error_label.bind(size=error_label.setter("text_size"))
            layout.add_widget(error_label)
        else:
            layout.add_widget(Widget(size_hint=(1, None), height=30))  # Reserved empty space

        layout.add_widget(Widget())

        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)

        finish_btn = StyledButton(text=self.dictlanguage[self.current_language]["add_routine"][1])
        layout.register_focusable(finish_btn)
        cancel_btn = StyledButton(text=self.dictlanguage[self.current_language]["add_routine"][2])
        layout.register_focusable(cancel_btn)

        def validate_add(instance):
            name = routine_name_input.text.strip()
            if not name:
                self.set_root_content(self.page_ajouter_routine(self.dictlanguage[self.current_language]["add_routine"][3]))  # "Empty name!"
            elif name in self.routines:
                self.set_root_content(self.page_ajouter_routine(self.dictlanguage[self.current_language]["add_routine"][4]))  # "Routine already exists!"
            else:
                self.routines[name] = {"name": name, "fonctions": []}
                self.sauvegarder_routines()
                self.set_root_content(self.page_accueil())

        finish_btn.bind(on_press=validate_add)
        cancel_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))

        btn_layout.add_widget(finish_btn)
        btn_layout.add_widget(cancel_btn)

        layout.add_widget(btn_layout)

        return layout

    def page_routine(self, name):
        """Display routine page with list of exercises and control buttons."""
        routine = self.routines[name]
        layout = FocusableForm(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])
        layout.add_widget(Widget(size_hint=(1, None), height=10))

        # Centered title label with auto-resize
        title_label = AutoResizeLabel(
            text=f"{self.dictlanguage[self.current_language]['routine_page'][0]} {routine['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40,
            halign="center",
            valign="middle",
        )
        title_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (value[0] - 20, None))
        )
        layout.add_widget(title_label)

        layout.add_widget(Widget(size_hint=(1, None), height=10))

        # ScrollView containing exercises
        scroll = ScrollView(size_hint=(1, 0.70))
        exercice_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=20, padding=[0, 5])
        exercice_layout.bind(minimum_height=exercice_layout.setter("height"))

        for index, ex in enumerate(routine["fonctions"]):
            ex_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)

            # Build exercise description text
            if ex["duration"]:
                text = (
                    f"{ex['name']}\n"
                    f"{ex['repetitions']} {self.dictlanguage[self.current_language]['routine_page'][1]}, "
                    f"{ex['duration']}{self.dictlanguage[self.current_language]['routine_page'][2]}"
                )
            else:
                text = (
                    f"{ex['name']}\n"
                    f"{ex['repetitions']} {self.dictlanguage[self.current_language]['routine_page'][1]}, "
                    f"{ex['units']} {self.dictlanguage[self.current_language]['routine_page'][3]}"
                )

            label = Label(
                text=text,
                size_hint=(0.5, 1),
                halign="center",
                valign="middle"
            )
            label.bind(
                size=lambda instance, value: setattr(instance, 'text_size', value)
            )
            ex_layout.add_widget(label)

            # Buttons for each exercise: up, down, modify
            up_btn = StyledButton(text="↑", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(name, i, -1))
            layout.register_focusable(up_btn)
            ex_layout.add_widget(up_btn)

            down_btn = StyledButton(text="↓", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(name, i, 1))
            layout.register_focusable(down_btn)
            ex_layout.add_widget(down_btn)

            modify_btn = StyledButton(text="\N{pencil}", font_name='necessary/SegoeUIEmoji.TTF', size_hint=(0.1, 1))
            modify_btn.bind(on_press=lambda instance, i=index: self.set_root_content(self.page_modifier_exercice(name, i)))
            layout.register_focusable(modify_btn)
            ex_layout.add_widget(modify_btn)

            exercice_layout.add_widget(ex_layout)

        scroll.add_widget(exercice_layout)
        layout.add_widget(scroll)

        # Bottom buttons: launch, modify, back
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)

        has_exercises = len(routine["fonctions"]) > 0
        launch_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][4], size_hint=(0.4, None), height=50, disabled=not has_exercises)
        layout.register_focusable(launch_btn)
        launch_btn.bind(on_press=lambda *args: self.lancer_routine(name))

        modify_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][5], size_hint=(0.4, None), height=50)
        layout.register_focusable(modify_btn)
        modify_btn.bind(on_press=lambda *args: self.set_root_content(self.page_modifier_routine(name)))

        back_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][6], size_hint=(0.4, None), height=50)
        layout.register_focusable(back_btn)
        back_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))

        btn_layout.add_widget(launch_btn)
        btn_layout.add_widget(modify_btn)
        btn_layout.add_widget(back_btn)

        layout.add_widget(btn_layout)

        return layout

    def page_renommer_routine(self, nom):
        """Return layout to rename a routine."""
        layout = FocusableForm(orientation="vertical", spacing=10, padding=10)

        # Top spacer (10%)
        layout.add_widget(Widget(size_hint=(1, 0.1)))

        # Centered title
        label = Label(
            text=self.dictlanguage[self.current_language].get("rename_routine", "Rename the routine"),
            font_size=30,
            size_hint=(1, None),
            height=40,
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))
        layout.add_widget(label)

        # Text input for routine name
        routine_name_input = MyTextInput(
            text=self.routines[nom]["name"],
            size_hint=(1, None),
            height=40,
            max_length=20
        )
        layout.register_focusable(routine_name_input)
        layout.add_widget(routine_name_input)

        # Error label, initially empty
        error_label = Label(
            text="",
            font_size=18,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=30
        )
        layout.add_widget(error_label)

        # Spacer to push buttons down
        layout.add_widget(Widget())

        def valider_renommage(instance):
            """Validate and apply the new routine name."""
            nouveau_nom = routine_name_input.text.strip()
            if not nouveau_nom:
                error_label.text = self.dictlanguage[self.current_language]["add_routine"][3]
            elif nouveau_nom in self.routines and nouveau_nom != nom:
                error_label.text = self.dictlanguage[self.current_language]["add_routine"][4]
            else:
                # Preserve order when renaming
                routines_ordonnees = list(self.routines.items())
                index = [i for i, (k, _) in enumerate(routines_ordonnees) if k == nom][0]
                _, ancienne_valeur = routines_ordonnees.pop(index)
                ancienne_valeur["name"] = nouveau_nom
                routines_ordonnees.insert(index, (nouveau_nom, ancienne_valeur))

                self.routines = dict(routines_ordonnees)
                self.sauvegarder_routines()
                self.set_root_content(self.page_accueil())

        # Buttons layout
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        valider_btn = StyledButton(text=self.dictlanguage[self.current_language]["add_routine"][1])
        layout.register_focusable(valider_btn)
        valider_btn.bind(on_press=valider_renommage)

        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["add_routine"][2])
        layout.register_focusable(retour_btn)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))

        btn_layout.add_widget(valider_btn)
        btn_layout.add_widget(retour_btn)
        layout.add_widget(btn_layout)

        return layout


    def page_modifier_exercice(self, nom, index):
        """Return layout to edit an exercise."""
        routine = self.routines[nom]
        ex = routine["fonctions"][index]
        layout = FocusableForm(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])

        scroll = ScrollView(size_hint=(1, 0.85))
        content = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Widget(size_hint=(1, None), height=20))
        content.add_widget(AutoResizeLabel(
            text=f"{self.dictlanguage[self.current_language]['change_routine'][19]} {ex['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40,
            halign="center"
        ))

        def add_field(label_text, default_text="", length=20):
            """Helper to add labeled input."""
            content.add_widget(Label(text=label_text, size_hint=(1, None), height=25))
            input_widget = MyTextInput(text=default_text, size_hint=(1, None), max_length=length, height=40)
            content.add_widget(input_widget)
            layout.register_focusable(input_widget)
            return input_widget

        content.add_widget(Widget(size_hint=(1, None), height=10))

        exercice_name_input = add_field(self.dictlanguage[self.current_language]["change_routine"][1], ex["name"])

        is_duration = "duration" in ex and ex["duration"]
        valeur_init = ex["duration"] if is_duration else ex.get("units", "")
        exercice_valeur_input = add_field(self.dictlanguage[self.current_language]["change_routine"][8], str(valeur_init), 5)

        selected_type = {"value": "duration" if is_duration else "unit"}

        def update_type(new_type):
            """Update selected type button states."""
            selected_type["value"] = new_type
            duree_btn.selected = (new_type == "duration")
            unite_btn.selected = (new_type == "unit")
            duree_btn.update_opacity()
            unite_btn.update_opacity()

        type_btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        duree_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][2],
            size_hint=(0.5, None), height=40
        )
        unite_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][5],
            size_hint=(0.5, None), height=40
        )

        update_type(selected_type["value"])

        duree_btn.bind(on_press=lambda btn: update_type("duration"))
        unite_btn.bind(on_press=lambda btn: update_type("unit"))

        type_btn_layout.add_widget(duree_btn)
        type_btn_layout.add_widget(unite_btn)

        content.add_widget(type_btn_layout)
        layout.register_focusable(duree_btn)
        layout.register_focusable(unite_btn)

        exercice_reps_input = add_field(self.dictlanguage[self.current_language]["change_routine"][3], str(ex.get("repetitions", "")), 4)
        exercice_repos_input = add_field(self.dictlanguage[self.current_language]["change_routine"][4], str(ex.get("rest", "")), 4)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        enregistrer_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][20], size_hint=(0.45, None), height=50)

        enregistrer_btn.bind(on_press=lambda *args: self.enregistrer_modification_exercice(
            nom, index,
            exercice_name_input.text,
            exercice_valeur_input.text if selected_type["value"] == "duration" else "",
            exercice_reps_input.text,
            exercice_repos_input.text,
            exercice_valeur_input.text if selected_type["value"] == "unit" else ""
        ))

        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][7], size_hint=(0.45, None), height=50)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))

        remove_btn = StyledButton(text="X", size_hint=(0.1, None), height=50)
        remove_btn.bind(on_press=lambda instance, i=index: self.supprimer_exercice(nom, i))

        layout.register_focusable(enregistrer_btn)
        layout.register_focusable(retour_btn)
        layout.register_focusable(remove_btn)

        btn_layout.add_widget(enregistrer_btn)
        btn_layout.add_widget(retour_btn)
        btn_layout.add_widget(remove_btn)
        layout.add_widget(btn_layout)

        return layout
    
    def deplacer_exercice(self, routine_nom, index, direction):
        """Move an exercise up or down in the list."""
        exercices = self.routines[routine_nom]["fonctions"]
        if 0 <= index + direction < len(exercices):
            exercices.insert(index + direction, exercices.pop(index))
            self.sauvegarder_routines()
            self.set_root_content(self.page_routine(routine_nom))

    def supprimer_exercice(self, routine_nom, index):
        """Delete an exercise from the routine."""
        del self.routines[routine_nom]["fonctions"][index]
        self.sauvegarder_routines()
        self.set_root_content(self.page_routine(routine_nom))

    def lancer_routine(self, nom):
        """Start running the routine."""
        self.paused = False
        self.routine = self.routines[nom]
        self.current_exercise_index = 0
        self.current_repetition = 1
        self.is_resting = False
        self.remaining_time = self.routine["fonctions"][0]["duration"] or 0

        self.routine_layout = FocusableForm(orientation="vertical", spacing=10, padding=10)
        self.timer_label = AutoResizeLabel(
            text=self.dictlanguage[self.current_language]["start_routine"][0],
            font_size=24, halign='center', valign='middle'
        )
        self.routine_layout.add_widget(self.timer_label)

        # Done button
        self.fait_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["start_routine"][1], size_hint=(1, 0.2)
        )
        self.fait_btn.bind(on_press=self.marquer_fait)
        self.fait_btn.disabled = True
        self.routine_layout.add_widget(self.fait_btn)
        self.routine_layout.register_focusable(self.fait_btn)

        # Pause button
        self.pause_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["start_routine"][2], size_hint=(1, 0.2)
        )
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.routine_layout.add_widget(self.pause_btn)
        self.routine_layout.register_focusable(self.pause_btn)

        # Skip rest button
        self.skip_rest_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["start_routine"][3], size_hint=(1, 0.2)
        )
        self.skip_rest_btn.bind(on_press=self.pass_rest_time)
        self.skip_rest_btn.disabled = True
        self.routine_layout.add_widget(self.skip_rest_btn)
        self.routine_layout.register_focusable(self.skip_rest_btn)

        # Stop button
        stop_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["start_routine"][4], size_hint=(1, 0.2)
        )
        stop_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        self.routine_layout.add_widget(stop_btn)
        self.routine_layout.register_focusable(stop_btn)

        self.set_root_content(self.routine_layout)
        Clock.schedule_interval(self.update_routine, 1.0)

    def toggle_pause(self, instance):
        """Toggle pause/resume state."""
        self.paused = not self.paused
        instance.text = (
            self.dictlanguage[self.current_language]["toggle_pause"][0]
            if self.paused else
            self.dictlanguage[self.current_language]["toggle_pause"][1]
        )

    def pass_rest_time(self, instance):
        """Skip the current rest period."""
        self.is_resting = False
        self.remaining_time = 0
        self.skip_rest_btn.disabled = True  # Disable skip button after use

        # Advance to next repetition or exercise
        self.current_repetition += 1
        if self.current_repetition > self.routine["fonctions"][self.current_exercise_index]["repetitions"]:
            self.current_exercise_index += 1
            self.current_repetition = 1
        self.afficher_exercice()

    def update_routine(self, dt):
        """Update timer and routine state every second."""
        if self.paused:
            return

        if self.current_exercise_index >= len(self.routine["fonctions"]):
            self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
            Clock.unschedule(self.update_routine)
            return

        exercise = self.routine["fonctions"][self.current_exercise_index]

        if self.is_resting:
            self.skip_rest_btn.disabled = False  # Enable skip rest button
            self.fait_btn.disabled = True  # Disable done button during rest
            if self.remaining_time > 0:
                # Déterminer l'exercice suivant
                if self.current_repetition < exercise["repetitions"]:
                    next_ex = exercise["name"]
                elif self.current_exercise_index + 1 < len(self.routine["fonctions"]):
                    next_ex = self.routine["fonctions"][self.current_exercise_index + 1]["name"]

                self.timer_label.text = (
                    f"{self.dictlanguage[self.current_language]['update_routine'][1]} "
                    f"{self.remaining_time}{self.dictlanguage[self.current_language]['update_routine'][2]}\n"
                    f" -> {next_ex}"
                )
                self.remaining_time -= 1
            else:
                self.is_resting = False
                self.current_repetition += 1
                if self.current_repetition > exercise["repetitions"]:
                    self.current_exercise_index += 1
                    self.current_repetition = 1
                self.afficher_exercice()
        else:
            if exercise["duration"]:
                if self.remaining_time > 0:
                    self.timer_label.text = (
                        f"{exercise['name']}\n"
                        f"{self.dictlanguage[self.current_language]['update_routine'][3]} "
                        f"{self.current_repetition}/{exercise['repetitions']} - "
                        f"{self.remaining_time}{self.dictlanguage[self.current_language]['update_routine'][2]}"
                    )
                    self.remaining_time -= 1
                else:
                    last_exercise = self.current_exercise_index == len(self.routine["fonctions"]) - 1
                    last_repetition = self.current_repetition == exercise["repetitions"]

                    if not last_exercise or not last_repetition:
                        self.is_resting = True
                        self.remaining_time = exercise["rest"]
                    else:
                        # End of routine
                        self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
                        Clock.unschedule(self.update_routine)
            else:
                self.timer_label.text = (
                    f"{exercise['name']} - "
                    f"{self.dictlanguage[self.current_language]['update_routine'][3]} "
                    f"{self.current_repetition}/{exercise['repetitions']} - "
                    f"{exercise['units']} "
                    f"{self.dictlanguage[self.current_language]['update_routine'][4]}"
                )
                self.fait_btn.disabled = False

    def page_modifier_routine(self, nom):
        """Build UI to modify a routine."""
        routine = self.routines[nom]
        layout = FocusableForm(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])

        scroll = ScrollView(size_hint=(1, 0.85))
        content = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        # Spacer above title
        content.add_widget(Widget(size_hint=(1, None), height=20))

        # Title label
        content.add_widget(AutoResizeLabel(
            text=f"{self.dictlanguage[self.current_language]['change_routine'][0]} {routine['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40,
            halign="center",
        ))

        def add_field(label_text, length=20):
            """Add label and input field."""
            content.add_widget(Label(text=label_text, size_hint=(1, None), height=25))
            input_widget = MyTextInput(size_hint=(1, None), max_length=length, height=40)
            content.add_widget(input_widget)
            layout.register_focusable(input_widget)
            return input_widget

        content.add_widget(Widget(size_hint=(1, None), height=10))

        exercice_name_input = add_field(self.dictlanguage[self.current_language]["change_routine"][1])

        # Value field (duration or units)
        content.add_widget(Label(text=self.dictlanguage[self.current_language]["change_routine"][8], size_hint=(1, None), height=25))
        exercice_valeur_input = MyTextInput(size_hint=(1, None), max_length=5, height=40)
        content.add_widget(exercice_valeur_input)
        layout.register_focusable(exercice_valeur_input)

        selected_type = {"value": "duration"}

        def update_type(new_type):
            selected_type["value"] = new_type
            duree_btn.selected = (new_type == "duration")
            unite_btn.selected = (new_type == "unit")
            duree_btn.update_opacity()
            unite_btn.update_opacity()

        type_btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        duree_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][2],
            size_hint=(0.5, None),
            height=40
        )
        unite_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][5],
            size_hint=(0.5, None),
            height=40
        )

        update_type("duration")

        duree_btn.bind(on_press=lambda btn: update_type("duration"))
        unite_btn.bind(on_press=lambda btn: update_type("unit"))

        type_btn_layout.add_widget(duree_btn)
        type_btn_layout.add_widget(unite_btn)

        content.add_widget(type_btn_layout)
        layout.register_focusable(duree_btn)
        layout.register_focusable(unite_btn)

        exercice_reps_input = add_field(self.dictlanguage[self.current_language]["change_routine"][3], 4)
        exercice_repos_input = add_field(self.dictlanguage[self.current_language]["change_routine"][4], 4)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        ajouter_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][6], size_hint=(0.5, None), height=50)

        ajouter_btn.bind(on_press=lambda *args: self.ajouter_exercice(
            nom,
            exercice_name_input.text,
            exercice_valeur_input.text if selected_type["value"] == "duration" else "",
            exercice_reps_input.text,
            exercice_repos_input.text,
            exercice_valeur_input.text if selected_type["value"] == "unit" else ""
        ))

        layout.register_focusable(ajouter_btn)

        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][7], size_hint=(0.5, None), height=50)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        layout.register_focusable(retour_btn)

        btn_layout.add_widget(ajouter_btn)
        btn_layout.add_widget(retour_btn)
        layout.add_widget(btn_layout)

        return layout
    
    def ajouter_exercice(self, routine_nom, ex_nom, duree, repetitions, repos, unites):
        """Validate and add exercise to routine."""
        errors = []

        # Check if name is empty
        if not ex_nom.strip():
            errors.append(self.dictlanguage[self.current_language]["change_routine"][9])  # Empty name

        # Duration and units validation: at least one must be valid
        duree_val = None
        unites_val = None
        duree_ok = False
        unites_ok = False

        # Validate duration
        if duree:
            try:
                duree_val = int(duree)
                if duree_val > 0:
                    duree_ok = True
                else:
                    errors.append(self.dictlanguage[self.current_language]["change_routine"][10])  # Duration ≤ 0
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][14])  # Invalid duration

        # Validate units
        if unites:
            try:
                unites_val = int(unites)
                unites_ok = True
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][13])  # Invalid units

        if not duree and not unites:
            errors.append(self.dictlanguage[self.current_language]["change_routine"][17])  # No duration/units specified

        # Validate repetitions
        try:
            repetitions_val = int(repetitions)
            if repetitions_val <= 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][11])  # Repetitions ≤ 0
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][15])  # Invalid repetitions

        # Validate rest
        try:
            repos_val = int(repos)
            if repos_val < 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][12])  # Rest < 0
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][16])  # Invalid rest

        # Add exercise if no errors
        if not errors:
            exercice = {
                "name": ex_nom.strip(),
                "duration": duree_val if duree_ok else 0,
                "repetitions": repetitions_val,
                "rest": repos_val,
                "units": unites_val if unites_ok else None
            }
            self.routines[routine_nom]["fonctions"].append(exercice)
            self.sauvegarder_routines()
            self.set_root_content(self.page_routine(routine_nom))
        else:
            if len(errors) >= 3:
                error_message = self.dictlanguage[self.current_language]["change_routine"][18]
            else:
                error_message = "\n".join(errors)
            self.show_error_popup(error_message, routine_nom)

    def enregistrer_modification_exercice(self, routine_nom, index, ex_nom, duree, repetitions, repos, unites):
        """Validate and save exercise changes."""
        errors = []

        # Check empty name
        if not ex_nom.strip():
            errors.append(self.dictlanguage[self.current_language]["change_routine"][9])  # Empty name

        duree_val = None
        unites_val = None
        duree_ok = False
        unites_ok = False

        # Validate duration
        if duree:
            try:
                duree_val = int(duree)
                if duree_val > 0:
                    duree_ok = True
                else:
                    errors.append(self.dictlanguage[self.current_language]["change_routine"][10])  # Duration ≤ 0
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][14])  # Invalid duration

        # Validate units
        if unites:
            try:
                unites_val = int(unites)
                unites_ok = True
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][13])  # Invalid units

        # Check duration or units present
        if not duree and not unites:
            errors.append(self.dictlanguage[self.current_language]["change_routine"][17])  # No duration/unit

        # Validate repetitions
        try:
            repetitions_val = int(repetitions)
            if repetitions_val <= 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][11])  # Repetitions ≤ 0
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][15])  # Invalid repetitions

        # Validate rest
        try:
            repos_val = int(repos)
            if repos_val < 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][12])  # Negative rest
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][16])  # Invalid rest

        # Save changes if no errors
        if not errors:
            exercice = {
                "name": ex_nom.strip(),
                "duration": duree_val if duree_ok else 0,
                "repetitions": repetitions_val,
                "rest": repos_val,
                "units": unites_val if unites_ok else None
            }
            self.routines[routine_nom]["fonctions"][index] = exercice
            self.sauvegarder_routines()
            self.set_root_content(self.page_routine(routine_nom))
        else:
            if len(errors) >= 3:
                error_message = self.dictlanguage[self.current_language]["change_routine"][18]
            else:
                error_message = "\n".join(errors)
            self.show_error_popup(error_message, routine_nom)


    def show_error_popup(self, error_message, routine_nom):
        """Show error popup with a 'Return' button."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Centered label container
        label_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 1))
        label = AutoResizeLabel(
            text=error_message,
            font_size=20,
            halign='center',
            valign='middle'
        )
        # Force text size update for label alignment
        label.bind(size=lambda *x: label.setter('text_size')(label, label.size))

        label_container.add_widget(label)
        content.add_widget(label_container)

        # Return button
        retour_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][7],  # "Return"
            size_hint=(1, None),
            height=50
        )

        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        retour_btn.bind(on_press=lambda *args: popup.dismiss())
        content.add_widget(retour_btn)

        popup.open()

    def charger_routines(self):
        """Load routines from file or return default data."""
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                return json.load(f)
        return {"first_time": True, "language": "English", "routines": {}}


    def sauvegarder_routines(self):
        """Save current routines data to file."""
        self.routines_data["routines"] = self.routines
        with open(self.FILE_PATH, 'w') as f:
            json.dump(self.routines_data, f, indent=4)


    def afficher_exercice(self):
        """Display current exercise or stop if finished."""
        if self.current_exercise_index >= len(self.routine["fonctions"]):
            self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
            Clock.unschedule(self.update_routine)
            return

        exercise = self.routine["fonctions"][self.current_exercise_index]
        self.fait_btn.disabled = True

        if exercise["duration"]:
            self.remaining_time = exercise["duration"]
        else:
            self.timer_label.text = f"{exercise['name']} - {self.dictlanguage[self.current_language]['update_routine'][3]} {self.current_repetition}/{exercise['repetitions']} - {exercise['units']} {self.dictlanguage[self.current_language]['update_routine'][4]}"
            self.fait_btn.disabled = False


    def marquer_fait(self, instance):
        """Mark current exercise done and start rest or finish routine."""
        self.fait_btn.disabled = True
        if self.current_exercise_index < len(self.routine["fonctions"]) - 1:  # Avoid last rest
            self.is_resting = True
            self.remaining_time = self.routine["fonctions"][self.current_exercise_index]["rest"]
        else:
            if self.current_repetition < self.routine["fonctions"][self.current_exercise_index]["repetitions"]:
                self.is_resting = True
                self.remaining_time = self.routine["fonctions"][self.current_exercise_index]["rest"]
            else:
                self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
                Clock.unschedule(self.update_routine)

# Lauch the app    
if __name__ == "__main__":
    RoutineApp().run()