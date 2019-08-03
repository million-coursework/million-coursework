function Search(plan) {
    this.plan = plan;
    this.requests = {
        'course': null,
        'major': null,
        'minor': null,
        'spec': null
    };
    this.filters = [];

    this.courseSearch = function (query, before, after) {
        const plan = this.plan;
        if (this.requests['course'] !== null) this.requests['course'].abort();
        let activeFilters = this.filters;
        let filters = {
            'codes': [],
            'levels': [],
            'sessions': [],
        };

        if (this.plan.ugpg() === 1) filters['level'] = 'Undergraduate';
        if (this.plan.ugpg() === 2) filters['level'] = 'Postgraduate';
        // No 'level' key returns both UG and PG courses.

        for (let f of activeFilters) {
            if (f.type === 'level') filters.levels.push(f.data);
            else if (f.type === 'code') filters.codes.push(f.data);
            else {
                filters['sessions'].push({
                    year: parseInt(f.data.slice(0, 4)),
                    semester: SESSION_WORDS[f.data.slice(4)]});
            }
        }
        this.requests['course'] = $.ajax({
            url: 'search/coursesearch',
            data: {
                'query': query,
                'filters': JSON.stringify(filters)
            },
            type: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            beforeSend: before,
            success: function (data) {
                let new_data = [];
                let filtered_sessions = [];
                for (const filter of activeFilters) {
                    if (filter.type === 'session') filtered_sessions.push(filter.data);
                }
                if (!filtered_sessions.length) {    // Skip getting course data if no session filters.
                    after(data.response);
                    return;
                }
                let course_action_items = {};   // Get course data so that prerequisites can be checked.
                for (const course of data.response) {
                    const code = course['course_code'];
                    if (!(code in course_action_items)) course_action_items[code + '-' + THIS_YEAR] = [];
                    course_action_items[code + '-' + THIS_YEAR].push(function (offering) {
                        let matched_filters = !filtered_sessions.length;
                        for (const session of filtered_sessions) {
                            const checked = offering.checkRequirements(plan, session).sat;
                            const offered = offering.extras.sessions.includes(SESSION_WORDS[session.slice(4)]);
                            matched_filters = matched_filters || (checked && offered);
                        }
                        if (matched_filters) new_data.push(course)
                    })
                }
                batchCourseOfferingActions(course_action_items).then(function () {
                    after(new_data);
                });
            },
            error: console.log('Course search aborted or failed. '),
            complete: console.log('Course search initiated. ')
        })
    };

    this.mmsSearch = function (query, before, after) {
        for (let type in this.requests) {
            if (type !== 'course' && this.requests[type] !== null) this.requests[type].abort();
        }
        before();
        let body = {'query': query};
        if (this.plan.ugpg() === 1) body['level'] = 'undergraduate';
        if (this.plan.ugpg() === 2) body['level'] = 'postgraduate';
        // No 'level' key returns both UG and PG courses.
        if (this.plan.ugpg() !== 2) {
            this.requests['major'] = $.ajax({
                url: 'search/majors',
                type: 'GET',
                data: body,
                dataType: 'json',
                contentType: 'application/json',
                success: function (data) {
                    after(data, 'major')
                },
                error: console.log('Major search aborted or failed. '),
                complete: console.log('Major search initiated. ')
            });
            this.requests['minor'] = $.ajax({
                url: 'search/minors',
                type: 'GET',
                data: body,
                dataType: 'json',
                contentType: 'application/json',
                success: function (data) {
                    after(data, 'minor')
                },
                error: console.log('Minor search aborted or failed. '),
                complete: console.log('Minor search initiated. ')
            });
        }
        this.requests['spec'] = $.ajax({
            url: 'search/specs',
            type: 'GET',
            data: body,
            dataType: 'json',
            contentType: 'application/json',
            success: function (data) {
                after(data, 'specialisation')
            },
            error: console.log('Specialisation search aborted or failed. '),
            complete: console.log('Specialisation search initiated. ')
        });
    };

    this.addFilter = function (type, data) {
        if (this.getFilter(type, data) !== null) return false;
        const filter = new Filter(type, data);
        this.filters.push(filter);
        return filter;
    };

    this.deleteFilter = function (type, data) {
        let filter = this.getFilter(type, data);
        if (filter !== null) this.filters.splice(this.filters.indexOf(filter), 1);
        return filter || false;
    };

    this.getFilter = function (type, data) {
        for (const filter of this.filters) {
            if (filter.type === type && filter.data === data) return filter;
        }
        return null;
    }
}

function Filter(type, data) {
    this.type = type;   // "code", "level", or "session"
    this.data = data;   // e.g. "COMP", "2000", or "2016S1"

    this.toString = function () {
        if (type === 'session') {
            const year = this.data.slice(0, 4);
            const ses = this.data.slice(4);
            return "My " + year + " " + SESSION_WORDS[ses];
        } else return this.data;
    }
}
