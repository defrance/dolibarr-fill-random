from tabs.base_tab import BaseTab


class OthersTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('others', yaml_manager, **kwargs)