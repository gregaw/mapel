#!/usr/bin/env python

import copy
import os
from collections import Counter
from typing import Union

import numpy as np
from scipy.stats import gamma

import mapel.elections.models.euclidean as euclidean
import mapel.elections.models.group_separable as group_separable
import mapel.elections.models.guardians as guardians
import mapel.elections.models.impartial as impartial
import mapel.elections.models.mallows as mallows
import mapel.elections.models.single_crossing as single_crossing
import mapel.elections.models.single_peaked as single_peaked
import mapel.elections.models.urn_model as urn_model
from mapel.elections._glossary import *


def generate_approval_votes(model_id: str = None, num_candidates: int = None,
                            num_voters: int = None, params: dict = None) -> Union[list, np.ndarray]:

    main_models = {'approval_ic': impartial.generate_approval_ic_votes,
                   'approval_id': impartial.generate_approval_id_votes,
                   'approval_resampling': mallows.generate_approval_resampling_votes,
                   'approval_noise_model': mallows.generate_approval_noise_model_votes,
                   'approval_urn': urn_model.generate_approval_urn_votes,
                   'approval_euclidean': euclidean.generate_approval_euclidean_votes,
                   'approval_disjoint_resampling': mallows.generate_approval_disjoint_shumallows_votes,
                   'approval_vcr': euclidean.generate_approval_vcr_votes,
                   'approval_truncated_mallows': mallows.generate_approval_truncated_mallows_votes,
                   'approval_truncated_urn': urn_model.generate_approval_truncated_urn_votes,
                   'approval_moving_resampling': mallows.generate_approval_moving_resampling_votes,
                   'approval_simplex_shumallows': mallows.generate_approval_simplex_shumallows_votes,
                   'approval_anti_pjr': mallows.approval_anti_pjr_votes,
                   'approval_partylist': mallows.approval_partylist_votes,
                   }

    if model_id in main_models:
        return main_models.get(model_id)(num_voters=num_voters, num_candidates=num_candidates,
                                         params=params)
    elif model_id in ['approval_full']:
        return impartial.generate_approval_full_votes(num_voters=num_voters,
                                                      num_candidates=num_candidates)
    elif model_id in ['approval_empty']:
        return impartial.generate_approval_empty_votes(num_voters=num_voters)

    elif model_id in APPROVAL_FAKE_MODELS:
        return [model_id, num_candidates, num_voters, params]
    else:
        print("No such election model_id!", model_id)
        return []


def generate_ordinal_votes(model_id: str = None, num_candidates: int = None, num_voters: int = None,
                           params: dict = None) -> Union[list, np.ndarray]:
    naked_models = {'impartial_culture': impartial.generate_ordinal_ic_votes,
                    'iac': impartial.generate_impartial_anonymous_culture_election,
                    'conitzer': single_peaked.generate_ordinal_sp_conitzer_votes,
                    'spoc_conitzer': single_peaked.generate_ordinal_spoc_conitzer_votes,
                    'walsh': single_peaked.generate_ordinal_sp_walsh_votes,
                    'real_identity': guardians.generate_real_identity_votes,
                    'real_uniformity': guardians.generate_real_uniformity_votes,
                    'real_antagonism': guardians.generate_real_antagonism_votes,
                    'real_stratification': guardians.generate_real_stratification_votes}

    euclidean_models = {'1d_interval': euclidean.generate_ordinal_euclidean_votes,
                        '1d_gaussian': euclidean.generate_ordinal_euclidean_votes,
                        '1d_one_sided_triangle': euclidean.generate_ordinal_euclidean_votes,
                        '1d_full_triangle': euclidean.generate_ordinal_euclidean_votes,
                        '1d_two_party': euclidean.generate_ordinal_euclidean_votes,
                        '2d_disc': euclidean.generate_ordinal_euclidean_votes,
                        '2d_square': euclidean.generate_ordinal_euclidean_votes,
                        '2d_gaussian': euclidean.generate_ordinal_euclidean_votes,
                        '3d_cube': euclidean.generate_ordinal_euclidean_votes,
                        '4d_cube': euclidean.generate_ordinal_euclidean_votes,
                        '5d_cube': euclidean.generate_ordinal_euclidean_votes,
                        '10d_cube': euclidean.generate_ordinal_euclidean_votes,
                        '20d_cube': euclidean.generate_ordinal_euclidean_votes,
                        '2d_sphere': euclidean.generate_ordinal_euclidean_votes,
                        '3d_sphere': euclidean.generate_ordinal_euclidean_votes,
                        '4d_sphere': euclidean.generate_ordinal_euclidean_votes,
                        '5d_sphere': euclidean.generate_ordinal_euclidean_votes,
                        '4d_ball': euclidean.generate_ordinal_euclidean_votes,
                        '5d_ball': euclidean.generate_ordinal_euclidean_votes,
                        '2d_grid': euclidean.generate_elections_2d_grid}

    party_models = {'1d_gaussian_party': euclidean.generate_1d_gaussian_party,
                    '2d_gaussian_party': euclidean.generate_2d_gaussian_party,
                    'walsh_party': single_peaked.generate_sp_party,
                    'conitzer_party': single_peaked.generate_sp_party,
                    'mallows_party': mallows.generate_mallows_party,
                    'ic_party': impartial.generate_ic_party
                    }

    single_param_models = {'urn_model': urn_model.generate_urn_votes,
                           'group-separable':
                               group_separable.generate_ordinal_group_separable_votes,

                           'single-crossing': single_crossing.generate_ordinal_single_crossing_votes,}

    double_param_models = {'mallows': mallows.generate_mallows_votes,
                           'norm-mallows': mallows.generate_mallows_votes,
                           'norm-mallows_mixture': mallows.generate_norm_mallows_mixture_votes}

    if model_id in naked_models:
        votes = naked_models.get(model_id)(num_voters=num_voters,
                                           num_candidates=num_candidates)

    elif model_id in euclidean_models:
        votes = euclidean_models.get(model_id)(num_voters=num_voters,
                                               num_candidates=num_candidates,
                                               model=model_id, params=params)

    elif model_id in party_models:
        votes = party_models.get(model_id)(num_voters=num_voters,
                                           num_candidates=num_candidates,
                                           model=model_id, params=params)

    elif model_id in single_param_models:
        votes = single_param_models.get(model_id)(num_voters=num_voters,
                                                  num_candidates=num_candidates,
                                                  params=params)

    elif model_id in double_param_models:
        votes = double_param_models.get(model_id)(num_voters, num_candidates, params)

    elif model_id in LIST_OF_FAKE_MODELS:
        votes = [model_id, num_candidates, num_voters, params]
    else:
        votes = []
        print("No such election model_id!", model_id)

    if model_id not in LIST_OF_FAKE_MODELS:
        votes = [[int(x) for x in row] for row in votes]

    return votes




def store_approval_election(experiment, model_id, election_id, num_candidates, num_voters,
                            params, ballot):
    """ Store approval election in an .app file """

    if model_id in APPROVAL_FAKE_MODELS:
        path = os.path.join("experiments", str(experiment.experiment_id),
                            "elections", (str(election_id) + ".app"))
        file_ = open(path, 'w')
        file_.write(f'$ {model_id} {params} \n')
        file_.write(str(num_candidates) + '\n')
        file_.write(str(num_voters) + '\n')
        file_.close()

    else:
        path = os.path.join("experiments", str(experiment.experiment_id), "elections",
                            (str(election_id) + ".app"))

        store_votes_in_a_file(experiment, model_id, election_id, num_candidates, num_voters,
                              params, path, ballot)



def store_votes_in_a_file(election, model_id, election_id, num_candidates, num_voters,
                          params, path, ballot, votes=None):
    """ Store votes in a file """
    if votes is None:
        votes = election.votes

    with open(path, 'w') as file_:

        if model_id in NICE_NAME:
            file_.write("# " + NICE_NAME[model_id] + " " + str(params) + "\n")
        else:
            file_.write("# " + model_id + "\n")

        file_.write(str(num_candidates) + "\n")

        for i in range(num_candidates):
            file_.write(str(i) + ', c' + str(i) + "\n")

        c = Counter(map(tuple, votes))
        counted_votes = [[count, list(row)] for row, count in c.items()]
        counted_votes = sorted(counted_votes, reverse=True)

        file_.write(str(num_voters) + ', ' + str(num_voters) + ', ' +
                    str(len(counted_votes)) + "\n")

        if ballot == 'approval':
            for i in range(len(counted_votes)):
                file_.write(str(counted_votes[i][0]) + ', {')
                for j in range(len(counted_votes[i][1])):
                    file_.write(str(int(counted_votes[i][1][j])))
                    if j < len(counted_votes[i][1]) - 1:
                        file_.write(", ")
                file_.write("}\n")

        elif ballot == 'ordinal':
            for i in range(len(counted_votes)):
                file_.write(str(counted_votes[i][0]) + ', ')
                for j in range(len(counted_votes[i][1])):
                    file_.write(str(int(counted_votes[i][1][j])))
                    if j < len(counted_votes[i][1]) - 1:
                        file_.write(", ")
                file_.write("\n")

# # # # # # # # # # # # # # # #
# LAST CLEANUP ON: 22.10.2021 #
# # # # # # # # # # # # # # # #
