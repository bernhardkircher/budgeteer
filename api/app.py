from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api, fields, marshal_with,marshal, reqparse, inputs

#https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api

app = Flask(__name__)
api = Api(app)


class DictObject(dict):
    def __init__(self, d):
        self.update(d)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class BudgeteerDataAccess:

    INCOMES = [
        DictObject({'id': '1', 'type': 1, 'amount': 1234, 'start': datetime(2020, 2, 22), 'end': datetime(2022, 11, 28)}),
        DictObject({'id': '2', 'type': 2, 'amount': 21323, 'start': datetime(2020, 2, 22), 'end': datetime(2020, 11, 28)})
    ]


    def get_all_expenses(self):
        return BudgeteerDataAccess.INCOMES

    def get(self, id: str):
        return BudgeteerDataAccess.INCOMES[int(id)-1]

    def add(self, type: int, amount: int, start: datetime, end: datetime):
        entry = DictObject({'id': len(BudgeteerDataAccess.INCOMES) + 1,  'type': type, 'amount': amount, 'start': start, 'end': end})
        BudgeteerDataAccess.INCOMES.append(entry)
        return entry

    def update(self, entry):
        # nothing to do right now.
        return entry

    def delete(self, id: str):
        # this will obviously not work, becuase we will get 
        # same id twice, since we use the array length for id generation...
        del BudgeteerDataAccess.INCOMES[int(id)-1]

    def get_in_range(self, start: datetime, end: datetime):
        return list(filter(lambda x: x.end >= start or (end is None or x.start <= end), BudgeteerDataAccess.INCOMES))
        


expense_parser = reqparse.RequestParser()
# TODO add meaningfull description.
expense_parser.add_argument('amount', required=True, type=int, help='Amount is a required integer.')
expense_parser.add_argument('start', required=True, type=inputs.datetime_from_iso8601)
expense_parser.add_argument('end', required=False, type=inputs.datetime_from_iso8601, help='end is an optional datetime.')
expense_parser.add_argument('type', required=True, type=int, help='type is a required int.')


entry_fields = {
    'uri': fields.Url('expense', absolute=True),
    'amount': fields.Integer(),
    'start': fields.DateTime(dt_format='iso8601'),
    'end': fields.DateTime(dt_format='iso8601'),
    'type': fields.Integer(),
}


class Expense(Resource):

    def __init__(self):
        self.data_access = BudgeteerDataAccess()

    @marshal_with(entry_fields)
    def get(self, id):
        return self.data_access.get(id)
    
    def delete(self, id):
        self.data_access.delete(id)
        return '', 204

    @marshal_with(entry_fields)
    def put(self, id):
        args = expense_parser.parse_args()
        amount = args['amount']
        start = args['start']
        end = args['end']
        type = args['type']
        entry = self.data_access.get(id)
        entry.amount = amount
        entry.type = type
        entry.start = start
        entry.end = end
        return self.data_access.update(entry)


api.add_resource(Expense, '/expense/<string:id>')


expense_query_parser = reqparse.RequestParser()
expense_query_parser.add_argument('start', required=False, type=inputs.datetime_from_iso8601)
expense_query_parser.add_argument('end', required=False, type=inputs.datetime_from_iso8601)


list_fields = {
    'entries': fields.List(fields.Nested(entry_fields)),
    'total': fields.Integer(),
}


class ExpenseCalculator:
    def calculate(self, expense, start, end):
        """ calcualtes the toal amount of the given expense within the given perioud """
        if expense.type == 1:
            return self._calculate_monthly_expense(expense, start, end)
        
        # todo throw an error - unsupported type.
        return 0

    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    def _calculate_monthly_expense(self, expense, start, end):
        # get number of months that the expense is valid.
        if expense.start > start:
            start = expense.start
        
        if end > expense.end:
            end = expense.end

        months = ExpenseCalculator.diff_month(end, start)
        # there could be a rounding error, e.g. half a month.. etc but I ignore this for now.
        return months * expense.amount

class ExpenseList(Resource):

    def __init__(self):
        self.data_access = BudgeteerDataAccess()

    @marshal_with(list_fields)
    def get(self):
        args = expense_query_parser.parse_args()
        start = args['start']
        # todo calculate sum etc.
        if not start:
            return self.data_access.get_all_expenses()

        end = args['end']
        entries = self.data_access.get_in_range(start, end)
        total = 0
        calculator = ExpenseCalculator()
        for entry in entries:
            total = total + calculator.calculate(entry, start, end)

        return { 'entries' : entries, 'total': total }

    @marshal_with(entry_fields)
    def post(self):
        args = expense_parser.parse_args()
        amount = args['amount']
        start = args['start']
        end = args['end']
        if not end:
            end = start

        type = args['type']
        entry = self.data_access.add(type, amount, start, end)
        return entry
        

api.add_resource(ExpenseList, '/expense')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


# TODO use file as data store. file needs to be mapped to host os