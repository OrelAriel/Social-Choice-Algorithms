import csv
import copy

def main():
    q1()


def q1():
    """
    in
    :return:
    """

    """ Reading the four files """
    #   Read SOC
    #   (contains a profile consisting of a complete, transitive, and asymmetric relation over a group of objects)
    soc = read_file_to_list('ED-00009-00000001.soc')
    #   Read PWG (describe a set of pairwise relations. Every possible pairwise comparison is listed)
    pwg = read_file_to_list('ED-00009-00000001.pwg')
    #   Read TOG (describe a tournament graph - complete directed graph over a set of alternatives)
    tog = read_file_to_list('ED-00009-00000001.tog')
    #   Read WMG (describe a majority graph relation with weights)
    #   number of times the particular relation was listed minus the number of times the reverse relation was listed
    wmg = read_file_to_list('ED-00009-00000001.wmg')


    """ Arranging the data """
    number_of_candidates = int(soc[0][0])
    candidates_number_and_name = soc[1:number_of_candidates + 1]
    candidates_numbers = []
    for candidates in candidates_number_and_name:
        candidates_numbers.append(int(candidates[0]))

    soc_info = soc[number_of_candidates + 1]
    soc = soc[number_of_candidates + 2:]
    new_soc = []
    for line in soc:
        int_line = []
        for num in line:
            int_line.append(int(num))
        new_soc.append(int_line)
    soc = new_soc

    pwg_info = pwg[number_of_candidates + 1]
    pwg = pwg[number_of_candidates + 2:]

    tog_info = tog[number_of_candidates + 1]
    tog = tog[number_of_candidates + 2:]
    tog_arranging = []
    for line in tog:
        int_winner = int(line[1])
        int_loser = int(line[2])
        result = [int_winner, int_loser]
        tog_arranging.append(result)
    tog = tog_arranging

    wmg_info = wmg[number_of_candidates + 1]
    wmg = wmg[number_of_candidates + 2:]

    """ Check for Condorcet winner """

    winner_candidate = candorcet_winner(tog, number_of_candidates)

    if winner_candidate > 0:
        winner_info = candidates_number_and_name[winner_candidate - 1]
        print('alternative ‘{}’ is a Condorcet winner'.format(winner_info[0]))

        """ Update variables """
        number_of_candidates -= 1
        candidates_numbers.remove(int(winner_info[0]))
        candidates_number_and_name.remove(winner_info)
        pwg = update_pwg(pwg, winner_info[0])
        tog = update_tog(tog, int(winner_info[0]))
        wmg = update_wmg(wmg, winner_info[0])
        soc = update_soc(soc, int(winner_info[0]))
        # print(pwg)
        # print(tog)
        # print(len(wmg))
        # print(soc)

    """ Check the winners """

    # Plurality winner
    plurality_winner_candidate = plurality_winner(tog, number_of_candidates)
    winner_info = candidates_number_and_name[plurality_winner_candidate - 1][0]
    print('alternative ‘{}’ is a Plurality winner'.format(winner_info[0]))

    # Borda winner
    borda_winner_candidate = borda_winner(soc, number_of_candidates)
    winner_info = candidates_number_and_name[borda_winner_candidate - 1][0]
    print('alternative ‘{}’ is a Borda winner'.format(winner_info[0]))

    # Nanson winner
    nanson_winner_candidate = nanson_winner(soc, number_of_candidates, candidates_number_and_name)
    winner_info = candidates_number_and_name[nanson_winner_candidate - 1][0]
    print('alternative ‘{}’ is a Nanson winner'.format(winner_info[0]))

    # Copland winner
    copland_winner_candidate = copland_winner(tog, number_of_candidates)
    winner_info = candidates_number_and_name[copland_winner_candidate - 1][0]
    print('alternative ‘{}’ is a copland winner'.format(winner_info[0]))


def update_soc(soc, winner):
    """
    :param soc: Contains a profile consisting of a complete, transitive, and asymmetric relation over a group of objects
    :param winner: Integer of the winner number
    :return: Contains a profile without the winner
    """
    updated_soc = []
    for line in soc:
        fix_line = line[0]
        fix_line2 = line[1:]
        fix_line2.remove(winner)
        updated_soc.append([fix_line] + fix_line2)
    return updated_soc


def update_wmg(wmg, winner):
    """
    :param wmg: Majority graph relation with weights
    :param winner: String of the winner number
    :return: Majority graph relation with weights. Without the winner
    """
    updated_wmg = []
    for line in wmg:
        if not (winner == line[1]) and not (winner == line[2]):
            updated_wmg.append(line)
    return updated_wmg


def update_tog(tog, winner):
    """
    :param tog: tournament graph
    :param winner: Integer of the winner number
    :return: Tournament graph without the winner
    """
    updated_tog = []
    for line in tog:
        if winner not in line:
            updated_tog.append(line)
    return updated_tog


def update_pwg (pwg, winner):
    """
    :param pwg: Set of pairwise relations. Every possible pairwise comparison is listed
    :param winner: String of the winner number
    :return: Set of pairwise relations. Without candidate pairwise comparison
    """
    updated_pwg = []
    for line in pwg:
        if not(winner == line[1]) and not(winner == line[2]):
            updated_pwg.append(line)
    return updated_pwg


def nanson_winner(soc, number_of_candidates, candidates_info):

    candidate_left = number_of_candidates
    copy_soc = []
    copy_candidates_info = copy.deepcopy(candidates_info)
    for relation in soc:
        copy_soc.append(relation)

    k = 4

    while candidate_left > 1:
        win_score = [0] * (number_of_candidates + 1)
        total_score = 0
        for relation in copy_soc:
            number_of_voters = relation[0]
            minus_score = 1
            for position in relation[1:]:

                win_score[position] += ((candidate_left - minus_score) * number_of_voters)
                total_score += ((candidate_left - minus_score) * number_of_voters)
                minus_score += 1
        score_avg = total_score / candidate_left
        delete_positions = []

        for position in win_score[1:]:

            if position < score_avg:
                delete_positions.append(win_score.index(position))
        delete_positions = delete_positions[::-1]

        for position in delete_positions:

            if position != 0:
                copy_soc = update_soc(copy_soc, position)
                copy_candidates_info.pop()
                candidate_left -= 1

        k -= 1

    return win_score.index(max(win_score))


def borda_winner(soc, number_of_candidates):
    win_score = [0] * (number_of_candidates + 1)
    for relation in soc:
        number_of_voters = relation[0]
        minus_score = 1
        for position in relation[1:]:
            win_score[position] += ((number_of_candidates - minus_score) * number_of_voters)
            minus_score += 1
    return win_score.index(max(win_score))


def plurality_winner(tog, number_of_candidates):
    """
    :param tog: Complete directed graph over a set of alternatives
    :param number_of_candidates: Number of candidates
    :return: Number of condorcet winner
    """
    win_score = [0] * (number_of_candidates + 1)
    for winner in tog:
        win_score[winner[0]] += 1
    return win_score.index(max(win_score))


def copland_winner(tog, number_of_candidates):
    """
       :param tog: Complete directed graph over a set of alternatives
       :param number_of_candidates: Number of candidates
       :return: Number of copland winner (else 0)
    """
    win_score = [0] * (number_of_candidates + 1)
    for winner in tog:
        win_score[winner[0]] += 1
    return win_score.index(max(win_score))


def candorcet_winner(tog, number_of_candidates):
    """
    :param tog: Complete directed graph over a set of alternatives
    :param number_of_candidates: Number of candidates
    :return: Number of condorcet winner (else 0)
    """
    win_score = [0] * (number_of_candidates + 1)

    for winner in tog:
        win_score[winner[0]] += 1

    if number_of_candidates - 1 in win_score:
        return win_score.index(number_of_candidates - 1)

    else:
        return 0


def read_file_to_list(x):
    """
    :param x: File's name form the current folder
    :return: List of lists of the metadata and data
    """
    lis = []
    with open(x) as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            lis.append(line)
    return lis


if __name__ == "__main__":
    main()
