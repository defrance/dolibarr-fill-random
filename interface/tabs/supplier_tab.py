from tabs.base_tab import BaseTab


class SupplierTab(BaseTab):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__('supplier', yaml_manager, **kwargs)