from datetime import datetime
from tqdm import tqdm

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dolibarr_api import *
from generators import *


GENERATORS = [
    {
        "name": "Articles",
        "count": nbNewKnowledge,
        "module": "knowledgemanagement",
        "generator": generate_knowledge,
        "progress_label": "Création des articles",
    },
    {
        "name": "Congés",
        "count": nbHoliday,
        "module": "holiday",
        "generator": generate_holiday,
        "progress_label": "Création des congés",
    },
    {
        "name": "Notes de frais",
        "count": nbExpenseReport,
        "module": "expensereport",
        "generator": generate_expense_report,
        "progress_label": "Création des notes de frais",
    },
]