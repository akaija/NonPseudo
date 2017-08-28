
import sys
import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.sql import text

from non_pseudo.db import Base, session, engine

class Material(Base):
    """Declarative class mapping to table storing material/simulation data.

    Attributes:
    """
    __tablename__ = 'materials'
    # COLUMN                                                 UNITS
    id = Column(Integer, primary_key=True)                 # dimm.
    name = Column(String(150))
    run_id = Column(String(50))

    # DATA COLLECTED

    # first-pressure gas adsorption
    ga0_absolute_volumetric_loading = Column(Float)            # cm^3 / cm^3
    ga0_absolute_gravimetric_loading = Column(Float)           # cm^3 / g
    ga0_absolute_molar_loading = Column(Float)                 # mol / kg
    ga0_excess_volumetric_loading = Column(Float)              # cm^3 / cm^3
    ga0_excess_gravimetric_loading = Column(Float)             # cm^3 / g
    ga0_excess_molar_loading = Column(Float)                   # mol /kg
    ga0_host_host_avg = Column(Float)                          # K
    ga0_host_host_vdw = Column(Float)                          # K
    ga0_host_host_cou = Column(Float)                          # K
    ga0_adsorbate_adsorbate_avg = Column(Float)                # K
    ga0_adsorbate_adsorbate_vdw = Column(Float)                # K
    ga0_adsorbate_adsorbate_cou = Column(Float)                # K
    ga0_host_adsorbate_avg = Column(Float)                     # K
    ga0_host_adsorbate_vdw = Column(Float)                     # K
    ga0_host_adsorbate_cou = Column(Float)                     # K

    # second-pressure gas adsorption
    ga1_absolute_volumetric_loading = Column(Float)            # cm^3 / cm^3
    ga1_absolute_gravimetric_loading = Column(Float)           # cm^3 / g
    ga1_absolute_molar_loading = Column(Float)                 # mol / kg
    ga1_excess_volumetric_loading = Column(Float)              # cm^3 / cm^3
    ga1_excess_gravimetric_loading = Column(Float)             # cm^3 / g
    ga1_excess_molar_loading = Column(Float)                   # mol /kg
    ga1_host_host_avg = Column(Float)                          # K
    ga1_host_host_vdw = Column(Float)                          # K
    ga1_host_host_cou = Column(Float)                          # K
    ga1_adsorbate_adsorbate_avg = Column(Float)                # K
    ga1_adsorbate_adsorbate_vdw = Column(Float)                # K
    ga1_adsorbate_adsorbate_cou = Column(Float)                # K
    ga1_host_adsorbate_avg = Column(Float)                     # K
    ga1_host_adsorbate_vdw = Column(Float)                     # K
    ga1_host_adsorbate_cou = Column(Float)                     # K

    # surface area
    sa_unit_cell_surface_area = Column(Float)                 # angstroms ^ 2
    sa_volumetric_surface_area = Column(Float)                # m^2 / cm^3
    sa_gravimetric_surface_area = Column(Float)               # m^2 / g

    # void fraction
    vf_helium_void_fraction = Column(Float)                   # dimm.

    def __init__(self, name, ):
        """Init material-row.

        Args:
            self (class): row in material table.
            run_id : identification string for run (default = None).

        Initializes row in materials datatable.

        """
        self.name = name
