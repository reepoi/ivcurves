import datetime
import json
import utils_docs as utils
from utils_docs import mp # same instance of mpmath's mp imported in ivcurves/utils


def load_scores_database():
    with open('scores_database.json', 'r') as file:
        return json.load(file)


def submissions():
    """
    Get the submissions in the scores database, excluding those marked broken.

    Returns
    -------
        A dict mapping pull request numbers to submission data.
    """
    database = load_scores_database()
    return {pr_number: submission_data
            for pr_number, submission_data in database.items()
            if 'broken' not in submission_data.keys()}


def to_ghuser(username):
    return f':ghuser:`{username}`'


def to_pull(pr_number):
    return f':pull:`{pr_number}`'


def link_to_submission_main_at_commit(commit, username, submission_main):
    return f'https://github.com/cwhanse/ivcurves/tree/{commit}/submissions/{username}/{submission_main}'


def datetime_from_github_datetime_str(ghdatetime_str):
    return datetime.datetime.strptime(ghdatetime_str, '%Y-%m-%dT%H:%M:%SZ')


def leaderboard_entry_list():
    entries = []

    for pr_number, submission_data in submissions().items():
        submission_link = link_to_submission_main_at_commit(
            submission_data["merge_commit"],
            submission_data["username"],
            submission_data["submission_main"]
        )
        entries.append({
            'submission': f'`#{pr_number} <{submission_link}>`_',
            'username': to_ghuser(submission_data['username']),
            'overall_score': sum(mp.mpmathify(v) for v in submission_data['test_sets'].values()),
            'submission_datetime': datetime_from_github_datetime_str(submission_data['submission_datetime'])
        })

    # order entries from lowest score to highest, and then by submission datetime
    entries.sort(key=lambda l: l['submission_datetime'])
    entries.sort(key=lambda l: l['overall_score'])

    for idx, entry in enumerate(entries):
        entry['rank'] = f'#{idx + 1}'
        entry['overall_score'] = mp.nstr(entry['overall_score'])
        # use the submission date instead of datetime
        entry['submission_date'] = entry['submission_datetime'].strftime('%m/%d/%Y')

    return entries


def compare_submissions_entry_list():
    entries = []

    for pr_number, submission_data in submissions().items():
        submission_link = link_to_submission_main_at_commit(
            submission_data["merge_commit"],
            submission_data["username"],
            submission_data["submission_main"]
        )
        entry = {
            'submission': f'`#{pr_number} <{submission_link}>`_',
            'username': to_ghuser(submission_data['username'])
        }
        for name, score in submission_data['test_sets'].items():
            entry[name] = mp.nstr(mp.mpmathify(score))

        entries.append(entry)

    return entries


def test_set_name_to_parameters_and_image():
    mapping = {}
    test_set_names = list(utils.get_filenames_in_directory(utils.TEST_SETS_DIR))
    test_set_names.sort()
    for name in test_set_names:
        info = {}
        for idx, parameters in utils.read_iv_curve_parameter_sets(f'{utils.TEST_SETS_DIR}/{name}').items():
            info[idx] = {'title': f'Case {idx}',
                         'parameters': list(map(mp.nstr, parameters[:-1])), # exclude cells_in_series
                         'image_path': f'./_images/test_cases/{utils.make_iv_curve_name(name, idx)}.png'}
        mapping[name] = info
    return mapping

