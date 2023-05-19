from pycistem.core import Project

pro = Project()
pro.OpenProjectFromFile("/nrs/elferich/old_THP1_brequinar/20230407_THP1_C_glycerol_g2_aa26/20230407_THP1_C_glycerol_g2_aa26.db")

pro.database.CheckandUpdateSchema()
pro.Close(True,True)
