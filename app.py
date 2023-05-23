from flask import Flask
from flask_restplus import Api, Resource, fields
from gpiozero import RGBLED
from time import sleep

 

app = Flask(__name__)
api = Api(app,
          version='1.0',
          title='RPI REST',
          description='Raspbery Pi RESTful API',
          doc='/docs')

ns = api.namespace('rgbled', description='RGB Led related operations')

pin_model = api.model('rgbled', {
    'id': fields.Integer(readonly=True, description='The unique identifier'),
    'red_pin': fields.Integer(required=True, description='red GPIO pin'),
    'green_pin': fields.Integer(required=True, description='green GPIO pin'),
    'blue_pin': fields.Integer(required=True, description='blue GPIO pin'),
    'state':  { "red_pin" :  fields.Integer, "green_pin": fields.Integer , "blue_pin": fields.Integer }
   
})



class PinUtil(object):
    def __init__(self):
        self.counter = 0
        self.leds = []

    def get(self, id):
        for led in self.leds:
            if led['id'] == id:
                return led
        api.abort(404, f"led {id} doesn't exist.")

    def create(self, data):
        led =RGBLED( 'red_pin':)
        led['id'] = self.counter = self.counter + 1
        led['state']= [0,0,0]
        self.leds.append(led)
        return led

    def update(self, id, data):
        led = self.get(id)
        led.update(data)  # this is the dict_object update method
        return led

    def delete(self, id):
        led = self.get(id)
        GPIO.output(pin['pin_num'], GPIO.LOW)
        self.leds.remove(led)


@ns.route('/')  # keep in mind this our ns-namespace (pins/)
class PinList(Resource):
    """Shows a list of all pins, and lets you POST to add new pins"""

    @ns.marshal_list_with(pin_model)
    def get(self):
        """List all pins"""
        return pin_util.pins

    @ns.expect(pin_model)
    @ns.marshal_with(pin_model, code=201)
    def post(self):
        """Create a new pin"""
        return pin_util.create(api.payload)


@ns.route('/<int:id>')
@ns.response(404, 'pin not found')
@ns.param('id', 'The pin identifier')
class Pin(Resource):
    """Show a single pin item and lets you update/delete them"""

    @ns.marshal_with(pin_model)
    def get(self, id):
        """Fetch a pin given its resource identifier"""
        return pin_util.get(id)

    @ns.response(204, 'pin deleted')
    def delete(self, id):
        """Delete a pin given its identifier"""
        pin_util.delete(id)
        return '', 204

    @ns.expect(pin_model, validate=True)
    @ns.marshal_with(pin_model)
    def put(self, id):
        """Update a pin given its identifier"""
        return pin_util.update(id, api.payload)
    
    @ns.expect(pin_model)
    @ns.marshal_with(pin_model)
    def patch(self, id):
        """Partially update a pin given its identifier"""
        return pin_util.update(id, api.payload)




pin_util = PinUtil()
pin_util.create({'red_pin': 12, 'green_pin': 13,'blue_pin': 19, 'state':[0,0,0]})



if __name__ == '__main__':
    app.run(debug=True)
