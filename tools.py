# *************************************************************************************
# TOOLS DICTIONARY
# *************************************************************************************

# Dictionary Structure:
#   "Tool Name": [
#       "Google_Trends_file.csv",      # Index 0: Google Trends (GT)
#       ["Tool Name"],                 # Index 1: Keywords list
#       "Google_Books_file.csv",       # Index 2: Google Books (GB)
#       "Bain_Usage_file.csv",         # Index 3: Bain Usage (BU)
#       "Crossref_file.csv",           # Index 4: Crossref (CR)
#       "Bain_Satisfaction_file.csv"   # Index 5: Bain Satisfaction (BS)
#   ]

tool_file_dic = {   'Alianzas y Capital de Riesgo': [   'GT_Alianzas_y_Capital_de_Riesgo_0589.csv',
                                        ['Alianzas y Capital de Riesgo'],
                                        'GB_Alianzas_y_Capital_de_Riesgo_6982.csv',
                                        'BU_Alianzas_y_Capital_de_Riesgo_2190.csv',
                                        'CR_AlianzasyCapitaldeRiesgo_monthly_relative.csv',
                                        'BS_Alianzas_y_Capital_de_Riesgo_3848.csv'],
    'Benchmarking': [   'GT_Benchmarking_9762.csv',
                        ['Benchmarking'],
                        'GB_Benchmarking_7798.csv',
                        'BU_Benchmarking_2485.csv',
                        'CR_Benchmarking_monthly_relative.csv',
                        'BS_Benchmarking_6010.csv'],
    'Calidad Total': [   'GT_Calidad_Total_9935.csv',
                         ['Calidad Total'],
                         'GB_Calidad_Total_9438.csv',
                         'BU_Calidad_Total_6313.csv',
                         'CR_CalidadTotal_monthly_relative.csv',
                         'BS_Calidad_Total_7261.csv'],
    'Competencias Centrales': [   'GT_Competencias_Centrales_7463.csv',
                                  ['Competencias Centrales'],
                                  'GB_Competencias_Centrales_9111.csv',
                                  'BU_Competencias_Centrales_3509.csv',
                                  'CR_CompetenciasCentrales_monthly_relative.csv',
                                  'BS_Competencias_Centrales_8232.csv'],
    'Cuadro de Mando Integral': [   'GT_Cuadro_de_Mando_Integral_8613.csv',
                                    ['Cuadro de Mando Integral'],
                                    'GB_Cuadro_de_Mando_Integral_3080.csv',
                                    'BU_Cuadro_de_Mando_Integral_5505.csv',
                                    'CR_CuadrodeMandoIntegral_monthly_relative.csv',
                                    'BS_Cuadro_de_Mando_Integral_7880.csv'],
    'Estrategias de Crecimiento': [   'GT_Estrategias_de_Crecimiento_0953.csv',
                                      ['Estrategias de Crecimiento'],
                                      'GB_Estrategias_de_Crecimiento_2064.csv',
                                      'BU_Estrategias_de_Crecimiento_2612.csv',
                                      'CR_EstrategiasdeCrecimiento_monthly_relative.csv',
                                      'BS_Estrategias_de_Crecimiento_7581.csv'],
    'Experiencia del Cliente': [   'GT_Experiencia_del_Cliente_3856.csv',
                                   ['Experiencia del Cliente'],
                                   'GB_Experiencia_del_Cliente_1253.csv',
                                   'BU_Experiencia_del_Cliente_5464.csv',
                                   'CR_ExperienciadelCliente_monthly_relative.csv',
                                   'BS_Experiencia_del_Cliente_7129.csv'],
    'Fusiones y Adquisiciones': [   'GT_Fusiones_y_Adquisiciones_3141.csv',
                                    ['Fusiones y Adquisiciones'],
                                    'GB_Fusiones_y_Adquisiciones_1255.csv',
                                    'BU_Fusiones_y_Adquisiciones_8219.csv',
                                    'CR_FusionesyAdquisiciones_monthly_relative.csv',
                                    'BS_Fusiones_y_Adquisiciones_9843.csv'],
    'Gestión de Costos': [   'GT_Gestion_de_Costos_9839.csv',
                             ['Gestión de Costos'],
                             'GB_Gestion_de_Costos_0679.csv',
                             'BU_Gestion_de_Costos_5492.csv',
                             'CR_GestióndeCostos_monthly_relative.csv',
                             'BS_Gestion_de_Costos_2796.csv'],
    'Gestión de la Cadena de Suministro': [   'GT_Gestion_de_la_Cadena_de_Suministro_7968.csv',
                                              ['Gestión de la Cadena de Suministro'],
                                              'GB_Gestion_de_la_Cadena_de_Suministro_9121.csv',
                                              'BU_Gestion_de_la_Cadena_de_Suministro_2519.csv',
                                              'CR_GestióndelaCadenadeSuministro_monthly_relative.csv',
                                              'BS_Gestion_de_la_Cadena_de_Suministro_5471.csv'],
    'Gestión del Cambio': [   'GT_Gestion_del_Cambio_9306.csv',
                              ['Gestión del Cambio'],
                              'GB_Gestion_del_Cambio_4427.csv',
                              'BU_Gestion_del_Cambio_7720.csv',
                              'CR_GestióndelCambio_monthly_relative.csv',
                              'BS_Gestion_del_Cambio_7699.csv'],
    'Gestión del Conocimiento': [   'GT_Gestion_del_Conocimiento_0940.csv',
                                    ['Gestión del Conocimiento'],
                                    'GB_Gestion_del_Conocimiento_2957.csv',
                                    'BU_Gestion_del_Conocimiento_0878.csv',
                                    'CR_GestióndelConocimiento_monthly_relative.csv',
                                    'BS_Gestion_del_Conocimiento_4066.csv'],
    'Innovación Colaborativa': [   'GT_Innovacion_Colaborativa_7878.csv',
                                   ['Innovación Colaborativa'],
                                   'GB_Innovacion_Colaborativa_7436.csv',
                                   'BU_Innovacion_Colaborativa_7921.csv',
                                   'CR_InnovaciónColaborativa_monthly_relative.csv',
                                   'BS_Innovacion_Colaborativa_8131.csv'],
    'Lealtad del Cliente': [   'GT_Lealtad_del_Cliente_5304.csv',
                               ['Lealtad del Cliente'],
                               'GB_Lealtad_del_Cliente_6994.csv',
                               'BU_Lealtad_del_Cliente_8749.csv',
                               'CR_LealtaddelCliente_monthly_relative.csv',
                               'BS_Lealtad_del_Cliente_1980.csv'],
    'Optimización de Precios': [   'GT_Optimizacion_de_Precios_6724.csv',
                                   ['Optimización de Precios'],
                                   'GB_Optimizacion_de_Precios_1351.csv',
                                   'BU_Optimizacion_de_Precios_4984.csv',
                                   'CR_OptimizacióndePrecios_monthly_relative.csv',
                                   'BS_Optimizacion_de_Precios_4880.csv'],
    'Outsourcing': [   'GT_Outsourcing_8336.csv',
                       ['Outsourcing'],
                       'GB_Outsourcing_0748.csv',
                       'BU_Outsourcing_6584.csv',
                       'CR_Outsourcing_monthly_relative.csv',
                       'BS_Outsourcing_1345.csv'],
    'Planificación Estratégica': [   'GT_Planificacion_Estrategica_1480.csv',
                                     ['Planificación Estratégica'],
                                     'GB_Planificacion_Estrategica_7516.csv',
                                     'BU_Planificacion_Estrategica_0262.csv',
                                     'CR_PlanificaciónEstratégica_monthly_relative.csv',
                                     'BS_Planificacion_Estrategica_1370.csv'],
    'Planificación de Escenarios': [   'GT_Planificacion_de_Escenarios_5438.csv',
                                       ['Planificación de Escenarios'],
                                       'GB_Planificacion_de_Escenarios_7511.csv',
                                       'BU_Planificacion_de_Escenarios_5065.csv',
                                       'CR_PlanificacióndeEscenarios_monthly_relative.csv',
                                       'BS_Planificacion_de_Escenarios_1037.csv'],
    'Presupuesto Base Cero': [   'GT_Presupuesto_Base_Cero_2649.csv',
                                 ['Presupuesto Base Cero'],
                                 'GB_Presupuesto_Base_Cero_5007.csv',
                                 'BU_Presupuesto_Base_Cero_7895.csv',
                                 'CR_PresupuestoBaseCero_monthly_relative.csv',
                                 'BS_Presupuesto_Base_Cero_0056.csv'],
    'Propósito y Visión': [   'GT_Proposito_y_Vision_7345.csv',
                              ['Propósito y Visión'],
                              'GB_Proposito_y_Vision_7742.csv',
                              'BU_Proposito_y_Vision_5388.csv',
                              'CR_PropósitoyVisión_monthly_relative.csv',
                              'BS_Proposito_y_Vision_9777.csv'],
    'Reingeniería de Procesos': [   'GT_Reingenieria_de_Procesos_8373.csv',
                                    ['Reingeniería de Procesos'],
                                    'GB_Reingenieria_de_Procesos_2346.csv',
                                    'BU_Reingenieria_de_Procesos_4015.csv',
                                    'CR_ReingenieríadeProcesos_monthly_relative.csv',
                                    'BS_Reingenieria_de_Procesos_0061.csv'],
    'Segmentación de Clientes': [   'GT_Segmentacion_de_Clientes_3757.csv',
                                    ['Segmentación de Clientes'],
                                    'GB_Segmentacion_de_Clientes_1851.csv',
                                    'BU_Segmentacion_de_Clientes_3670.csv',
                                    'CR_SegmentacióndeClientes_monthly_relative.csv',
                                    'BS_Segmentacion_de_Clientes_4595.csv'],
    'Talento y Compromiso': [   'GT_Talento_y_Compromiso_9324.csv',
                                ['Talento y Compromiso'],
                                'GB_Talento_y_Compromiso_7890.csv',
                                'BU_Talento_y_Compromiso_8832.csv',
                                'CR_TalentoyCompromiso_monthly_relative.csv',
                                'BS_Talento_y_Compromiso_3961.csv']}