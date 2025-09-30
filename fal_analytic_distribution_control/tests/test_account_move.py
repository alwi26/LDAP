from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged

@tagged("at_install", "cluedoo")
class TestAccountMove(TransactionCase):

    def setUp(self):
        super(TestAccountMove, self).setUp()

        # Create a dummy analytic account and a plan
        self.analytic_plan = self.env['account.analytic.plan'].create({'name': 'Test Plan'})
        self.analytic_account1 = self.env['account.analytic.account'].create({
            'name': 'Test Account 1',
            'plan_id': self.analytic_plan.id
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Partner'
        })
        
        # Create a dummy account move
        self.account_move = self.env['account.move'].create({
            'name': 'Test Move',
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Line 1',
                'product_id': self.env.ref("product.product_product_4").id,
                'analytic_distribution': {
                    str(self.analytic_account1.id): 50,  # Set to 50% initially
                },
                'price_unit': 100.0,
                'quantity': 1.0,
            })]
        })

    def test_action_post_valid_distribution(self):
        """Test that action_post works with valid analytic distribution"""
        self.account_move.action_post()
        # If no exception is raised, the test is successful

    def test_action_post_invalid_distribution(self):
        """Test that action_post raises UserError with invalid analytic distribution"""
        # Modify the analytic distribution to sum to more than 100%
        self.account_move.invoice_line_ids[0].analytic_distribution = {
            str(self.analytic_account1.id): 110,  # Set to 110% to trigger the error
        }
        with self.assertRaises(UserError):
            self.account_move.action_post()

    def test_action_post_empty_analytic_distribution(self):
        """Test action_post with empty analytic distribution"""
        self.account_move.invoice_line_ids[0].analytic_distribution = {}
        self.account_move.action_post()
        # If no exception is raised, the test is successful
