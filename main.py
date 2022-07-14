import requests
import csv
import itertools

from results import Results


def main():
    data = get_data()
    if data == "Quitting":
        return

    yes_vote, no_vote, didnt_vote, was_evel = determine_scottish_votes(data)

    if was_evel:
        return

    result = did_it_pass(data)
    stats = vote_stats(yes_vote, no_vote, didnt_vote, result)
    display_results(stats)


def get_data():
    valid_div_id = False
    while valid_div_id is False:
        try:
            division_id = int(input("Which division do you wish to get data for>>"))
            valid_div_id = True
            will_quit = False
        except TypeError:
            valid_div_id = False
            wish_to_quit = str(input("Invalid input, do you wish to continue>>"))
            if wish_to_quit.lower() == "no":
                pass
            else:
                valid_div_id = True
                will_quit = True

    if will_quit:
        return "Quitting"

    data = requests.get(f'https://commonsvotes-api.parliament.uk/data/division/{division_id}.json')

    try:
        return data.json()
    except:
        print("Error Getting Data")
        return "Quitting"


def load_constit_data():
    with open("constituency_list_scotland.csv", "r") as file:
        reader = csv.reader(file)
        tlist = list(reader)
    scottish_constituency_list = list(itertools.chain.from_iterable(tlist))

    return scottish_constituency_list


def determine_scottish_votes(data):
    was_evel = False
    if data["EVELCountry"] != "":
        print("This vote was an EVEL vote.")
        was_evel = True
    constit_scot = load_constit_data()
    scot_yes_votes = []
    scot_no_votes = []
    scot_didnt_vote = []

    for votes in range(len(data["Ayes"])):
        if (data["Ayes"][votes]["MemberFrom"]) in constit_scot:
            scot_yes_votes.append(data["Ayes"][votes])

    for votes in range(len(data["Noes"])):
        if (data["Noes"][votes]["MemberFrom"]) in constit_scot:
            scot_no_votes.append(data["Noes"][votes])

    for votes in range(len(data["NoVoteRecorded"])):
        if (data["NoVoteRecorded"][votes]["MemberFrom"]) in constit_scot:
            scot_didnt_vote.append(data["NoVoteRecorded"][votes])

    return scot_yes_votes, scot_no_votes, scot_didnt_vote, was_evel


def did_it_pass(data):
    pass_value = data["AyeCount"] - data["NoCount"]
    if pass_value > 0:
        return True
    else:
        return False


def vote_stats(yes_vote, no_vote, didnt_vote, vote_result):
    yes_count = len(yes_vote)
    no_count = len(no_vote)
    abstain_count = len(didnt_vote)
    total_votes = yes_count + no_count
    scot_pass_value = yes_count - no_count

    if scot_pass_value > 0:
        scot_pass = True
    else:
        scot_pass = False

    if scot_pass and vote_result:
        agreement = True
    elif not scot_pass and not vote_result:
        agreement = True
    elif scot_pass and not vote_result:
        agreement = False
    elif not scot_pass and vote_result:
        agreement = False

    vote_percentage = round(total_votes / 59 * 100, 2)
    yes_percentage = round(yes_count / total_votes * 100, 2)
    no_percentage = round(no_count / total_votes * 100, 2)
    abstain_percentage = round(abstain_count / 59 * 100, 2)

    stats = Results(yes_count, no_count, abstain_count, total_votes, scot_pass, agreement, vote_percentage, yes_percentage, no_percentage, abstain_percentage)

    return stats


def display_results(results):
    if results.scot_pass and results.agreement:
        print("Scottish MPs voted in favour, in agreement (voted in favour) with MPs from the rest of the United Kingdom.")
    elif results.scot_pass and not results.agreement:
        print("Scottish MPs voted in favour, in disagreement (voted against) with MPs from the rest of the United Kingdom.")
    elif not results.scot_pass and results.agreement:
        print("Scottish MPs voted against, in agreement (voted against) with MPs from the rest of the United Kingdom.")
    elif not results.scot_pass and not results.agreement:
        print("Scottish MPs voted against, in disagreement (voted in favour) with MPs from the rest of the United Kingdom.")

    if results.abstain_count > results.total_votes:
        print(f"More Scottish MPs ({results.abstain_count}) have no vote registered than actually voted ({results.total_votes})")

    print(f"Total Votes:\n{results.total_votes} ({results.vote_percentage}% of possible Scottish votes)\n")
    print(f"Votes For:\n{results.yes_count} ({results.yes_percentage}%)\n")
    print(f"Votes Against:\n{results.no_count} ({results.no_percentage}%)\n")
    print(f"No Vote Registered:\n{results.abstain_count} ({results.abstain_percentage}%)")


if __name__ == "__main__":
    main()
