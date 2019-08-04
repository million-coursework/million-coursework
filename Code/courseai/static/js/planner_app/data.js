// Cached Data
let KNOWN_COURSES = {};         // 2D Dictionary: (code, year) -> CourseOffering object
let KNOWN_MMS = {};             // 2D Dictionary: (code, year) -> MMS object
let KNOWN_DEGREES = {};         // 2D Dictionary: (code, year) -> Degree object
let KNOWN_COURSE_LISTS = {};    // Dictionary: list name (e.g. CBE_List_1) -> List of codes

let COURSE_REQUESTS = {};       // Dictionary: code -> AJAX call to degree/coursedata

// Retrieve Data

/**
 * Batch retrieve course titles, and perform an action with each one.
 * Retrieve titles for all the courses at once.
 * Then, the function provided with each course code will be evaluated with the title as a parameter.
 * @param courses_actions   An object, mapping [code - year] (e.g. "COMP1100-2016") to a list of functions.
 */
// async function batchCourseTitles(courses_actions) {
//     let new_ca = {};
//     for (combo in courses_actions) {
//         if (!(combo in new_ca)) new_ca[combo] = [];
//         for (const action of courses_actions[combo]) {
//             new_ca[combo].push(function (offering) {
//                 action(offering.title);
//             })
//         }
//     }
//     await batchCourseOfferingActions(new_ca);
// }

async function getCourseOffering(code, year) {
    if (!(code in KNOWN_COURSES)) KNOWN_COURSES[code] = {};
    if (!(year in KNOWN_COURSES[code])) {
        if (code in COURSE_REQUESTS) {   // Check if there is already a request to get this course.
            await COURSE_REQUESTS[code]; // Wait for that request to complete.
        } else {
            const req = $.ajax({
                url: 'degree/coursedata',
                data: {'codes': '["' + code + '"]'},
                success: function (data) {
                    recordCourseOfferings(code, data.response[code].versions);
                },
            });
            if (!(code in COURSE_REQUESTS)) COURSE_REQUESTS[code] = {};
            COURSE_REQUESTS[code][year] = req;
            await req;
            console.log();
        }
    }
    return KNOWN_COURSES[code][closestYear(year, Object.keys(KNOWN_COURSES[code]))];
}

/**
 * Batch retrieve course data, and perform an action with each one.
 * Retrieve data for all the courses at once.
 * Then, the function provided with each course code will be evaluated with the CourseOffering as a parameter.
 * @param courses_actions   An object, mapping [code - year] (e.g. "COMP1100-2016") to a list of functions.
 * Can provide a course only to automatically operate on the closest available year to the current year.
 */
async function batchCourseOfferingActions(courses_actions) {
    if ($.isEmptyObject(courses_actions)) return;   // TODO: Check for other pending requests and only request new codes.
    let codesToRetrieve = [];
    for (const combo in courses_actions) {
        const code = combo.split('-')[0];
        // if (code in KNOWN_COURSES || code in COURSE_REQUESTS) continue;
        if (code in KNOWN_COURSES) continue;
        codesToRetrieve.push(code);
    }
    const req = $.ajax({
        url: 'degree/coursedata',
        data: {
            'codes': JSON.stringify(codesToRetrieve)
        },
        success: function (data) {
            console.log();
            for (const code in data.response) {
                if (!(data.response.hasOwnProperty(code))) continue;
                recordCourseOfferings(code, data.response[code].versions);
            }
            for (const combo in courses_actions) {
                const code = combo.split('-')[0];
                if (!(code in KNOWN_COURSES) || $.isEmptyObject(KNOWN_COURSES[code])) continue;
                const year = closestYear(combo.split('-')[1] || THIS_YEAR, Object.keys(KNOWN_COURSES[code]));
                for (const action of courses_actions[combo]) {
                    action(KNOWN_COURSES[code][year]);
                }
            }
        }
    });
    for (const code of codesToRetrieve) {
        COURSE_REQUESTS[code] = req;
    }
    await req;
    return await req; // This forces the planner to wait for the success callback? Don't know why its necessary.
}

async function getMMSOffering(code, year) {
    if (!(code in KNOWN_MMS)) KNOWN_MMS[code] = {};
    if (!(year in KNOWN_MMS[code])) {
        await $.ajax({
            url: 'search/mms',
            data: {'query': code},
            success: function (data) {
                recordMMSOfferings(code, data.versions)
            }
        })
    }
    return KNOWN_MMS[code][closestYear(year, Object.keys(KNOWN_MMS[code]))];
}

async function batchMMSData(mms_actions) {
    for (const mms in mms_actions) {
        if (!mms_actions.hasOwnProperty(mms)) continue;
        const code = mms.split('/')[0];
        const year = mms.split('/')[1];
        if (!(code in KNOWN_COURSES)) {
            $.ajax({
                url: 'search/mms',
                data: {
                    'query': code,
                },
                success: function (data) {
                    recordMMSOfferings(code, data.versions);
                    for (const action of mms_actions[mms]) {
                        action(KNOWN_MMS[code][closestYear(year, Object.keys(KNOWN_MMS[code]))])
                    }
                }
            });
        } else {
            for (const action of mms_actions[mms]) {
                action(KNOWN_MMS[code][closestYear(year, Object.keys(KNOWN_MMS[code]))])
            }
        }
    }
}

async function getDegreeOffering(code, year) {
    if (!(code in KNOWN_DEGREES)) KNOWN_DEGREES[code] = {};
    if (!(year in KNOWN_DEGREES[code])) {
        try {
            await $.ajax({
                url: 'degree/degreereqs',
                data: {'query': code + '-' + year},
                success: function (data) {
                    if (!(code in KNOWN_DEGREES)) KNOWN_DEGREES[code] = {};
                    KNOWN_DEGREES[code][year] = new Degree(code, year, data.name, data.units, data.required);
                    //TODO: Support for Optional Rule Sections
                }
            });
        } catch (error) {
            console.log('Failed to retrieve degree program requirements for ' + code + '-' + year);
            console.log('Attempting to get 2018 requirements.');
            try {
                await $.ajax({
                    url: 'degree/degreereqs',
                    data: {'query': code},
                    success: function (data) {
                        if (!(code in KNOWN_DEGREES)) KNOWN_DEGREES[code] = {};
                        KNOWN_DEGREES[code][year] = new Degree(code, THIS_YEAR, data.name, data.units, data.required);
                        //TODO: Support for Optional Rule Sections
                    }
                });
            } catch (error) {
                const name = (code === degree_code) ? degree_name : degree_name2;
                KNOWN_DEGREES[code][year] = new Degree(code, year, name, 144, {});
                console.log('Failed to retrieve degree program requirements for ' + code);
                console.log('Creating generic degree');
            }

        }
        let defaultPlan;
        try {
            defaultPlan = await $.ajax({
                url: 'degree/degreeplan',
                data: {
                    'degree_code': code,
                    'year': year
                }
            });
        } catch (e) {
            defaultPlan = {response: []};
        }
        const suggestedPlan = {};
        let session = year + "S1"; // Starting value
        for (const ses of defaultPlan.response) {
            suggestedPlan[session] = ses;
            session = nextSession(session, 3);
        }
        KNOWN_DEGREES[code][year].suggestedPlan = suggestedPlan;
    }
    return KNOWN_DEGREES[code][year];
}

async function getCourseList(name) {
    if (name in KNOWN_COURSE_LISTS) return KNOWN_COURSE_LISTS[name];
    await $.ajax({
        url: 'search/courselists',
        data: {'query': name},
        success: function (data) {
            KNOWN_COURSE_LISTS[name] = data.response;
        }
    });
    return KNOWN_COURSE_LISTS[name]
}

// Send Data
function preparePlanForUpload(plan) {
    sessions = [];
    for (const session of plan.sessions) {
        to_add = {[session]: []};
        for (const enrolment of plan.courses[session]) {
            to_add[session].push({'code': enrolment.code, 'title': enrolment.course.title});
        }
        sessions.push(to_add);
    }
    return sessions;
}

// Helpers
function recordCourseOfferings(code, offerings) {
    for (const year in offerings) {
        let data = offerings[year];

        if (Object.keys(data)[0] === "sessions" && Object.keys(data).length === 1) {
            data = offerings[year - 1];
            if (year > LATEST_YEAR && Object.keys(data).length > 1) {
                data.sessions = offerings[year].sessions;
            } else continue;
        }

        if (!(code in KNOWN_COURSES)) KNOWN_COURSES[code] = {};
        KNOWN_COURSES[code][year] = new CourseOffering(
            code, year,
            data.title,
            data.units,
            data.prerequisites || [],
            {
                'description': data.description,
                'prerequisite_text': data.prerequisite_text,
                'sessions': data.sessions || [],
                'majors': data.majors || [],
                'minors': data.minors || [],
                'areas_of_interest': data.areas_of_interest,
                'convener': data.convener,
                'learning_outcomes': data.learning_outcomes,
            },
            data['repeatable'] || false);
    }
}

function recordMMSOfferings(code, offerings) {
    for (const year in offerings) {
        let data = offerings[year];
        if (!(code in KNOWN_MMS)) KNOWN_MMS[code] = {};
        KNOWN_MMS[code][year] = new MMS(
            code, year,
            data.title,
            data.requirements,
            {
                'description': data.description,
                'learning_outcomes': data.learning_outcomes,
            });
    }
}

function closestYear(year, list = []) {
    list = list.map(x => typeof(x)==='string' ? parseInt(x) : x);
    if (!year) year = THIS_YEAR;
    if (typeof(year)==='string') year = parseInt(year);

    if (list.includes(year)) return year;
    const maxYear = Math.max(...list);
    const minYear = Math.min(...list);
    if (year >= maxYear) return maxYear;
    if (year <= minYear) return minYear;
    for (let i = 1; i <= Math.max(maxYear - year, year - minYear); i++) {
        if (list.includes(year + i)) return year + i;
        if (list.includes(year - i)) return year - i;
    }
    throw Error("Closest year not found");
}
