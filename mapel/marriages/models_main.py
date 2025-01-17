#!/usr/bin/env python

from typing import Union

import numpy as np

import mapel.marriages.models.euclidean as euclidean
import mapel.marriages.models.impartial as impartial
import mapel.marriages.models.mallows as mallows
import mapel.marriages.models.urn as urn
import mapel.marriages.models.group_separable as group_separable


def generate_votes(model_id: str = None, num_agents: int = None,
                   params: dict = None) -> Union[list, np.ndarray]:
    independent_models = {
        'ic': impartial.generate_ic_votes,
        'id': impartial.generate_id_votes,
        'asymmetric': impartial.generate_asymmetric_votes,
        'symmetric': group_separable.generate_symmetric_votes,
        'norm-mallows': mallows.generate_norm_mallows_votes,
        'urn': urn.generate_urn_votes,
    }
    dependent_models = {
        'euclidean': euclidean.generate_euclidean_votes,

    }

    if model_id in independent_models:
        votes_1 = independent_models.get(model_id)(num_agents=num_agents, params=params)
        votes_2 = independent_models.get(model_id)(num_agents=num_agents, params=params)
        return [votes_1, votes_2]

    elif model_id in independent_models:
        return dependent_models.get(model_id)(num_agents=num_agents, params=params)

    else:
        print("No such election model_id!", model_id)
        return []

# # # # # # # # # # # # # # # #
# LAST CLEANUP ON: 22.10.2021 #
# # # # # # # # # # # # # # # #
