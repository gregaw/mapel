import csv
import os
import math

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import tikzplotlib


def print_approvals_histogram(election):
    print(election.election_id)
    plt.title(election.election_id, size=20)
    bins = np.linspace(0, 100, 51)
    plt.hist([len(vote) for vote in election.votes], bins=bins)
    # x_axis = np.arange(0, 100, 0.01)
    # plt.plot(x_axis, norm.pdf(x_axis, 50, 2)*2000)
    plt.ylim([0, election.num_voters])
    plt.xlim([-1, election.num_candidates+1])
    plt.savefig("images/histograms/" + election.election_id + ".png")
    plt.show()


# Main functions
def print_map_2d(experiment,
                 xlabel=None, shading=False, shift_legend=1,
                 angle=0, reverse=False, update=False, feature=None,
                 axis=False, rounding=1,
                 ticks=None, skeleton=None, roads=None,
                 title=None, dim=2, event='none',
                 saveas=None, show=True, ms=20, normalizing_func=None,
                 xticklabels=None, cmap=None, marker_func=None, tex=False,
                 legend=True, adjust=False) -> None:
    if skeleton is None:
        skeleton = []

    if roads is None:
        roads = []

    experiment.compute_coordinates_by_families()

    if adjust:
        adjust_the_map(experiment)

    if angle != 0:
        experiment.rotate(angle)

    if reverse:
        experiment.reverse()

    if experiment.store and (adjust or update):
        experiment.update()

    if cmap is None:
        cmap = custom_div_cmap()

    if feature is not None:
        fig = plt.figure(figsize=(6.4, 6.4 + 0.48))
    else:
        fig = plt.figure()

    ax = fig.add_subplot()

    plt.axis('equal')

    if not axis:
        plt.axis('off')

    add_skeleton(experiment=experiment, skeleton=skeleton, ax=ax)

    # COLORING
    if feature is not None:
        color_map_by_feature(experiment=experiment, fig=fig, ax=ax,
                             feature=feature, rounding=rounding,
                             normalizing_func=normalizing_func,
                             marker_func=marker_func,
                             xticklabels=xticklabels, ms=ms, cmap=cmap,
                             ticks=ticks)
    else:

        if event in {'skeleton'}:
            skeleton_coloring(experiment=experiment, ax=ax, ms=ms, dim=dim)
            add_roads(experiment=experiment, roads=roads, ax=ax)
        else:
            if shading:
                basic_coloring_with_shading(experiment=experiment, ax=ax, ms=ms, dim=dim,
                                            skeleton=skeleton)
            else:
                basic_coloring(experiment=experiment, ax=ax, ms=ms, dim=dim, skeleton=skeleton)

    # BACKGROUND
    basic_background(ax=ax, values=feature, legend=legend,
                     saveas=saveas, xlabel=xlabel,
                     title=title, shift_legend=shift_legend)

    if tex:
        saveas_tex(saveas=saveas)

    if show:
        plt.show()


def print_map_3d(experiment,
                 xlabel=None, reverse=False, feature=None,
                 attraction_factor=1, axis=False,
                 distance_name="emd-positionwise",
                 ticks=None, dim=3,
                 title=None, shading=False,
                 saveas="map_2d", show=True, ms=20, normalizing_func=None,
                 xticklabels=None, cmap=None, marker_func=None, tex=False,
                 legend=True):
    experiment.compute_coordinates_by_families()

    if cmap is None:
        cmap = custom_div_cmap()

    if feature is not None:
        fig = plt.figure(figsize=(6.4, 4.8 + 0.48))
    else:
        fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    if not axis:
        plt.axis('off')

    # COLORING
    if feature is not None:
        color_map_by_feature(experiment=experiment, fig=fig, ax=ax,
                             feature=feature,
                             normalizing_func=normalizing_func,
                             marker_func=marker_func,
                             xticklabels=xticklabels, ms=ms, cmap=cmap,
                             ticks=ticks, dim=dim)
    else:
        basic_coloring(experiment=experiment, ax=ax, ms=ms, dim=dim)

    # BACKGROUND
    basic_background(ax=ax, values=feature, legend=legend,
                     saveas=saveas, xlabel=xlabel,
                     title=title)

    if tex:
        saveas_tex(saveas=saveas)

    if show:
        plt.show()


def get_values_from_csv_file(experiment, feature) -> dict:
    """Import values for a feature from a .csv file """

    path = os.path.join(os.getcwd(), 'experiments', experiment.experiment_id,
                        'features', f'{feature}.csv')

    values = {}
    with open(path, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')

        for row in reader:
            election_id = row['election_id']
            value = row['value']
            values[election_id] = float(value)

    return values


# HELPER FUNCTIONS FOR PRINT_2D
def import_values_for_feature(experiment, feature, normalizing_func=None, marker_func=None, dim=2):
    """ Import values for a feature """

    if isinstance(feature, str):
        if feature in experiment.features:
            values = experiment.features[feature]
        else:
            values = get_values_from_csv_file(experiment, feature)
    else:
        values = feature

    _min = 0
    _max = 0
    _min = min(values.values())
    _max = max(values.values())
    shades = []
    xx = []
    yy = []
    zz = []
    markers = []

    ctr = 0

    for family_id in experiment.families:

        for k in range(experiment.families[family_id].size):
            if experiment.families[family_id].size == 1:
                election_id = family_id
            else:
                election_id = family_id + '_' + str(k)

            shade = values[election_id]
            if normalizing_func is not None:
                shade = normalizing_func(shade)
            else:
                shade = (shade - _min) / (_max - _min)
            shades.append(shade)

            marker = experiment.families[family_id].marker
            if marker_func is not None:
                marker = marker_func(shade)
            markers.append(marker)

            xx.append(experiment.coordinates[election_id][0])
            yy.append(experiment.coordinates[election_id][1])
            if dim == 3:
                zz.append(experiment.coordinates[election_id][2])

            ctr += 1

    xx = np.asarray(xx)
    yy = np.asarray(yy)
    if dim == 3:
        zz = np.asarray(zz)

    shades = np.asarray(shades)
    markers = np.asarray(markers)
    return xx, yy, zz, shades, markers, _min, _max


def get_values_from_file_3d(experiment, experiment_id, values, normalizing_func):
    path = os.path.join(os.getcwd(), "experiments", experiment_id, "controllers", "advanced",
                        str(values) + ".txt")
    _min = 0
    _max = 0
    values = []
    with open(path, 'r') as txt_file:
        for _ in range(experiment.num_elections):
            values.append(float(txt_file.readline()))
    _min = min(values)
    _max = max(values)

    with open(path, 'r') as txt_file:

        shades = []
        xx = []
        yy = []
        zz = []
        markers = []

        ctr = 0
        for k in range(experiment.num_families):
            for _ in range(experiment.families[k].size):

                shade = float(txt_file.readline())
                if normalizing_func is not None:
                    shade = normalizing_func(shade)
                else:
                    shade = (shade - _min) / (_max - _min)
                shades.append(shade)

                marker = experiment.families[k].marker
                markers.append(marker)

                xx.append(experiment.coordinates[experiment.main_order[ctr]][0])
                yy.append(experiment.coordinates[experiment.main_order[ctr]][1])
                zz.append(experiment.coordinates[experiment.main_order[ctr]][2])

                ctr += 1
        xx = np.asarray(xx)
        yy = np.asarray(yy)
        zz = np.asarray(zz)
        shades = np.asarray(shades)
        markers = np.asarray(markers)
        return xx, yy, zz, shades, markers, _min, _max


def color_map_by_feature(experiment=None, fig=None, ax=None, feature=None,
                         normalizing_func=None, marker_func=None, xticklabels=None, ms=None,
                         cmap=None, ticks=None, dim=2, rounding=1):
    xx, yy, zz, shades, markers, _min, _max = import_values_for_feature(
        experiment, feature, normalizing_func, marker_func, dim=dim)
    unique_markers = set(markers)
    images = []

    for um in unique_markers:
        masks = (markers == um)
        if dim == 2:
            images.append(ax.scatter(xx[masks], yy[masks], c=shades[masks], vmin=0, vmax=1,
                                     cmap=cmap, marker=um, s=ms))
        elif dim == 3:
            images.append(ax.scatter(xx[masks], yy[masks], zz[masks], c=shades[masks], vmin=0,
                                     vmax=1, cmap=cmap, marker=um, s=ms))

    if dim == 2:

        from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
        ax_divider = make_axes_locatable(ax)
        cax = ax_divider.append_axes("bottom", size="5%", pad="5%")

        if xticklabels is None:
            lin = np.linspace(_min, _max, 6)
            if rounding == 0:
                xticklabels = [int(lin[i]) for i in range(6)]
            else:
                xticklabels = [np.round(lin[i], rounding) for i in range(6)]

        cb = fig.colorbar(images[0], cax=cax, orientation="horizontal",
                          shrink=1, ticks=ticks)  # shrink not working
        cb.ax.locator_params(nbins=len(xticklabels), tight=True)
        cb.ax.tick_params(labelsize=14)
        if xticklabels is not None:
            cb.ax.set_xticklabels(xticklabels)


# HELPER FUNCTIONS FOR PRINT_3D
def add_advanced_points_to_picture_3d(fig, ax, experiment, experiment_id,
                                      values=None, cmap=None, ms=None,
                                      normalizing_func=None):
    xx, yy, zz, shades, markers, _min, _max = get_values_from_file_3d(
        experiment, experiment_id, values, normalizing_func)
    unique_markers = set(markers)
    images = []

    for um in unique_markers:
        masks = (markers == um)
        images.append(
            [ax.scatter(xx[masks], yy[masks], zz[masks], c=shades[masks],
                        vmin=0, vmax=1, cmap=cmap, marker=um, s=ms)])


# COLORING
def basic_coloring(experiment=None, ax=None, ms=None, dim=2, skeleton=None):
    if skeleton is None:
        skeleton = []
    for family in experiment.families.values():

        if family.show:
            if dim == 2:
                if family.label in skeleton:
                    label = '_nolegend_'
                else:
                    label = family.label
                ax.scatter(experiment.coordinates_by_families[family.family_id][0],
                           experiment.coordinates_by_families[family.family_id][1],
                           color=family.color,
                           label=label,
                           alpha=family.alpha, s=ms,
                           marker=family.marker)
            elif dim == 3:
                ax.scatter(experiment.coordinates_by_families[family.family_id][0],
                           experiment.coordinates_by_families[family.family_id][1],
                           experiment.coordinates_by_families[family.family_id][2],
                           color=family.color,
                           label=family.label,
                           alpha=family.alpha, s=ms,
                           marker=family.marker)


def basic_coloring_with_shading(experiment=None, ax=None, ms=None, dim=2, skeleton=None):
    if skeleton is None:
        skeleton = []
    for family_id in experiment.families:
        if experiment.families[family_id].show:
            if dim == 2:
                if '_path' in family_id:
                    for i in range(experiment.families[family_id].size):
                        election_id = experiment.families[family_id].election_ids[i]
                        alpha = experiment.elections[election_id].alpha
                        alpha *= experiment.families[family_id].alpha
                        alpha = (alpha + 0.2) / 1.2
                        if i == experiment.families[family_id].size - 1:
                            ax.scatter(experiment.coordinates_by_families[family_id][0][i],
                                       experiment.coordinates_by_families[family_id][1][i],
                                       color=experiment.families[family_id].color,
                                       label=family_id,
                                       alpha=alpha, s=ms,
                                       marker=experiment.families[family_id].marker)
                        else:
                            ax.scatter(experiment.coordinates_by_families[family_id][0][i],
                                       experiment.coordinates_by_families[family_id][1][i],
                                       color=experiment.families[family_id].color,
                                       alpha=alpha, s=ms,
                                       marker=experiment.families[family_id].marker)
                else:
                    if family_id in skeleton:
                        label = '_nolegend_'
                    else:
                        label = family_id
                    ax.scatter(experiment.coordinates_by_families[family_id][0],
                               experiment.coordinates_by_families[family_id][1],
                               color=experiment.families[family_id].color,
                               label=label,
                               alpha=experiment.families[family_id].alpha, s=ms,
                               marker=experiment.families[family_id].marker)
            elif dim == 3:
                ax.scatter(experiment.coordinates_by_families[family_id][0],
                           experiment.coordinates_by_families[family_id][1],
                           experiment.coordinates_by_families[family_id][2],
                           color=experiment.families[family_id].color,
                           label=experiment.families[family_id].label,
                           alpha=experiment.families[family_id].alpha, s=ms,
                           marker=experiment.families[family_id].marker)


# BACKGROUNDS
def mask_background(fig=None, ax=None, black=None, saveas=None, tex=None):
    fig.set_size_inches(10, 10)
    corners = [[-1, 1, 1, -1], [1, 1, -1, -1]]
    ax.scatter(corners[0], corners[1], alpha=0)

    add_mask_100_100(fig, ax, black=black)

    file_name = saveas + ".png"
    path = os.path.join(os.getcwd(), "images", file_name)
    plt.savefig(path, bbox_inches='tight')
    plt.grid(True)

    plt.xlim(-1.4, 1.3)
    plt.ylim(-1.4, 1.3)

    if tex:
        import tikzplotlib
        file_name = saveas + ".tex"
        path = os.path.join(os.getcwd(), "images", "tex", file_name)
        tikzplotlib.save(path)


def basic_background(ax=None, values=None, legend=None, saveas=None, xlabel=None, title=None,
                     shift_legend=1):
    file_name = os.path.join(os.getcwd(), "images", str(saveas))
    # print(file_name)

    if xlabel is not None:
        plt.xlabel(xlabel, size=14)
    if title is not None:
        plt.suptitle(title, fontsize=16)

    if saveas is not None:

        try:
            os.mkdir(os.path.join(os.getcwd(), "images"))
        except FileExistsError:
            pass

        if values is None and legend:
            ax.legend(loc='center left', bbox_to_anchor=(shift_legend, 0.5))
            # ax.legend()
            plt.savefig(file_name, bbox_inches='tight')
        else:
            plt.savefig(file_name, bbox_inches='tight')

    elif values is None and legend:
        ax.legend(loc='center left', bbox_to_anchor=(shift_legend, 0.5))


# TEX
def saveas_tex(saveas=None):
    try:
        os.mkdir(os.path.join(os.getcwd(), "images", "tex"))
    except FileExistsError:
        pass
    file_name = saveas + ".tex"
    path = os.path.join(os.getcwd(), "images", "tex", file_name)
    tikzplotlib.save(path)


# MAIN FUNCTIONS
def print_matrix(experiment=None, scale=1., distance_name='', saveas="matrix", show=True,
                 self_distances=False, yticks='left', with_std=False, time=False):
    """Print the matrix with average distances between each pair of experiments """

    # CREATE MAPPING FOR BUCKETS
    bucket = np.array([[family_id for _ in range(experiment.families[family_id].size)]
                       for family_id in experiment.families]).flatten()

    # CREATE MAPPING FOR ELECTIONS
    mapping = {}
    ctr = 0
    for family_id in experiment.families:
        for election_id in experiment.families[family_id].election_ids:
            mapping[ctr] = election_id
            ctr += 1

    # PREPARE EMPTY DICTS
    matrix = {}
    quantities = {}
    for family_id_1 in experiment.families:
        matrix[family_id_1] = {}
        quantities[family_id_1] = {}
        for family_id_2 in experiment.families:
            matrix[family_id_1][family_id_2] = 0
            quantities[family_id_1][family_id_2] = 0

    # ADD VALUES
    for i in range(experiment.num_elections):
        limit = i + 1
        if self_distances:
            limit = i
        for j in range(limit, experiment.num_elections):
            if time:
                matrix[bucket[i]][bucket[j]] += experiment.times[mapping[i]][
                    mapping[j]]
            else:
                # print('map', mapping[i], mapping[j])
                # print(experiment.distances)
                # print(experiment.distances[mapping[i]][mapping[j]])
                matrix[bucket[i]][bucket[j]] += experiment.distances[mapping[i]][mapping[j]]
            quantities[bucket[i]][bucket[j]] += 1
    #
    # for i, family_id_1 in enumerate(experiment.families):
    #     for election_id_1 in experiment.families[family_id_1].election_ids:
    #         for j, family_id_2 in enumerate(experiment.families):
    #             for election_id_2 in experiment.families[family_id_2].election_ids:
    #                 if time:
    #                     matrix[bucket[i]][bucket[j]] += experiment.times[election_id_1][election_id_2]
    #                 else:
    #                     matrix[bucket[i]][bucket[j]] += experiment.distances[election_id_1][election_id_2]
    #                 quantities[bucket[i]][bucket[j]] += 1

    # NORMALIZE
    for i, family_id_1 in enumerate(experiment.families):
        for j, family_id_2 in enumerate(experiment.families):
            if (self_distances and i == j) or i < j:
                if quantities[family_id_1][family_id_2] != 0.:
                    matrix[family_id_1][family_id_2] /= float(
                        quantities[family_id_1][family_id_2])
                matrix[family_id_1][family_id_2] *= scale
                matrix[family_id_1][family_id_2] = int(
                    round(matrix[family_id_1][family_id_2], 0))
                matrix[family_id_2][family_id_1] = matrix[family_id_1][
                    family_id_2]

    # THE REST
    fig, ax = plt.subplots()
    num_families_new = experiment.num_families

    matrix_new = np.zeros([num_families_new, num_families_new])

    # FIND MIN & MAX
    _min = min([min(matrix[family_id].values()) for family_id in experiment.families])
    _max = max([max(matrix[family_id].values()) for family_id in experiment.families])
    threshold = _min + 0.75 * (_max - _min)

    # PRINT
    if with_std:
        for i, family_id_1 in enumerate(experiment.families):
            for j, family_id_2 in enumerate(experiment.families):
                c = int(matrix[family_id_1][family_id_2])
                std = int(
                    round(experiment.stds[mapping[i]][mapping[j]] * scale, 0))
                matrix_new[i][j] = c
                color = "black"
                if c >= threshold:
                    color = "white"
                ax.text(j - 0.1, i + 0.1, str(c), va='bottom', ha='center',
                        color=color, size=12)
                if std >= 10:
                    ax.text(j - 0.3, i + 0.1, '$\pm$' + str(std), va='top',
                            ha='left', color=color, size=9)
                else:
                    ax.text(j - 0.1, i + 0.1, '$\pm$' + str(std), va='top',
                            ha='left', color=color, size=9)
    else:
        for i, family_id_1 in enumerate(experiment.families):
            for j, family_id_2 in enumerate(experiment.families):
                c = int(matrix[family_id_1][family_id_2])
                matrix_new[i][j] = c
                color = "black"
                if c >= threshold:
                    color = "white"
                ax.text(j, i, str(c), va='center', ha='center', color=color)

    labels = []
    for family_id in experiment.families:
        labels.append(experiment.families[family_id].label)

    ax.matshow(matrix_new, cmap=plt.cm.Blues)

    x_values = labels
    y_values = labels
    y_axis = np.arange(0, num_families_new, 1)
    x_axis = np.arange(0, num_families_new, 1)

    if yticks != 'none':
        ax.set_yticks(y_axis)
        if yticks == 'left':
            ax.set_yticklabels(y_values, rotation=25, size=12)
        if yticks == 'right':
            ax.set_yticklabels(y_values, rotation=-25, size=12)
            ax.yaxis.tick_right()
    else:
        ax.set_yticks([])

    ax.set_xticks(x_axis)
    ax.set_xticklabels(x_values, rotation=75, size=12)

    if experiment.store:
        file_name = os.path.join(os.getcwd(), "images", str(saveas) + ".png")
        plt.savefig(file_name, bbox_inches='tight')

    if show:
        plt.show()


# HELPER FUNCTIONS
def custom_div_cmap(num_colors=101, name='custom_div_cmap', colors=None):
    if colors is None:
        colors = ["lightgreen", "yellow", "orange", "red", "black"]
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list(name=name, colors=colors, N=num_colors)


def add_margin(pil_img, top, right, bottom, left, color):
    """ Add margin to the picture """
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def map_diameter(c):
    """ Compute the diameter """
    return 1. / 3. * float((c + 1) * (c - 1))


# SKELETON RELATED
def add_skeleton(experiment=None, skeleton=None, ax=None, size=12):
    """ Add skeleton """

    def my_text(x1, y1, text, color="black", alpha=1., size=size):
        ax.text(x1, y1, text, size=size, rotation=0., ha="center",
                va="center",
                color=color, alpha=alpha, zorder=100,
                bbox=dict(boxstyle="round", ec="black", fc="white"))

    for name in skeleton:
        x = experiment.coordinates[name][0]
        y = experiment.coordinates[name][1]
        my_text(x, y, name)


def add_roads(experiment=None, roads=None, ax=None):
    def my_line(x1, y1, x2, y2, text):
        ax.arrow(x1, y1, x2 - x1, y2 - y1, head_width=0., head_length=0.,
                 fc='k', ec='k')
        dx = x1 + (x2 - x1) / 2
        dy = y1 + (y2 - y1) / 2
        ax.annotate(text, xy=(dx, dy), size=12)

    for road in roads:
        x1 = experiment.coordinates[road[0]][0]
        y1 = experiment.coordinates[road[0]][1]
        x2 = experiment.coordinates[road[1]][0]
        y2 = experiment.coordinates[road[1]][1]
        pos_dist = experiment.distances[road[0]][road[1]]
        pos_dist /= map_diameter(experiment.default_num_candidates)
        pos_dist = round(pos_dist, 2)
        text = str(pos_dist)
        # print(road)
        if experiment.default_num_candidates == 10 and road in [['WAL', 'UN'], ['UN', 'WAL']]:
            x1 -= 0.5
            y1 -= 2
            x2 -= 0.5
            y2 -= 2

        my_line(x1, y1, x2, y2, text)


def skeleton_coloring(experiment=None, ax=None, ms=None, dim=2):
    for family_id in experiment.families:
        if experiment.families[family_id].show:
            if dim == 2:
                if family_id in {'A', 'B', 'C', 'D', 'E'}:
                    MAL_COUNT = len(experiment.coordinates_by_families[family_id][0])
                    print(MAL_COUNT)
                    for i in range(MAL_COUNT):
                        normphi = 1.0 / MAL_COUNT * i
                        if family_id == 'A':  # Mal 0.
                            color = (normphi, normphi, 1)
                        elif family_id == 'B':  # Mal 0.25
                            color = (normphi, 0.75, normphi)
                        elif family_id == 'C':  # Mal 0.5
                            color = (1, normphi, normphi)
                        elif family_id == 'D':  # Walsh
                            color = (1, normphi, 1)
                        elif family_id == 'E':  # Conitzer
                            color = (1, 0.5, normphi)
                        else:
                            color = 'black'
                        ax.scatter([experiment.coordinates_by_families[family_id][0][i]
                                    for _ in range(2)],
                                   [experiment.coordinates_by_families[family_id][1][i]
                                    for _ in range(2)],
                                   color=color,
                                   alpha=1., s=ms + 6,
                                   marker=experiment.families[family_id].marker)
                else:
                    if len(experiment.coordinates_by_families[family_id][0]) == 1:
                        ax.scatter([experiment.coordinates_by_families[family_id][0][0]
                                    for _ in range(2)],
                                   [experiment.coordinates_by_families[family_id][1][0]
                                    for _ in range(2)],
                                   color=experiment.families[family_id].color,
                                   label=experiment.families[family_id].label,
                                   alpha=1,
                                   s=ms,
                                   marker=experiment.families[
                                       family_id].marker)

                    else:
                        ax.scatter(experiment.coordinates_by_families[family_id][0],
                                   experiment.coordinates_by_families[family_id][1],
                                   color=experiment.families[family_id].color,
                                   label=experiment.families[family_id].label,
                                   alpha=0.8,
                                   s=ms,
                                   marker=experiment.families[family_id].marker)


def add_mask_100_100(fig, ax, black=False):
    def my_arrow(x1, y1, x2, y2):
        ax.arrow(x1, y1, x2 - x1, y2 - y1, head_width=0.02, head_length=0.05,
                 fc='k', ec='k')

    def my_line(x1, y1, x2, y2):
        ax.arrow(x1, y1, x2 - x1, y2 - y1, head_width=0., head_length=0.,
                 fc='k', ec='k')

    def my_text(x1, y1, text, color="black", alpha=1.):

        if black:
            color = "black"
            alpha = 1

        plt.text(x1, y1, text, size=12, rotation=0., ha="center", va="center",
                 color=color, alpha=alpha,
                 bbox=dict(boxstyle="round", ec="black", fc="white"))

    def my_number(x1, y1, number, color="black"):

        if black:
            color = "black"

        plt.text(x1, y1, number, size=8, rotation=0., ha="center", va="center",
                 color=color, fontweight='bold')

    def my_plot(points):

        x = [p[0] for p in points]
        y = [p[1] for p in points]
        from scipy.interpolate import interp1d

        t = np.arange(len(x))
        ti = np.linspace(0, t.max(), 10 * t.size)

        xi = interp1d(t, x, kind='cubic')(ti)
        yi = interp1d(t, y, kind='cubic')(ti)

        ax.plot(xi, yi, color='black')

    # 1D Euclidean
    points = [[0.31, 0.74], [0.37, 0.8], [0.53, 0.66], [0.69, 0.43],
              [0.71, 0.26], [0.68, 0.12], [0.59, 0.02],
              [0.49, -0.04], [0.45, 0.04], [0.44, 0.3], [0.31, 0.74]]
    my_plot(points)
    # ax.add_line(plt.Polygon(points, fill=None, edgecolor='black',
    # lw=2, joinstyle="round", capstyle="round"))
    my_arrow(0.64, 0.71, 0.61, 0.66)
    my_line(0.75, 0.90, 0.64, 0.71)
    my_line(0.95, 0.65, 0.64, 0.71)
    my_text(0.75, 0.90, "1D Interval", color="darkgreen")
    my_text(0.95, 0.65, "SP (Con.)", color="limegreen")

    # Walsh SP
    # points = [[0.04, -0.64], [0, -0.89], [-0.07, -1.02], [-0.16, -1], [-0.28, -0.93],
    # [-0.34, -0.79], [-0.22, -0.69], [0.04, -0.64]]
    points = [[0.04, -0.66], [-0.005, -0.89], [-0.07, -1.02], [-0.16, -1],
              [-0.28, -0.93], [-0.34, -0.79],
              [-0.22, -0.69], [0.04, -0.66]]
    my_plot(points)

    ax.arrow(-0.32, -1.2, 0.07, 0.16, head_width=0.02, head_length=0.05,
             fc='k', ec='k')
    my_text(-0.32, -1.2, "SP (Wal.)", color="OliveDrab")

    # Mallows next to Walsh
    points = [[0.04, -0.66], [0.12, -0.64], [0.15, -0.72], [0.15, -0.98],
              [0.11, -1.05], [-0.07, -1.02]]
    my_plot(points)

    # Mallows 0.5
    points = [[0.43, -0.95], [0.38, -1.03], [0.32, -1.04], [0.19, -0.98],
              [0.19, -0.69], [0.24, -0.63], [0.3, -0.69]]
    my_plot(points)

    # Mallows 0.25
    points = [[0.3, -0.69], [0.35, -0.57], [0.42, -0.58], [0.44, -0.71],
              [0.55, -0.83], [0.54, -0.95], [0.43, -0.95],
              [0.3, -0.69]]
    my_plot(points)

    # Mallows [many]
    points = [[0.42, -0.58], [0.55, -0.45], [0.67, -0.48], [0.76, -0.59],
              [0.72, -0.78], [0.65, -0.84],
              [0.55, -0.83]]

    my_plot(points)

    my_arrow(0.56, -1.2, 0.61, -0.92)
    my_arrow(0.56, -1.2, 0.51, -1.05)
    my_arrow(0.56, -1.2, 0.45, -1.07)
    my_arrow(0.56, -1.2, 0.2, -1.05)
    my_text(0.56, -1.2, "Mallows", color="DodgerBlue")

    # Sphere
    points = [[-0.8, 0.42], [-0.64, 0.71], [-0.43, 0.86], [-0.31, 0.90],
              [-0.17, 0.88], [-0.14, 0.78],
              [-0.22, 0.53], [-0.42, 0.10], [-0.62, 0.01], [-0.77, 0.06],
              [-0.82, 0.22], [-0.8, 0.42]]
    my_plot(points)

    my_arrow(-0.63, 0.94, -0.59, 0.85)
    my_line(-0.9, 0.9, -0.63, 0.94)
    my_line(-0.41, 1.1, -0.63, 0.94)
    my_text(-0.9, 0.9, "SPOC", color="darkred", alpha=0.7)
    my_text(-0.41, 1.1, "2/3/5D H-Sphere", color="black", alpha=0.8)

    # Impartial Culture & Mallows 0.999
    points = [[-0.41, 0.75], [-0.32, 0.68], [-0.29, 0.47], [-0.35, 0.34],
              [-0.50, 0.21], [-0.61, 0.27],
              [-0.63, 0.41], [-0.41, 0.75]]
    my_plot(points)

    my_arrow(-0.84, 0.37, -0.66, 0.34)
    my_line(-1.05, 0.32, -0.84, 0.37)
    my_line(-1, 0.55, -0.84, 0.37)
    my_text(-1.05, 0.32, "IC", color="black")
    my_text(-1, 0.55, "Mallows", color="darkblue")

    # 2D
    points = [[0.12, 0.27], [0.3, 0.37], [0.41, 0.18], [0.41, -0.03],
              [0.31, -0.18]]
    my_plot(points)
    my_arrow(1.07, -0.22, 0.47, -0.08)
    my_text(1.07, -0.22, "2D Square", color="green")

    # 3D
    points = [[0.31, -0.18], [0.16, -0.26], [0.08, -0.03], [0, 0.24],
              [0.12, 0.27], [0.26, 0.04], [0.31, -0.18]]
    my_plot(points)
    my_arrow(1.0, -0.47, 0.37, -0.22)
    my_text(1.0, -0.47, "3D Cube", color="ForestGreen", alpha=0.7)

    # 5D, 10D, 20D
    points = [[0.16, -0.26], [-0.11, -0.32], [-0.38, -0.22], [-0.43, -0.05],
              [0, 0.24]]
    my_plot(points)

    my_arrow(-1.05, -0.10, -0.49, -0.12)
    my_text(-1.05, -0.10, "5/10/20D H-Cube", color="MediumSeaGreen", alpha=0.9)

    # Mallows 0.95 (next to SC)
    points = [[-0.23, -0.4], [-0.3, -0.5], [-0.58, -0.47], [-0.64, -0.28],
              [-0.23, -0.4]]
    my_plot(points)

    ax.arrow(-0.95, -0.44, 0.24, 0.03, head_width=0.02, head_length=0.05,
             fc='k', ec='k')
    ax.arrow(-0.95, -0.44, 0.59, 0.5, head_width=0.02, head_length=0.05,
             fc='k', ec='k')
    my_text(-0.95, -0.44, "Mallows", color="darkblue", alpha=0.8)

    # Single-Crossing
    points = [[-0.23, -0.4], [-0.04, -0.37], [0.24, -0.29], [0.39, -0.28],
              [0.4, -0.33], [0.14, -0.47],
              [-0.3, -0.65], [-0.52, -0.6], [-0.58, -0.47]]
    my_plot(points)

    my_arrow(-0.80, -0.84, -0.48, -0.67)
    my_text(-0.80, -0.84, "Single Crossing", color="purple", alpha=0.6)

    # Mallows 0.99
    points = [[-0.26, 0.34], [-0.1, 0.48], [-0.05, 0.41], [-0.04, 0.34],
              [-0.14, 0.2], [-0.26, 0.1],
              [-0.34, 0.13], [-0.26, 0.34]]
    my_plot(points)

    # [free] URN
    # ax.arrow(-0.67, -1.77, 0.12, 0.12, head_width=0.02, head_length=0.05, fc='k', ec='k')
    my_arrow(0.11, 1.0, -0.07, 0.72)
    my_arrow(0.11, 1.0, 0.16, 0.64)
    my_text(0.11, 1.0, "Urn", color="Orange")
    my_arrow(1., 0.2, 0.73, 0)
    my_text(1., 0.2, "Urn", color="OrangeRed")

    # Mallows parameters
    my_number(0.78, -0.85, "0.001", color="darkblue")
    my_number(0.82, -0.74, "0.01", color="darkblue")
    my_number(0.84, -0.63, "0.05", color="darkblue")
    my_number(0.55, -0.39, "0.1", color="darkblue")
    my_number(0.35, -0.5, "0.25", color="darkblue")
    my_number(0.23, -0.57, "0.5", color="darkblue")
    my_number(0.08, -0.58, "0.75", color="darkblue")
    my_number(-0.65, -0.52, "0.95", color="darkblue")
    my_number(-0.91, -0.31, "0.99", color="darkblue")
    my_number(-0.94, 0.67, "0.999", color="darkblue")

    # Urn parameters
    my_number(-0.08, 0.88, "0.01", color="orangered")
    my_number(0.07, 0.81, "0.02", color="orangered")
    my_number(0.2, 0.87, "0.05", color="orangered")
    my_number(0.26, 0.75, "0.1", color="orangered")
    my_number(0.77, 0.13, "0.2", color="orangered")
    my_number(0.82, -0.03, "0.5", color="orangered")


def level_background(fig=None, ax=None, saveas=None, tex=None):
    fig.set_size_inches(10, 10)

    # corners = [[-1, 1, 1, -1], [1, 1, -1, -1]]
    # ax.scatter(corners[0], corners[1], alpha=0)

    def my_line(x1, y1, x2, y2):
        ax.arrow(x1, y1, x2 - x1, y2 - y1, head_width=0., head_length=0.,
                 fc='k', ec='k')

    def my_plot(points, color='black', _type='--'):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        from scipy.interpolate import interp1d

        t = np.arange(len(x))
        ti = np.linspace(0, t.max(), 10 * t.size)

        xi = interp1d(t, x, kind='cubic')(ti)
        yi = interp1d(t, y, kind='cubic')(ti)

        ax.plot(xi, yi, _type, color=color)

    """
    points = [[-0.97, 0.95], [-0.37, 0.97], [0.11, 1.33], [0.27, 1.75]]
    my_plot(points)

    points = [[-0.58, 0.22], [0, 0.45], [0.38, 0.87], [0.57, 1.6]]
    my_plot(points)

    points = [[-0.1, -0.02], [0.3, 0.42], [0.57, 0.88], [0.69, 1.42]]
    my_plot(points)

    points = [[0.21, -0.07], [0.46, 0.36], [0.69, 0.86], [0.84, 1.33]]
    my_plot(points)
    """

    """
    # FROM ID
    points = [[0.74, -0.18], [0.92, 0.33], [0.97, 1.06], [0.93, 1.63]]
    my_plot(points)
    points = [[1.55, -0.5], [1.61, 0.15], [1.55, 0.77], [1.38, 1.45]]
    my_plot(points)
    points = [[2.04, -0.11], [1.98, 0.38], [1.92, 0.78], [1.84, 1.2]]
    my_plot(points)
    """

    # FROM UN
    my_plot([[0.55, 0.01], [0.76, 0.48], [0.76, 0.87], [0.5, 1.16]],
            color='darkblue')
    my_plot([[0.96, -0.28], [1.5, 0.45], [1.32, 1.15], [1.06, 1.54]],
            color='darkblue')
    my_plot([[1.64, -0.44], [1.8, 0.08], [1.9, 0.67], [1.85, 1.2]],
            color='darkblue')

    # FROM ST
    my_plot([[1.06, -0.36], [1.36, 0.06], [1.76, 0.23], [2.19, 0.02]],
            color='darkred')
    my_plot([[0.58, -0.02], [1.05, 0.87], [1.63, 1.03], [2.32, 0.81]],
            color='darkred')
    my_plot([[0.11, 0.57], [0.52, 0.96], [0.91, 1.3], [1.22, 1.45]],
            color='darkred')

    # plt.legend(bbox_to_anchor=(1.25, 1.))
    file_name = saveas + ".png"
    path = os.path.join(os.getcwd(), "images", file_name)
    plt.savefig(path, bbox_inches='tight')
    plt.grid(True)

    # plt.xlim(-1.4, 1.3)
    # plt.ylim(-1.4, 1.3)

    if tex:
        import tikzplotlib
        file_name = saveas + ".tex"
        path = os.path.join(os.getcwd(), "images", "tex", file_name)
        tikzplotlib.save(path)


def get_values_from_file_old(experiment, experiment_id, values,
                             normalizing_func=None, marker_func=None):
    path = os.path.join(os.getcwd(), "experiments", experiment_id, "features",
                        str(values) + ".txt")

    _min = 0
    _max = 0
    values = []
    with open(path, 'r') as txtfile:
        for _ in range(experiment.num_elections):
            values.append(float(txtfile.readline()))
    _min = min(values)
    _max = max(values)

    with open(path, 'r') as txtfile:

        shades = []
        xx = []
        yy = []
        markers = []

        ctr = 0
        for family_id in experiment.families:
            for k in range(experiment.families[family_id].size):
                election_id = family_id + '_' + str(k)

                shade = float(txtfile.readline())
                if normalizing_func is not None:
                    shade = normalizing_func(shade)
                else:
                    shade = (shade - _min) / (_max - _min)
                shades.append(shade)

                marker = experiment.families[family_id].marker
                if marker_func is not None:
                    marker = marker_func(shade)
                markers.append(marker)

                xx.append(experiment.points[election_id][0])
                yy.append(experiment.points[election_id][1])

                ctr += 1

        xx = np.asarray(xx)
        yy = np.asarray(yy)
        shades = np.asarray(shades)
        markers = np.asarray(markers)
        return xx, yy, shades, markers, _min, _max


# Adjusting the map
# def adjust_the_map_on_four_points(experiment, left, right, up, down):
#     try:
#         d_x = experiment.coordinates[right][0] - experiment.coordinates[left][0]
#         d_y = experiment.coordinates[right][1] - experiment.coordinates[left][1]
#         alpha = math.atan(d_x / d_y)
#         experiment.rotate(alpha - math.pi / 2.)
#         if experiment.coordinates[left][0] > experiment.coordinates[right][0]:
#             experiment.rotate(math.pi)
#         if experiment.coordinates[up][1] < experiment.coordinates[down][1]:
#             experiment.reverse()
#     except Exception:
#         pass


def adjust_the_map_on_three_points(experiment, left, right, down) -> None:
    try:
        d_x = experiment.coordinates[right][0] - experiment.coordinates[left][0]
        d_y = experiment.coordinates[right][1] - experiment.coordinates[left][1]
        alpha = math.atan(d_x / d_y)
        experiment.rotate(alpha - math.pi / 2.)
        if experiment.coordinates[left][0] > experiment.coordinates[right][0]:
            experiment.rotate(math.pi)
    except Exception:
        pass

    if experiment.coordinates[left][1] < experiment.coordinates[down][1]:
        experiment.reverse()


def adjust_the_map(experiment) -> None:
    if experiment.election_type == 'ordinal':

        try:
            left = experiment.get_election_id_from_model_name('uniformity')
            right = experiment.get_election_id_from_model_name('identity')
            # up = experiment.get_election_id_from_model_name('antagonism')
            down = experiment.get_election_id_from_model_name('stratification')
            adjust_the_map_on_three_points(experiment, left, right, down)
        except Exception:
            pass

    # elif type(experiment) is ApprovalElectionExperiment:
    elif experiment.election_type == 'approval':
        try:
            left = 'IC 0.5'
            right = 'ID 0.5'
            # up = experiment.get_election_id_from_model_name('approval_full')
            down = experiment.get_election_id_from_model_name('approval_empty')
            adjust_the_map_on_three_points(experiment, left, right, down)
        except Exception:
            try:
                left = 'IC 0.25'
                right = 'ID 0.25'
                # up = experiment.get_election_id_from_model_name('approval_full')
                down = experiment.get_election_id_from_model_name('approval_empty')
                adjust_the_map_on_three_points(experiment, left, right, down)
            except Exception:
                pass


# # # # # # # # # # # # # # # #
# LAST CLEANUP ON: 12.10.2021 #
# # # # # # # # # # # # # # # #