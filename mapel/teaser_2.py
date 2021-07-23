import mapel

if __name__ == "__main__":

    experiment = mapel.prepare_experiment()

    city_size = 20

    # cities
    experiment.add_family(election_model='conitzer', size=city_size, color='blue')
    experiment.add_family(election_model='walsh', size=city_size, color='green')

    # paths
    experiment.add_family(election_model='unid', size=48, color='black', param_1=4)
    experiment.add_family(election_model='anid', size=36, color='black', param_1=4)
    experiment.add_family(election_model='stid', size=23, color='black', param_1=4)
    experiment.add_family(election_model='anun', size=23, color='black', param_1=4)
    experiment.add_family(election_model='stun', size=36, color='black', param_1=4)
    experiment.add_family(election_model='stan', size=39, color='black', param_1=4)

    # single points
    experiment.add_election(election_model='identity', color='blue')
    experiment.add_election(election_model='uniformity', color='black')
    experiment.add_election(election_model='antagonism', color='red')
    experiment.add_election(election_model='stratification', color='green')
    experiment.add_election(election_model='conitzer_matrix', color='cyan')
    experiment.add_election(election_model='walsh_matrix', color='lime')
    experiment.add_election(election_model='gs_caterpillar_matrix', color='brown')

    experiment.compute_distances()
    experiment.embed(algorithm='mds')
    experiment.print_map()