##Постпроцессинг жирностей и добычи компонентов с учетом коэф. дизадаптации
##Считает:
##Скорректированный дебит скважин С5+ и С3+С4
##Скорректированный дебит установок С5+ и С3+С4
##Скорректированную жирность скважин С5+ и С3+С4
##Скорректированную жирность установок С5+ и С3+С4
##Скорректированную накопленную добычу скважин С5+ и С3+С4
##Скорректированную накопленную добычу установок С5+ и С3+С4
##Скорректиованный состав, соответствующий скорректированным содержаниям с разбиением до С10+

##Bombycilla Garrulus:
##https://cdn.download.ams.birds.cornell.edu/api/v1/asset/162296061/1800

def open_yield_file(filename, mode = "Yield"):
    ##
    ##takes:
    ##path to file with yield multipliers
    ##
    ##returns:
    ##dictionary in the following format: key = well; value = yield multiplier
    ##
    import json
    
    result = open(filename, "r").read()

    result = result.replace("\r","") ##удаление возврата каретки (тянется из VBA)
    result = result.replace("\n","") ##удаление новой строки
    if mode == "Yield":
        result = result[:-3] + result[-1] ##удаление запятой после последнего элемента
    result = json.loads(result)
    
    return result
    
   
def group_rate_total_yield_corr(group):
    ##
    ##takes:
    ##group name
    ##
    ##returns:
    ##nothing, but exports group rate, total production and yield (both C5+ and C3+C4) graphs
    ##
    group_C5p_rate = C5p_rate.sum(objects = get_group_by_name(group).all_wells)
    group_C5p_total = cum_sum_t(group_C5p_rate)
    group_C3_C4_rate = C3_C4_rate.sum(objects = get_group_by_name(group).all_wells)
    group_C3_C4_total = cum_sum_t(group_C3_C4_rate)
    group_C5_yield = group_C5p_rate / gwgpr[get_group_by_name (group)] * 1e6
    group_C3_C4_yield = group_C3_C4_rate / gwgpr[get_group_by_name (group)] * 1e6
    group_C2_yield = gcpr_4[get_group_by_name (group)] / gwgpr[get_group_by_name (group)] * 1e6
    group_He_yield = gcpr_2[get_group_by_name (group)] / gwgpr[get_group_by_name (group)] * 1e6
    
    export(group_C5p_rate, name = "%s C5+ Rate Corr" % group, units = "weight_rate") 
    export(group_C5p_total, name = "%s C5+ Total Corr"  % group, units = "weight")
    export(group_C5_yield, name = "%s C5+ Yield Corr"  % group, units = "density")
    export(group_C3_C4_rate, name = "%s C3+C4 Rate Corr"  % group, units = "weight_rate")
    export(group_C3_C4_total, name = "%s C3+C4 Total Corr"  % group, units = "weight")
    export(group_C3_C4_yield, name = "%s C3+C4 Yield Corr"  % group, units = "density")
    export(group_C2_yield, name = "%s C2 Yield"  % group, units = "density")
    export(group_He_yield, name = "%s He Yield"  % group, units = "density")
    export(group_C3_C4_yield * 0.62826182, name = "%s C3 Yield"  % group, units = "density")         ## Коэф. не от начального состава
    export(group_C3_C4_yield * 0.37173818, name = "%s C4 Yield"  % group, units = "density")         ## а от соотношения в продукции в модели
    
def get_pres_from_region(dict_path: str):

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
        result = result.replace("\n", '",')  ##удаление новых строки и замыкающих пробелов
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
    
def shift_to_hist(historic, calculated, graph_type = "well", shift_type = "mult"):

##Shifts calculated graph so that it matches to the most recent historic point
##Arg desc:
##historic - takes a tNav graph object, this is the graph to which the calculated will be shifted
##calculated - takes a tNav graph object, this is the graph to be shifted
##graph_type - takes the same arguments as the tNav's graph(function)
##shift_type - describes the logic which is used to shift the graph - multiplies the calculated graph when set to "mult", subtracts\adds from the calculated graph when set to "add"


    vector_corr = graph(type=graph_type, default_value=0)

    for model in get_all_models():

        mults_intermediate = get_all_wells()
        well_names = []
        for well in mults_intermediate:
            well_names.append(well.name)
        mults = dict.fromkeys(well_names)
        
        for well_name in well_names:
        
            if shift_type == "mult":
                mults[well_name] = 1
            else:
                mults[well_name] = 0

        for well_name in mults:
            for timestep in get_all_timesteps():
                if historic[model, get_well_by_name(well_name), timestep] > 0:
                    if shift_type == "add":
                        mults[well_name] = float((calculated - historic)[model, get_well_by_name(well_name), timestep])
                    if shift_type == "mult":
                        mults[well_name] = float((calculated / historic)[model, get_well_by_name(well_name), timestep])
        
        for well_name in mults:
            if shift_type == "add":
                vector_corr[model, get_well_by_name(well_name)] = calculated[model, get_well_by_name(well_name)] - mults[well_name]
            if shift_type == "mult":
                vector_corr[model, get_well_by_name(well_name)] = calculated[model, get_well_by_name(well_name)] / mults[well_name]

    return vector_corr
    
import sys, json

sys.path.insert(0, r'z:\zhivotikov_ip\Py_Scripts\Globals')

from Alcedo import rtwell, NegativePressureException
# from Cinclus import shift_to_hist
# from Cygnus import get_pres_from_region

extended_mode = False    ##флаг для ввыгрузки в расширенном виде для Свистуна

well_props = json.loads(open(r"Z:\zhivotikov_ip\Py_Scripts\Ya\Wells\well_properties.json", "r").read())
rtwells = {witem["name"]:rtwell(witem) for witem in well_props}
   
wpres_reg = get_pres_from_region(dict_path=r"Z:\zhivotikov_ip\Py_Scripts\Globals\Configs\well_region_pairs.txt")
wpres_reg = shift_to_hist(historic=wthph, calculated=wpres_reg, shift_type="add")
   
##====================C5+ Correction================================================
multsC5 = open_yield_file("Z:\zhivotikov_ip\Py_Scripts\Ya\Корректировка_Жирностей\Dict_Yield_C5.txt")

C5p_rate = wcpr_7 + wcpr_8 + wcpr_9
C5p_rate_bhp_cvd = graph(type="well", default_value=0)
C5p_selection_flag = graph(type="well", default_value=0)      ## коды: 1 - по тренду с последнего ГКИ, 2 - через ретроградную

for model in get_all_models():
    for timestep in get_all_timesteps():
        for well in get_group_by_name('KGAS').all_wells:
        
            ##try-except блок для пропуска скважин, для которых нет множителя (нагнеталки, пилоты и т.д.)
            try:
                C5p_rate[model, timestep, well] = C5p_rate[model, timestep, well] * multsC5[str(well)]
            except KeyError:
                C5p_rate[model, timestep, well] = C5p_rate[model, timestep, well]
                
            try:
                rtwell_pres = rtwells[str(well)].bhpab(pres=wpres_reg[model, timestep, well], rate=wwgpr[model, timestep, well] / 1e3)
                C5p_rate_bhp_cvd[model, timestep, well] = wwgpr[model, timestep, well] * rtwells[str(well)].yield_cvd(kind="C5+", pres=rtwell_pres) / 1e6
                
            except NegativePressureException:
                C5p_rate_bhp_cvd[model, timestep, well] = C5p_rate[model, timestep, well]
                print(
                    "WARNING At timestep {0}, well {1}, pres {2}, rate {3} BHP calculation through a and b resulted in BHP value below 0, yields from BHP will not be used for this timestep".format(
                    timestep.name, well.name, wpres_reg[model, timestep, well], wwgpr[model, timestep, well] / 1e3
                    )
                )
            
            except KeyError:
                C5p_rate_bhp_cvd[model, timestep, well] = C5p_rate[model, timestep, well]
            
            
            if C5p_rate[model, timestep, well] > C5p_rate_bhp_cvd[model, timestep, well]:
                C5p_rate[model, timestep, well] = C5p_rate_bhp_cvd[model, timestep, well]
                C5p_selection_flag[model, timestep, well] = 2
            else:
                C5p_selection_flag[model, timestep, well] = 1
            

C5p_total = cum_sum_t(C5p_rate)
C5p_yield = C5p_rate / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6

export(C5p_total, name = "C5+ Total Corrected, W", units = "weight")
export(C5p_rate, name = "C5+ Rate Corrected, W", units = "weight_rate")
export(C5p_yield, name = "C5+ Yield Corrected, W", units = "density")
export(C5p_selection_flag, name = "C5+ Selection Flag, W")
##===================================================================================


##-----------------C3+C4 Correction---------------------------------------------------
multsC3_C4 = open_yield_file("Z:\zhivotikov_ip\Py_Scripts\Ya\Корректировка_Жирностей\Dict_Yield_C3_C4.txt")

C3_C4_rate = wcpr_5 + wcpr_6
C3_C4_rate_bhp_cvd = graph(type="well", default_value=0)
C3_C4_selection_flag = graph(type="well", default_value=0)      ## коды: 1 - по тренду с последнего ГКИ, 2 - через ретроградную

for model in get_all_models():
    for timestep in get_all_timesteps():  
        for well in get_group_by_name('KGAS').all_wells:
            ##try-except блок для пропуска скважин, для которых нет множителя (нагнеталки, пилоты и т.д.)
            
            try:
                C3_C4_rate[model, timestep, well] = C3_C4_rate[model, timestep, well] * multsC3_C4[str(well)]
            except KeyError:
                C3_C4_rate[model, timestep, well] = C3_C4_rate[model, timestep, well]
                
            try:
                rtwell_pres = rtwells[str(well)].bhpab(pres=wpres_reg[model, timestep, well], rate=wwgpr[model, timestep, well] / 1e3)
                C3_C4_rate_bhp_cvd[model, timestep, well] = wwgpr[model, timestep, well] * rtwells[str(well)].yield_cvd(kind="C3+C4", pres=rtwell_pres) / 1e6
            except (NegativePressureException, KeyError):
                C3_C4_rate_bhp_cvd[model, timestep, well] = C3_C4_rate[model, timestep, well]
            
            if C3_C4_rate[model, timestep, well] > C3_C4_rate_bhp_cvd[model, timestep, well]:
                C3_C4_rate[model, timestep, well] = C3_C4_rate_bhp_cvd[model, timestep, well]
                C3_C4_selection_flag[model, timestep, well] = 2
            else:
                C3_C4_selection_flag[model, timestep, well] = 1
            
                
C3_C4_total = cum_sum_t(C3_C4_rate)
C3_C4_yield = C3_C4_rate / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6

export(C3_C4_selection_flag, name = "C3+C4 Selection flag")
export(C3_C4_total, name = "C3+C4 Total Corrected W", units = "weight")
export(C3_C4_rate, name = "C3+C4 Rate Corrected W", units = "weight_rate")
export(C3_C4_yield, name = "C3+C4 Yield Corrected, W", units = "density")
##------------------------------------------------------------------------------------


##//////////////NGL Calculations//////////////////////////////////////////////////////
He_rate_w = wcmpr_2 * 4 / 1e3              ##intended units = t
He_total_w = cum_sum_t(He_rate_w)
He_yield_w = He_rate_w / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6
He_NGL_rate_w = wcnmr_2 * 4 / 1e3          ##intended units = t
He_NGL_total_w = cum_sum_t(He_NGL_rate_w)
He_NGL_yield_w = He_NGL_rate_w / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6

C2_rate_w = wcmpr_4 * 30.07 / 1e3          ##intended units = t
C2_total_w = cum_sum_t(C2_rate_w)
C2_yield_w = C2_rate_w / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6
C2_NGL_rate_w = wcnmr_4 * 30.07 / 1e3      ##intended units = t
C2_NGL_total_w = cum_sum_t(C2_NGL_rate_w)
C2_NGL_yield_w = C2_NGL_rate_w / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6

export(He_rate_w, name = "He Rate non NGL, W", units = "weight_rate")
export(He_total_w, name = "He Total non NGL, W", units = "weight")
export(He_yield_w, name = "He Yield non NGL, W", units = "density")
export(He_NGL_rate_w, name = "He Rate NGL, W", units = "weight_rate")
export(He_NGL_total_w, name = "He Total NGL, W", units = "weight")
export(He_NGL_yield_w, name = "He Yield NGL, W", units = "density")

export(C2_rate_w, name = "C2 Rate non NGL, W", units = "weight_rate")
export(C2_total_w, name = "C2 Total non NGL, W", units = "weight")
export(C2_yield_w, name = "C2 Yield non NGL, W", units = "density")
export(C2_NGL_rate_w, name = "C2 Rate NGL, W", units = "weight_rate")
export(C2_NGL_total_w, name = "C2 Total NGL, W", units = "weight")
export(C2_NGL_yield_w, name = "C2 Yield NGL, W", units = "density")
##////////////////////////////////////////////////////////////////////////////////////



group_rate_total_yield_corr("UPPPNG")
##try-except блок для использования в моделях, с совмещенным GRUPTREE (без разделения на 3.6 и 12)
try:
    group_rate_total_yield_corr("UPPPNG_3.6")
except:
    pass
    
try:
    group_rate_total_yield_corr("UPPPNG_12")
except:
    pass
##-----------------------расширенная выгрузка для Свистуна------------------------------
if extended_mode:

    C1_yield_ext = wcpr_3 / wwgpr / weff[get_model_by_name(get_project_name())] * 1e6
    C3_yield_ext = C3_C4_yield * (wcpr_5 / (wcpr_5 + wcpr_6))
    C4_yield_ext = C3_C4_yield * (wcpr_6 / (wcpr_5 + wcpr_6))
    C5_yield_ext = C5p_yield * 0.1305
    C6p_yield_ext = C5p_yield - C5_yield_ext
    
    export(C1_yield_ext, name = "C1 Yield non NGL, W", units = "density")
    export(C3_yield_ext, name = "C3 Yield non NGL, W", units = "density")
    export(C4_yield_ext, name = "C4 Yield non NGL, W", units = "density")
    export(C5_yield_ext, name = "C5 Yield non NGL, W", units = "density")
    export(C6p_yield_ext, name = "C6+ Yield non NGL, W", units = "density")

##==============корректировка и разбиение составов================================

MW = open_yield_file("Z:\zhivotikov_ip\Py_Scripts\Ya\Корректировка_Жирностей\Bombycilla_Config\MW.txt", mode = "")
comp_partition_parts = open_yield_file("Z:\zhivotikov_ip\Py_Scripts\Ya\Корректировка_Жирностей\Bombycilla_Config\Comp_partition.txt", mode = "")

##расчет скорректированного состава
C5p_molar_part = C5p_yield / float(MW["C5+"]) * 24.04 / 1e3
C3_C4_molar_part = C3_C4_yield / float(MW["C3-4"]) * 24.04 / 1e3

total_molar_rate = wcmpr_1 + wcmpr_2 + wcmpr_3 + wcmpr_4 + wcmpr_5 + wcmpr_6 + wcmpr_7 + wcmpr_8 + wcmpr_9
CN_molar_part = wcmpr_1 / total_molar_rate
He_molar_part = wcmpr_2 / total_molar_rate
C1_molar_part = wcmpr_3 / total_molar_rate
C2_molar_part = wcmpr_4 / total_molar_rate

##нормировка скорректированного состава
molar_parts_precorr = CN_molar_part + He_molar_part + C1_molar_part + C2_molar_part# + C3_C4_molar_part + C5p_molar_part

CN_molar_part = CN_molar_part / (molar_parts_precorr / (1 - C3_C4_molar_part - C5p_molar_part))
He_molar_part = He_molar_part / (molar_parts_precorr / (1 - C3_C4_molar_part - C5p_molar_part))
C1_molar_part = C1_molar_part / (molar_parts_precorr / (1 - C3_C4_molar_part - C5p_molar_part))
C2_molar_part = C2_molar_part / (molar_parts_precorr / (1 - C3_C4_molar_part - C5p_molar_part))

# CN_molar_part = CN_molar_part / molar_parts_precorr
# He_molar_part = He_molar_part / molar_parts_precorr
# C1_molar_part = C1_molar_part / molar_parts_precorr
# C2_molar_part = C2_molar_part / molar_parts_precorr
#C3_C4_molar_part = C3_C4_molar_part / molar_parts_precorr
#C5p_molar_part = C5p_molar_part / molar_parts_precorr

##разбиение скорректированного состава
H2_molar_part = CN_molar_part * float(comp_partition_parts["H2"])
N2_molar_part = CN_molar_part * float(comp_partition_parts["N2"])
CO2_molar_part = CN_molar_part * float(comp_partition_parts["CO2"])
C3_molar_part = C3_C4_molar_part * float(comp_partition_parts["C3"])
C4i_molar_part = C3_C4_molar_part * float(comp_partition_parts["C4i"])
C4n_molar_part = C3_C4_molar_part * float(comp_partition_parts["C4n"])
C5i_molar_part = C5p_molar_part * float(comp_partition_parts["C5i"])
C5n_molar_part = C5p_molar_part * float(comp_partition_parts["C5n"])
C6_molar_part = C5p_molar_part * float(comp_partition_parts["C6"])
C7_molar_part = C5p_molar_part * float(comp_partition_parts["C7"])
C8_molar_part = C5p_molar_part * float(comp_partition_parts["C8"])
C9_molar_part = C5p_molar_part * float(comp_partition_parts["C9"])
C10p_molar_part = C5p_molar_part * float(comp_partition_parts["C10+"])


export(H2_molar_part, name = "Extended Component H2 Molar Part")
export(N2_molar_part, name = "Extended Component N2 Molar Part")
export(CO2_molar_part, name = "Extended Component CO2 Molar Part")
export(He_molar_part, name = "Extended Component He Molar Part")
export(C1_molar_part, name = "Extended Component C1 Molar Part")
export(C2_molar_part, name = "Extended Component C2 Molar Part")
export(C3_molar_part, name = "Extended Component C3 Molar Part")
export(C4i_molar_part, name = "Extended Component C4i Molar Part")
export(C4n_molar_part, name = "Extended Component C4n Molar Part")
export(C5i_molar_part, name = "Extended Component C5i Molar Part")
export(C5n_molar_part, name = "Extended Component C5n Molar Part")
export(C6_molar_part, name = "Extended Component C6 Molar Part")
export(C7_molar_part, name = "Extended Component C7 Molar Part")
export(C8_molar_part, name = "Extended Component C8 Molar Part")
export(C9_molar_part, name = "Extended Component C9 Molar Part")
export(C10p_molar_part, name = "Extended Component C10+ Molar Part")
