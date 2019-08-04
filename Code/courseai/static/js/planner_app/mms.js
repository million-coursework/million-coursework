/**
 * Class that represents a Major, Minor, or Specialisation.
 * @param code      ANU's code for the MMS, e.g. THCS-SPEC.
 * @param year      Year of the MMS, for the purpose of rules.
 * @param title     Name of the MMS, e.g. Theoretical Computer...
 * @param rules     Program Requirements (requirements to graduate).
 */
function MMS(code, year, title, rules, extras) {
    this.code = code;
    this.year = year;
    this.title = title;
    this.rules = rules;
    this.extras = extras;

    this.identifier = code + '-' + year;
    this.type = code.split('-')[1]; // Type of MMS, e.g. MAJ, MIN, etc.
    this.units = MMS_TYPE_UNITS[this.type]; // Total number of required units, e.g. 48 for Majors.

    /**
     * Check if this MMS's requirements are satisfied in the given plan.
     * @param plan  The user's plan to check.
     * @returns {{sat: boolean, units: int, rule_details: Array}}
     *      sat:    boolean; Whether or not the MMS requirements were met overall.
     *      units:  int;     The number of units from all courses contributing to this MMS.
     *      rule_details: {sat: boolean, units: int, codes: [string]}[]
     *          Details on satisfying of individual components.
     *          List items are in the same order as the rules themselves.
     *          sat:    Whether or not this particular component was satisfied.
     *          units:  The number of units from courses contributing to this component.
     *          codes:  List of course codes which contributed to this component.
     */
    this.checkRequirements = function (plan) {
        let overall_sat = true;
        let overall_units = 0;
        let rule_details = [];

        let req = this.rules;
        for (let type in req) {
            if (!(req.hasOwnProperty(type))) continue;

            if (["compulsory_courses", "one_from_here", "x_from_here"].includes(type)) {
                for (const section of (type === "compulsory_courses") ? [req[type]] : req[type]) {
                    const courses = (type === "x_from_here") ? section.courses : section;
                    const matches = matchInDegree(plan, new Set(courses.map(cs => cs[0].code))); // TODO: Fix for MMS "OR" requirements
                    let section_units = matches.map(c => c.course.units).reduce((x, y) => x + y, 0);
                    let section_codes = matches.map(c => c.code);
                    let section_sat = true;
                    if (type === "compulsory_courses") section_sat = matches.length === section.length;
                    if (type === "one_from_here") section_sat = matches.length >= 1;
                    if (type === "x_from_here") {
                        if (section.type !== 'maximum') section_sat = section_units >= (section.num || section.units);
                    }
                    section_units = (section.type === 'maximum') ? Math.min(section_units, section.units) : section_units;
                    overall_units += section_units;
                    overall_sat = overall_sat && section_sat;
                    rule_details.push({
                        'type': type, 'sat': section_sat, 'units': section_units, 'codes': section_codes
                    });
                }
            }
            else if (["x_from_category", "max_by_level"].includes(type)) {
                for (const i in req[type]) {
                    const section = req[type][i];
                    let courseCodes = [];
                    let courseLevels = [];
                    let unitThreshold = 0;
                    courseCodes = section["area"] || [];
                    courseLevels = section["level"] || [];
                    unitThreshold = section["units"];
                    const matches = matchCategoryInDegree(plan, courseCodes, courseLevels);
                    let section_units = matches.map(c => c.course.units).reduce((x, y) => x + y, 0);
                    let section_codes = matches.map(c => c.code);
                    let section_sat = true;
                    if (section.type === "minimum") section_sat = section_units >= unitThreshold;
                    if (section.type === "maximum") section_sat = section_units <= unitThreshold;
                    if (section.type === "min_max") {
                        section_sat = section_units >= unitThreshold.minimum && section_units <= unitThreshold.maximum;
                    }
                    overall_units += section_units;
                    overall_sat = overall_sat && section_sat;
                    rule_details.push({'type': type, 'sat': section_sat, 'units': section_units, 'codes': section_codes});

                }
            }
            else if (type === "required_m/m/s".includes(type)) {
            const section = req[type];
                let matched_codes = [];
                let completed_codes = [];
                let units_completed = 0;
                for (const mms of plan.trackedMMS) {
                    if (section.includes(mms.code)) {
                        matched_codes.push(mms.code);
                        const results = mms.checkRequirements(plan);
                        if (results.sat) {
                            completed_codes.push(mms.code);
                            units_completed = Math.max(units_completed, results.units);
                        }
                    }

                }
                let section_sat = completed_codes.length > 0;
                overall_sat = overall_sat && section_sat;
                rule_details.push({
                    'type': type, 'sat': section_sat,
                    'units': units_completed, 'codes': matched_codes, 'completed': completed_codes
                });
            }
        }
        overall_sat = overall_sat && overall_units >= this.units;
        return {'sat': overall_sat, 'units': overall_units, 'rule_details': rule_details};
    }
}

/**
 * Find courses in a plan which have particular codes. Ignore courses which are marked as failed.
 * @param {Plan} plan       The user's plan to check against.
 * @param {string[]} codes  The course codes to look for.
 * @returns {CourseEnrolment[]} A list of CourseEnrolments from the degree which are in the code list.
 */
function matchInDegree(plan, codes) {
    let matches = [];
    for (let session of plan.sessions) {
        const courses = plan.courses[session];
        for (let c of courses) {
            if (!c.failed && codes.delete(c.code)) matches.push(c);
        }
    }
    return matches;
}

/**
 * Dictionary to convert from MMS type code (MAJ/MIN) to required units.
 * @type {{MAJ: number, MIN: number, SPEC: number, HSPC: number}}
 */
const MMS_TYPE_UNITS = {
    "MAJ": 48,
    "MIN": 24,
    "SPEC": 24,
    "HSPC": 48
};

/**
 * Dictionary to convert from MMS type code (MAJ/MIN) to full text.
 * @type {{MAJ: string, MIN: string, SPEC: string, HSPC: string}}
 */
const MMS_TYPE_PRINT = {
    "MAJ": "Major",
    "MIN": "Minor",
    "SPEC": "Specialisation",
    "HSPC": "Honours Specialisation"
};
