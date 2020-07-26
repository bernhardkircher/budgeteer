import unittest
from datetime import datetime
from app import ExpenseCalculator, DictObject

class ExpenseCalculatorCase(unittest.TestCase):
    def test_calculate_monthly_sum_one_year(self):
        calculator = ExpenseCalculator()
        monthly_expense = DictObject({'type': 1, 'amount': 1, 'start': datetime(2020, 2, 22), 'end': datetime(2022, 2, 22)})
        start = datetime(2020, 2, 22)
        end = datetime(2021, 2, 22)
        total_one_year = calculator.calculate(monthly_expense, start, end)
        self.assertEqual(total_one_year, 12)

    def test_calculate_monthly_sum_expense_start_after_start(self):
        """ if the expense start date is after the queried start date, the expense end date should be used """
        calculator = ExpenseCalculator()
        monthly_expense = DictObject({'type': 1, 'amount': 1, 'start': datetime(2020, 2, 22), 'end': datetime(2022, 2, 22)})
        start_before_expense_start = datetime(2019, 2, 22)
        end = datetime(2021, 2, 22)
        total_one_year = calculator.calculate(monthly_expense, start_before_expense_start, end)
        self.assertEqual(total_one_year, 12)

    def test_calculate_monthly_sum_expense_end_after_end(self):
        """ if the expense end date is after the queried end date, the expense end date should be used """
        calculator = ExpenseCalculator()
        monthly_expense = DictObject({'type': 1, 'amount': 1, 'start': datetime(2020, 2, 22), 'end': datetime(2025, 2, 22)})
        start = datetime(2020, 2, 22)
        end = datetime(2021, 2, 22)
        total_one_year = calculator.calculate(monthly_expense, start, end)
        self.assertEqual(total_one_year, 12)


    def test_calculate_monthly_sum_expense_end_and_start_outside_of_start_end(self):
        """ if the expense end and startdate is outside of queried date, the queried date should be used. """
        calculator = ExpenseCalculator()
        monthly_expense = DictObject({'type': 1, 'amount': 1, 'start': datetime(2019, 2, 22), 'end': datetime(2025, 2, 22)})
        start = datetime(2020, 2, 22)
        end = datetime(2021, 2, 22)
        total_one_year = calculator.calculate(monthly_expense, start, end)
        self.assertEqual(total_one_year, 12)

def main():
    unittest.main()

if __name__ == "__main__":
    main()