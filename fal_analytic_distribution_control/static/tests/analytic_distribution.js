/** @odoo-module */

import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";
import { makeTestEnv, createComponent, createService } from "@web/../tests/helpers/mock_services";
import { QUnit } from "@web/qunit";

QUnit.module("AnalyticDistribution", (hooks) => {
    let env;

    hooks.beforeEach(async () => {
        env = await makeTestEnv();
        patch(AnalyticDistribution.prototype, {
            setup() {
                super.setup();
                this.user = createService({
                    async hasGroup(group) {
                        return group === 'fal_analytic_distribution_control.group_analytic_distribution_new_line' ||
                               group === 'fal_analytic_distribution_control.group_analytic_distribution_new_model';
                    }
                });
                onWillStart(async () => {
                    this.group_new_line = await this.user.hasGroup('fal_analytic_distribution_control.group_analytic_distribution_new_line');
                    this.group_new_model = await this.user.hasGroup('fal_analytic_distribution_control.group_analytic_distribution_new_model');
                });
            },
        });
    });

    QUnit.test("allowSave returns correct value", async (assert) => {
        const component = await createComponent(env, AnalyticDistribution, {
            props: { allow_save: true },
            state: { formattedData: [{ valid: true }] },
        });

        assert.strictEqual(component.allowSave, true, "allowSave should return true when group_new_model is true and allow_save is true");

        component.group_new_model = false;
        assert.strictEqual(component.allowSave, false, "allowSave should return false when group_new_model is false");
    }, { tags: ['cluedoo'] });

    QUnit.test("allowNewLine returns correct value", async (assert) => {
        const component = await createComponent(env, AnalyticDistribution);

        assert.strictEqual(component.allowNewLine, true, "allowNewLine should return true when group_new_line is true");

        component.group_new_line = false;
        assert.strictEqual(component.allowNewLine, false, "allowNewLine should return false when group_new_line is false");
    }, { tags: ['cluedoo'] });

    QUnit.test("save method works correctly", async (assert) => {
        const component = await createComponent(env, AnalyticDistribution, {
            props: { record: { discard: async () => {}, model: { load: async () => {} }, update: async () => {} }, name: "test" },
        });

        const spyDiscard = sinon.spy(component.props.record, "discard");
        const spyLoad = sinon.spy(component.props.record.model, "load");
        const spyUpdate = sinon.spy(component.props.record, "update");

        // Simulate data that causes alert
        component.state = {
            formattedData: [{ total: 0.5 }, { total: 0.6 }],
        };

        await component.save();
        assert.ok(spyDiscard.calledOnce, "record.discard should be called once");
        assert.ok(spyLoad.calledOnce, "record.model.load should be called once");
        assert.ok(spyUpdate.notCalled, "record.update should not be called when sumTotal > 1");

        // Reset spies and simulate data that does not cause alert
        spyDiscard.resetHistory();
        spyLoad.resetHistory();
        component.state = {
            formattedData: [{ total: 0.5 }, { total: 0.4 }],
        };

        await component.save();
        assert.ok(spyDiscard.notCalled, "record.discard should not be called when sumTotal <= 1");
        assert.ok(spyLoad.notCalled, "record.model.load should not be called when sumTotal <= 1");
        assert.ok(spyUpdate.calledOnce, "record.update should be called once");
    }, { tags: ['cluedoo'] });
});
