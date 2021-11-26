#!/usr/bin/env python

import copy
from typing import Union

import numpy as np

import mapel.roommates.models.impartial as impartial
import mapel.roommates.models.mallows as mallows
import mapel.roommates.models.urn as urn
import mapel.roommates.models.euclidean as euclidean
from mapel.roommates.objects.Roommates import Roommates


# GENERATE VOTES
def generate_roommates_votes(model_id: str = None, num_agents: int = None,
                             params: dict = None) -> Union[list, np.ndarray]:
    main_models = {'roommates_ic': impartial.generate_roommates_ic_votes,
                   'roommates_id': impartial.generate_roommates_id_votes,
                   'roommates_cy': impartial.generate_roommates_cy_votes,
                   'roommates_norm-mallows': mallows.generate_roommates_norm_mallows_votes,
                   'roommates_urn': urn.generate_roommates_urn_votes,
                   'roommates_euclidean': euclidean.generate_roommates_euclidean_votes}

    if model_id in main_models:
        return main_models.get(model_id)(num_agents=num_agents, params=params)
    else:
        print("No such election model_id!", model_id)
        return []


# GENERATE INSTANCE
def generate_roommates_instance(experiment=None, model_id: str = None, instance_id: str = None,
                                num_agents: int = None, params: dict = None) -> Roommates:
    if params is None:
        params = {}

    if model_id == 'roommates_norm-mallows' and 'norm-phi' not in params:
        params['norm-phi'] = np.random.rand()
        alpha = params['norm-phi']
    elif model_id == 'roommates_urn' and 'alpha' not in params:
        params['alpha'] = np.random.rand()
        alpha = params['alpha']
    else:
        alpha = 1

    votes = generate_roommates_votes(model_id=model_id, num_agents=num_agents, params=params)
    return Roommates("virtual", instance_id, votes=votes, model_id=model_id, alpha=alpha)


# PREPARE INSTANCES
def prepare_roommates_instances(experiment=None, model_id: str = None,
                                family_id: str = None, params: dict = None):
    instances = {}
    for j in range(experiment.families[family_id].size):

        if experiment.families[family_id].single_instance:
            instance_id = family_id
        else:
            instance_id = family_id + '_' + str(j)


        instance = generate_roommates_instance(experiment=experiment, model_id=model_id,
                                               instance_id=instance_id,
                                               num_agents=experiment.families[family_id].num_agents,
                                               params=copy.deepcopy(params))

        experiment.instances[instance_id] = instance
        instances[instance_id] = instance

    return instances

# # # # # # # # # # # # # # # #
# LAST CLEANUP ON: 22.10.2021 #
# # # # # # # # # # # # # # # #
