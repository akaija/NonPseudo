import sys
import uuid

from sqlalchemy import MetaData, Table, select

from non_pseudo.db import Base, session, engine

meta = MetaData(bind=engine)
materials = Table('materials', meta, autoload=True)

#def check_for_data(name):
#    result = engine.execute(select(
##        
##        [materials.c.name]))
##
##    exists = False
##    name = None
##    for row in result:
##        name = row[0]
##    result.close()
##    if name != None:
##        exists = True
#
#                [materials.c.ga0_absolute_volumetric_loading,
#                    materials.c.ga1_absolute_volumetric_loading,
#                    materials.c.sa_volumetric_surface_area,
#                    materials.c.vf_helium_void_fraction],
#                materials.c.name == name
#            )
#        )
#    exists = False
#    g0 = None
#    g1 = None
#    s = None
#    v = None
#    for row in result:
#        g0 = row[0]
#        g1 = row[1]
#        s = row[2]
#        v = row[3]
#    result.close()
#    if g0 != None and g1 != None and s != None and v != None:
#        exists = True
#
#    return exists
#
