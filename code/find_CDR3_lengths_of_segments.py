from utils import read_rtcr_refs


def get_cdr3_lengths(references, v_alleles, j_alleles):
    """This function takes a hashmap of reference segment coding sequences containing the nucleotide sequences and
    the start or stop positions of the CDR3 region as well as lists of V and J segment alleles, and determines the
    length of each of the segments' CDR3 nucleotide sequences.

    :param references: dict - A hashmap or dictionary with segment sequences and CDR3 start/stop positions.
        {allele: [nucleotide_sequence, position]}
    :param v_alleles: list - A list with V segment alleles
    :param j_alleles: list - A list with J segment alleles
    :return:
    """
    v_cd3_len = {}
    j_cdr3_len = {}

    for v in v_alleles:
        # from the allele sequence get the germline sequence, up until the end
        v_cd3_len.update({v: len(references[v][0][references[v][1] - 3:])})
    for j in j_alleles:
        # from the allele sequence get the germline sequence, up until the germline indicator
        j_cdr3_len.update({j: len(references[j][0][:references[j][1] + 3])})

    return v_cd3_len, j_cdr3_len


if __name__ == '__main__':
    refs = read_rtcr_refs()
    v_segments = [
        'TRBV1*01', 'TRBV12-1*01', 'TRBV12-2*01', 'TRBV13-1*01', 'TRBV13-2*01', 'TRBV13-3*01', 'TRBV14*01',
        'TRBV15*01', 'TRBV16*01', 'TRBV17*01', 'TRBV19*01', 'TRBV2*01', 'TRBV20*01', 'TRBV23*01', 'TRBV24*01',
        'TRBV26*01', 'TRBV29*01', 'TRBV3*01', 'TRBV30*01', 'TRBV31*01', 'TRBV4*01', 'TRBV5*01'
    ]
    j_segments = [
        'TRBJ1-1*01', 'TRBJ1-2*01', 'TRBJ1-3*01', 'TRBJ1-4*01', 'TRBJ1-5*01', 'TRBJ2-1*01', 'TRBJ2-2*01',
        'TRBJ2-3*01', 'TRBJ2-4*01', 'TRBJ2-5*01', 'TRBJ2-7*01'
    ]
    v, j = get_cdr3_lengths(refs, v_segments, j_segments)
    print(v)
    print(j)

