import pandas as pd
import numpy as np
import argparse
import dataio
import json
import glob
import os


parser = argparse.ArgumentParser(description='Combine runs')
parser.add_argument('--datasets', type=str, nargs='+')
options = parser.parse_args()

for DATASET_NAME in options.datasets:
    CSV_FOLDER, CSV_TRAIN, CSV_TEST, CSV_VAL, CONFIG_FILE, Q_NPZ = dataio.build_paths(DATASET_NAME)

    tracked_metrics = ['accuracy', 'll_mcmc_all']
    experiments = next(os.walk(CSV_FOLDER))[1]  # List all folders
    for experiment in experiments:
        results = {}
        df = {}
        for run_id in range(5):
            rlog = os.path.join(CSV_FOLDER, experiment, str(run_id), 'rlog.csv')
            results_file = os.path.join(CSV_FOLDER, experiment, str(run_id), 'results.json')
            if os.path.isfile(rlog):
                df[run_id] = pd.read_csv(rlog)
            if os.path.isfile(results_file):
                with open(results_file) as f:
                    results[run_id] = json.load(f)
        if df:
            mean_df = pd.DataFrame()
            for column in tracked_metrics:
                mean_df[column] = np.column_stack([df[i][column] for i in df]).mean(axis=1)
            mean_df.to_csv(os.path.join(CSV_FOLDER, experiment, 'rlog.csv'))

        if results:
            with open(os.path.join(CSV_FOLDER, experiment, 'results.json'), 'w') as f:
                f.write(json.dumps({
                    'args': results[0]['args'],
                    'legends': {
                        'short': results[0]['legends']['short'],
                        'full': results[0]['legends']['full'],
                        'latex': results[0]['legends']['latex']
                    },
                    'metrics': {
                        metric: np.mean([results[i]['metrics'][metric] for i in results])
                        for metric in {'ACC', 'AUC', 'NLL'}
                    }
                }, indent=4))
