from tabs.base_tab import BaseTab


class ProjectTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('project', yaml_manager, **kwargs)