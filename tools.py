# *************************************************************************************
# FILE INDEX
# *************************************************************************************

# Estructura:
#   "Título para el menú": ["nombre_del_archivo.csv de GT",
#                          ["keywords","en el mismo orden", "como aparecen en el archivo", 
#                               "y escritos de forma identica a como aparecen en el archivo"],
#                           "nombre_del_archivo.csv de GB", "nombre_del_archivo.csv de Bein", ]
tool_file_dic = {
    "Just in Time": ["justintime.csv", ["Just in Time"],"GB_Just_in_time.csv"],
    "Outsourcing": ["outsourcing.csv", ["Outsourcing"],"GB_Outsourcing.csv"],
    "Project Management": ["projectmanagement.csv", ["Project Management"],"GB_Project_Management.csv"],
    "Strategic Planning": ["strategic_planning.csv", ["Strategic Planning"],""],
    "Outsourcing - Six Sigma": ["outsourcingsixsigma.csv", ["Outsourcing", "Six Sigma"],""],
    "Outsourcing - Strategic Planning": ["Outso_Strategic.csv", ["Strategic Planning","Outsourcing"],""],
    # add more pairs here
}