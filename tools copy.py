# *************************************************************************************
# FILE INDEX
# *************************************************************************************

# Estructura:
#   "Título para el menú igual": 
#        ["nombre_del_archivo.csv de GT",
#        ["keywords","en el mismo orden", "como aparecen en el archivo", "y escritos de forma identica a como aparecen en el archivo"],
#        "nombre_del_archivo.csv de GB", 
#        "nombre_del_archivo.csv de Bein Uso BR", 
#        "nombre_del_archivo.csv de CR",
#        "nombre_del_archivo.csv de Bein Satisfacción BS"]

tool_file_dic = {
    "Just in Time":             # Nombre en el menú
        ["justintime.csv",      # Archivo de Google Trends GT
        ["Just in Time"],       # Keywords
        "GB_Just_in_time.csv",  # Archivo de GoogleBooks Ngram GB
        "BR_Just_in_Time_7600.csv",  # Archivo de Bein Research BR Usability
        "CR_Just in Ti_1168ec.csv",  # Archivo de Crossref.org
        "BS_Just_in_Time_6604.csv"], # Archivo de Bein Research BS Satisfaction
    "Outsourcing": 
        ["outsourcing.csv", 
        ["Outsourcing"],
        "GB_Outsourcing.csv", 
        "BR_Outsourcing_6877.csv", 
        "CR_Outsourcin_421676.csv",
        "BS_Outsourcing_3352.csv"],
    "Project Management": 
        ["projectmanagement.csv", 
        ["Project Management"],
        "GB_Project_Management.csv", 
        "BR_Project_Management_4635.csv", 
        "CR_Project Ma_9c1330.csv",
        "BS_Project_Management_7554.csv"],
    "Strategic Planning": 
        ["strategic_planning.csv", 
        ["Strategic Planning"],
        "GB_Strategic_Planning.csv", 
        "R_Strategic_Planning_9700.csv", 
        "CR_Strategic _1056ea.csv",
        "BS_Strategic_Planning_6290.csv"],
    "Balanced Scorecard":
        ["",
        ["Balanced Scorecard"],
        "",
        "BR_Balanced_Scorecard_5615.csv",
        "CR_Balanced S_997a15.csv",
        "BS_Balanced_Scorecard_5020.csv"],# add more entries here
}