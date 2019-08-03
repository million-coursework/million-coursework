const MIN_AUTOSAVE_INTERVAL = 2000; // Minimum time between autosaves, even if multiple actions are performed.

function AutoSave(plan, code) {
    this.plan = plan;
    this.code = code;

    this.intervalID = null;

    this.enableSaving = function () {   // Turn on the saving loop (it is off on object creation).
        if (this.intervalID !== null) return;
        this.intervalID = setInterval(this.save.bind(this), MIN_AUTOSAVE_INTERVAL);
    };

    this.disableSaving = function () {  // Turn off the saving loop.
        clearInterval(this.intervalID);
        this.intervalID = null;
    };

    this.save = function () {
        if (!this.plan.changesMade) return;    // Check if the plan needs saving.
        
        if (loggedIn && this.code) { // update degree plan details on the user's profile
            $.ajax({
                url: 'accounts/degree_plan_view',
                method: 'PUT',
                data: {
                    "mode": "PLAN",
                    "code": this.code,
                    "plan": this.plan.serializeSimple()
                },
                dataType: 'json',
                contentType: 'application/json',
                success: function(data) {
                    console.log("Degree plan saved to user profile." );
                }
            })
        }
        
        if (this.code) {    // Code present. Use update endpoint.
            $.ajax({
                url: 'degree/stored_plans',
                method: 'PUT',
                data: {
                    "code": this.code,
                    "plan": this.plan.serialize()
                },
                dataType: 'json',
                contentType: 'application/json',
            })
        } else {    // Code not present. Use store endpoint.
            const autoSaver = this;
            $.ajax({
                url: 'degree/stored_plans',
                method: 'POST',
                data: {
                    "plan": this.plan.serialize()
                },
                dataType: 'json',
                contentType: 'application/json',
                success: function (data) {
                    console.log('store success, code = ' + data.response);
                    if (data.response) autoSaver.code = data.response;
                    CS.setCode(data.response);  // Store the new code in a cookie.
                    save_code = data.response; // TODO: Find a way to uncouple these two lines.
                }
            })
        }
        this.plan.changesMade = false;
    };
}
