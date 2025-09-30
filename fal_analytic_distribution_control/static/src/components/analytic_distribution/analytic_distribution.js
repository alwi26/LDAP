/** @odoo-module */

import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(
    AnalyticDistribution.prototype, {
        setup() {
            super.setup();
            onWillStart(async () => {
                this.group_new_line = await user.hasGroup('fal_analytic_distribution_control.group_analytic_distribution_new_line');
                this.group_new_model = await user.hasGroup('fal_analytic_distribution_control.group_analytic_distribution_new_model');

            });
        },
        get allowSave() {
            if(this.group_new_model){
                return this.props.allow_save && this.state.formattedData.some((line) => this.lineIsValid(line));
            }
            else{
                return false;
            }
        },

        get allowNewLine() {
            if(this.group_new_line){
                return true;
            }
            else{
                return false;
            }
        },

        async save() {
            const summary = this.accountTotalsByPlan();
            let check_alert = false;

            if (summary) {
                for (let planId in summary) {
                    let sumTotal = 0;

                    for (let accId in summary[planId]) {
                        if (summary[planId][accId].total) {
                            sumTotal += summary[planId][accId].total;
                        }
                    }

                    if (sumTotal > 1 && !check_alert) {
                        await this.props.record.discard();
                        await this.props.record.model.load();
                        alert("Analytic Distribution Plan More Than 100%");
                        check_alert = true;
                    }

                    if (check_alert) {
                        break;
                    }
                }

                // Update the record after checking all plans
                this.props.record.update({ [this.props.name]: this.dataToJson() });
            }
        },
    }
);


