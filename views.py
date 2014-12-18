from flask import render_template, request, jsonify, session
from app import app
#from schedule_api import get_terms, get_schools, get_sections, parse_search, get_courseDescription, get_selected_section, get_selected_section_days, get_selected_section_times, get_subjects

term = ''
school = ''
className = ''
subjectCode = ''
catalogNumber = ''
search = False
options = {'subjects':[], 'backpack':[], 'discussions':[], 'Meeting':{'Days':[""],'Times':[""]}}
InvalidAPIUsage = 0

@app.route('/')
def index():
    
    global options, search
    try:
        options = {'show_backpack':[], 'subj_search':[], 'subjects':[], 'backpack':[], 'discussions':[], 'Meeting':{'Days':[""],'Times':[""]}}
        options['terms'] = get_terms()
        options['schools'] = get_schools('2020') #on first search uses term code 2020
    except:
        options['api_error'] = True
        
    options['backpack'][:] = []
    options['subjects'][:] = []
    search = False
    return render_template('index.html', **options)

@app.route('/', methods = ['POST'])
def index2():
    global term, school, className, subjectCode, catalogNumber, options, InvalidAPIUsage, search
    term = request.form['termCode']
    school = request.form['schoolCode']
    options['backpack_error'] = False
    options['search_error'] = False
    className_test = request.form['className']
    if className_test.lower() == 'subj':
        options['school'] = school
        options['subjects'] = get_subjects(term, school)
        options['terms'] = get_terms()
        options['schools'] = get_schools(term)
        options['subj_search'] = True
        search = True
    else:
        className = className_test
        try:    #This "try" can deal with input such as "" or "183"
            subjectCode = parse_search(className)[0]
            catalogNumber = parse_search(className)[1]
            try:
                if request.method == 'POST':
                    options['terms'] = get_terms()
                    options['schools'] = get_schools(term)
                    options['sections'] = get_sections(term, school, subjectCode, catalogNumber)
                    options['CourseDescr'] = get_courseDescription(term, school, subjectCode, catalogNumber)
                    options['backpack']
            except:
                options['terms'] = get_terms()
                options['schools'] = get_schools(term)
                options['search_error'] = True
                options['CourseDescr'] = "This course doesn't exist! "          # To cover the results from last search
                options['sections'] = []
        except:
            options['terms'] = get_terms()
            options['schools'] = get_schools(term)
            options['CourseDescr'] = "This course doesn't exist!" # To cover the results from last search
            options['sections'] = []
            options['search_error'] = True
            
    return render_template('index.html', **options)
 
@app.route('/') #give a "Search fail" message when search fails
def invalid_data():
    global options, InvalidAPIUsage
    if options.get('search_error') == True:
        InvalidAPIUsage = 410
    if InvalidAPIUSage != 0:
        raise ScheduleApiError('This is a non-existing class!', status_code = InvalidAPIUsage)

@app.route('/backpack', methods = ['GET','POST'])
def index3():
    
    global className, selectedCourse, session, options
    session['backpack'] = options['backpack']
    session['subjects'] = options['subjects']
    if search:
        session['school'] = options['school']
        session['subjects'] = options['subjects']

    try:
        if request.method == 'POST':
            session['terms'] = options['terms']
            session['schools'] = options['schools']
            session['sections'] = options['sections']
            session['CourseDescr'] = options['CourseDescr']
            options['backpack_error'] = False

            if 'backpack' not in session:
                session['backpack'] = []
            if 'discussions' not in session:
                session ['discussions'] = []
            
            try:
                removedCourse = request.form['remove']
                display = str(removedCourse)
                session['backpack'].remove(display)
                options['backpack'] = session['backpack']

            except:
                display = ''
                selectedDiscussion = ''
                try:
                    lab = request.form['lab']
                    selectedDays_lab = get_selected_section_days(term, school, subjectCode, catalogNumber,lab)
                    selectedTimes_lab = get_selected_section_times(term, school, subjectCode, catalogNumber,lab)
                    selectedDiscussion = 'Lab: ' + lab + ", Day(s): " + str(selectedDays_lab) + ", Time: " + str(selectedTimes_lab)
                    display = str(className.upper()) + " "
                    try:
                        selectedCourse = request.form['lecture']
                        selectedDays = get_selected_section_days(term, school, subjectCode, catalogNumber,selectedCourse)
                        selectedTimes = get_selected_section_times(term, school, subjectCode, catalogNumber,selectedCourse)
                        display = str(className.upper()) + ", Section: " + str(selectedCourse) + ", Day(s): " + str(selectedDays) + ", Time: " + str(selectedTimes)+ " "
                        try:
                            discussion = request.form['discussion']
                            selectedDays_dis = get_selected_section_days(term, school, subjectCode, catalogNumber,discussion)
                            selectedTimes_dis = get_selected_section_times(term, school, subjectCode, catalogNumber,discussion)
                            selectedDiscussion = ' Discussion: ' + discussion + ", Day(s): " + str(selectedDays_dis) + ", Time: " + str(selectedTimes_dis)
                        except:
                            pass
                    except:
                        pass
                except:
                    try:
                        selectedCourse = request.form['lecture']
                        selectedDays = get_selected_section_days(term, school, subjectCode, catalogNumber,selectedCourse)
                        selectedTimes = get_selected_section_times(term, school, subjectCode, catalogNumber,selectedCourse)
                        display = str(className.upper()) + ", Section: " + str(selectedCourse) + ", Day(s): " + str(selectedDays) + ", Time: " + str(selectedTimes)
                        try:
                            discussion = request.form['discussion']
                            selectedDays_dis = get_selected_section_days(term, school, subjectCode, catalogNumber,discussion)
                            selectedTimes_dis = get_selected_section_times(term, school, subjectCode, catalogNumber,discussion)
                            selectedDiscussion = ' Discussion: ' + discussion + ", Day(s): " + str(selectedDays_dis) + ", Time: " + str(selectedTimes_dis)
                        except:
                            pass
                    except:
                        pass
                session['backpack'].append(display + selectedDiscussion)
                options['backpack'] = session['backpack']
                options['show_backpack'] = True
    except:
        options['backpack_error'] = True

    return render_template('index.html',**session)

@app.route("/schedule")
def backpackToJSON():
    backPackedOptions = session['backpack']
    return jsonify(array=backPackedOptions)


@app.route('/schedule', methods = ['POST'])
def schedule():
    return render_template('schedule.html', **session)


