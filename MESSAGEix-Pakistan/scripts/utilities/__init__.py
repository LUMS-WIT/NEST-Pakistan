# NB for additions, emulate the style of add_AFOLU_CO2_accounting / get_nodes

from .get_historical_years import main as get_historical_years
from .get_nodes import get_nodes
from .get_optimization_years import main as get_optimization_years
from .utilities import CAGR as CAGR
from .utilities import calc_real_cf as calc_real_cf
from .utilities import closest as closest
from .utilities import f_index as f_index
from .utilities import f_slice as f_slice
from .utilities import get_cum_inst_cap as get_cum_inst_cap
from .utilities import idx_memb as idx_memb
from .utilities import intpol as intpol
from .utilities import unit_uniform as unit_uniform

__all__ = [
    "get_historical_years",
    "get_nodes",
    "get_optimization_years",
    "get_cum_inst_cap",
    "calc_real_cf",
    "closest",
    "f_index",
    "f_slice",
    "idx_memb",
    "intpol",
    "CAGR",
    "unit_uniform",
]

