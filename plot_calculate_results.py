import matplotlib.pyplot as plt
import json
import argparse

plt.rc('xtick', labelsize=18)
plt.rc('ytick', labelsize=18)
parser = argparse.ArgumentParser('Calculate statistics and produce graphs for test data.')
parser.add_argument('statsfile', help='JSON file with relevant statistics data.')
parser.add_argument('schema_name', help='Name of schema for which we calculate the stats.')
parser.add_argument('out', help='Output file name prefix.')

def bar_from_dict(ax: plt.Axes, data: dict, title):
    ax.bar(range(len(data)), list(data.values()))
    ax.set_xticks(range(len(data)), list(data.keys()), fontsize=20)
    ax.set_title(title, fontsize=20)


def calculate_precision_recall_f1(data: dict, size=50):
    result = {}
    result['literal'] = {
        'precision': data['literal'] / (data['literal'] + (size - data['distraction'])),
        'recall': data['literal'] / (data['literal'] + (size - data['literal'])),
        'f1': 2 * data['literal'] / (2 * data['literal'] + (size - data['literal']) + (size - data['distraction']))
    }
    result['non-literal'] = {
        'precision': data['non-literal'] / (data['non-literal'] + (size - data['distraction'])),
        'recall': data['non-literal'] / (data['non-literal'] + (size - data['non-literal'])),
        'f1': 2 * data['non-literal'] / (
                    2 * data['non-literal'] + (size - data['non-literal']) + (size - data['distraction']))
    }
    result['overall'] = {
        'precision': (data['literal'] + data['non-literal']) /
                     (data['literal'] + data['non-literal'] + (size - data['distraction'])),
        'recall': (data['literal'] + data['non-literal']) /
                  (data['literal'] + (size - data['literal']) + data['non-literal'] + (size - data['non-literal'])),
        'f1': 2 * (data['literal'] + data['non-literal']) /
              (2 * (data['literal'] + data['non-literal']) + (size - data['literal']) + (size - data['non-literal'])
               + (size - data['distraction']))
    }
    return result


args = parser.parse_args()
#stats_fname_containment = args.statsfile
#stats_fname_source_path_goal = 'result_stats_source-path-goal.json'
stats_fname = args.statsfile

#stats_file_containment = open(stats_fname_containment)
#stats_file_source_path_goal = open(stats_fname_source_path_goal)
stats_file = open(stats_fname)

#stats_containment = json.load(stats_file_containment)
#stats_source_path_goal = json.load(stats_file_source_path_goal)
stats = json.load(stats_file)

#print(calculate_precision_recall_f1(stats_containment))
#print(calculate_precision_recall_f1(stats_source_path_goal))

metrics = calculate_precision_recall_f1(stats)
with open(args.out + '_metrics.json', 'w') as metrics_file:
    json.dump(metrics, metrics_file)

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
#bar_from_dict(axes[0], stats_containment, 'Accuracy for CONTAINMENT')
#bar_from_dict(axes[1], stats_source_path_goal, 'Accuracy for SOURCE-PATH-GOAL')
bar_from_dict(axes, stats, 'Accuracy for ' + args.schema_name)
#plt.show()
fig.savefig(args.out + '_graph.png')