from flask import Flask
from flask_restful import Resource, Api
import sys
from flask_restful import reqparse
from flask_restful import inputs
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask import abort
from flask import request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar1.db'
api = Api(app)
db = SQLAlchemy(app)


class EventRow(db.Model):  # this class model can be converted into a table with __tablename__ and fields as below.
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    event = db.Column(db.String(120), nullable=False)


db.create_all()

# define and add resources


class EventToday(Resource):
    def get(self):
        today_events = EventRow.query.filter(EventRow.date == datetime.date.today()).all()
        serialized_today_events = [{
            'id': ev.id,
            'event': ev.event,
            'date': str(ev.date)
        }
            for ev in today_events
        ]
        return serialized_today_events


api.add_resource(EventToday, "/event/today")


class Event(Resource):
    def post(self):
        args = my_parser.parse_args()
        user_event = EventRow(event=args['event'], date=args['date'].date())
        db.session.add(user_event)
        db.session.commit()
        return {
            "message": "The event has been added!",
            "event": args['event'],
            "date": str(args['date'].date())
        }

    def get(self):
        start_time = request.args.get('start_time', default='1999-01-01', type=str)
        end_time = request.args.get('end_time', default='2999-12-31', type=str)
        all_events = EventRow.query.filter(EventRow.date.between(start_time, end_time)).all()
        serialized_all_events = [{
            'id': ev.id,
            'event': ev.event,
            'date': str(ev.date)
        }
            for ev in all_events
        ]
        return serialized_all_events


api.add_resource(Event, '/event')


class EventByID(Resource):
    def get(self, event_id):
        requested_event = EventRow.query.filter(EventRow.id == event_id).first()
        if requested_event is None:
            abort(404, "The event doesn't exist!")
        return dict(id=requested_event.id, event=requested_event.event, date=str(requested_event.date))

    def delete(self, event_id):
        requested_event = EventRow.query.filter(EventRow.id == event_id).first()
        if requested_event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(requested_event)
            db.session.commit()
            return {
                "message": "The event has been deleted!"
            }


api.add_resource(EventByID, '/event/<int:event_id>')

# instantiate parser to parse post request arguments
my_parser = reqparse.RequestParser()
my_parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
my_parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()