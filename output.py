import csv


def append_to_csv(result):
    fields = [result['time'], result['match']['mode'], result['match']['map'], result['match']['time'], result['self']['hero']]

    for i in range(0, 5):
        fields.append(result['players']['allies'][i]['name'])
        fields.append(result['players']['allies'][i]['elims'])
        fields.append(result['players']['allies'][i]['assists'])
        fields.append(result['players']['allies'][i]['deaths'])
        fields.append(result['players']['allies'][i]['dmg'])
        fields.append(result['players']['allies'][i]['heal'])
        fields.append(result['players']['allies'][i]['mit'])

    for i in range(0, 5):
        fields.append(result['players']['enemies'][i]['name'])
        fields.append(result['players']['enemies'][i]['elims'])
        fields.append(result['players']['enemies'][i]['assists'])
        fields.append(result['players']['enemies'][i]['deaths'])
        fields.append(result['players']['enemies'][i]['dmg'])
        fields.append(result['players']['enemies'][i]['heal'])
        fields.append(result['players']['enemies'][i]['mit'])

    with open(r'log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

