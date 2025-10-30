from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class ParamField(BoxLayout):
    """Widget pour afficher un champ paramètre avec son label"""
    
    def __init__(self, param_name, param_value, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 40
        self.spacing = 10
        
        self.param_name = param_name
        
        # Label
        label = Label(
            text=self.format_label(param_name),
            size_hint_x=0.6,
            halign='right',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        self.add_widget(label)
        
        # Input
        self.text_input = TextInput(
            text=str(param_value),
            size_hint_x=0.4,
            multiline=False,
            input_filter='int'
        )
        self.add_widget(self.text_input)
    
    def format_label(self, param_name):
        """Formate le nom du paramètre pour l'affichage"""
        return param_name.replace('_', ' ').title() + ':'
    
    def get_value(self):
        """Récupère la valeur du champ"""
        try:
            return int(self.text_input.text) if self.text_input.text else 0
        except ValueError:
            return 0
    
    def set_value(self, value):
        """Définit la valeur du champ"""
        self.text_input.text = str(value)