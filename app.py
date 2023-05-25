from flask import Flask
 

import collections

collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping


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

led_model = api.model('rgbled', {
    'id': fields.Integer(readonly=True, description='The unique identifier'),
    'red_pin': fields.Integer(required=True, description='red GPIO pin'),
    'green_pin': fields.Integer(required=True, description='green GPIO pin'),
    'blue_pin': fields.Integer(required=True, description='blue GPIO pin'),
    'state':  { "red_pin" :  fields.Integer, "green_pin": fields.Integer , "blue_pin": fields.Integer }
   
})



class PinUtil(object):
    def __init__(self,red=0,green=0,blue=0):
        self.counter = 0
        self.leds = []
        led = RGBLED(red=red, green=green, blue=blue)
        led['id'] = self.counter = self.counter + 1
        led['state']= [0,0,0]
        self.leds.append(led)

    def get(self, id):
        for led in self.leds:
            if led['id'] == id:
                return led
        api.abort(404, f"led {id} doesn't exist.")

 


    def update(self, id, data):
        led = self.get(id)
        led.update(data)  # this is the dict_object update method
        return led
 


@ns.route('/')  # keep in mind this our ns-namespace (pins/)
class PinList(Resource):
    """Shows a list of all pins, and lets you POST to add new pins"""

    @ns.marshal_list_with(led_model)
    def get(self):
        """List all pins"""
        return pin_util.leds




@ns.route('/<int:id>')
@ns.response(404, 'pin not found')
@ns.param('id', 'The pin identifier')
class Pin(Resource):
    """Show a single pin item and lets you update/delete them"""

    @ns.marshal_with(led_model)
    def get(self, id):
        """Fetch a pin given its resource identifier"""
        return pin_util.get(id)

 

    @ns.expect(led_model, validate=True)
    @ns.marshal_with(led_model)
    def put(self, id):
        """Update a pin given its identifier"""
        return pin_util.update(id, api.payload)
    
    @ns.expect(led_model)
    def patch(self, id):
        """Partially update a pin given its identifier"""
        return pin_util.update(id, api.payload)

pin_util = PinUtil(12, 13,19)

if __name__ == '__main__':
    app.run(debug=True)
