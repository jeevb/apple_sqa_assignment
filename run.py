import numpy as np

from pylogs.LogContainer import LogContainer

if __name__ == '__main__':
    # Initialize a container to store logs
    #   i.   Specify the format of log, identifying individual fields as
    #        named regex groups.
    #   ii.  Specify a dict to coerce certain fields to the correct types
    #   iii. Specify the date format
    container = LogContainer(
        log_fmt=(
            r'^(?P<date>\w{3} \d{2} \d{2}\:\d{2}\:\d{2}) (?P<note>\w+) '
            r'(?P<path>.+)\: (?P<fruit>\w+) \[(?P<hexcode>.+)\]\: '
            r'(?P<value>-?\d+)$'
        ),
        field_types={
            'date': 'date',
            'value': 'integer'
        },
        date_fmt='%b %d %H:%M:%S'
    )

    # Parse logs from files of name 'fruit.log' from the directory 'HomeWork'
    container.parse('HomeWork', 'fruit.log')

    # Reorder logs by date and then by fruit name in ascending order
    container.order('date', 'fruit')

    # Summarize the values for the fruit 'Kiwi', by calculating
    # the minimum, maximum, mean, and standard deviation. 'print_result=True'
    # prints a pretty dictionary of the summary values to the screen.
    container.summarize(val='value', by='fruit', var='Kiwi',
                        funcs=[min, max, np.mean, np.std], print_result=True)

    # Write out the ordered logs
    # container.write_to('combined.log')
