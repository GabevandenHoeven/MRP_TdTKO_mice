import pandas
from plots import plot_vj_distance_reads, plot_vj_distance_perc


def calculate_average_v_j_distance(fn, delim):
    """

    :param fn:
    :param delim:
    :return:
    """
    df = pandas.read_csv(fn, sep=delim, header=0)
    sum_ = df['V.J.distance'].sum()
    # reads = list(df['Number.of.reads'])
    reads = 0
    distances = list(df['V.J.distance'])
    distance_occ = list(df['V.J.distance'].value_counts().sort_index())
    unique_distances = sorted(list(df['V.J.distance'].unique()))
    n_rows = len(df)
    avg = sum_ / n_rows
    print(f'The average VJ distance is: {sum_} / {n_rows} = {avg}')
    return distances, reads, unique_distances, distance_occ, avg


if __name__ == '__main__':
    vj_distances = []
    read_counts = []
    unique_distances = []
    distance_occurrences = []
    labels = []
    averages = []
    filenames = [
        '..\\data_files\\TdTKO\\filtered_data\\filtered_data_exp_TdTKO_v2.tsv',
        '..\\data_files\\Normal\\filtered_data\\filtered_data_exp_Normal_v2.tsv'
        # '..\\data_files\\TdTKo\\filtered_data\\filtered_data_gen_TdTKO_v2.tsv',
        # '..\\data_files\\Normal\\filtered_data\\filtered_data_gen_Normal_v2.tsv'
                ]
    for file in filenames:
        d, r, unique_d, d_occ, average = calculate_average_v_j_distance(file, '\t')
        vj_distances.append(d)
        read_counts.append(r)
        averages.append(average)
        unique_distances.append(unique_d)
        d_occ = [occ * 100 / sum(d_occ) for occ in d_occ]
        distance_occurrences.append(d_occ)
        labels.append(file.split('_')[-1].rstrip('.tsv'))
    # plot_vj_distance_reads(vj_distances, read_counts, labels)
    out_fn = f'..\\img\\unique_seq_img\\VJ_distance_distribution_seq_fraction_{"-".join(labels)}'
    # out_fn = f'..\\img\\unique_seq_img\\Generated_VJ_distance_distribution_seq_fraction_{"-".join(labels)}'
    plot_vj_distance_perc(unique_distances, distance_occurrences, averages, labels, out_fn)
