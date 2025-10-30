from tabs.base_tab import BaseTab

class ConfigurationsTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('configurations', yaml_manager, **kwargs)