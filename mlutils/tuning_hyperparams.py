from scipy.sparse.construct import random
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
import optuna
from optuna.samplers import RandomSampler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import explained_variance_score, max_error
from sklearn.metrics import mean_squared_log_error, median_absolute_error
from sklearn.metrics import make_scorer
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    precision_score,
    f1_score,
    recall_score,
)

from mlutils.feature_engineering import select_data


def tuning_hyperparams(
    df,
    target: str,
    parameters: dict,
    algorithm,
    metric,
    scoring_option: str,
    n_trials: int,
):

    """
    Perform hyperparameters optimization using optuna framework for the chosen technique.

    :param df: DataFrame pandas
    :type: DataFrame
    :param target: target variable
    :type: str
    :param parameters: Dict that contains all the threshold given for optimization testing
    :type: dict
    :param algorithm: Machine Learning algorithm used for fit the model
    :type: class
    :param metric: Metric used for the evaluation of the tests
    :type: function
    :param scoring_option: Maximize or minimize objectives
    :type: str
    :param n_trials: The of trials that the framework must perform
    :type: int
    :raise exception: The optimization method couldn't be processed
    :return: Best hyperparameter features chosen by the technique 
    :rtype: dict

    """
    x, y = select_data(df=df, target=target)

    parameters_dict = {}

    def objective(trial=n_trials, parameters=parameters, metric=metric, x=x, y=y):

        if parameters:
            for i, param in enumerate(parameters):

                if param["type"] == "Real":
                    parameters_dict[param["name"]] = trial.suggest_uniform(
                        name=param["name"], low=param["low"], high=param["high"]
                    )
                elif param["type"] == "Categorical":
                    parameters_dict[param["name"]] = trial.suggest_categorical(
                        name=param["name"], choices=param["choices"]
                    )

                elif param["type"] == "Integer":
                    parameters_dict[param["name"]] = trial.suggest_int(
                        name=param["name"], low=param["low"], high=param["high"]
                    )
                else:
                    raise NotImplemented("Not implemented yet")

        my_model = algorithm(**parameters_dict)
        cv = KFold(n_splits=10, shuffle=True, random_state=42)
        metric_cv = cross_val_score(
            estimator=my_model, X=x, y=y, scoring=make_scorer(metric), cv=cv
        )
        result = abs(metric_cv.mean())

        return result

    study = optuna.create_study(
        direction=scoring_option, sampler=RandomSampler(seed=42)
    )
    study.optimize(objective, n_trials=n_trials)

    return study.best_params
