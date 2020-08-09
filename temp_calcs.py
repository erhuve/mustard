from compareColleges import compare

DRIVER_PATH = '/Users/pastel/Downloads/chromedriverReal'
colleges = compare('New York University', 'Stanford University', DRIVER_PATH=DRIVER_PATH, returnDf=False)

def calculate(colleges, field, salary, urbanicity):

    print(field)
    college_scores = []
    for college in colleges:
        field_score = 0

        fields = college['fields'].replace('[','')
        fields = fields.replace(']','')
        fields = fields.split('",',)

        for rank, study in enumerate(fields):

            study = study.replace('"','')
            study = study.strip()

            if study == field:

                field_score = max(10 - rank, 0)

        salary_score = min(float(college['salary']) / salary * 5, 5)

        urban_score = 0
        urbanicity = set(urbanicity)
        if college['location_type'] in urbanicity:
            urban_score += 1
        
        college_scores.append([field_score, salary_score, urban_score])
    return college_scores

print(calculate(colleges, 'Liberal Arts and Sciences, General Studies and Humanities - Bachelor\'s Degree', 50000, ['Suburban','City']))