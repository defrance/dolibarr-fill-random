# Regles de nommage des fonctions
# fill_ = on récupère les données de l'api et on retourne un tableau
# get_random = on retourne un élément aliéatoire d'un tableau

# fill
from .fill_expensereport_types import fill_expensereport_types
from .fill_projects import fill_projects
from .fill_users import fill_users
from .fill_banks import fill_banks
from .fill_groups_users import fill_groups_users

# get
from .get_enabled_modules import get_enabled_modules
from .get_projects_of_contactID import get_projects_of_contactID
from .get_projects_of_userID import get_projects_of_userID
from .get_realistic_qty_price import get_realistic_qty_price

# get random
from .get_random_address import get_random_address
from .get_random_holiday_type import get_random_holiday_type
from .get_random_project_id import get_random_project_id
from .get_random_user_id import get_random_user_id



# all

__all__ = [
    "fill_expensereport_types",
    "fill_projects",
    "fill_users",
    "fill_banks",
    "fill_groups_users",
    "get_enabled_modules",
    "get_projects_of_contactID",
    "get_projects_of_userID",
    "get_random_address",
    "get_random_holiday_type",
    "get_random_project_id",
    "get_random_user_id",
    "get_realistic_qty_price"
]