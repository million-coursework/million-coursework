function Course(code, sessions) {
    this.code = code;
    this.sessions = sessions || [];

    this.addSession = function (session) {
        if (this.sessions.includes(session)) return;
        this.sessions.push(session)
    }
}

/**
 * Class that represents a course in a particular year.
 * @param {string} code     Course code, e.g. COMP1100.
 * @param {int} year        Version of the course, e.g. 2016, for the 2016 version of COMP1100.
 * @param {string} title    Title of the course.
 * @param {int} units       Number of units the course provides. Usually 6.
 * @param {Object} rules    Course prerequisite and incompatibility rules.
 * @param {Object} extras   Description, learning outcomes, etc.
 * @param {boolean} repeatable  Whether or not this course can be taken across multiple sessions.
 */
function CourseOffering(code, year, title, units, rules, extras, repeatable = false) {
    this.code = code;
    this.year = year;
    this.title = title;
    this.units = units;
    this.rules = rules;
    this.extras = extras;
    this.repeatable = repeatable;

    if (typeof units === "number") {
        this.units = units;
    } else if (units === undefined) {
        this.units = 6;
    } else {
        const bounds = this.units.split(" to ");
        this.units = parseInt(bounds[0]);
        this.maxUnits = parseInt(bounds[1]);
    }

    /**
     * Check if the requirements for this course have been met.
     * @param plan  The degree plan to check requirements against.
     * @param session   The prospective session for this course.
     * @param adding    Default to true, assume that requirements are being checked for the
     *                  adding of a new instance of this course to the session.
     *                  Set to false for evaluating courses that already exist in the plan.
     */
    this.checkRequirements = function (plan, session, adding = true) {
        let incompatible_courses = [];
        let overall_sat = true;
        let res = {};

        let courses_taken = [];
        for (let ses of plan.sessions) {
            if (sessionIsAfter(ses, session) || ses === session) continue;
            Array.prototype.push.apply(courses_taken, plan.courses[ses]);
        }
        let courses_taking = plan.courses[session] || [];

        function checkItem(item) {
            if (/^[A-Z]{4}[0-9]{4}/.test(item)) { // Prerequisite course
                return checkCoursePresent(courses_taken, item)
            } else try {
                const clause = JSON.parse(item);
                if (clause.type === 'co-requisite') {
                    return checkCoursePresent(courses_taken.concat(courses_taking), clause.course);
                } else if ('units' in clause) {
                    const unitsRequired = clause.units;
                    const unitsCompleted = countCourses(courses_taken, function (code) {
                        let areaSat = true;
                        if (clause.areas && clause.areas.length) areaSat = clause.areas.includes(code.slice(0, 4));
                        let levelSat = true;
                        if (clause.levels && clause.levels.length) levelSat = clause.levels.includes(parseInt(code.charAt(4)) * 1000);
                        return areaSat && levelSat;
                    });
                    return unitsCompleted >= unitsRequired;
                }
            } catch (e) {
                if (e.name === 'SyntaxError') return true; // Unreadable clause
                else throw e;
            }
        }

        for (let code of this.rules['incompatible'] || []) {
            if (checkItem(code)) {
                overall_sat = false;
                incompatible_courses.push(code);
            }
        }

        for (let clause of this.rules['pre-requisite'] || []) {
            let clause_sat = false;
            for (let item of clause) {
                if (checkItem(item)) clause_sat = true;
            }
            overall_sat = overall_sat && clause_sat;
        }

        if (this.rules['min-units'] !== undefined && countCourses(courses_taken) < this.rules['min-units']) {
            overall_sat = false;
            res['units'] = this.rules['min-units'];
        }

        const existingUnits = countCourses(courses_taken.concat(courses_taking), x => x===this.code);
        const unitDifference = existingUnits - (this.maxUnits || this.units);
        if (adding && unitDifference >=0 || !adding && unitDifference > 0) {
            overall_sat = false;
            res['duplicate'] = existingUnits;
        }

        res['sat'] = overall_sat;
        res['inc'] = incompatible_courses;
        return res;
    }
}

/**
 * Class that represents a course currently in a plan.
 * @param {CourseOffering} course   CourseOffering object representing the course.
 * @param {string} session          The session that this course is taken in, e.g. 2016S1.
 */
function CourseEnrolment(course, session) {
    this.code = course.code;
    this.course = course;
    this.session = session;

    this.failed = false;    // Default to not failed.
    this.grade = null;      // Do not store grade data by default.
    this.notes = null;      // Do not store notes data by default.

    /**
     * Mark a course as having been failed.
     * @param {boolean} failed    Set to false to remove failed tag. Otherwise defaults to true.
     */
    this.markFailed = function (failed = true) {
        this.failed = failed
    };

    /**
     * Set the student's grade for a course.
     * @param {int} grade   User's grade from 0 to 100.
     */
    this.setGrade = function (grade) {
        this.grade = grade;
    };

    /**
     * Clear the student's grade info for a course.
     */
    this.clearGrade = function () {
        this.grade = null;
    };

    /**
     * Set the student's custom notes for a course.
     * @param {string} notes   User's own custom notes for the course.
     */
    this.setNotes = function (notes) {
        this.notes = notes;
    };

    /**
     * Clear the student's custom notes for a course.
     */
    this.clearNotes = function () {
        this.notes = null;
    };
}

/**
 * Determine if a user has completed a course code within a list of courses.
 * Ignores courses in the list which the user has marked as failed.
 * @param courses   The completed courses to look through.
 * @param code      The course code to search for.
 * @returns {boolean}   Whether the course with the code has been completed without failure.
 */
function checkCoursePresent(courses, code) {
    for (let c of courses) {
        if (c.code !== code || c.failed) continue;
        return true;
    }
    return false;
}

/**
 * Count the units or number of courses in a list of courses.
 * Ignores courses in the list which the user has marked as failed.
 * @param courses   The courses to look through.
 * @param units     Count units (true) or just the number of courses (false).
 * @param filter    A function (code -> boolean) that dictates whether or not a course code should be included in these calculations.
 * @return {number} The final count of units/courses completed without failure.
 */
function countCourses(courses, filter = (() => true), units = true) {
    let count = 0;
    for (let c of courses) {
        if (!filter(c.code) || c.failed) continue;
        count += units ? c.course.units : 1;
    }
    return count;
}