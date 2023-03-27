def open_hash_file(filename):
    ##
    ##takes:
    ##path to file with well-region pairs
    ##
    ##returns:
    ##dictionary in the following format: key = well; value = associated region number
    ##
    
    import json
    
    result = open(filename, "r").read() ## открытие файла, присвоение содержимого в переменную
    
#    i = 0                     ##
#    while  result[i] != "'":  ## поиск номера символа "'", чтобы убрать шапку из навигатора
#        i += 1                ##
#    
    result = result[result.find("'"):]       ## отрезание шапки
    
#    result = "{" + result     ## добавление скобки в начало стринга
    
    result = result.replace(".000000", "")##удаление ненужных десятичных знаков у номеров регионов
    result = result.replace(" \n", '",')  ##удаление новых строки и замыкающих пробелов
    result = result.replace(" ", ':"')    ##замена пробелов на двоеточия
    result = result.replace("'", '"')     ##замена одинарных кавычек на двойные
    result = result[:-1]                  ##отрезание лишней запятой в конце
    
    result = "{" + result + "}"     ## добавелние скобок в стринг

    result = json.loads(result)        ## преобразование отформатированного стринга в хеш
    
    return(result)
    

def match_well_to_region(well, dict):
    ##
    ##takes:
    ##well name
    ##
    ##returns:
    ##according FIP region number
    ##
    
    return(int(dict[str(well)]))
    
    
def get_pres_from_region(dict_path: str):
    
    # import copy

    # dict_path = "Z:\zhivotikov_ip\Py_Scripts\Ya\Pres\HM_Well_FIP_Dict.txt"

    well_region_pairs = open_hash_file(dict_path)

    ##-----присвоение скважинам давлений в соответствующих регионах---------------------------
    ##3 лупа необходимо для копирования данных из векторов регионов в векторы скважин,
    ##так копируются скаляры, без полной индексации (модель + таймстеп + скважина)
    ##ругается на операции с разнородными векторами

    # reg_pres = copy.copy(wstath)    ## создание нового объекта вектора путем копирования существующего,
                                    ## вектор wstath выбран как заведомо пустой для надежности
									
    reg_pres = graph(type="well", default_value=0) 
	
    for model in get_all_models():
        for timestep in get_all_timesteps():
            for well in get_all_wells():
                try:
                    reg_pres[model, well, timestep] = rprp[model, get_fip_region("FIPPRH", match_well_to_region(well, well_region_pairs)), timestep]
                except KeyError:
                    reg_pres[model, well, timestep] = 0

    return reg_pres
#export(reg_pres, name = "Average Pressure in Region Matching", units = "pressure")
##-----------------------------------------------------------------------------------------