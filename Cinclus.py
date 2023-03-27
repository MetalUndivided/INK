##Считает скорректированную пластовку (модель совпадает с последним замером)

##Cinclus Cinclus
##https://ebird.org/species/whtdip1#


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



#export(shift_to_hist(historic=wthph, calculated=wbp9, shift_type = "add"), name = "WBP9 Corr", units = "pressure")