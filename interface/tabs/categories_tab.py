from tabs.base_tab import BaseTab


class CategoriesTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('categories', yaml_manager, **kwargs)