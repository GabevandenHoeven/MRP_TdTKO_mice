import csv
import difflib


# IGoR_dict = {}
# category = "NA"
# igordir = "."  # replace with the download of https://github.com/qmarcou/IGoR on your system
# with open(igordir + "/models/human/tcr_beta/models/model_parms.txt") as input_file:
#     for line in input_file:
#         if line[0] == "#":
#             if "GeneChoice" in line:
#                 category = line.split(";")[1]
#             else:
#                 category = "NA"
#         if category != "NA" and line[0] == "%":
#             identifier, sequence, seqIndex = line.rstrip().split(";")
#             if "|" in identifier:
#                 gene_name = identifier.split("|")[1]
#             else:
#                 gene_name = identifier[2:]
#             IGoR_dict[category[0] + seqIndex] = gene_name


def read_rtcr_refs():
    """Parses a file with reference alleles from RTCR. Filters for relevant alleles and stores those in a dictionary
    :returns RTCR_ref: dict -
    """
    # read RTCR refs
    # RTCR_ref_filename = "./immune_receptor_reference.tsv"
    # replace with the gunzipped download of https://github.com/uubram/RTCR/tree/master/rtcr
    RTCR_ref_filename = "C:\\Users\\gabev\\PycharmProjects\\MRP\\immune_receptor_reference.tsv"

    RTCR_ref = {}
    with open(RTCR_ref_filename, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        header = next(reader)
        for row in reader:
            # if row[0] == "HomoSapiens" and "TR" in row[1]:
            if row[0] == "MusMusculus" and "TR" in row[1]:
                if row[1] not in RTCR_ref:
                    RTCR_ref[row[1]] = [row[-1], int(row[-3])]
                else:
                    print(row[0], "observed twice")
    return RTCR_ref


def read_tcrb_data(rtcr_ref: dict, tcrb_data_filename, data_suffix, threshold, delim):
    """Reads the datafile with the nucleotide sequences and used vdj genes
    :param rtcr_ref: dict - reference sequences of TCR genes.
    :param tcrb_data_filename: str - Path to the file containing the TCR data.
    :param data_suffix: str - suffix of the data file used to write results to a new file.
    :param threshold: int - Threshold for a minimum amount of supporting reads.
    :return:
    """

    with open(tcrb_data_filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delim)
        header = next(reader)
        outfile = ["Column1\tMouse_ID\tNo_reads\tV_used\tD_used\tD_length\tJ_used\tV_deleted\tJ_deleted\tinsertion_length\tV_gene\tJ_gene\tV_end\tJ_start\tmin_phred\tcdr3\tphenotype\tstrain\tseq_id\n"]
        outfile_ins = ["Column1\tMouse_ID\tNo_reads\tV_used\tD_used\tD_length\tJ_used\tV_deleted\tJ_deleted\tinsertion_length\tV_gene\tJ_gene\tV_end\tJ_start\tmin_phred\tcdr3\tphenotype\tstrain\tseq_id\n"]
        outfile_below_threshold = ["Column1\tMouse_ID\tNo_reads\tV_used\tD_used\tD_length\tJ_used\tV_deleted\tJ_deleted\tinsertion_length\tV_gene\tJ_gene\tV_end\tJ_start\tmin_phred\tcdr3\tphenotype\tstrain\tseq_id\n"]
        supporting_read_count = {
            # number of reads: count of sequences
        }
        for row in reader:
            column, reads, v_gene, j_gene, cdr3nt_seq = row[0], \
                row[header.index('Number.of.reads')], row[header.index('V.gene')], row[header.index('J.gene')], \
                row[header.index('Junction.nucleotide.sequence')]
            try:
                mouse_id = row[header.index('mouse')]
            except ValueError:
                mouse_id = row[header.index('dirname')]

            line = get_vdj_lengths([v_gene, j_gene, cdr3nt_seq], rtcr_ref)
            out_line = [str(column), mouse_id, reads]
            out_line.extend(line)
            v_end, j_start, phred, phenotype, strain = row[header.index('V.gene.end.position')], \
                row[header.index('J.gene.start.position')], row[header.index('Minimum.Phred')], \
                row[header.index('phenotype')], row[header.index('strain')]
            out_line.extend([v_gene, j_gene, v_end, j_start, phred, cdr3nt_seq, phenotype, strain])
            out_line = "\t".join(e for e in out_line) + "\n"
            try:
                out_line = out_line.replace('\n', f'\t{row[header.index("Nucleotide.seq.id")]}\n')
            except ValueError:
                pass
            if int(reads) < threshold:
                outfile_below_threshold.append(out_line)
            elif line[-1] == "0":
                outfile.append(out_line)
            else:
                outfile_ins.append(out_line)
            try:
                supporting_read_count[int(reads)] += 1
            except KeyError:
                supporting_read_count.update({int(reads): 1})

    # with open('count_reads.txt', 'w') as file:
    #     file.write('Number_of_reads: number_of_sequences\n')
    #     for i in sorted(supporting_read_count.keys()):
    #         file.write(f'{i}: {supporting_read_count[i]}\n')

    # new_filename = f'data_files\\B6\\no_insertions_above_threshold\\{data_suffix}_results_above_{threshold}.tsv'
    new_filename = f'data_files\\TdTKo\\no_insertions_above_threshold\\{data_suffix}_results_above_{threshold}.tsv'
    with open(new_filename, 'w') as file:
        file.writelines(outfile)
    # new_insertion_filename = f'data_files\\B6\\insertions_above_threshold\\{data_suffix}_insertions_above_{threshold}.tsv'
    new_insertion_filename = f'data_files\\TdTKo\\insertions_above_threshold\\{data_suffix}_insertions_above_{threshold}.tsv'
    with open(new_insertion_filename, 'w') as file:
        file.writelines(outfile_ins)
    # below_threshold_filename = f'data_files\\B6\\below_threshold\\{data_suffix}_below_{threshold}.tsv'
    below_threshold_filename = f'data_files\\TdTKo\\below_threshold\\{data_suffix}_below_{threshold}.tsv'
    with open(below_threshold_filename, 'w') as file:
        file.writelines(outfile_below_threshold)
    return


def get_vdj_lengths(input_list: list, RTCR_ref: dict):
    """Code from P.C. de Greef: Accepts a list containing a V- and J-allele and a CDR3 sequence,
    and a dictionary containing reference VDJ alleles with their respective nucleotide sequences.
    This function matches the given alleles to the CDR3, and searches for remnants of the D sequence to find likely
    inserted nucleotides. Adapted by Gabe van den Hoeven Feb. 2024.

    :param input_list: list - [v_gene, j_gene, cdr3 nucleotide sequence]
    :param RTCR_ref: dict - dictionary with all the TCR reference sequences, in the function read_rtcr_refs it can be
    specified which organism.
    :returns line_result: list -
    [#nt used of V, #nt matching D, #nt used of J, #nt deleted of V, #nt deleted of J, #nt insertions]

    """
    V, J, CDR3nt = input_list
    # the specific V and J genes and the whole sequence combined
    if V not in RTCR_ref or J not in RTCR_ref:
        return [25] * 6  # not possible
    germline_V = RTCR_ref[V][0][RTCR_ref[V][1] - 3:]
    # from the allele sequence get the germline sequence, up until the end
    germline_J = RTCR_ref[J][0][:RTCR_ref[J][1] + 3]
    # from the allele sequence get the germline sequence, up until the germline indicator

    match_V = -1
    for i in range(min(len(germline_V), len(CDR3nt))):
        # Match the start of CDR3 to the end of V (germline)
        if germline_V[i] == CDR3nt[i]:
            match_V = i
        else:
            break
    if match_V == -1:
        Vdel = len(germline_V)
        noV_CDR3 = CDR3nt
        Vused = ""
    else:
        Vdel = len(germline_V) - match_V - 1
        noV_CDR3 = CDR3nt[match_V + 1:]
        Vused = germline_V[:match_V + 1]

    match_J = 0
    for i in range(1, min(len(germline_J), len(noV_CDR3)) + 1):
        # Match the end of CDR3 to the start of J (germline)
        if germline_J[-i] == noV_CDR3[-i]:
            match_J = i
        else:
            break
    if match_J == 0:
        Jdel = len(germline_J)
        noVJ_CDR3 = noV_CDR3
        Jused = ""
    else:
        Jdel = len(germline_J) - match_J
        noVJ_CDR3 = noV_CDR3[:-match_J]
        Jused = germline_J[-match_J:]

    # D_seq_string = "gggacagggggc,gggactagcggggggg,gggactagcgggaggg".upper()
    # here human, replace with mouse seqs from IMGT

    D_seq_string = "GGGACAGGGGGC,GGGACTGGGGGGGC".upper()
    # mice seqs from IMGT

    # This is TRB, so check for D
    d = difflib.SequenceMatcher(None, noVJ_CDR3, D_seq_string)
    matchingDlen = max(d.get_matching_blocks(), key=lambda x: x[2])[2]
    d_match = d.find_longest_match()
    Dused = noVJ_CDR3[d_match.a:d_match.a+matchingDlen]
    inslen = len(noVJ_CDR3) - matchingDlen
    # line_result = [len(Vused), matchingDlen, len(Jused), Vdel, Jdel, inslen]
    line_result = [str(len(Vused)), Dused, str(matchingDlen), str(len(Jused)), str(Vdel), str(Jdel), str(inslen)]
    return line_result


def reconfigure_header_tdt_normal_data(fn):
    """Used to fix the header of the wild type data files, the header was missing a column making it difficult
    to use it to get values from a specific column.
    :param fn: The path of the file that needed to be edited.

    :return:
    """
    with open(fn, 'r') as file:
        header = next(file)
        header = header.split('\t')
        header.insert(0, 'Column1')
        header = "\t".join(header)
        out = []
        for row in file:
            out.append(row)
    print('Reconfigured header.\nWriting to file...')
    with open(fn, 'w') as file:
        file.write(header)
        file.writelines(out)


def fraction_insertions(all_sequences_filenames: list, insertions_filenames: list):
    """Calculates the fraction of sequences found containing insertions having above a given threshold of supporting
    reads.
    :param all_sequences_filenames: list - The path to the file containing all sequences of the sample
    :param insertions_filenames: list -
    """
    total_lines_ins = 0
    total_lines_all = 0
    for all_sequences_filename in all_sequences_filenames:
        with open(all_sequences_filename, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)


    for insertions_filename in insertions_filenames:
        with open(insertions_filename, 'r') as f:
            lines = len(f.readlines()) - 1
            total_lines_ins += lines
            print(lines)
    fraction = total_lines_ins * 100 / total_lines_all
    print(f'fraction = {total_lines_ins} * 100 / {total_lines_all} = {fraction}')


def get_junction_length(fn, lengths: list, reads: list, delim: str):
    """

    :return:
    """
    with open(fn, 'r') as file:
        reader = csv.reader(file, delimiter=delim)
        header = next(reader)
        for row in reader:
            length = len(row[header.index('Junction.nucleotide.sequence')])
            lengths.append(length)
            reads.append(int(row[header.index('Number.of.reads')]))
    return lengths, reads


if __name__ == "__main__":
    sequence_lengths = []
    read_counts = []
    file_list = [
        "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\tdt.csv"
        # "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893369_RP-Mandl-28-M65&M66.tsv",
        # "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893370_RP-Mandl-30-M67&M68.tsv",
        # "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893365_RP-Mandl-05-M69&M70.tsv",
        # "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893366_RP-Mandl-06-M71&M72.tsv",
        # "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893367_RP-Mandl-07-M73&M74.tsv"
    ]

    # for filename in file_list:
    #     sequence_lengths, read_counts = get_junction_length(filename, sequence_lengths, read_counts, delim=',')

    # from plots import plot_sequence_length_read_count
    # plot_sequence_length_read_count(sequence_lengths, read_counts, label='TdTKO')

    # average = sum(sequence_lengths) / len(sequence_lengths)
    # print(f'The average is: {average}')

    # filename = "C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893370_RP-Mandl-30-M67&M68.tsv"
    # file_suffix = 'mandl-30'
    threshold_list = [0, 5, 10, 15, 20, 25, 50]
    refs = read_rtcr_refs()
    for threshold in threshold_list:
        files1 = [
            f"C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\B6\\insertions_above_threshold\\mandl-28_insertions_above_{threshold}.tsv",
            f"C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\B6\\insertions_above_threshold\\mandl-30_insertions_above_{threshold}.tsv",
            f"C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\B6\\insertions_above_threshold\\mandl-05_insertions_above_{threshold}.tsv",
            f"C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\B6\\insertions_above_threshold\\mandl-06_insertions_above_{threshold}.tsv",
            f"C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\B6\\insertions_above_threshold\\mandl-07_insertions_above_{threshold}.tsv"
        ]
        # read_tcrb_data(refs, filename, file_suffix, threshold)
        # fraction_insertions(filename, file_suffix, threshold)
        fraction_insertions(file_list, files1)

    for filename in file_list:
        # suffix = '-'.join([filename.split('-')[1], filename.split('-')[2]])
        suffix = 'TdTKO'
        for threshold in threshold_list:
            read_tcrb_data(refs, filename, suffix, threshold, delim=',')
    # filename = 'C:\\Users\\gabev\\PycharmProjects\\MRP\\data_files\\GSM6893362_Mandl-AF-human-07082016.tsv'
    # reconfigure_header_tdt_normal_data(filename)