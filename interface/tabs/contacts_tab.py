from tabs.base_tab import BaseTab


class ContactsTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('contacts', yaml_manager, **kwargs)