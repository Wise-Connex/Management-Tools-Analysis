# *************************************************************************************
# FILE INDEX
# *************************************************************************************

# Estructura:
#   "Título para el menú igual": 
#        ["nombre_del_archivo.csv de GT",
#        ["keywords","en el mismo orden", "como aparecen en el archivo", "y escritos de forma identica a como aparecen en el archivo"],
#        "nombre_del_archivo.csv de GB", 
#        "nombre_del_archivo.csv de Bein", 
#        "nombre_del_archivo.csv de CR"]

tool_file_dic = {
    "Just in Time": 
        ["justintime.csv", 
        ["Just in Time"],
        "GB_Just_in_time.csv", 
        "", 
        "CR_Just_in_Time.csv"],
    "Outsourcing": 
        ["outsourcing.csv", 
        ["Outsourcing"],
        "GB_Outsourcing.csv", 
        "", 
        "CR_Outsourcing.csv"],
    "Project Management": 
        ["projectmanagement.csv", 
        ["Project Management"],"GB_Project_Management.csv", 
        "", 
        "CR_Project_Management.csv"],
    "Strategic Planning": 
        ["strategic_planning.csv", 
        ["Strategic Planning"],
        "GB_Strategic_Planning.csv", 
        "", 
        "CR_Strategic_Planning.csv"],
    "Balanced Scorecard":
        ["",
        ["Balanced Scorecard"],
        "",
        "",
        "CR_Balanced_Scorecard.csv"],
    "Outsourcing - Six Sigma": 
        ["outsourcingsixsigma.csv", 
        ["Outsourcing", "Six Sigma"],
        "", 
        "", 
        ""],
    "Outsourcing - Strategic Planning": 
        ["Outso_Strategic.csv", 
        ["Strategic Planning","Outsourcing"],
        "", 
        "", 
        ""],
    # add more entries here
}