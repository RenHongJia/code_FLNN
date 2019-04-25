from model.scaling.ProactiveSLAScaling import SLABasedOnVms as BrokerScaling
from utils.IOUtil import load_number_of_vms, save_scaling_results_to_csv
from utils.MetricUtil import ADI
import numpy as np

model_names = {"fl_bfonn": "fl_bfonn"}
input_types = {"uni": "uni", "multi": "multi"}

models = [
    {"name": model_names["fl_bfonn"],
     "sliding": 3,
     "input_type": input_types["uni"],
     "cpu": "FL_BFONN-sliding_3-ex_func_3-act_func_0-pop_size_70-elim_disp_steps_2-repro_steps_5-chem_steps_80-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_4",
     "ram": "FL_BFONN-sliding_3-ex_func_2-act_func_0-pop_size_100-elim_disp_steps_1-repro_steps_5-chem_steps_80-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_8"},
    {"name": model_names["fl_bfonn"],
     "sliding": 3,
     "input_type": input_types["multi"],
     "cpu": "FL_BFONN-sliding_3-ex_func_3-act_func_0-pop_size_100-elim_disp_steps_2-repro_steps_5-chem_steps_60-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_8",
     "ram": "FL_BFONN-sliding_3-ex_func_3-act_func_0-pop_size_100-elim_disp_steps_1-repro_steps_3-chem_steps_80-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.1-p_eliminate_0.25-swim_length_8"},
    {"name": model_names["fl_bfonn"],
     "sliding": 4,
     "input_type": input_types["uni"],
     "cpu": "FL_BFONN-sliding_4-ex_func_3-act_func_0-pop_size_100-elim_disp_steps_2-repro_steps_3-chem_steps_60-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.1-p_eliminate_0.25-swim_length_8",
     "ram": "FL_BFONN-sliding_4-ex_func_2-act_func_0-pop_size_100-elim_disp_steps_2-repro_steps_5-chem_steps_80-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.15-p_eliminate_0.25-swim_length_4"},
    {"name": model_names["fl_bfonn"],
     "sliding": 4,
     "input_type": input_types["multi"],
     "cpu": "FL_BFONN-sliding_4-ex_func_3-act_func_0-pop_size_100-elim_disp_steps_2-repro_steps_5-chem_steps_60-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_8",
     "ram": "FL_BFONN-sliding_4-ex_func_3-act_func_0-pop_size_70-elim_disp_steps_1-repro_steps_5-chem_steps_60-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_4"},
    {"name": model_names["fl_bfonn"],
     "sliding": 5,
     "input_type": input_types["uni"],
     "cpu": "FL_BFONN-sliding_5-ex_func_3-act_func_0-pop_size_100-elim_disp_steps_1-repro_steps_3-chem_steps_80-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_4",
     "ram": "FL_BFONN-sliding_5-ex_func_3-act_func_0-pop_size_50-elim_disp_steps_2-repro_steps_5-chem_steps_80-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.1-p_eliminate_0.25-swim_length_4"},
    {"name": model_names["fl_bfonn"],
     "sliding": 5,
     "input_type": input_types["multi"],
     "cpu": "FL_BFONN-sliding_5-ex_func_3-act_func_0-pop_size_100-elim_disp_steps_2-repro_steps_5-chem_steps_60-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_8",
     "ram": "FL_BFONN-sliding_2-ex_func_3-act_func_0-pop_size_50-elim_disp_steps_2-repro_steps_3-chem_steps_60-d_attr_0.1_w_attr_0.2-h_rep_0.1_w_rep_10-step_size_0.05-p_eliminate_0.25-swim_length_4"},
]

s_coffs = [ 1 + x / 10 for x in range(0, 21)]
L_adaps = [ x for x in range(2, 51)]


resource_real_used = load_number_of_vms('vms_real_used_CPU_RAM.csv')
for model in models:

    if model["input_type"] == "multi":
        cpu_file = "results/" + model["name"] + "/multi_cpu/" + model["cpu"] + ".csv"
        ram_file = "results/" + model["name"] + "/multi_ram/" + model["ram"] + ".csv"
    else:
        cpu_file = "results/" + model["name"] + "/cpu/" + model["cpu"] + ".csv"
        ram_file = "results/" + model["name"] + "/ram/" + model["ram"] + ".csv"

    violated_arrays = []
    adi_arrays = []
    for s_coff in s_coffs:

        violated_arr = []
        adi_arr = []
        for L_adap in L_adaps:

            broker = BrokerScaling(scaling_coefficient=s_coff, adaptation_len=L_adap)
            neural_net = broker.sla_violate(cpu_file, ram_file)
            eval_scaler = ADI(lower_bound=0.6, upper_bound = 0.8, metric='CPU Utilisation %')
            adi = sum(np.array(eval_scaler.calculate_ADI(resource_used=resource_real_used, resource_allocated=neural_net[1][-1])))

            violated_arr.append(round(neural_net[0], 2))
            adi_arr.append(round(adi, 2))

        violated_arrays.append(violated_arr)
        adi_arrays.append(adi_arr)

    violated_path_file = "results/scaling2/sliding_" + str(model["sliding"]) + "/" + model["input_type"] + "/" + model["name"] + "_violated"
    adi_path_file = "results/scaling2/sliding_" + str(model["sliding"]) + "/" + model["input_type"] + "/" + model["name"] + "_adi"

    save_scaling_results_to_csv(violated_arrays, violated_path_file)
    save_scaling_results_to_csv(adi_arrays, adi_path_file)



