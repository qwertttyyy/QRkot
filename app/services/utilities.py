def format_time(seconds):
    days = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds = int(seconds)

    day_word = 'day' if days == 1 else 'days'

    return f'{days} {day_word}, {hours:02d}:{minutes:02d}:{seconds:02d}'


def convert_fundraising_time_projects(projects: list) -> list[dict[str, str]]:
    results = []
    for project in projects:
        formatted_time = format_time(project.fundraising_time)
        results.append(
            {
                'name': project.name,
                'fundraising_time': formatted_time,
                'description': project.description,
            }
        )

    return results
