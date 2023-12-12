def hbar_option(title, y_category, x_data):
    labels = [f"{y}, {x}" for y, x in zip(y_category, x_data)]
    return {
        'title': {'text': title},
        'xAxis': {

            'type': 'value',
            'position': 'top',
            'splitLine': {'lineStyle': {'type': 'dashed'}}
        },
        'yAxis': {
            'type': 'category',
            'inverse': True,
            'axisLine': {'show': False},
            'axisLabel': {'show': False},
            'axisTick': {'show': False},
            'splitLine': {'show': False},
            'data': labels
        },
        'series': [
            {
                'name': '',
                'type': 'bar',
                'label': {'show': True, 'formatter': '{b}'},
                'data': x_data
            }
        ]
    }
