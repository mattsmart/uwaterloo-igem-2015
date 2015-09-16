import datetime
import matplotlib.pyplot as plt
import os
import random

from genome_plot import genome_plot_polar
from init_genome_camv import init_genome_camv, init_targets_all_domains
from probabilistic import prob_repair


# output management
runs_folder = "runs" + os.sep  # store timestamped runs here
current_time = datetime.datetime.now().strftime("%Y-%m-%d %I.%M.%S%p")
time_folder = current_time + os.sep
current_run_folder = runs_folder + time_folder
# subfolders in the timestamped run directory:
data_folder = os.path.join(current_run_folder, "data")
plot_genome_folder = os.path.join(current_run_folder, "plot_genome")
plot_data_folder = os.path.join(current_run_folder, "plot_data")
# create dirs conditionally
dir_list = [runs_folder, current_run_folder, data_folder, plot_genome_folder, plot_data_folder]
for dirs in dir_list:
    if not os.path.exists(dirs):
        os.makedirs(dirs)

# simulation parameters (time in seconds)
complex_concentration = 135000000000
dt = 1.0
t0 = 0.0
t1 = 3600.0  # 18.0
total_turns = int((t1 - t0) / dt)
time_sim = t0
plot_period = 6  # in turns
plot_count = 0

# initialize genome
pseudo_targets = init_targets_all_domains(complex_concentration)
genome_camv = init_genome_camv(pseudo_targets)
genome_camv.initialize_target_cut_probabilities(dt)

# simulation pre-loop behaviour
target_dict = genome_camv.get_targets_from_genome()
open_targets = genome_camv.get_open_targets_from_genome()
probability_to_repair = prob_repair(dt)
double_cut_probability = 0.5#1.55*10.0**(-5)

# for logging data
data_log = ""
data_file = os.path.join(data_folder, "simulation_data")

# optional plotting
make_plot = False


for turn in xrange(total_turns):

    # clear turn log and set to turn
    turn_log = "Time: " + str(turn*dt) + "s\n"

    # get current targets
    targets_from_genome = genome_camv.get_targets_from_genome()

    # deletion module
    if len(open_targets) > 1:
        # time_with_double_cut += dt
        print open_targets
        double_cut_success = False
        if random.random() < double_cut_probability:
            double_cut_success = True
        if double_cut_success:
            targets = random.sample(open_targets, 2)
            # target1, target2 = targets_from_genome[targets[0][0]][targets[0][1]], targets_from_genome[targets[1][0]]targets[1][1]
            print target1, target2
            first = min(target1.current_start, target2.current_start)
            second = max(target1.current_start, target2.current_start)
            genome_camv.large_deletion(target1, target2)
            turn_log += "Large deletion spanning from", first, "to", second + "\n"

    # cut and repair module
    for key_domain in targets_from_genome.keys():
        domain = genome_camv.domains[key_domain]
        targets_from_domain = domain.targets
        success_cut = False
        success_repair = False
        for key_target in targets_from_domain.keys():
            target = targets_from_domain[key_target]
            if target.repaired:  # i.e. not cut
                probability_to_cut = target.cut_probability
                if random.random() < probability_to_cut:
                    success_cut = True
                if success_cut:
                    target.cut()
                    open_targets.append((key_domain, key_target))
                    turn_log += target.label + " cut at " + str(target.cut_position) + "\n"

            else:
                if random.random() < probability_to_repair:
                    success_repair = True
                if success_repair:
                    extra = ""
                    old_sequence = target.sequence
                    old_shift = target.shift
                    target.repair(dt)
                    open_targets.remove((key_domain, key_target))
                    net_indel_size = target.shift - old_shift
                    if old_sequence != target.sequence:
                        extra = "The sequence was changed from " + old_sequence + " to " + target.sequence
                    turn_log += target.label + " repaired at " + str(target.repair_position) + " with an indel of " + str(net_indel_size) + "\n" + extra + "\n"

    # save turn data (maybe only if stuff happened?)
    # \n's count number of events in turn (starts with one)
    if turn_log.count('\n') > 1:
        data_log += turn_log
        print turn_log

    # update plots if actively showing plots
    if turn % plot_period == 0 and make_plot:
        plot_path = os.path.join(plot_genome_folder, "genome_%05d" % plot_count)
        genome_plot_polar(genome_camv, 'CaMV', time=time_sim/60, output_path=plot_path, flag_show=False)
        plt.close()
        plot_count += 1

    # increment timer
    time_sim += dt

# print data_log
f = open(data_file, 'w')
f.write(data_log)
f.close()
