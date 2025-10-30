from tabs.base_tab import BaseTab


class ElementsTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('elements', yaml_manager, **kwargs)