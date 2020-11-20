from comet_ml import Experiment
import os
import torch
import torch.nn as nn

from utils.helpers import config_dict, Config, get_optimizer, load_model
from scripts.training import train
from scripts.testing import test
from scripts.loaders import load_cifar10_dataset
from scripts.criterions import cross_entropy_loss


def initialization(configs):

    # Load dataset
    configs.loader, configs.labels = load_cifar10_dataset(configs)

    # Load model
    model = load_model(configs)

    if torch.cuda.is_available() == True:
        model = nn.DataParallel(model)
        configs.model = model
    else:
        print("Please run the experiment in gpu")
        exit(1)

    # Set optimizer and criterion
    configs.criterion = cross_entropy_loss()
    configs.optimizer = get_optimizer(configs)

    # Register experiment in comet ML
    configs.experiment.set_name(configs.experiment_name)
    configs.experiment.add_tag(configs.base_model)
    configs.experiment.log_parameters(configs)

    # Start training and testing
    train(configs)

    if configs.test:
        test(configs)

    # End the experiment in comet ML
    configs.experiment.end()


if __name__ == "__main__":
    params_dict = config_dict(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'configs.txt'))
    configs = Config(params_dict)

    # Config comet ML Experiment
    experiment = Experiment(api_key=configs.api_key,
                            project_name="learning-deep", workspace="lordvoldemort28")

    configs.experiment = experiment

    initialization(configs)
