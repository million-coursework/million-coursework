function Plan() {
    this.degrees = []; // A list of Degree objects
    this.sessions = []; // List of active sessions in the plan, in order.
    this.courses = {};  // Map from active sessions to list of CourseEnrolments.
    this.trackedMMS = [];  // List of Majors, Minors, etc. currently tracked.
    this.warnings = []; // List of warnings that have been ignored by the user.

    this.changesMade = false;

    this.unsatisfiedCourses = function () {
        let unsat = [];
        for (const session of this.sessions) {
            for (const enrolment of this.courses[session]) {
                let res = enrolment.course.checkRequirements(this, enrolment.session, false);
                if (!(res.sat)) unsat.push({'course': enrolment, 'inc': res.inc});
            }
        }
        return unsat;
    };

    this.countCourseLoads = function () {
        let courseLoads = {};
        if (!(this.sessions)) return courseLoads;
        for (const session of this.sessions) {
            let current_half_year = this.sessions[0].slice(0, 4) + SESSION_HALF_YEARS[this.sessions[0].slice(4)];
            for (const enrolment of this.courses[session]) {
                if (enrolment.failed) continue;
                courseLoads[current_half_year] = (courseLoads[current_half_year] || 0) + enrolment.course.units;
            }
        }
        return courseLoads;
    };

    this.checkOverload = function (session, units) {
        let priorUnits = 0;
        let maxSessionUnits = 0;
        let gradesCounted = 0;
        let gradesTotal = 0;
        let previousSessionGradesCounted = 0;
        let previousSessionGradesTotal = 0;
        for (let i = 0; i < this.sessions.indexOf(session); i++) {
            currentSession = this.sessions[i];
            let sessionUnits = 0;
            for (const c of currentSession) {
                if (c.grade !== null) {
                    gradesCounted++;
                    gradesTotal += c;
                    if (i === this.sessions.indexOf(session) - 1) {
                        previousSessionGradesCounted++;
                        previousSessionGradesTotal += c;
                    }
                }
                if (c.failed) continue;
                priorUnits += c.course.units;
                sessionUnits += c.course.units;
            }
            maxSessionUnits = Math.max(maxSessionUnits, sessionUnits);
        }
        const gradeAverage = gradesTotal / gradesCounted;
        const previousSessionGradeAverage = previousSessionGradesTotal / previousSessionGradesCounted;
        const rules = OVERLOAD_RULES[units];
        const satisfied = priorUnits >= rules.units
            && maxSessionUnits >= rules.oneSessionUnits
            && gradeAverage >= rules.overallMark
            && previousSessionGradeAverage >= rules.lastSessionMark;
        return {'sat': satisfied, priorUnits, maxSessionUnits, gradeAverage, previousSessionGradeAverage};
    };

    /**
     * Add a degree to the user's plan.
     * @param code  The text code for the specified degree, e.g. AACRD.
     * @param year  The version of the degree to add, e.g. 2016 version, 2017 version.
     * @return      The Degree if it was added, null if it was already there.
     */
    this.addDegree = async function (code, year) {
        for (const deg of this.degrees) if (deg.code === code) return;
        const refDegree = await getDegreeOffering(code, year);
        let degree = Object.assign({}, refDegree);
        this.degrees.push(degree);
        if (this.degrees.length === 1) return degree;
        for (const deg of this.degrees) {
            deg.units -= 48; // Remove elective unit requirement
        }
        this.changesMade = true;
        return degree;
    };

    this.getDegree = function (code, year) {
        for (const deg of this.degrees) {
            if (deg.code === code) return deg;
        }
    };

    /**
     * Remove a degree from the list of degrees the user is working towards.
     * @param {string} degreeCode    The code of the degree to remove.
     * @returns {boolean}   True if the degree was present and is now removed. False if it was not there.
     */
    this.removeDegree = function (degreeCode) {
        for (let i = 0; i < degrees.size; i++) {
            if (this.degrees[i].code === degreeCode) {
                this.degrees.splice(i, 1);
                this.degrees[0].units += 48; // Re-add elective unit requirement
                this.changesMade = true;
                return true;
            }
        }
        return false;
    };

    /**
     * Add a new session of courses to the plan. The course list for the session will begin empty.
     * If the session is already present, nothing happens.
     * Otherwise the session is added in its correct position.
     * @param session   The session to add to the plan.
     * @return {boolean}    Whether not a new session was added.
     */
    this.addSession = function (session) {
        if (session in this.sessions) return false;
        this.changesMade = true;
        for (let i = 0; i < this.sessions.length; i++) {
            if (!sessionIsAfter(session, this.sessions[i])) {
                this.sessions.splice(i, 0, session);
                this.courses[session] = [];
                return true;
            }
        }
        this.sessions.push(session);
        this.courses[session] = [];
        return true;
    };

    /**
     * Remove a session of courses from the plan. Courses will not be moved anywhere else.
     * @param session   The session to remove.
     * @return {CourseEnrolment[]}  List of courses that were removed. undefined if no such session.
     */
    this.removeSession = function (session) {
        const sessionIndex = this.sessions.indexOf(session);
        if (sessionIndex === -1) return;
        this.sessions.splice(sessionIndex, 1);
        deletedCourses = this.courses[session];
        delete this.courses[session];
        this.changesMade = true;
        return deletedCourses;
    };

    /**
     * addCourse: Register a new course to the plan, in a particular session.
     * The version of the course added will be the one that is offered in the specified session.
     * @param session   The text code of the session, e.g. "2016S1" or "2017Wi" to add the course to.
     * @param code      The text code of the course, e.g. COMP1100.
     * @return {boolean}    true if the course was added, false if the session was not in the plan.
     */
    this.addCourse = async function (session, code) {
        if (!(this.sessions.includes(session))) return false;
        let year = session.slice(0, 4);
        let offering = await getCourseOffering(code, year);
        let enrolment = new CourseEnrolment(offering, session);
        this.courses[session].push(enrolment);
        this.changesMade = true;
        return true;
        //TODO: Throw exception when course doesn't exist or couldn't be retrieved.
    };

    this.removeCourse = function (session, code) {
        if (!(this.sessions.includes(session))) return false;
        courses = this.courses[session];
        for (const i in courses) {
            const enrolment = courses[i];
            if (enrolment.code === code) {
                courses.splice(i, 1);
                this.changesMade = true;
                return true;
            }
        }
        return false;
    };

    this.getCourses = function (code) {
        let matches = [];
        for (const session of this.sessions) {
            for (const course of this.courses[session]) {
                if (course.code === code) matches.push(course);
            }
        }
        return matches;
    };

    this.clearAllCourses = function () {
        for (session of this.sessions) {
            this.courses[session] = [];
        }
        this.changesMade = true;
    };

    /**
     * addMMS: Begin tracking a new major, minor, or specialisation in the plan.
     * Adds the new MMS to the beginning of currently tracked MMSs.
     * @param code  The text code for the specified MMS.
     * @param year  The version of the MMS to add, e.g. 2016 version, 2017 version.
     * @return {boolean}    true if the MMS was added, false if it was already there.
     * @throws {NonExistentMMS} There is no such combination of code and year.
     */
    this.addMMS = async function (code, year) {
        for (const mms of this.trackedMMS) if (mms.code === code) return false;
        let newMMS = await getMMSOffering(code, year);
        this.trackedMMS.unshift(newMMS);
        this.changesMade = true;
        return true;
        //TODO: Throw exception when MMS doesn't exist or couldn't be retrieved.
    };

    this.removeMMS = function (code, year) {
        for (let i in this.trackedMMS) {
            const mms = this.trackedMMS[i];
            if (mms.code === code && mms.year === year) {
                this.trackedMMS.splice(i, 1);
                this.changesMade = true;
                return true;
            }
        }
        return false
    };

    /**
     * Determine whether a particular MMS is currently being tracked in the degree.
     * @param code {string} The code of the MMS to query.
     * @param year {string} The year of the MMS to query. Leave blank to check all possible years of the given code.
     * @returns {boolean}   Whether or not any MMS with the given code (and year) are present in the plan.
     */
    this.trackingMMS = function (code, year = null) {
        for (const mms of this.trackedMMS) {
            if (mms.code === code && (year === null || mms.year === year)) return true;
        }
        return false;
    };

    this.addWarning = function (type, text, actions, positionCode = "") {
        this.changesMade = true;
        let warning = new Warning(type, text, actions, positionCode);
        this.warnings.push(warning);
        return warning
    };

    this.removeWarning = function (type, text) {
        for (const warn of this.warnings) {
            if (warn.type === type && warn.text === text) {
                this.warnings.splice(this.warnings.indexOf(warn), 1);
                this.changesMade = true;
                return warn;
            }
        }
    };

    this.getWarning = function (type, text) {
        for (const warn of this.warnings) {
            if (warn.type === type && warn.text === text) return warn;
        }
    };

    this.getNextSession = function () {
        return nextSession(this.sessions[this.sessions.length - 1]);
    };

    this.clearWarnings = function () {
        this.changesMade = true;
        this.warnings = [];
    };

    this.serializeSimple = function () {
        var d = new Date();

        let saved = {
            degrees: [],
            trackedMMS: [],
            created: d.getDate() + '/' + d.getMonth() + '/' + d.getFullYear(),
            startYear: Infinity,
            name: ""
        };

        for (const degree of this.degrees) {
            if (degree.year < saved.startYear) saved.startYear = degree.year;
            saved.degrees.push(degree.code);
        }

        for (const mms of this.trackedMMS) {
            saved.trackedMMS.push({
                code: mms.code,
                year: mms.year
            })
        }

        if (this.startSem) saved.startSem = this.startSem;
        return JSON.stringify(saved);
    };

    this.serialize = function () {
        let saved = {
            degrees: [],
            sessions: this.sessions,
            courses: {},
            trackedMMS: [],
            warnings: []
        };
        for (const degree of this.degrees) {
            saved.degrees.push({
                code: degree.code,
                year: degree.year
            })
        }
        for (const session in this.courses) {
            if (!this.courses.hasOwnProperty(session)) continue;
            saved.courses[session] = [];
            for (const enrolment of this.courses[session]) {
                let to_add = Object.assign({}, enrolment);
                to_add.course = {
                    code: enrolment.course.code,
                    year: enrolment.course.year
                };
                saved.courses[session].push(to_add);
            }
        }
        for (const mms of this.trackedMMS) {
            saved.trackedMMS.push({
                code: mms.code,
                year: mms.year
            })
        }
        for (const warning of this.warnings) {
            let to_add = {
                type: warning.type,
                text: warning.text,
                actions: []
            };
            for (const action of warning.actions) {
                if (action.toString().includes("boxShadow: '0 0 25px #007bff'")) { // Crude check to see if the action is a scroll-and-glow one
                    const target = action.target;
                    to_add.actions.push({
                        type: 'scroll-and-glow',
                        session: target.siblings().find('.row-ses').text(),
                        code: target.find('.course-code').text()
                    });
                }
            }
            saved.warnings.push(to_add);
        }
        if (this.startSem) saved.startSem = this.startSem;
        return JSON.stringify(saved);

    };

    /**
     * Determine if the current plan is undergrad, postgrad, or both.
     * @return {number}   1 for undergrad, 2 for postgrad, 3 for both.
     */
    this.ugpg = function () {
        let individuals = this.degrees.map(x => x.postgrad);
        if (individuals.includes(false) && individuals.includes(true)) return 3;
        else if (individuals.includes(true)) return 2;
        else if (individuals.includes(false)) return 1;
        else return 0;
    }
}

const SESSION_ORDER = ['Su', 'S1', 'Au', 'Wi', 'S2', 'Sp'];
const SESSION_HALF_YEARS = {
    'Su': 'First',
    'S1': 'First',
    'Au': 'First',
    'Wi': 'Second',
    'S2': 'Second',
    'Sp': 'Second'
};

/**
 * Determine if a particular session comes after another.
 * e.g. 2016S2 comes after 2016S1 and 2016Su (summer) and 2017S1 comes after 2016S2.
 * @param ses1  First session
 * @param ses2  Second session
 * @returns {boolean}   Does ses1 come after ses2?
 */
function sessionIsAfter(ses1, ses2) {
    if (ses1.slice(0, 4) > ses2.slice(0, 4)) return true;
    if (ses1.slice(0, 4) < ses2.slice(0, 4)) return false;
    return SESSION_ORDER.indexOf(ses1.slice(4)) > SESSION_ORDER.indexOf(ses2.slice(4));
}

function nextSession(session, number = 1) {
    let curr_year = session.slice(0, 4);
    let curr_ses = session.slice(4);
    for (let i = 0; i < number; i++) {
        let position = SESSION_ORDER.indexOf(curr_ses);
        if (position === SESSION_ORDER.length - 1) {
            curr_year++;
            curr_ses = SESSION_ORDER[0];
        } else curr_ses = SESSION_ORDER[position + 1]
    }
    return curr_year + curr_ses;
}

const OVERLOAD_RULES = {
    30: {
        'totalUnits': 48,
        'oneSessionUnits': 24,
        'overallMark': 60,
        'lastSessionMark': 60
    },
    36: {
        'totalUnits': 96,
        'oneSessionUnits': 30,
        'overallMark': 70,
        'lastSessionMark': 70
    }
};

function NoSession(message) {
    this.name = "NoSession";
    this.message = message || "";
}

NoSession.prototype = Error.prototype;

function NonExistentMMS(message) {
    this.name = "NonExistentMMS";
    this.message = message || "";
}

NonExistentMMS.prototype = Error.prototype;


function Warning(type, text, actions = [], positionCode) {
    this.type = type;   // e.g. "CourseForceAdded"
    this.text = text;
    this.actions = actions;
    this.positionCode = positionCode; // encoding of the associated card's position on the planner (semester code + plan cell index)

    this.runActions = function () {
        for (const action of this.actions) {
            action();
        }
    }
}
