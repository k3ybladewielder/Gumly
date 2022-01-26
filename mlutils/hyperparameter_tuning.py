import pandas as pd
from sklearn.model_selection import cross_val_score, KFold
import optuna
from optuna.samplers import RandomSampler
from sklearn.metrics import make_scorer
from mlutils.feature_engineering import split_features_and_target


def hyperparameter_tuning(
    df: pd.DataFrame,
    target: str,
    parameters: dict,
    algorithm,
    metric,
    scoring_option: str,
    n_trials: int,
    n_splits: int,
    suffle: bool,
    random_state: int
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
    (eg: RandomForestClassifier, RandomForestRegressor)
    :type: class
    :param metric: Metric used for the evaluation of the tests (eg: accuracy_score, r2)
    :type: function
    :param scoring_option: Maximize or minimize objectives
    :type: str
    :param n_trials: The of trials that the framework must perform
    :type: int
    :param n_splits: The number of splits that must be done in the dataset
    :type: int
    :param suffle: The flag true or false for suffle data before execution
    :type: bool
    :param random_state: The number choosen for seed
    :type: int
    :return: Best hyperparameter features chosen by the technique
    :rtype: dict

    """
    x, y = split_features_and_target(df=df, target=target)

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
                    raise NotImplementedError("Not implemented yet")

        my_model = algorithm(**parameters_dict)
        cv = KFold(n_splits=n_splits, shuffle=suffle, random_state=random_state)
        metric_cv = cross_val_score(estimator=my_model, X=x, y=y, scoring=make_scorer(metric), cv=cv)
        result = abs(metric_cv.mean())

        return result

    study = optuna.create_study(direction=scoring_option, sampler=RandomSampler(seed=random_state))
    study.optimize(objective, n_trials=n_trials)

    return study.best_params
